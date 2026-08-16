#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.util
import json
import math
import os
import platform
from pathlib import Path
from typing import Any, Callable


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_config(path: Path | None) -> tuple[dict[str, Any], str | None]:
    if path is None:
        return {}, None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Calculator config must be a JSON object.")
    return payload, sha256_file(path)


def resolve_factory(spec: str) -> tuple[Callable[..., Any], dict[str, Any]]:
    if ":" not in spec:
        raise ValueError("Factory must use MODULE:CALLABLE syntax.")
    module_name, attribute_path = spec.split(":", 1)
    module = importlib.import_module(module_name)
    value: Any = module
    for part in attribute_path.split("."):
        value = getattr(value, part)
    if not callable(value):
        raise TypeError(f"Resolved factory is not callable: {spec}")
    metadata = {
        "mode": "factory",
        "spec": spec,
        "module": module_name,
        "module_version": getattr(module, "__version__", None),
    }
    return value, metadata


def load_adapter(path: Path) -> tuple[Callable[[dict[str, Any]], Any], Callable[[dict[str, Any]], Any] | None, dict[str, Any]]:
    spec = importlib.util.spec_from_file_location("project_mlip_adapter", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load adapter: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    builder = getattr(module, "build_calculator", None)
    if not callable(builder):
        raise AttributeError("Adapter must define build_calculator(config).")
    metadata_builder = getattr(module, "model_metadata", None)
    if metadata_builder is not None and not callable(metadata_builder):
        raise TypeError("Adapter model_metadata must be callable when present.")
    metadata = {"mode": "adapter", "path": str(path), "sha256": sha256_file(path)}
    return builder, metadata_builder, metadata


def calculator_builder(args: argparse.Namespace) -> tuple[Callable[[dict[str, Any]], Any], Callable[[dict[str, Any]], Any] | None, dict[str, Any]]:
    if args.factory:
        factory, metadata = resolve_factory(args.factory)

        def build(config: dict[str, Any]) -> Any:
            return factory(**config)

        return build, None, metadata
    adapter = args.adapter.expanduser().resolve()
    return load_adapter(adapter)


def single_point_results(atoms: Any, require_stress: bool) -> tuple[dict[str, Any], dict[str, Any]]:
    import numpy as np

    energy = float(atoms.get_potential_energy())
    forces = np.asarray(atoms.get_forces(), dtype=float)
    if not math.isfinite(energy):
        raise ValueError("Calculator returned a non-finite energy.")
    if forces.shape != (len(atoms), 3) or not np.isfinite(forces).all():
        raise ValueError(f"Calculator returned invalid forces with shape {forces.shape}.")
    results: dict[str, Any] = {"energy": energy, "forces": forces}
    stress = None
    try:
        stress = np.asarray(atoms.get_stress(voigt=True), dtype=float)
        if stress.size not in (6, 9) or not np.isfinite(stress).all():
            raise ValueError("Calculator returned invalid stress.")
        results["stress"] = stress
    except Exception:
        if require_stress:
            raise RuntimeError("Stress was required but the calculator did not provide a valid stress.")
    force_norms = np.linalg.norm(forces, axis=1) if len(forces) else np.asarray([], dtype=float)
    summary = {
        "energy_ev": energy,
        "energy_ev_per_atom": energy / len(atoms) if len(atoms) else None,
        "max_force_ev_per_angstrom": float(force_norms.max()) if force_norms.size else 0.0,
        "stress_available": stress is not None,
    }
    return results, summary


def relax_atoms(atoms: Any, optimizer_name: str, fmax: float, steps: int) -> tuple[bool, int]:
    from ase.optimize import BFGS, FIRE

    optimizer_cls = {"BFGS": BFGS, "FIRE": FIRE}[optimizer_name]
    optimizer = optimizer_cls(atoms, logfile=None)
    converged = bool(optimizer.run(fmax=fmax, steps=steps))
    return converged, int(optimizer.nsteps)


def relative_display(path: Path, base: Path) -> str:
    return os.path.relpath(str(path), str(base))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run trusted ASE calculator inference or relaxation with reproducibility metadata."
    )
    parser.add_argument("--input", type=Path, required=True, help="ASE-readable input structure or trajectory.")
    parser.add_argument("--output", type=Path, required=True, help="Output extxyz file with single-point results.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--factory", help="Calculator factory in MODULE:CALLABLE form; JSON config becomes keyword arguments.")
    source.add_argument("--adapter", type=Path, help="Trusted Python adapter defining build_calculator(config).")
    parser.add_argument("--config", type=Path, help="JSON calculator configuration; content is not copied into metadata.")
    parser.add_argument("--input-format", help="Optional ASE input format override.")
    parser.add_argument("--mode", choices=["single-point", "relax"], default="single-point")
    parser.add_argument("--optimizer", choices=["BFGS", "FIRE"], default="FIRE")
    parser.add_argument("--fmax", type=float, default=0.05, help="Relaxation force threshold in eV/Angstrom.")
    parser.add_argument("--steps", type=int, default=500, help="Maximum optimizer steps per frame.")
    parser.add_argument("--max-frames", type=int, default=0, help="Maximum frames to process; zero means all.")
    parser.add_argument("--require-stress", action="store_true", help="Fail if the calculator does not return stress.")
    parser.add_argument("--metadata-output", type=Path, help="Metadata JSON path; defaults beside the output.")
    parser.add_argument("--overwrite", action="store_true", help="Replace existing output and metadata files.")
    parser.add_argument(
        "--allow-code-execution",
        action="store_true",
        help="Acknowledge that importing a factory or adapter executes local Python code.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.allow_code_execution:
        raise SystemExit("Refusing to import calculator code without --allow-code-execution.")
    if args.max_frames < 0 or args.steps < 1 or args.fmax <= 0:
        raise SystemExit("Require --max-frames >= 0, --steps >= 1, and --fmax > 0.")
    input_path = args.input.expanduser().resolve()
    output_path = args.output.expanduser().resolve()
    if output_path.suffix.lower() not in {".xyz", ".extxyz"}:
        raise SystemExit("--output must use .xyz or .extxyz so labeled results remain portable.")
    metadata_path = (
        args.metadata_output.expanduser().resolve()
        if args.metadata_output
        else output_path.with_name(output_path.stem + ".metadata.json")
    )
    config_path = args.config.expanduser().resolve() if args.config else None
    if metadata_path in {input_path, output_path}:
        raise SystemExit("Metadata, input, and labeled-output paths must be distinct.")
    if config_path and config_path in {output_path, metadata_path}:
        raise SystemExit("Config, labeled-output, and metadata paths must be distinct.")
    for path in (output_path, metadata_path):
        if path.exists() and not args.overwrite:
            raise SystemExit(f"Output exists; use --overwrite to replace it: {path}")
    if input_path == output_path:
        raise SystemExit("Input and output paths must differ.")

    try:
        import ase
        import numpy as np
        from ase.calculators.singlepoint import SinglePointCalculator
        from ase.io import read, write
    except ImportError as exc:
        raise SystemExit(f"ASE and NumPy are required: missing {exc.name}") from exc

    config, config_hash = load_config(config_path)
    build, metadata_builder, calculator_source = calculator_builder(args)
    calculator = build(config)
    if calculator is None:
        raise RuntimeError("Calculator builder returned None.")

    raw_frames = read(str(input_path), index=":", format=args.input_format)
    frames = list(raw_frames) if isinstance(raw_frames, (list, tuple)) else [raw_frames]
    if args.max_frames:
        frames = frames[: args.max_frames]
    if not frames:
        raise RuntimeError("Input contains no structures.")

    output_frames: list[Any] = []
    frame_summaries: list[dict[str, Any]] = []
    for index, source_atoms in enumerate(frames):
        atoms = source_atoms.copy()
        atoms.calc = calculator
        converged = None
        optimizer_steps = 0
        if args.mode == "relax":
            converged, optimizer_steps = relax_atoms(atoms, args.optimizer, args.fmax, args.steps)
        results, summary = single_point_results(atoms, args.require_stress)
        atoms.info["surrogate_frame_index"] = index
        atoms.info["surrogate_mode"] = args.mode
        atoms.info["surrogate_calculator_source"] = args.factory or str(args.adapter)
        atoms.calc = SinglePointCalculator(atoms, **results)
        summary.update({"frame": index, "atoms": len(atoms), "relax_converged": converged, "optimizer_steps": optimizer_steps})
        output_frames.append(atoms)
        frame_summaries.append(summary)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    write(str(output_path), output_frames, format="extxyz", write_results=True)
    model_metadata: Any = {}
    if metadata_builder:
        model_metadata = metadata_builder(config)
        if model_metadata is None:
            model_metadata = {}
        if not isinstance(model_metadata, dict):
            raise TypeError("Adapter model_metadata(config) must return a dictionary.")

    base = Path.cwd().resolve()
    metadata = {
        "input": relative_display(input_path, base),
        "input_sha256": sha256_file(input_path),
        "output": relative_display(output_path, base),
        "output_sha256": sha256_file(output_path),
        "mode": args.mode,
        "calculator_source": calculator_source,
        "config_path": relative_display(config_path, base) if config_path else None,
        "config_sha256": config_hash,
        "config_content_recorded": False,
        "model_metadata": model_metadata,
        "software": {
            "python": platform.python_version(),
            "ase": getattr(ase, "__version__", None),
            "numpy": getattr(np, "__version__", None),
        },
        "settings": {
            "require_stress": args.require_stress,
            "optimizer": args.optimizer if args.mode == "relax" else None,
            "fmax_ev_per_angstrom": args.fmax if args.mode == "relax" else None,
            "max_steps": args.steps if args.mode == "relax" else None,
        },
        "frames": frame_summaries,
        "warnings": [
            "A successful inference is not target-domain validation.",
            "Config content is excluded from metadata; preserve the config securely and record checkpoint license and checksum separately.",
        ],
    }
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": metadata["output"], "metadata": relative_display(metadata_path, base), "frames": len(output_frames)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
