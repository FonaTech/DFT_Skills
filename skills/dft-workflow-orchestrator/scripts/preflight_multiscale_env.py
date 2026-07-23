#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import importlib.metadata
import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any


COMMANDS = {
    "electronic_structure": [
        ("vasp_std", "VASP"),
        ("vasp_gam", "VASP"),
        ("pw.x", "Quantum ESPRESSO"),
        ("cp2k", "CP2K"),
        ("cp2k.popt", "CP2K"),
        ("gpaw", "GPAW"),
        ("abinit", "ABINIT"),
        ("siesta", "SIESTA"),
    ],
    "atomistic_dynamics": [
        ("lmp", "LAMMPS"),
        ("lmp_mpi", "LAMMPS"),
        ("lammps", "LAMMPS"),
        ("i-pi", "i-PI"),
        ("plumed", "PLUMED"),
        ("phonopy", "phonopy"),
        ("phono3py", "phono3py"),
    ],
    "continuum": [
        ("comsol", "COMSOL"),
        ("ccx", "CalculiX"),
        ("moose-opt", "MOOSE"),
        ("moose", "MOOSE"),
        ("abaqus", "Abaqus"),
        ("FreeFem++", "FreeFEM"),
    ],
    "parallel_and_scheduler": [
        ("mpirun", "MPI"),
        ("mpiexec", "MPI"),
        ("srun", "Slurm"),
        ("sbatch", "Slurm"),
        ("qsub", "PBS/SGE"),
    ],
    "accelerator": [
        ("nvidia-smi", "NVIDIA GPU"),
        ("rocm-smi", "AMD GPU"),
    ],
}

MODULES = [
    ("numpy", "numpy", "numerics"),
    ("scipy", "scipy", "numerics"),
    ("pandas", "pandas", "data"),
    ("h5py", "h5py", "data"),
    ("ase", "ase", "atomistic"),
    ("pymatgen", "pymatgen", "atomistic"),
    ("mp_api", "mp-api", "structures"),
    ("MDAnalysis", "MDAnalysis", "trajectory_analysis"),
    ("phonopy", "phonopy", "lattice_dynamics"),
    ("phono3py", "phono3py", "lattice_dynamics"),
    ("torch", "torch", "machine_learning"),
    ("jax", "jax", "machine_learning"),
    ("mace", "mace-torch", "mlip"),
    ("nequip", "nequip", "mlip"),
    ("allegro", "allegro", "mlip"),
    ("deepmd", "deepmd-kit", "mlip"),
    ("chgnet", "chgnet", "mlip"),
    ("matgl", "matgl", "mlip"),
    ("sevenn", "sevenn", "mlip"),
    ("quippy", "quippy-ase", "mlip"),
    ("pyace", "python-ace", "mlip"),
    ("orb_models", "orb-models", "mlip"),
    ("gpaw", "gpaw", "electronic_structure"),
    ("dolfinx", "fenics-dolfinx", "continuum"),
    ("fenics", "fenics", "continuum"),
    ("gmsh", "gmsh", "meshing"),
    ("meshio", "meshio", "meshing"),
]

ENV_KEYS = [
    "MP_API_KEY",
    "PMG_MAPI_KEY",
    "MAPI_KEY",
    "PMG_VASP_PSP_DIR",
    "VASP_PSP_DIR",
    "VASP_POTCAR_ROOT",
    "POTCAR_ROOT",
    "LM_LICENSE_FILE",
    "ABAQUSLM_LICENSE_FILE",
    "TORCH_HOME",
    "HF_HOME",
    "MACE_CACHE",
]

SCAN_PATTERNS = {
    "structure": ["*.cif", "POSCAR*", "CONTCAR*", "*.vasp", "*.xyz", "*.extxyz"],
    "trajectory": ["*.traj", "*.lammpstrj", "*.dcd", "*.xtc", "*.trr", "XDATCAR*"],
    "reference_output": ["vasprun.xml", "OUTCAR", "*.h5", "*.hdf5"],
    "checkpoint": ["*.model", "*.pt", "*.pth", "*.ckpt", "*.jit", "*.pb"],
    "mesh_or_fem": ["*.msh", "*.xdmf", "*.vtu", "*.inp", "*.mph", "*.e"],
    "literature": ["*.pdf"],
}

IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "node_modules",
}


def relative_display(path: str | Path | None, base: Path) -> str | None:
    if path is None:
        return None
    raw = Path(path).expanduser()
    if not raw.is_absolute():
        return str(raw)
    return os.path.relpath(str(raw), str(base))


def distribution_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def module_status(import_name: str, distribution: str, category: str) -> dict[str, Any]:
    try:
        available = importlib.util.find_spec(import_name) is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        available = False
    return {
        "name": import_name,
        "distribution": distribution,
        "category": category,
        "available": available,
        "version": distribution_version(distribution) if available else None,
    }


def command_status(name: str, provider: str, category: str, base: Path) -> dict[str, Any]:
    path = shutil.which(name)
    return {
        "name": name,
        "provider": provider,
        "category": category,
        "available": path is not None,
        "path": relative_display(path, base),
    }


def detect_potcar_root(workspace: Path) -> str | None:
    for key in ("PMG_VASP_PSP_DIR", "VASP_PSP_DIR", "VASP_POTCAR_ROOT", "POTCAR_ROOT"):
        value = os.environ.get(key)
        if value:
            return value
    try:
        for child in workspace.iterdir():
            if child.is_dir() and child.name.startswith("potpaw_"):
                return str(child)
    except OSError:
        return None
    return None


def scan_workspace(workspace: Path, per_category_limit: int) -> dict[str, list[str]]:
    hits = {category: [] for category in SCAN_PATTERNS}
    for root, dirs, files in os.walk(workspace):
        dirs[:] = [name for name in dirs if name not in IGNORE_DIRS]
        rel_root = Path(root).relative_to(workspace)
        for filename in files:
            for category, patterns in SCAN_PATTERNS.items():
                if len(hits[category]) >= per_category_limit:
                    continue
                if any(fnmatch.fnmatch(filename, pattern) for pattern in patterns):
                    rel = rel_root / filename if rel_root != Path(".") else Path(filename)
                    hits[category].append(str(rel))
    return hits


def names_available(rows: list[dict[str, Any]]) -> set[str]:
    return {str(row["name"]) for row in rows if row["available"]}


def capability(status: str, reasons: list[str], providers: list[str] | None = None) -> dict[str, Any]:
    return {"status": status, "providers": providers or [], "notes": reasons}


def build_capabilities(
    commands: list[dict[str, Any]], modules: list[dict[str, Any]], workspace_hits: dict[str, list[str]], potcar_root: str | None
) -> dict[str, Any]:
    command_names = names_available(commands)
    module_names = names_available(modules)

    dft_providers: list[str] = []
    if {"vasp_std", "vasp_gam"} & command_names:
        dft_providers.append("VASP")
    if "pw.x" in command_names:
        dft_providers.append("Quantum ESPRESSO")
    if {"cp2k", "cp2k.popt"} & command_names:
        dft_providers.append("CP2K")
    if "gpaw" in command_names or "gpaw" in module_names:
        dft_providers.append("GPAW")
    if "abinit" in command_names:
        dft_providers.append("ABINIT")
    if "siesta" in command_names:
        dft_providers.append("SIESTA")

    mlip_modules = sorted(
        module_names
        & {"mace", "nequip", "allegro", "deepmd", "chgnet", "matgl", "sevenn", "quippy", "pyace", "orb_models"}
    )
    checkpoints = workspace_hits.get("checkpoint", [])
    atomistic_driver = "ase" in module_names or bool({"lmp", "lmp_mpi", "lammps"} & command_names)
    fem_providers: list[str] = []
    for command, provider in [("comsol", "COMSOL"), ("ccx", "CalculiX"), ("abaqus", "Abaqus")]:
        if command in command_names:
            fem_providers.append(provider)
    if {"moose", "moose-opt"} & command_names:
        fem_providers.append("MOOSE")
    if "dolfinx" in module_names:
        fem_providers.append("FEniCSx")
    elif "fenics" in module_names:
        fem_providers.append("FEniCS")

    dft_notes: list[str] = []
    if not dft_providers:
        dft_notes.append("No supported electronic-structure executable or GPAW module was detected.")
    if "VASP" in dft_providers and not potcar_root:
        dft_notes.append("VASP was detected but no pseudopotential root was found.")

    mlip_notes: list[str] = []
    if not mlip_modules:
        mlip_notes.append("No known MLIP Python package was detected.")
    if not checkpoints:
        mlip_notes.append("No checkpoint-like file was found in the scanned workspace; a package may still download or cache one elsewhere.")
    if not atomistic_driver:
        mlip_notes.append("Neither ASE nor a LAMMPS executable was detected for atomistic driving.")

    fem_notes = [] if fem_providers else ["No supported FEM or multiphysics backend was detected."]

    dft_status = "available" if dft_providers and not (dft_providers == ["VASP"] and not potcar_root) else "conditional"
    if not dft_providers:
        dft_status = "missing"
    mlip_status = "available" if mlip_modules and atomistic_driver and checkpoints else "conditional"
    if not mlip_modules and not checkpoints:
        mlip_status = "missing"
    fem_status = "available" if fem_providers else "missing"

    available_domains = sum(status == "available" for status in (dft_status, mlip_status, fem_status))
    coupled_status = "available" if available_domains >= 2 else "conditional" if dft_providers or mlip_modules or fem_providers else "missing"

    return {
        "planning": capability("available", ["Planning and scaffold generation use the Python standard library."]),
        "dft_reference": capability(dft_status, dft_notes, dft_providers),
        "aimd": capability(dft_status, dft_notes, dft_providers),
        "mlip_inference": capability(mlip_status, mlip_notes, mlip_modules),
        "mlip_md": capability(mlip_status, mlip_notes, mlip_modules),
        "fem": capability(fem_status, fem_notes, fem_providers),
        "coupled_multiscale": capability(
            coupled_status,
            ["Availability does not validate scientific compatibility or handoff contracts."],
            sorted(set(dft_providers + mlip_modules + fem_providers)),
        ),
    }


def build_report(workspace: Path, scan_limit: int) -> dict[str, Any]:
    cwd = Path.cwd().resolve()
    commands = [
        command_status(name, provider, category, cwd)
        for category, specs in COMMANDS.items()
        for name, provider in specs
    ]
    modules = [module_status(import_name, distribution, category) for import_name, distribution, category in MODULES]
    hits = scan_workspace(workspace, scan_limit)
    potcar_root = detect_potcar_root(workspace)
    capabilities = build_capabilities(commands, modules, hits, potcar_root)
    return {
        "workspace": relative_display(workspace, cwd) or ".",
        "python": {"executable": relative_display(sys.executable, cwd), "version": sys.version.split()[0]},
        "commands": commands,
        "modules": modules,
        "environment_flags": {key: bool(os.environ.get(key)) for key in ENV_KEYS},
        "potcar_root": relative_display(potcar_root, workspace),
        "workspace_artifacts": hits,
        "capabilities": capabilities,
        "interpretation": "Availability is a plumbing check, not scientific readiness or license verification.",
    }


def print_pretty(report: dict[str, Any]) -> None:
    print(f"Workspace: {report['workspace']}")
    print(f"Python: {report['python']['version']} ({report['python']['executable']})")
    print("Capabilities:")
    for name, item in report["capabilities"].items():
        providers = ", ".join(item["providers"]) or "none detected"
        print(f"  {name}: {item['status']} [{providers}]")
        for note in item["notes"]:
            print(f"    - {note}")
    print("Available commands:")
    for item in report["commands"]:
        if item["available"]:
            print(f"  {item['name']}: {item['provider']} ({item['path']})")
    print("Available Python modules:")
    for item in report["modules"]:
        if item["available"]:
            version = item["version"] or "version unknown"
            print(f"  {item['name']}: {version} [{item['category']}]")
    print("Workspace artifacts:")
    for category, paths in report["workspace_artifacts"].items():
        print(f"  {category}: {len(paths)}")
        for path in paths:
            print(f"    - {path}")
    print(f"Note: {report['interpretation']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe a DFT, AIMD, MLIP, MD, and FEM environment without importing heavy packages.")
    parser.add_argument("--workspace", type=Path, default=Path.cwd(), help="Workspace to scan for inputs, datasets, models, and meshes.")
    parser.add_argument("--scan-limit", type=int, default=20, help="Maximum artifact paths retained per category.")
    parser.add_argument("--pretty", action="store_true", help="Print a human-readable report instead of JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    workspace = args.workspace.expanduser().resolve()
    if not workspace.is_dir():
        raise SystemExit(f"Workspace is not a directory: {workspace}")
    if args.scan_limit < 0:
        raise SystemExit("--scan-limit must be non-negative.")
    report = build_report(workspace, args.scan_limit)
    if args.pretty:
        print_pretty(report)
    else:
        json.dump(report, sys.stdout, indent=2)
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
