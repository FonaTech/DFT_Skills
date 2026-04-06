#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path


COMMANDS = ["vasp_std", "vasp_gam", "mpirun", "pdftotext", "pdfinfo", "python3"]
MODULES = ["pymatgen", "ase", "mp_api", "numpy", "scipy", "fitz"]
ENV_KEYS = [
    "MP_API_KEY",
    "PMG_MAPI_KEY",
    "MAPI_KEY",
    "PMG_VASP_PSP_DIR",
    "VASP_PSP_DIR",
    "VASP_POTCAR_ROOT",
    "POTCAR_ROOT",
]
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
IGNORE_PREFIXES = ("potpaw_",)
SCAN_PATTERNS = [
    "*.pdf",
    "*.cif",
    "POSCAR*",
    "CONTCAR*",
    "*.vasp",
    "INCAR",
    "KPOINTS",
    "POTCAR",
    "OUTCAR",
    "OSZICAR",
    "vasprun.xml",
]


def detect_potcar_root(workspace: Path) -> str | None:
    for key in ("PMG_VASP_PSP_DIR", "VASP_PSP_DIR", "VASP_POTCAR_ROOT", "POTCAR_ROOT"):
        value = os.environ.get(key)
        if value:
            return value
    for child in workspace.iterdir():
        if child.is_dir() and child.name.startswith("potpaw_"):
            return str(child)
    return None


def relative_display(path: str | Path | None, base: Path) -> str | None:
    if path is None:
        return None
    raw = Path(path).expanduser()
    if not raw.is_absolute():
        return str(raw)
    return os.path.relpath(str(raw), str(base))


def scan_workspace(workspace: Path, limit: int) -> list[str]:
    hits: list[str] = []
    for root, dirs, files in os.walk(workspace):
        dirs[:] = [
            name
            for name in dirs
            if name not in IGNORE_DIRS and not any(name.startswith(prefix) for prefix in IGNORE_PREFIXES)
        ]
        rel_root = Path(root).relative_to(workspace)
        for filename in files:
            if any(fnmatch.fnmatch(filename, pattern) for pattern in SCAN_PATTERNS):
                rel_path = rel_root / filename if rel_root != Path(".") else Path(filename)
                hits.append(str(rel_path))
                if len(hits) >= limit:
                    return hits
    return hits


def module_status(name: str) -> dict[str, object]:
    spec = importlib.util.find_spec(name)
    return {"name": name, "available": spec is not None}


def command_status(name: str) -> dict[str, object]:
    path = shutil.which(name)
    return {"name": name, "available": path is not None, "path": relative_display(path, Path.cwd().resolve())}


def build_report(workspace: Path, scan_limit: int) -> dict[str, object]:
    commands = [command_status(name) for name in COMMANDS]
    modules = [module_status(name) for name in MODULES]
    env = {key: bool(os.environ.get(key)) for key in ENV_KEYS}
    potcar_root = detect_potcar_root(workspace)
    examples = scan_workspace(workspace, scan_limit)

    has_vasp = any(item["available"] for item in commands if item["name"] in {"vasp_std", "vasp_gam"})
    has_mpi = any(item["available"] for item in commands if item["name"] == "mpirun")
    has_pymatgen = any(item["available"] for item in modules if item["name"] == "pymatgen")

    ready_for_scaffolding = True
    ready_for_structure_fetch = has_pymatgen
    ready_for_runs = has_vasp and has_mpi and bool(potcar_root)

    reasons: list[str] = []
    if not has_pymatgen:
        reasons.append("pymatgen is missing; structure normalization and slab generation will be unavailable.")
    if not has_vasp:
        reasons.append("No VASP executable was found; calculation launch is unavailable.")
    if not has_mpi:
        reasons.append("mpirun was not found; parallel VASP launch is unavailable.")
    if not potcar_root:
        reasons.append("No pseudopotential root was detected; POTCAR generation will fail.")

    return {
        "workspace": relative_display(workspace, Path.cwd().resolve()) or ".",
        "commands": commands,
        "modules": modules,
        "env": env,
        "potcar_root": relative_display(potcar_root, workspace),
        "workspace_examples": examples,
        "ready": {
            "scaffolding": ready_for_scaffolding,
            "structure_fetch": ready_for_structure_fetch,
            "runs": ready_for_runs,
        },
        "notes": reasons,
    }


def print_pretty(report: dict[str, object]) -> None:
    commands = report["commands"]
    modules = report["modules"]
    ready = report["ready"]

    print(f"Workspace: {report['workspace']}")
    print(f"POTCAR root: {report['potcar_root'] or 'missing'}")
    print("Readiness:")
    print(f"  scaffolding: {'yes' if ready['scaffolding'] else 'no'}")
    print(f"  structure_fetch: {'yes' if ready['structure_fetch'] else 'no'}")
    print(f"  runs: {'yes' if ready['runs'] else 'no'}")
    print("Commands:")
    for item in commands:
        status = "ok" if item["available"] else "missing"
        print(f"  {item['name']}: {status} {item.get('path') or ''}".rstrip())
    print("Modules:")
    for item in modules:
        status = "ok" if item["available"] else "missing"
        print(f"  {item['name']}: {status}")
    print("Environment flags:")
    for key, value in report["env"].items():
        print(f"  {key}: {'set' if value else 'unset'}")
    if report["workspace_examples"]:
        print("Workspace examples:")
        for path in report["workspace_examples"]:
            print(f"  - {path}")
    if report["notes"]:
        print("Notes:")
        for note in report["notes"]:
            print(f"  - {note}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe the local DFT and VASP environment.")
    parser.add_argument("--workspace", type=Path, default=Path.cwd(), help="Workspace to scan.")
    parser.add_argument("--scan-limit", type=int, default=20, help="Maximum example files to list.")
    parser.add_argument("--pretty", action="store_true", help="Print a human-readable summary.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    workspace = args.workspace.expanduser().resolve()
    report = build_report(workspace, args.scan_limit)
    if args.pretty:
        print_pretty(report)
    else:
        json.dump(report, sys.stdout, indent=2)
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
