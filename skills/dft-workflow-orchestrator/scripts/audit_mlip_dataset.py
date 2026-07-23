#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


DEFAULT_GROUP_KEYS = ["trajectory_id", "parent_id", "source_id", "configuration_group"]


def parse_split(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("Split must use NAME=PATH syntax.")
    name, raw_path = value.split("=", 1)
    name = name.strip()
    if not name:
        raise argparse.ArgumentTypeError("Split name cannot be empty.")
    if not raw_path.strip():
        raise argparse.ArgumentTypeError("Split path cannot be empty.")
    return name, Path(raw_path).expanduser()


def stable_value(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    except TypeError:
        return str(value)


def structure_fingerprint(atoms: Any, decimals: int) -> str:
    import numpy as np

    numbers = np.asarray(atoms.numbers, dtype=int)
    pbc = np.asarray(atoms.pbc, dtype=bool)
    cell = np.round(np.asarray(atoms.cell.array, dtype=float), decimals=decimals)
    if pbc.all() and abs(float(np.linalg.det(cell))) > 10 ** (-decimals):
        coords = np.asarray(atoms.get_scaled_positions(wrap=True), dtype=float)
    else:
        coords = np.asarray(atoms.positions, dtype=float)
    coords = np.round(coords, decimals=decimals)
    rows = sorted((int(number), *(float(item) for item in coord)) for number, coord in zip(numbers, coords))
    payload = {
        "numbers_and_coordinates": rows,
        "cell": cell.reshape(-1).tolist(),
        "pbc": pbc.astype(int).tolist(),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def optional_energy(atoms: Any) -> float | None:
    try:
        value = float(atoms.get_potential_energy())
    except Exception:
        return None
    return value if math.isfinite(value) else float("nan")


def optional_forces(atoms: Any) -> Any | None:
    import numpy as np

    try:
        value = np.asarray(atoms.get_forces(), dtype=float)
    except Exception:
        return None
    return value


def optional_stress(atoms: Any) -> Any | None:
    import numpy as np

    try:
        value = np.asarray(atoms.get_stress(voigt=True), dtype=float)
    except Exception:
        return None
    return value


def basic_stats(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"count": 0, "min": None, "max": None, "mean": None}
    finite = [value for value in values if math.isfinite(value)]
    if not finite:
        return {"count": len(values), "min": None, "max": None, "mean": None}
    return {
        "count": len(values),
        "min": min(finite),
        "max": max(finite),
        "mean": sum(finite) / len(finite),
    }


def load_frames(paths: list[Path], file_format: str | None, max_configs: int) -> Iterable[tuple[Path, Any]]:
    from ase.io import iread

    count = 0
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(path)
        for atoms in iread(str(path), index=":", format=file_format):
            yield path, atoms
            count += 1
            if max_configs and count >= max_configs:
                return


def audit_split(
    name: str,
    paths: list[Path],
    file_format: str | None,
    max_configs: int,
    group_keys: list[str],
    fingerprint_decimals: int,
) -> tuple[dict[str, Any], dict[str, list[str]], dict[str, list[str]], list[str]]:
    import numpy as np

    energies_per_atom: list[float] = []
    force_magnitudes: list[float] = []
    elements: set[str] = set()
    pbc_patterns: set[str] = set()
    fingerprints: dict[str, list[str]] = defaultdict(list)
    groups: dict[str, list[str]] = defaultdict(list)
    warnings: list[str] = []
    config_count = 0
    atom_count = 0
    missing_energy = 0
    missing_forces = 0
    missing_stress = 0
    invalid_energy = 0
    invalid_forces = 0
    invalid_stress = 0

    for path, atoms in load_frames(paths, file_format, max_configs):
        config_count += 1
        atom_count += len(atoms)
        config_id = str(atoms.info.get("config_id") or atoms.info.get("structure_id") or f"{path.name}:{config_count - 1}")
        elements.update(atoms.get_chemical_symbols())
        pbc_patterns.add("".join("1" if flag else "0" for flag in atoms.pbc))
        fingerprints[structure_fingerprint(atoms, fingerprint_decimals)].append(config_id)

        for key in group_keys:
            if key in atoms.info and atoms.info[key] not in (None, ""):
                groups[f"{key}={stable_value(atoms.info[key])}"].append(config_id)

        energy = optional_energy(atoms)
        if energy is None:
            missing_energy += 1
        elif not math.isfinite(energy):
            invalid_energy += 1
        elif len(atoms):
            energies_per_atom.append(energy / len(atoms))

        forces = optional_forces(atoms)
        if forces is None:
            missing_forces += 1
        elif forces.shape != (len(atoms), 3) or not np.isfinite(forces).all():
            invalid_forces += 1
        else:
            force_magnitudes.extend(np.linalg.norm(forces, axis=1).tolist())

        stress = optional_stress(atoms)
        if stress is None:
            missing_stress += 1
        elif stress.size not in (6, 9) or not np.isfinite(stress).all():
            invalid_stress += 1

    duplicates_within = {fingerprint: ids for fingerprint, ids in fingerprints.items() if len(ids) > 1}
    if duplicates_within:
        warnings.append(f"{len(duplicates_within)} exact rounded-geometry fingerprint(s) repeat within split {name}.")
    summary = {
        "paths": [str(path) for path in paths],
        "configurations": config_count,
        "atoms": atom_count,
        "elements": sorted(elements),
        "pbc_patterns": sorted(pbc_patterns),
        "labels": {
            "missing_energy": missing_energy,
            "invalid_energy": invalid_energy,
            "missing_forces": missing_forces,
            "invalid_forces": invalid_forces,
            "missing_stress": missing_stress,
            "invalid_stress": invalid_stress,
        },
        "energy_per_atom": basic_stats(energies_per_atom),
        "force_magnitude": basic_stats(force_magnitudes),
        "groups_found": len(groups),
        "duplicate_fingerprints_within_split": len(duplicates_within),
    }
    return summary, fingerprints, groups, warnings


def cross_split_overlaps(index: dict[str, dict[str, list[str]]]) -> list[dict[str, Any]]:
    owners: dict[str, list[tuple[str, list[str]]]] = defaultdict(list)
    for split, values in index.items():
        for key, config_ids in values.items():
            owners[key].append((split, config_ids))
    return [
        {"key": key, "splits": [{"name": split, "config_ids": ids[:10]} for split, ids in split_rows]}
        for key, split_rows in owners.items()
        if len(split_rows) > 1
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit ASE-readable atomistic datasets for MLIP labels and split leakage.")
    parser.add_argument("--split", action="append", type=parse_split, required=True, metavar="NAME=PATH", help="Dataset split and ASE-readable file; repeat as needed.")
    parser.add_argument("--format", help="Optional ASE format override, such as extxyz or traj.")
    parser.add_argument("--group-key", action="append", default=[], help="Atoms.info key used to detect group leakage; repeat as needed.")
    parser.add_argument("--max-configs", type=int, default=0, help="Maximum configurations per split; zero reads all.")
    parser.add_argument("--fingerprint-decimals", type=int, default=6, help="Coordinate rounding used for exact-duplicate detection.")
    parser.add_argument("--allow-missing-energy", action="store_true", help="Do not fail when energy labels are absent.")
    parser.add_argument("--allow-missing-forces", action="store_true", help="Do not fail when force labels are absent.")
    parser.add_argument("--require-stress", action="store_true", help="Fail when stress labels are absent.")
    parser.add_argument("--allow-cross-split-overlap", action="store_true", help="Report but do not fail on group or geometry overlap across splits.")
    parser.add_argument("--energy-unit", default="eV", help="Declared energy unit for the report; ASE does not infer provenance.")
    parser.add_argument("--length-unit", default="Angstrom", help="Declared length unit for the report.")
    parser.add_argument("--stress-unit", default="eV/Angstrom^3", help="Declared stress unit for the report.")
    parser.add_argument("--pretty", action="store_true", help="Print a human-readable report instead of JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.max_configs < 0:
        raise SystemExit("--max-configs must be non-negative.")
    if not 0 <= args.fingerprint_decimals <= 12:
        raise SystemExit("--fingerprint-decimals must be between 0 and 12.")
    try:
        import ase  # noqa: F401
        import numpy  # noqa: F401
    except ImportError as exc:
        print(json.dumps({"valid": False, "errors": [f"Missing required package: {exc.name}"]}, indent=2))
        return 1

    split_paths: dict[str, list[Path]] = defaultdict(list)
    for name, path in args.split:
        split_paths[name].append(path.expanduser().resolve())
    group_keys = args.group_key or DEFAULT_GROUP_KEYS
    summaries: dict[str, Any] = {}
    fingerprint_index: dict[str, dict[str, list[str]]] = {}
    group_index: dict[str, dict[str, list[str]]] = {}
    warnings: list[str] = []
    errors: list[str] = []

    for name, paths in split_paths.items():
        try:
            summary, fingerprints, groups, split_warnings = audit_split(
                name, paths, args.format, args.max_configs, group_keys, args.fingerprint_decimals
            )
        except Exception as exc:
            errors.append(f"Could not read split {name}: {type(exc).__name__}: {exc}")
            continue
        summaries[name] = summary
        fingerprint_index[name] = fingerprints
        group_index[name] = groups
        warnings.extend(split_warnings)
        labels = summary["labels"]
        if summary["configurations"] == 0:
            errors.append(f"Split {name} contains no configurations.")
        if not args.allow_missing_energy and (labels["missing_energy"] or labels["invalid_energy"]):
            errors.append(f"Split {name} has missing or invalid energy labels.")
        if not args.allow_missing_forces and (labels["missing_forces"] or labels["invalid_forces"]):
            errors.append(f"Split {name} has missing or invalid force labels.")
        if args.require_stress and (labels["missing_stress"] or labels["invalid_stress"]):
            errors.append(f"Split {name} has missing or invalid stress labels.")

    fingerprint_overlap = cross_split_overlaps(fingerprint_index)
    group_overlap = cross_split_overlaps(group_index)
    if fingerprint_overlap:
        message = f"{len(fingerprint_overlap)} exact rounded-geometry fingerprint(s) occur across splits."
        (warnings if args.allow_cross_split_overlap else errors).append(message)
    if group_overlap:
        message = f"{len(group_overlap)} declared group identifier(s) occur across splits."
        (warnings if args.allow_cross_split_overlap else errors).append(message)

    result = {
        "valid": not errors,
        "units_declared": {
            "energy": args.energy_unit,
            "length": args.length_unit,
            "force": f"{args.energy_unit}/{args.length_unit}",
            "stress": args.stress_unit,
        },
        "group_keys": group_keys,
        "fingerprint_decimals": args.fingerprint_decimals,
        "splits": summaries,
        "cross_split": {
            "fingerprint_overlap_count": len(fingerprint_overlap),
            "group_overlap_count": len(group_overlap),
            "fingerprint_overlap_examples": fingerprint_overlap[:20],
            "group_overlap_examples": group_overlap[:20],
        },
        "errors": errors,
        "warnings": warnings,
        "limitations": [
            "Declared units are not inferred from ASE files and must be checked against source calculations.",
            "Rounded geometry fingerprints are duplicate checks, not symmetry- or translation-complete equivalence tests.",
            "Scientific coverage and target-domain validity require the MLIP workflow validation gates.",
        ],
    }
    if args.pretty:
        print(f"Valid: {'yes' if result['valid'] else 'no'}")
        for name, summary in summaries.items():
            labels = summary["labels"]
            print(f"{name}: {summary['configurations']} configurations, {summary['atoms']} atoms, elements={','.join(summary['elements'])}")
            print(
                "  labels: "
                f"missing_energy={labels['missing_energy']}, missing_forces={labels['missing_forces']}, "
                f"missing_stress={labels['missing_stress']}"
            )
        print(
            "Cross-split overlap: "
            f"fingerprints={len(fingerprint_overlap)}, groups={len(group_overlap)}"
        )
        for message in errors:
            print(f"ERROR: {message}")
        for message in warnings:
            print(f"WARNING: {message}")
    else:
        json.dump(result, sys.stdout, indent=2)
        print()
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
