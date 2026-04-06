#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ENERGY_PATTERNS = [
    re.compile(r"F=\s*([-+]?\d+(?:\.\d+)?)"),
    re.compile(r"TOTEN\s*=\s*([-+]?\d+(?:\.\d+)?)"),
]


def iter_job_dirs(project_root: Path) -> list[Path]:
    runs_root = project_root / "runs"
    if not runs_root.exists():
        return []
    job_dirs: list[Path] = []
    for incar in runs_root.rglob("INCAR"):
        job_dir = incar.parent
        if (job_dir / "POSCAR").exists() and (job_dir / "KPOINTS").exists():
            job_dirs.append(job_dir)
    return sorted(job_dirs)


def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="ignore")
    except OSError:
        return ""


def parse_system(incar_path: Path) -> str:
    for line in read_text(incar_path).splitlines():
        if line.strip().startswith("SYSTEM"):
            parts = line.split("=", 1)
            if len(parts) == 2:
                return parts[1].strip()
    return ""


def parse_status(job_dir: Path) -> tuple[str, int | None]:
    status_path = job_dir / ".status"
    if not status_path.exists():
        return "unknown", None
    line = read_text(status_path).strip()
    if "rc=" in line:
        match = re.search(r"rc=(\d+)", line)
        if match:
            return line, int(match.group(1))
    return line, None


def parse_energy(job_dir: Path) -> float | None:
    for candidate in (job_dir / "OSZICAR", job_dir / "OUTCAR"):
        text = read_text(candidate)
        if not text:
            continue
        matches: list[float] = []
        for pattern in ENERGY_PATTERNS:
            matches.extend(float(item) for item in pattern.findall(text))
        if matches:
            return matches[-1]
    return None


def detect_converged(job_dir: Path) -> bool:
    outcar = read_text(job_dir / "OUTCAR")
    if "reached required accuracy" in outcar:
        return True
    status, rc = parse_status(job_dir)
    return rc == 0 and status.startswith("DONE")


def summarize_job(project_root: Path, job_dir: Path) -> dict[str, object]:
    status, rc = parse_status(job_dir)
    return {
        "job_dir": str(job_dir.relative_to(project_root)),
        "system": parse_system(job_dir / "INCAR"),
        "status": status,
        "rc": rc,
        "energy_ev": parse_energy(job_dir),
        "converged": detect_converged(job_dir),
        "has_outcar": (job_dir / "OUTCAR").exists(),
        "has_contcar": (job_dir / "CONTCAR").exists(),
        "has_vasprun_xml": (job_dir / "vasprun.xml").exists(),
    }


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_verdicts(path: Path, rows: list[dict[str, object]]) -> None:
    lines = [
        "# Claim Verdicts",
        "",
        "Use this file to map scientific claims to finished calculations.",
        "",
        "| Job | Status | Converged | Energy (eV) | Notes |",
        "|---|---|---|---:|---|",
    ]
    for row in rows:
        energy = "" if row["energy_ev"] is None else f"{row['energy_ev']:.6f}"
        lines.append(
            f"| {row['job_dir']} | {row['status']} | {'yes' if row['converged'] else 'no'} | {energy} | |"
        )
    lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_open_questions(path: Path, rows: list[dict[str, object]]) -> None:
    lines = [
        "# Open Questions",
        "",
        "Fill in unresolved method or interpretation risks here.",
        "",
    ]
    unfinished = [row for row in rows if not row["converged"]]
    if unfinished:
        for row in unfinished:
            lines.append(f"- `{row['job_dir']}` is not yet converged or finished.")
    else:
        lines.append("- No unfinished runs detected in the current scan.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize VASP runs in a project tree.")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = args.project_root.expanduser().resolve()
    rows = [summarize_job(project_root, job_dir) for job_dir in iter_job_dirs(project_root)]

    analysis_dir = project_root / "analysis"
    write_csv(
        analysis_dir / "energy_summary.csv",
        rows,
        ["job_dir", "system", "status", "rc", "energy_ev", "converged"],
    )
    write_csv(
        analysis_dir / "run_status.csv",
        rows,
        ["job_dir", "status", "rc", "converged", "has_outcar", "has_contcar", "has_vasprun_xml"],
    )
    write_verdicts(analysis_dir / "claim_verdicts.md", rows)
    write_open_questions(analysis_dir / "open_questions.md", rows)
    (analysis_dir / "run_status.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
