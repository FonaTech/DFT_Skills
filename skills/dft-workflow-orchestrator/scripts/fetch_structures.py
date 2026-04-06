#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import urllib.request
from pathlib import Path
from typing import Any

from pymatgen.core import Structure
from pymatgen.core.surface import SlabGenerator
from pymatgen.io.vasp import Poscar
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer


PLACEHOLDER_PATTERN = re.compile(r"\{\{[^{}]+\}\}")


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def preset_root() -> Path:
    return skill_root() / "presets"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def relative_display(path: Path, base: Path) -> str:
    return os.path.relpath(str(path), str(base))


def detect_mp_api_key() -> str | None:
    for key in ("MP_API_KEY", "PMG_MAPI_KEY", "MAPI_KEY"):
        value = os.environ.get(key)
        if value:
            return value
    return None


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


def normalize_structure(structure: Structure, mode: str) -> Structure:
    if mode == "none":
        return structure
    analyzer = SpacegroupAnalyzer(structure, symprec=1e-2)
    if mode == "conventional":
        return analyzer.get_conventional_standard_structure()
    if mode == "primitive":
        return analyzer.get_primitive_standard_structure()
    raise ValueError(f"Unsupported normalization mode: {mode}")


def fetch_cod(cod_id: str, dst: Path) -> dict[str, Any]:
    url = f"https://www.crystallography.net/cod/{cod_id}.cif"
    with urllib.request.urlopen(url, timeout=60) as response:
        dst.write_bytes(response.read())
    return {"source": "cod", "value": cod_id, "url": url}


def fetch_url(url: str, dst: Path) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=60) as response:
        dst.write_bytes(response.read())
    return {"source": "url", "url": url}


def fetch_mp(material_id: str, dst: Path) -> dict[str, Any]:
    api_key = detect_mp_api_key()
    if not api_key:
        raise RuntimeError("Materials Project API key is not set.")
    from mp_api.client import MPRester

    with MPRester(api_key) as rester:
        structure = rester.get_structure_by_material_id(material_id, conventional_unit_cell=True)
    structure.to(filename=str(dst))
    return {"source": "mp", "value": material_id}


def fetch_file(src: Path, dst: Path) -> dict[str, Any]:
    shutil.copy2(src, dst)
    return {"source": "file"}


def materialize_raw_file(entry: dict[str, Any], raw_dir: Path, source_base: Path) -> tuple[Path, dict[str, Any]]:
    filename = entry.get("filename") or f"{entry['label']}.cif"
    dst = raw_dir / filename
    if dst.exists():
        return dst, {"source": entry["source"], "cached": True}

    source = entry["source"]
    if source == "cod":
        return dst, fetch_cod(str(entry["value"]), dst)
    if source == "url":
        return dst, fetch_url(str(entry["value"]), dst)
    if source == "mp":
        return dst, fetch_mp(str(entry["value"]), dst)
    if source == "file":
        raw_value = Path(str(entry["value"])).expanduser()
        source_path = raw_value if raw_value.is_absolute() else (source_base / raw_value)
        return dst, fetch_file(source_path.resolve(), dst)
    raise ValueError(f"Unsupported source: {source}")


def write_poscar(structure: Structure, path: Path) -> None:
    Poscar(structure).write_file(path)


def collect_placeholders(value: Any, path: str = "$") -> list[dict[str, str]]:
    placeholders: list[dict[str, str]] = []
    if isinstance(value, dict):
        for key, item in value.items():
            child_path = f"{path}.{key}" if path else key
            placeholders.extend(collect_placeholders(item, child_path))
        return placeholders
    if isinstance(value, list):
        for index, item in enumerate(value):
            placeholders.extend(collect_placeholders(item, f"{path}[{index}]"))
        return placeholders
    if isinstance(value, str):
        for match in PLACEHOLDER_PATTERN.finditer(value):
            placeholders.append({"path": path, "placeholder": match.group(0)})
    return placeholders


def placeholder_tokens(manifest: dict[str, Any]) -> list[str]:
    return sorted({item["placeholder"] for item in collect_placeholders(manifest)})


def iter_preset_paths() -> list[Path]:
    root = preset_root()
    if not root.exists():
        return []
    return sorted(path for path in root.glob("*.json") if path.is_file())


def load_preset_manifest(name: str) -> tuple[dict[str, Any], Path]:
    path = preset_root() / f"{name}.json"
    if not path.exists():
        available = ", ".join(item.stem for item in iter_preset_paths()) or "<none>"
        raise ValueError(f"Unsupported preset: {name}. Available presets: {available}")
    return read_json(path), path


def list_presets_payload() -> dict[str, Any]:
    presets: list[dict[str, Any]] = []
    for path in iter_preset_paths():
        manifest = read_json(path)
        placeholders = placeholder_tokens(manifest)
        presets.append(
            {
                "name": manifest.get("name", path.stem),
                "path": relative_display(path, skill_root()),
                "description": manifest.get("description", ""),
                "workflow_tags": manifest.get("workflow_tags", []),
                "required_user_inputs": manifest.get("required_user_inputs", []),
                "placeholder_tokens": placeholders,
            }
        )
    return {"preset_root": relative_display(preset_root(), skill_root()), "presets": presets}


def default_template_path(project_root: Path, preset_name: str) -> Path:
    return project_root / "workflow" / f"structure_manifest.{preset_name}.json"


def normalize_scaling_matrix(value: Any) -> list[int] | list[list[int]]:
    if isinstance(value, (list, tuple)) and len(value) == 3 and all(
        not isinstance(item, (list, tuple)) for item in value
    ):
        return [int(item) for item in value]
    if isinstance(value, (list, tuple)) and len(value) == 3 and all(
        isinstance(row, (list, tuple)) and len(row) == 3 for row in value
    ):
        return [[int(item) for item in row] for row in value]
    raise ValueError("Supercell scaling_matrix must be a length-3 vector or a 3x3 integer matrix.")


def make_supercell_structure(structure: Structure, scaling_matrix: Any) -> Structure:
    expanded = structure.copy()
    expanded.make_supercell(normalize_scaling_matrix(scaling_matrix))
    return expanded


def choose_spread_indices(structure: Structure, candidate_indices: list[int], count: int) -> list[int]:
    if count < 1:
        raise ValueError("proton_count must be at least 1.")
    if count > len(candidate_indices):
        raise ValueError("proton_count cannot exceed the number of candidate host sites.")

    chosen = [candidate_indices[0]]
    remaining = set(candidate_indices[1:])
    while len(chosen) < count:
        next_index = max(
            remaining,
            key=lambda idx: min(structure.get_distance(idx, other_idx) for other_idx in chosen),
        )
        chosen.append(next_index)
        remaining.remove(next_index)
    return chosen


def make_protonated_structure(
    structure: Structure,
    proton_count: int,
    host_species: str = "O",
    anchor_species: str | None = None,
    bond_length: float = 1.0,
) -> Structure:
    host_indices = [index for index, site in enumerate(structure) if site.specie.symbol == host_species]
    if not host_indices:
        raise RuntimeError(f"Base structure does not contain any {host_species} sites for protonation.")

    anchor_indices = []
    if anchor_species:
        anchor_indices = [index for index, site in enumerate(structure) if site.specie.symbol == anchor_species]
        if not anchor_indices:
            raise RuntimeError(f"Base structure does not contain any {anchor_species} sites for protonation anchoring.")

    chosen = choose_spread_indices(structure, host_indices, proton_count)
    doped = structure.copy()
    cell_center = doped.lattice.get_cartesian_coords([0.5, 0.5, 0.5])
    for host_index in chosen:
        host_site = doped[host_index]
        if anchor_indices:
            nearest_anchor = min(anchor_indices, key=lambda idx: doped.get_distance(host_index, idx))
            vector = host_site.coords - doped[nearest_anchor].coords
        else:
            vector = host_site.coords - cell_center

        norm = sum(float(component) ** 2 for component in vector) ** 0.5
        if norm < 1e-8:
            vector = [0.0, 0.0, 1.0]
            norm = 1.0
        hydrogen_cart = [
            float(host_site.coords[index]) + float(bond_length) * float(vector[index]) / norm for index in range(3)
        ]
        doped.append("H", hydrogen_cart, coords_are_cartesian=True)
    return doped


def apply_derived_operation(base: Structure, derived: dict[str, Any]) -> Structure:
    operation = derived["operation"]
    if operation == "supercell":
        scaling_matrix = derived.get("scaling_matrix", derived.get("scale"))
        if scaling_matrix is None:
            raise ValueError("Derived supercell operation requires scaling_matrix or scale.")
        return make_supercell_structure(base, scaling_matrix)
    if operation == "protonate":
        return make_protonated_structure(
            base,
            proton_count=int(derived["proton_count"]),
            host_species=str(derived.get("host_species", "O")),
            anchor_species=derived.get("anchor_species"),
            bond_length=float(derived.get("bond_length", 1.0)),
        )
    raise ValueError(f"Unsupported derived operation: {operation}")


def load_manifest(args: argparse.Namespace, project_root: Path) -> tuple[dict[str, Any], Path, dict[str, Any]]:
    if args.preset:
        manifest, manifest_path = load_preset_manifest(args.preset)
        metadata = {
            "mode": "preset",
            "name": manifest.get("name", args.preset),
            "path": relative_display(manifest_path, skill_root()),
            "description": manifest.get("description", ""),
        }
        return manifest, manifest_path.parent, metadata

    manifest_path = args.manifest.expanduser().resolve()
    manifest = read_json(manifest_path)
    metadata = {
        "mode": "manifest",
        "name": manifest.get("name", manifest_path.stem),
        "path": relative_display(manifest_path, project_root),
        "description": manifest.get("description", ""),
    }
    return manifest, manifest_path.parent, metadata


def maybe_write_template(
    manifest: dict[str, Any],
    manifest_meta: dict[str, Any],
    project_root: Path,
    preset_name: str | None,
    write_template: Path | None,
) -> bool:
    placeholders = collect_placeholders(manifest)
    if write_template is None and not (preset_name and placeholders):
        return False

    template_path = write_template.expanduser().resolve() if write_template else default_template_path(project_root, preset_name)
    ensure_dir(template_path.parent)
    write_json(template_path, manifest)
    payload = {
        "status": "template_written",
        "reason": "explicit_template_export" if write_template else "preset_requires_user_inputs",
        "template_path": relative_display(template_path, project_root),
        "manifest": manifest_meta,
        "placeholders": placeholders,
    }
    print(json.dumps(payload, indent=2))
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch and normalize structures for a DFT project.")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root.")
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--preset", help="Preset name from presets/*.json.")
    source_group.add_argument("--manifest", type=Path, help="JSON manifest with entries, derived structures, and slabs.")
    source_group.add_argument("--list-presets", action="store_true", help="List built-in structure presets and exit.")
    parser.add_argument("--write-template", type=Path, help="Write the selected preset or manifest to a JSON template and exit.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.list_presets:
        print(json.dumps(list_presets_payload(), indent=2))
        return 0

    project_root = args.project_root.expanduser().resolve()
    manifest, source_base, manifest_meta = load_manifest(args, project_root)
    if maybe_write_template(manifest, manifest_meta, project_root, args.preset, args.write_template):
        return 0

    unresolved_placeholders = placeholder_tokens(manifest)
    if unresolved_placeholders:
        joined = ", ".join(unresolved_placeholders)
        raise ValueError(f"Manifest contains unresolved placeholders: {joined}")

    raw_dir = project_root / "structures" / "raw_cif"
    poscar_dir = project_root / "structures" / "poscar"
    slab_dir = project_root / "structures" / "slabs"
    ensure_dir(raw_dir)
    ensure_dir(poscar_dir)
    ensure_dir(slab_dir)

    normalized_structures: dict[str, Structure] = {}
    provenance: dict[str, Any] = {"manifest": manifest_meta, "entries": [], "derived": [], "slabs": []}

    for entry in manifest.get("entries", []):
        raw_path, source_meta = materialize_raw_file(entry, raw_dir, source_base)
        structure = Structure.from_file(raw_path)
        structure = normalize_structure(structure, entry.get("normalize", "conventional"))
        species_order = entry.get("species_order")
        if species_order:
            structure = reorder_structure(structure, species_order)
        normalized_structures[entry["label"]] = structure

        poscar_name = entry.get("poscar")
        poscar_path = None
        if poscar_name:
            poscar_path = poscar_dir / poscar_name
            write_poscar(structure, poscar_path)

        provenance["entries"].append(
            {
                "label": entry["label"],
                "raw_file": str(raw_path.relative_to(project_root)),
                "normalized": entry.get("normalize", "conventional"),
                "species_order": species_order or [],
                "poscar": str(poscar_path.relative_to(project_root)) if poscar_path else None,
                "source_meta": source_meta | {
                    "path": str(entry["value"]) if entry["source"] == "file" else source_meta.get("path")
                },
            }
        )

    for derived in manifest.get("derived", []):
        base = normalized_structures[derived["source_label"]]
        structure = apply_derived_operation(base, derived)
        species_order = derived.get("species_order")
        if species_order:
            structure = reorder_structure(structure, species_order)
        normalized_structures[derived["label"]] = structure

        poscar_name = derived.get("poscar")
        poscar_path = None
        if poscar_name:
            poscar_path = poscar_dir / poscar_name
            write_poscar(structure, poscar_path)

        record = {key: value for key, value in derived.items() if key not in {"species_order", "poscar"}}
        record["species_order"] = species_order or []
        record["poscar"] = str(poscar_path.relative_to(project_root)) if poscar_path else None
        provenance["derived"].append(record)

    for slab_spec in manifest.get("slabs", []):
        base = normalized_structures[slab_spec["source_label"]]
        slab = SlabGenerator(
            base,
            miller_index=tuple(slab_spec["miller_index"]),
            min_slab_size=float(slab_spec["min_slab_size"]),
            min_vacuum_size=float(slab_spec["min_vacuum_size"]),
            center_slab=bool(slab_spec.get("center_slab", True)),
            in_unit_planes=bool(slab_spec.get("in_unit_planes", False)),
        ).get_slabs(symmetrize=False)[0]
        species_order = slab_spec.get("species_order") or [site.specie.symbol for site in slab]
        slab = reorder_structure(slab, species_order)
        slab_path = slab_dir / slab_spec["filename"]
        write_poscar(slab, slab_path)

        record = {key: value for key, value in slab_spec.items() if key != "species_order"}
        record["species_order"] = species_order
        record["file"] = str(slab_path.relative_to(project_root))
        provenance["slabs"].append(record)

    write_json(project_root / "structures" / "provenance.json", provenance)
    print(json.dumps(provenance, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
