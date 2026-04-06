#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from pymatgen.core import Structure
from pymatgen.io.vasp import Poscar


PRESETS = {
    "metal-relax": {"kmesh": (16, 16, 16), "is_metal": True, "isif": 3, "nsw": 120, "d3": "none"},
    "bulk-relax": {"kmesh": (8, 8, 8), "is_metal": False, "isif": 3, "nsw": 120, "d3": "none"},
    "correlated-relax": {"kmesh": (6, 6, 4), "is_metal": False, "isif": 3, "nsw": 120, "d3": "none"},
    "adsorption-relax": {"kmesh": (4, 4, 1), "is_metal": False, "isif": 2, "nsw": 120, "d3": "bj"},
    "static-dos": {"kmesh": (10, 10, 10), "is_metal": False, "isif": 2, "nsw": 0, "d3": "none"},
    "optics-static": {"kmesh": (12, 12, 12), "is_metal": False, "isif": 2, "nsw": 0, "d3": "none"},
}

DEFAULT_POTCAR_MAP = {
    "Sm": "Sm_3",
    "Ni": "Ni_pv",
    "O": "O",
    "H": "H",
    "Pt": "Pt",
    "La": "La",
    "Al": "Al",
}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def relative_display(path: Path, base: Path) -> str:
    return os.path.relpath(str(path), str(base))


def infer_project_root(job_dir: Path) -> Path:
    for candidate in [job_dir] + list(job_dir.parents):
        if (candidate / "workflow").exists() and (candidate / "runs").exists():
            return candidate
    return Path.cwd().resolve()


def unique_species_order(structure: Structure) -> list[str]:
    ordered: list[str] = []
    for site in structure:
        symbol = site.specie.symbol
        if symbol not in ordered:
            ordered.append(symbol)
    return ordered


def reorder_structure(structure: Structure, species_order: list[str]) -> Structure:
    indexed_sites = list(enumerate(structure))
    indexed_sites.sort(
        key=lambda item: (
            species_order.index(item[1].specie.symbol),
            item[1].frac_coords[0],
            item[1].frac_coords[1],
            item[1].frac_coords[2],
            item[0],
        )
    )
    lattice = structure.lattice
    species = [site.specie for _, site in indexed_sites]
    frac_coords = [site.frac_coords for _, site in indexed_sites]
    return Structure(lattice, species, frac_coords)


def kpoints_text(mesh: tuple[int, int, int]) -> str:
    return (
        "Automatic mesh\n"
        "0\n"
        "Gamma\n"
        f"{mesh[0]} {mesh[1]} {mesh[2]}\n"
        "0 0 0\n"
    )


def detect_potcar_root(explicit: Path | None) -> Path | None:
    if explicit:
        return explicit.expanduser().resolve()
    for key in ("PMG_VASP_PSP_DIR", "VASP_PSP_DIR", "VASP_POTCAR_ROOT", "POTCAR_ROOT"):
        value = os.environ.get(key)
        if value:
            return Path(value).expanduser().resolve()
    return None


def parse_assignments(values: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in values:
        if "=" not in item:
            raise ValueError(f"Expected KEY=VALUE assignment, got: {item}")
        key, value = item.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def build_magmom(structure: Structure, u_element: str | None, afm_element: str | None) -> list[float]:
    magmom: list[float] = []
    counters: dict[str, int] = {}
    active = {element for element in (u_element, afm_element) if element}
    for site in structure:
        symbol = site.specie.symbol
        if afm_element and symbol == afm_element:
            index = counters.get(symbol, 0)
            magmom.append(1.0 if index % 2 == 0 else -1.0)
            counters[symbol] = index + 1
        elif symbol in active:
            magmom.append(1.0)
        else:
            magmom.append(0.0)
    return magmom


def format_magmom(values: list[float]) -> str:
    return " ".join(f"{value:.1f}" for value in values)


def build_potcar(species_order: list[str], potcar_root: Path, mapping: dict[str, str], dst: Path) -> None:
    chunks: list[str] = []
    for element in species_order:
        label = mapping.get(element, element)
        potcar_path = potcar_root / label / "POTCAR"
        if not potcar_path.exists():
            raise FileNotFoundError(
                f"Missing POTCAR for {element}: {relative_display(potcar_path, Path.cwd().resolve())}"
            )
        chunks.append(potcar_path.read_text())
    dst.write_text("".join(chunks))


def render_incar(args: argparse.Namespace, structure: Structure, species_order: list[str]) -> str:
    preset = PRESETS[args.preset]
    is_metal = preset["is_metal"] or args.metal
    spin_polarized = args.preset == "correlated-relax" or bool(args.u_element) or bool(args.afm_element)

    lines = [
        f"SYSTEM = {args.system}",
        "PREC = Accurate",
        f"ENCUT = {args.encut}",
        f"EDIFF = {args.ediff:g}",
        f"EDIFFG = {args.ediffg:g}",
        "NELM = 120",
        "LASPH = .TRUE.",
        "ADDGRID = .TRUE.",
        "LREAL = .FALSE.",
        "ALGO = Normal",
        f"NCORE = {args.ncore}",
        "LWAVE = .FALSE.",
        "LCHARG = .TRUE.",
    ]
    if args.functional == "pbesol":
        lines.append("GGA = PS")

    if preset["nsw"] > 0:
        lines.extend(
            [
                "IBRION = 2",
                f"NSW = {preset['nsw']}",
                f"ISIF = {preset['isif']}",
            ]
        )
    else:
        lines.extend(["IBRION = -1", "NSW = 0", "ISIF = 2"])

    if is_metal:
        lines.extend(["ISMEAR = 1", "SIGMA = 0.20"])
    else:
        lines.extend(["ISMEAR = 0", "SIGMA = 0.05"])

    if spin_polarized:
        magmom = build_magmom(structure, args.u_element, args.afm_element)
        lines.append("ISPIN = 2")
        if any(abs(value) > 1e-8 for value in magmom):
            lines.append(f"MAGMOM = {format_magmom(magmom)}")
        lines.append("ISYM = 0")
    else:
        lines.append("ISPIN = 1")

    if args.u_element:
        if args.u_value is None:
            raise ValueError("--u-value is required when --u-element is provided.")
        ldaul = []
        ldauu = []
        ldauj = []
        for element in species_order:
            if element == args.u_element:
                ldaul.append(str(args.u_orbital))
                ldauu.append(f"{args.u_value:.1f}")
                ldauj.append("0")
            else:
                ldaul.append("-1")
                ldauu.append("0")
                ldauj.append("0")
        lines.extend(
            [
                "LDAU = .TRUE.",
                "LDAUTYPE = 2",
                f"LDAUL = {' '.join(ldaul)}",
                f"LDAUU = {' '.join(ldauu)}",
                f"LDAUJ = {' '.join(ldauj)}",
                f"LMAXMIX = {6 if args.u_orbital == 3 else 4}",
                "LDAUPRINT = 1",
            ]
        )

    d3_mode = preset["d3"] if args.d3 == "auto" else args.d3
    if d3_mode == "zero":
        lines.append("IVDW = 11")
    elif d3_mode == "bj":
        lines.append("IVDW = 12")

    if args.preset == "static-dos":
        lines.extend(["LORBIT = 11", "NEDOS = 2000"])
    elif args.preset == "optics-static":
        lines.extend(["LORBIT = 11", "NEDOS = 2000", "LOPTICS = .TRUE.", "CSHIFT = 0.100"])

    lines.extend(args.extra_incar)
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a VASP job directory from a structure file.")
    parser.add_argument("--structure", type=Path, required=True, help="Input structure file.")
    parser.add_argument("--job-dir", type=Path, required=True, help="Job directory to create.")
    parser.add_argument("--preset", choices=sorted(PRESETS), required=True, help="Job preset.")
    parser.add_argument("--system", required=True, help="SYSTEM tag value.")
    parser.add_argument("--species-order", nargs="+", help="Species order for POSCAR and POTCAR.")
    parser.add_argument("--kmesh", nargs=3, type=int, help="Explicit k-point mesh.")
    parser.add_argument("--functional", choices=["pbe", "pbesol"], default="pbesol")
    parser.add_argument("--encut", type=int, default=520)
    parser.add_argument("--ediff", type=float, default=1e-6)
    parser.add_argument("--ediffg", type=float, default=-0.02)
    parser.add_argument("--ncore", type=int, default=2)
    parser.add_argument("--u-element", help="Element receiving +U.")
    parser.add_argument("--u-value", type=float, help="Ueff value.")
    parser.add_argument("--u-orbital", type=int, default=2, help="Angular momentum channel for +U.")
    parser.add_argument("--afm-element", help="Element to initialize with alternating moments.")
    parser.add_argument("--metal", action="store_true", help="Force metallic smearing.")
    parser.add_argument("--d3", choices=["auto", "none", "zero", "bj"], default="auto")
    parser.add_argument("--potcar-root", type=Path, help="Explicit POTCAR root.")
    parser.add_argument("--potcar-map", action="append", default=[], help="Override POTCAR labels with ELEMENT=LABEL.")
    parser.add_argument("--skip-potcar", action="store_true", help="Skip POTCAR generation.")
    parser.add_argument("--extra-incar", action="append", default=[], help="Append raw INCAR lines like KEY = VALUE.")
    args = parser.parse_args()

    structure = Structure.from_file(args.structure.expanduser().resolve())
    species_order = args.species_order or unique_species_order(structure)
    ordered = reorder_structure(structure, species_order)

    job_dir = args.job_dir.expanduser().resolve()
    ensure_dir(job_dir)
    Poscar(ordered).write_file(job_dir / "POSCAR")

    preset = PRESETS[args.preset]
    kmesh = tuple(args.kmesh) if args.kmesh else preset["kmesh"]
    (job_dir / "KPOINTS").write_text(kpoints_text(kmesh))
    (job_dir / "INCAR").write_text(render_incar(args, ordered, species_order))

    potcar_written = False
    potcar_root = detect_potcar_root(args.potcar_root)
    if not args.skip_potcar:
        if not potcar_root:
            raise RuntimeError("No POTCAR root detected. Use --potcar-root or set a VASP pseudopotential environment variable.")
        mapping = DEFAULT_POTCAR_MAP | parse_assignments(args.potcar_map)
        build_potcar(species_order, potcar_root, mapping, job_dir / "POTCAR")
        potcar_written = True

    display_root = infer_project_root(job_dir)
    metadata = {
        "preset": args.preset,
        "system": args.system,
        "structure": relative_display(args.structure.expanduser().resolve(), display_root),
        "job_dir": relative_display(job_dir, display_root),
        "species_order": species_order,
        "kmesh": list(kmesh),
        "functional": args.functional,
        "u_element": args.u_element,
        "u_value": args.u_value,
        "afm_element": args.afm_element,
        "d3": preset["d3"] if args.d3 == "auto" else args.d3,
        "potcar_root": relative_display(potcar_root, display_root) if potcar_root else None,
        "potcar_written": potcar_written,
    }
    (job_dir / "job_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
