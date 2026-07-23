#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


def parse_indices(value: str) -> list[int]:
    try:
        indices = [int(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Invalid atom-index list: {value}") from exc
    if not indices:
        raise argparse.ArgumentTypeError("Atom-index list cannot be empty.")
    return indices


def parse_pair(value: str) -> tuple[int, int]:
    indices = parse_indices(value)
    if len(indices) != 2:
        raise argparse.ArgumentTypeError("A distance pair must contain exactly two indices, such as 0,7.")
    if indices[0] == indices[1]:
        raise argparse.ArgumentTypeError("A distance pair needs two different atom indices.")
    return indices[0], indices[1]


def finite_summary(values: list[float]) -> dict[str, Any]:
    finite = [value for value in values if math.isfinite(value)]
    if not finite:
        return {"count": len(values), "finite": 0, "mean": None, "std": None, "min": None, "max": None}
    mean = sum(finite) / len(finite)
    variance = sum((value - mean) ** 2 for value in finite) / len(finite)
    return {
        "count": len(values),
        "finite": len(finite),
        "mean": mean,
        "std": math.sqrt(variance),
        "min": min(finite),
        "max": max(finite),
    }


def linear_slope(values: list[float], timestep_fs: float | None) -> float | None:
    if timestep_fs is None or len(values) < 2:
        return None
    finite = [(index * timestep_fs, value) for index, value in enumerate(values) if math.isfinite(value)]
    if len(finite) < 2:
        return None
    mean_x = sum(item[0] for item in finite) / len(finite)
    mean_y = sum(item[1] for item in finite) / len(finite)
    denominator = sum((x - mean_x) ** 2 for x, _ in finite)
    if denominator == 0:
        return None
    return sum((x - mean_x) * (y - mean_y) for x, y in finite) / denominator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Diagnose ASE-readable AIMD or MLMD trajectories.")
    parser.add_argument("--input", type=Path, required=True, help="ASE-readable trajectory, extxyz, or VASP-derived file.")
    parser.add_argument("--format", help="Optional ASE format override.")
    parser.add_argument("--output", type=Path, help="JSON report path; otherwise print JSON.")
    parser.add_argument("--csv-output", type=Path, help="Optional per-frame CSV path.")
    parser.add_argument("--timestep-fs", type=float, help="Trajectory timestep in femtoseconds for drift and time labels.")
    parser.add_argument("--equilibration-frames", type=int, default=0, help="Frames excluded from production summaries.")
    parser.add_argument("--distance-pair", action="append", type=parse_pair, default=[], help="Atom-index pair for distance tracking; repeat as needed.")
    parser.add_argument("--msd-indices", type=parse_indices, help="Atom indices used for MSD; defaults to all atoms.")
    parser.add_argument("--max-frames", type=int, default=0, help="Maximum frames to read; zero means all.")
    parser.add_argument("--no-unwrap", action="store_true", help="Do not unwrap periodic displacements for MSD.")
    parser.add_argument("--pretty", action="store_true", help="Print a compact summary.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.equilibration_frames < 0 or args.max_frames < 0:
        raise SystemExit("--equilibration-frames and --max-frames must be non-negative.")
    if args.timestep_fs is not None and args.timestep_fs <= 0:
        raise SystemExit("--timestep-fs must be positive.")
    try:
        import numpy as np
        from ase.io import iread
        from ase.units import kB
    except ImportError as exc:
        raise SystemExit(f"ASE and NumPy are required: missing {exc.name}") from exc

    input_path = args.input.expanduser().resolve()
    if not input_path.is_file():
        raise SystemExit(f"Trajectory does not exist: {input_path}")
    output_path = args.output.expanduser().resolve() if args.output else None
    csv_path = args.csv_output.expanduser().resolve() if args.csv_output else None
    selected_outputs = [path for path in (output_path, csv_path) if path is not None]
    if input_path in selected_outputs or len(selected_outputs) != len(set(selected_outputs)):
        raise SystemExit("Input, JSON output, and CSV output paths must be distinct.")
    indices_for_msd = args.msd_indices
    previous_scaled = None
    unwrapped_positions = None
    initial_positions = None
    frame_rows: list[dict[str, Any]] = []
    warnings: list[str] = []
    nonfinite_frames: list[int] = []
    invalid_volume_frames: list[int] = []
    missing_energy_frames: list[int] = []
    missing_temperature_frames: list[int] = []
    expected_atoms: int | None = None
    elements: list[str] = []

    for frame_index, atoms in enumerate(iread(str(input_path), index=":", format=args.format)):
        if args.max_frames and frame_index >= args.max_frames:
            break
        if expected_atoms is None:
            expected_atoms = len(atoms)
            elements = sorted(set(atoms.get_chemical_symbols()))
            indices_for_msd = indices_for_msd or list(range(len(atoms)))
            if any(index < 0 or index >= len(atoms) for index in indices_for_msd):
                raise SystemExit("--msd-indices contains an out-of-range atom index.")
            if any(index < 0 or index >= len(atoms) for pair in args.distance_pair for index in pair):
                raise SystemExit("--distance-pair contains an out-of-range atom index.")
            initial_positions = np.asarray(atoms.positions, dtype=float).copy()
            unwrapped_positions = initial_positions.copy()
        elif len(atoms) != expected_atoms:
            warnings.append(f"Frame {frame_index} changes atom count from {expected_atoms} to {len(atoms)}.")

        energy = None
        try:
            energy = float(atoms.get_potential_energy())
        except Exception:
            missing_energy_frames.append(frame_index)

        temperature = None
        velocities = atoms.get_velocities()
        if velocities is not None and len(atoms):
            kinetic_energy = float(atoms.get_kinetic_energy())
            temperature = 2.0 * kinetic_energy / (3.0 * len(atoms) * float(kB))
        else:
            missing_temperature_frames.append(frame_index)

        volume = None
        if bool(np.any(atoms.pbc)):
            volume = abs(float(np.linalg.det(np.asarray(atoms.cell.array, dtype=float))))
            if not math.isfinite(volume) or volume <= 0:
                if bool(np.all(atoms.pbc)):
                    invalid_volume_frames.append(frame_index)
                volume = None

        positions = np.asarray(atoms.positions, dtype=float)
        if not np.isfinite(positions).all() or (energy is not None and not math.isfinite(energy)):
            nonfinite_frames.append(frame_index)

        if frame_index == 0:
            unwrapped_positions = positions.copy()
            if bool(np.all(atoms.pbc)):
                previous_scaled = np.asarray(atoms.get_scaled_positions(wrap=False), dtype=float)
        elif len(atoms) == expected_atoms and not args.no_unwrap and previous_scaled is not None and bool(np.all(atoms.pbc)):
            current_scaled = np.asarray(atoms.get_scaled_positions(wrap=False), dtype=float)
            delta_scaled = current_scaled - previous_scaled
            delta_scaled -= np.rint(delta_scaled)
            unwrapped_positions = unwrapped_positions + delta_scaled @ np.asarray(atoms.cell.array, dtype=float)
            previous_scaled = current_scaled
        else:
            unwrapped_positions = positions.copy()

        if len(atoms) == expected_atoms:
            displacement = unwrapped_positions - initial_positions
            msd = float(np.mean(np.sum(displacement[indices_for_msd] ** 2, axis=1))) if indices_for_msd else None
        else:
            msd = None
        row: dict[str, Any] = {
            "frame": frame_index,
            "time_fs": frame_index * args.timestep_fs if args.timestep_fs is not None else None,
            "energy_ev": energy,
            "temperature_K": temperature,
            "volume_angstrom3": volume,
            "msd_angstrom2": msd,
        }
        for first, second in args.distance_pair:
            key = f"distance_{first}_{second}_angstrom"
            try:
                row[key] = float(atoms.get_distance(first, second, mic=True))
            except Exception:
                row[key] = None
        frame_rows.append(row)

    if not frame_rows:
        raise SystemExit("Trajectory contains no readable frames.")
    production = frame_rows[min(args.equilibration_frames, len(frame_rows)) :]
    if not production:
        raise SystemExit("Equilibration frames consume the entire trajectory.")

    def values(key: str) -> list[float]:
        return [float(row[key]) for row in production if row.get(key) is not None]

    energy_values = values("energy_ev")
    temperature_values = values("temperature_K")
    volume_values = values("volume_angstrom3")
    msd_values = values("msd_angstrom2")
    distance_summaries = {
        key: finite_summary(values(key))
        for key in frame_rows[0]
        if key.startswith("distance_")
    }
    report = {
        "input": str(input_path),
        "frames": len(frame_rows),
        "production_start_frame": min(args.equilibration_frames, len(frame_rows) - 1),
        "atoms": expected_atoms,
        "elements": elements,
        "timestep_fs": args.timestep_fs,
        "msd_indices": indices_for_msd,
        "unwrapped_periodic_displacement": not args.no_unwrap,
        "production_summary": {
            "energy_ev": finite_summary(energy_values),
            "temperature_K": finite_summary(temperature_values),
            "volume_angstrom3": finite_summary(volume_values),
            "msd_angstrom2": finite_summary(msd_values),
            "energy_slope_ev_per_fs": linear_slope(energy_values, args.timestep_fs),
            "temperature_slope_K_per_fs": linear_slope(temperature_values, args.timestep_fs),
            "distance": distance_summaries,
        },
        "diagnostics": {
            "missing_energy_frames": missing_energy_frames,
            "missing_temperature_frames": missing_temperature_frames,
            "invalid_volume_frames": invalid_volume_frames,
            "nonfinite_frames": nonfinite_frames,
            "warnings": warnings,
        },
        "timeseries": frame_rows,
        "limitations": [
            "Temperature requires velocities and uses the classical kinetic estimator.",
            "MSD unwrapping assumes fully periodic cells with modest cell changes; inspect variable-cell trajectories separately.",
            "A trajectory diagnostic does not establish equilibrium, kinetics, or mechanism without sampling and control analysis.",
        ],
    }

    if args.csv_output:
        assert csv_path is not None
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        import csv

        fields = list(frame_rows[0])
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(frame_rows)
        report["csv_output"] = str(csv_path)
    if args.output:
        assert output_path is not None
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    if args.pretty:
        summary = report["production_summary"]
        print(f"Frames: {report['frames']} (production starts at {report['production_start_frame']})")
        print(f"Energy: {summary['energy_ev']}")
        print(f"Temperature: {summary['temperature_K']}")
        print(f"Volume: {summary['volume_angstrom3']}")
        print(f"MSD: {summary['msd_angstrom2']}")
        for key, value in report["diagnostics"].items():
            if value:
                print(f"{key}: {value}")
    elif not args.output:
        json.dump(report, sys.stdout, indent=2)
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
