#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


FLOAT_RE = r"[-+]?\d+(?:\.\d+)?(?:[Ee][-+]?\d+)?"
IONIC_RE = re.compile(
    rf"^\s*(\d+)\s+F=\s*({FLOAT_RE})\s+E0=\s*({FLOAT_RE})\s+d E =\s*({FLOAT_RE}).*$"
)
ITER_RE = re.compile(r"Iteration\s+(\d+)\(\s*(\d+)\)")
LOOP_RE = re.compile(rf"LOOP:\s+cpu time\s+\S+:\s+real time\s+({FLOAT_RE})")
RC_RE = re.compile(r"rc=(\d+)")
QUEUE_START_RE = re.compile(r"^START\s+(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+(.+)$")
QUEUE_DONE_RE = re.compile(r"^DONE\s+(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+rc=(\d+)\s+(.+)$")

WARNING_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("brmix", re.compile(r"BRMIX", re.IGNORECASE)),
    ("zbrent", re.compile(r"ZBRENT", re.IGNORECASE)),
    ("subspace", re.compile(r"Sub-Space-Matrix is not hermitian", re.IGNORECASE)),
    ("zhegv", re.compile(r"ZHEGV|ZHEEV", re.IGNORECASE)),
    ("edddav", re.compile(r"EDDDAV", re.IGNORECASE)),
    ("walltime", re.compile(r"time limit|SIGTERM|signal 15", re.IGNORECASE)),
]


def relative_display(path: str | Path, base: Path) -> str:
    return os.path.relpath(str(Path(path).expanduser()), str(base))


def normalize_logged_path(raw: str, project_root: Path) -> str:
    candidate = Path(raw).expanduser()
    if candidate.is_absolute():
        return relative_display(candidate, project_root)
    return str(candidate)


@dataclass
class QueueRow:
    queue_name: str
    state: str
    started_jobs: int
    finished_jobs: int
    active_job: str
    last_event: str


@dataclass
class JobRow:
    job_dir: str
    queue_names: str
    system: str
    state: str
    status: str
    rc: int | None
    converged: bool
    ionic_step: int | None
    electronic_step: int | None
    energy_ev: float | None
    delta_e_ev: float | None
    recent_energy_span_ev: float | None
    max_force_ev_per_a: float | None
    rms_force_ev_per_a: float | None
    last_loop_time_s: float | None
    recent_loop_mean_s: float | None
    last_update_iso: str
    last_update_age_minutes: float | None
    warning_tags: str
    progress_hint: str
    recommendation: str
    has_outcar: bool
    has_oszicar: bool
    has_contcar: bool
    has_vasprun_xml: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Live monitor for VASP job trees.")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root with runs/, logs/, and analysis/.")
    parser.add_argument(
        "--interval-seconds",
        type=float,
        default=0.0,
        help="Polling interval in seconds. Use 0 for a single scan.",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=1,
        help="Number of scans when interval-seconds is positive. Use 0 for unlimited.",
    )
    parser.add_argument(
        "--stale-minutes",
        type=float,
        default=30.0,
        help="Treat RUNNING jobs as stale when no runtime file changed for this many minutes.",
    )
    parser.add_argument("--pretty", action="store_true", help="Print a compact live summary to stdout.")
    return parser.parse_args()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def read_tail(path: Path, max_bytes: int = 200_000) -> str:
    try:
        with path.open("rb") as handle:
            handle.seek(0, 2)
            size = handle.tell()
            handle.seek(max(0, size - max_bytes))
            return handle.read().decode("utf-8", errors="ignore")
    except OSError:
        return ""


def iter_job_dirs(project_root: Path) -> list[Path]:
    runs_root = project_root / "runs"
    if not runs_root.exists():
        return []
    job_dirs: list[Path] = []
    for incar in runs_root.rglob("INCAR"):
        job_dir = incar.parent
        if (job_dir / "POSCAR").exists() and (job_dir / "KPOINTS").exists():
            job_dirs.append(job_dir.resolve())
    return sorted(set(job_dirs))


def parse_joblists(project_root: Path) -> tuple[dict[Path, list[str]], list[tuple[str, Path]]]:
    mapping: dict[Path, list[str]] = {}
    missing: list[tuple[str, Path]] = []
    joblists_root = project_root / "joblists"
    if not joblists_root.exists():
        return mapping, missing
    for joblist in sorted(joblists_root.glob("*.txt")):
        queue_name = joblist.stem
        for raw_line in read_text(joblist).splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            target = Path(line)
            resolved = target if target.is_absolute() else (project_root / target)
            resolved = resolved.expanduser().resolve()
            mapping.setdefault(resolved, []).append(queue_name)
            if not resolved.exists():
                missing.append((queue_name, resolved))
    return mapping, missing


def parse_queues(project_root: Path) -> list[QueueRow]:
    logs_root = project_root / "logs"
    if not logs_root.exists():
        return []
    rows: list[QueueRow] = []
    for queue_log in sorted(logs_root.glob("*/queue.log")):
        queue_name = queue_log.parent.name
        started_jobs = 0
        finished_jobs = 0
        active_job = ""
        last_event = ""
        for line in read_text(queue_log).splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            last_event = stripped
            start_match = QUEUE_START_RE.match(stripped)
            done_match = QUEUE_DONE_RE.match(stripped)
            if start_match:
                started_jobs += 1
                active_job = normalize_logged_path(start_match.group(2), project_root)
            elif done_match:
                finished_jobs += 1
                active_job = ""
        if last_event.startswith("Finished:"):
            state = "finished"
        elif active_job:
            state = "running"
        elif started_jobs:
            state = "partial"
        else:
            state = "idle"
        rows.append(
            QueueRow(
                queue_name=queue_name,
                state=state,
                started_jobs=started_jobs,
                finished_jobs=finished_jobs,
                active_job=active_job,
                last_event=last_event,
            )
        )
    return rows


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
    line = read_text(status_path).strip() or "unknown"
    match = RC_RE.search(line)
    return line, int(match.group(1)) if match else None


def parse_last_ionic(oszicar_text: str) -> tuple[int | None, float | None, float | None, float | None, float | None]:
    last_step = None
    last_f = None
    last_de = None
    history: list[float] = []
    for line in oszicar_text.splitlines():
        match = IONIC_RE.match(line)
        if not match:
            continue
        last_step = int(match.group(1))
        last_f = float(match.group(2))
        last_de = float(match.group(4))
        history.append(last_f)
    if not history:
        return None, None, None, None, None
    window = history[-5:]
    return last_step, last_f, last_de, max(window) - min(window), history[-1]


def parse_last_iteration(outcar_text: str) -> tuple[int | None, int | None]:
    last_ionic = None
    last_electronic = None
    for line in outcar_text.splitlines():
        match = ITER_RE.search(line)
        if match:
            last_ionic = int(match.group(1))
            last_electronic = int(match.group(2))
    return last_ionic, last_electronic


def parse_last_force_block(outcar_text: str) -> tuple[float | None, float | None]:
    lines = outcar_text.splitlines()
    header_idx = None
    for index, line in enumerate(lines):
        if "POSITION" in line and "TOTAL-FORCE" in line:
            header_idx = index
    if header_idx is None:
        return None, None

    forces: list[float] = []
    for line in lines[header_idx + 2 :]:
        stripped = line.strip()
        if not stripped or stripped.startswith("---"):
            break
        parts = line.split()
        if len(parts) < 6:
            continue
        try:
            fx, fy, fz = map(float, parts[3:6])
        except ValueError:
            continue
        forces.append(math.sqrt(fx * fx + fy * fy + fz * fz))
    if not forces:
        return None, None
    rms = math.sqrt(sum(value * value for value in forces) / len(forces))
    return max(forces), rms


def parse_loop_times(outcar_text: str) -> tuple[float | None, float | None]:
    values = [float(match.group(1)) for match in LOOP_RE.finditer(outcar_text)]
    if not values:
        return None, None
    recent = values[-10:]
    return values[-1], sum(recent) / len(recent)


def detect_converged(outcar_text: str, status: str, rc: int | None) -> bool:
    if "reached required accuracy" in outcar_text:
        return True
    return rc == 0 and status.startswith("DONE") and "General timing and accounting informations" in outcar_text


def warning_tags(*texts: str) -> list[str]:
    combined = "\n".join(texts)
    tags = [label for label, pattern in WARNING_PATTERNS if pattern.search(combined)]
    return sorted(set(tags))


def newest_runtime_update(job_dir: Path) -> tuple[str, float | None]:
    newest_ts = None
    newest_name = ""
    for name in (".heartbeat", ".status", "vasp.out", "OSZICAR", "OUTCAR", "vasprun.xml"):
        path = job_dir / name
        if not path.exists():
            continue
        ts = path.stat().st_mtime
        if newest_ts is None or ts > newest_ts:
            newest_ts = ts
            newest_name = name
    if newest_ts is None:
        return "", None
    stamp = datetime.fromtimestamp(newest_ts).isoformat(timespec="seconds")
    age_minutes = (time.time() - newest_ts) / 60.0
    return f"{stamp} ({newest_name})", age_minutes


def classify_state(
    status: str,
    rc: int | None,
    converged: bool,
    in_queue: bool,
    age_minutes: float | None,
    stale_minutes: float,
    job_exists: bool,
    has_outputs: bool,
) -> str:
    if not job_exists:
        return "queue-missing-target"
    if status.startswith("DONE") and rc is not None:
        if rc != 0:
            return "finished-error"
        if converged:
            return "finished-converged"
        return "finished-unverified"
    if status.startswith("RUNNING"):
        if age_minutes is not None and age_minutes > stale_minutes:
            return "running-stale"
        return "running"
    if in_queue:
        return "queued"
    if has_outputs:
        if age_minutes is not None and age_minutes > stale_minutes:
            return "orphaned-stale"
        return "orphaned-active"
    return "not-started"


def progress_hint(state: str, max_force: float | None) -> str:
    if state == "finished-converged":
        return "converged"
    if state == "running-stale":
        return "no recent runtime updates"
    if max_force is None:
        return "waiting for force block"
    if max_force < 0.02:
        return "at or very near force convergence"
    if max_force < 0.05:
        return "late-stage relaxation"
    if max_force < 0.10:
        return "approaching convergence"
    if max_force < 0.20:
        return "mid-stage relaxation"
    return "early-stage or large reconstruction"


def recommendation(state: str, warnings: list[str], max_force: float | None) -> str:
    if state == "queue-missing-target":
        return "Repair the missing job directory or remove it from the queue before launch."
    if state == "finished-error":
        return "Inspect vasp.out and OUTCAR tail before any restart."
    if state == "running-stale":
        return "Check mpirun/VASP process health and inspect the last runtime lines."
    if state == "finished-unverified":
        return "Confirm the stopping condition in OUTCAR before treating this as converged."
    if warnings:
        return "Inspect warning signatures and decide whether mixing, optimizer, or restart settings need adjustment."
    if state == "finished-converged":
        return "Promote CONTCAR into the next dependent task and update the claim matrix."
    if state == "running" and max_force is not None and max_force < 0.05:
        return "Continue monitoring and prepare downstream static, DOS, or control jobs."
    if state == "queued":
        return "Keep the front-end routing aligned with experiment_matrix.csv while the queue advances."
    if state == "not-started":
        return "Launch the job or queue only after workflow and provenance files are complete."
    return "Continue monitoring and compare progress against workflow pass conditions."


def summarize_job(project_root: Path, job_dir: Path, queue_names: list[str], stale_minutes: float) -> JobRow:
    exists = job_dir.exists()
    queue_label = ",".join(queue_names)
    if not exists:
        return JobRow(
            job_dir=relative_display(job_dir, project_root),
            queue_names=queue_label,
            system="",
            state="queue-missing-target",
            status="missing",
            rc=None,
            converged=False,
            ionic_step=None,
            electronic_step=None,
            energy_ev=None,
            delta_e_ev=None,
            recent_energy_span_ev=None,
            max_force_ev_per_a=None,
            rms_force_ev_per_a=None,
            last_loop_time_s=None,
            recent_loop_mean_s=None,
            last_update_iso="",
            last_update_age_minutes=None,
            warning_tags="",
            progress_hint="missing queued target",
            recommendation="Repair the missing job directory or remove it from the queue before launch.",
            has_outcar=False,
            has_oszicar=False,
            has_contcar=False,
            has_vasprun_xml=False,
        )

    status, rc = parse_status(job_dir)
    outcar_text = read_tail(job_dir / "OUTCAR")
    oszicar_text = read_tail(job_dir / "OSZICAR")
    vasp_text = read_tail(job_dir / "vasp.out")
    system = parse_system(job_dir / "INCAR")
    ionic_step, energy_ev, delta_e_ev, recent_energy_span_ev, _ = parse_last_ionic(oszicar_text)
    outcar_ionic_step, electronic_step = parse_last_iteration(outcar_text)
    if ionic_step is None:
        ionic_step = outcar_ionic_step
    max_force, rms_force = parse_last_force_block(outcar_text)
    last_loop_time, recent_loop_mean = parse_loop_times(outcar_text)
    converged = detect_converged(outcar_text, status, rc)
    warnings = warning_tags(outcar_text, vasp_text)
    last_update_iso, age_minutes = newest_runtime_update(job_dir)
    has_outcar = (job_dir / "OUTCAR").exists()
    has_oszicar = (job_dir / "OSZICAR").exists()
    has_contcar = (job_dir / "CONTCAR").exists()
    has_vasprun_xml = (job_dir / "vasprun.xml").exists()
    state = classify_state(
        status=status,
        rc=rc,
        converged=converged,
        in_queue=bool(queue_names),
        age_minutes=age_minutes,
        stale_minutes=stale_minutes,
        job_exists=True,
        has_outputs=any((has_outcar, has_oszicar, has_contcar, has_vasprun_xml)),
    )
    rel_job = relative_display(job_dir, project_root)
    return JobRow(
        job_dir=rel_job,
        queue_names=queue_label,
        system=system,
        state=state,
        status=status,
        rc=rc,
        converged=converged,
        ionic_step=ionic_step,
        electronic_step=electronic_step,
        energy_ev=energy_ev,
        delta_e_ev=delta_e_ev,
        recent_energy_span_ev=recent_energy_span_ev,
        max_force_ev_per_a=max_force,
        rms_force_ev_per_a=rms_force,
        last_loop_time_s=last_loop_time,
        recent_loop_mean_s=recent_loop_mean,
        last_update_iso=last_update_iso,
        last_update_age_minutes=age_minutes,
        warning_tags=",".join(warnings),
        progress_hint=progress_hint(state, max_force),
        recommendation=recommendation(state, warnings, max_force),
        has_outcar=has_outcar,
        has_oszicar=has_oszicar,
        has_contcar=has_contcar,
        has_vasprun_xml=has_vasprun_xml,
    )


def write_csv(path: Path, rows: list[JobRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(asdict(rows[0]).keys()) if rows else list(JobRow.__dataclass_fields__.keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_report(path: Path, project_root_label: str, generated_at: str, rows: list[JobRow], queues: list[QueueRow]) -> None:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row.state] = counts.get(row.state, 0) + 1

    attention = [row for row in rows if row.state in {"queue-missing-target", "finished-error", "running-stale", "finished-unverified"}]
    running = [row for row in rows if row.state == "running"]
    converged = [row for row in rows if row.state == "finished-converged"]

    lines = [
        "# Live Monitor Report",
        "",
        f"- Generated: {generated_at}",
        f"- Project root: {project_root_label}",
        "",
        "## Overview",
        "",
        f"- Total tracked jobs: {len(rows)}",
    ]
    for key in sorted(counts):
        lines.append(f"- {key}: {counts[key]}")
    lines.extend(["", "## Queue State", ""])

    if queues:
        lines.extend(
            [
                "| Queue | State | Started | Finished | Active Job |",
                "|---|---|---:|---:|---|",
            ]
        )
        for row in queues:
            lines.append(
                f"| {row.queue_name} | {row.state} | {row.started_jobs} | {row.finished_jobs} | {row.active_job} |"
            )
    else:
        lines.append("- No queue logs detected.")

    lines.extend(["", "## Attention Items", ""])
    if attention:
        for row in attention:
            lines.append(f"- `{row.job_dir}`: {row.state}. {row.recommendation}")
    else:
        lines.append("- No immediate intervention items detected.")

    lines.extend(["", "## Running Jobs", ""])
    if running:
        lines.extend(
            [
                "| Job | Ionic Step | Max Force (eV/A) | Progress | Last Update |",
                "|---|---:|---:|---|---|",
            ]
        )
        for row in running:
            force = "" if row.max_force_ev_per_a is None else f"{row.max_force_ev_per_a:.4f}"
            ionic = "" if row.ionic_step is None else str(row.ionic_step)
            lines.append(f"| {row.job_dir} | {ionic} | {force} | {row.progress_hint} | {row.last_update_iso} |")
    else:
        lines.append("- No jobs are currently marked RUNNING.")

    lines.extend(["", "## Ready For Next Stage", ""])
    if converged:
        for row in converged:
            lines.append(f"- `{row.job_dir}` converged. Promote `CONTCAR` into the next dependent task family.")
    else:
        lines.append("- No converged jobs detected in this scan.")

    lines.extend(
        [
            "",
            "## Front-End Loop",
            "",
            "- Compare converged jobs against `workflow/experiment_matrix.csv` pass conditions before advancing the workflow.",
            "- For correlated or magnetic systems, do not stop at a single branch, magnetic order, or U value even if one bootstrap run converged.",
            "- If a job is stale or failed, fix the method issue before expanding the queue.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def collect_rows(project_root: Path, stale_minutes: float) -> tuple[list[JobRow], list[QueueRow]]:
    queue_map, missing_targets = parse_joblists(project_root)
    queues = parse_queues(project_root)
    job_dirs = set(iter_job_dirs(project_root))
    job_dirs.update(queue_map.keys())

    rows: list[JobRow] = []
    for job_dir in sorted(job_dirs):
        rows.append(summarize_job(project_root, job_dir, queue_map.get(job_dir, []), stale_minutes))

    for queue_name, target in missing_targets:
        if target in job_dirs:
            continue
        rows.append(summarize_job(project_root, target, [queue_name], stale_minutes))

    rows.sort(key=lambda item: item.job_dir)
    return rows, queues


def write_outputs(project_root: Path, rows: list[JobRow], queues: list[QueueRow]) -> dict[str, object]:
    generated_at = datetime.now().isoformat(timespec="seconds")
    analysis_dir = project_root / "analysis"
    project_root_label = relative_display(project_root, Path.cwd().resolve())
    write_csv(analysis_dir / "live_status.csv", rows)
    write_json(analysis_dir / "live_status.json", [asdict(row) for row in rows])
    write_json(analysis_dir / "queue_status.json", [asdict(row) for row in queues])
    write_report(analysis_dir / "live_monitor_report.md", project_root_label, generated_at, rows, queues)

    counts: dict[str, int] = {}
    for row in rows:
        counts[row.state] = counts.get(row.state, 0) + 1
    return {
        "generated_at": generated_at,
        "project_root": project_root_label,
        "total_jobs": len(rows),
        "counts": counts,
        "analysis_outputs": [
            "analysis/live_status.csv",
            "analysis/live_status.json",
            "analysis/queue_status.json",
            "analysis/live_monitor_report.md",
        ],
    }


def print_compact(summary: dict[str, object]) -> None:
    counts = summary.get("counts", {})
    pieces = [f"tracked={summary.get('total_jobs', 0)}"]
    if isinstance(counts, dict):
        pieces.extend(f"{key}={counts[key]}" for key in sorted(counts))
    print(f"[{summary['generated_at']}] " + " ".join(pieces))


def main() -> int:
    args = parse_args()
    project_root = args.project_root.expanduser().resolve()
    if not project_root.exists():
        raise SystemExit(f"Project root does not exist: {args.project_root}")

    scan_count = 0
    while True:
        scan_count += 1
        rows, queues = collect_rows(project_root, args.stale_minutes)
        summary = write_outputs(project_root, rows, queues)
        if args.pretty or args.interval_seconds <= 0:
            print_compact(summary)
        if args.interval_seconds <= 0:
            break
        if args.iterations > 0 and scan_count >= args.iterations:
            break
        time.sleep(args.interval_seconds)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
