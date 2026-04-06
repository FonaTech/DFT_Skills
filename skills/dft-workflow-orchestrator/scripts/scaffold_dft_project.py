#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
from pathlib import Path


HELPER_SCRIPTS = [
    "preflight_dft_env.py",
    "fetch_structures.py",
    "render_vasp_job.py",
    "monitor_vasp_runs.py",
    "summarize_vasp_runs.py",
    "run_one_vasp_job.sh",
    "run_vasp_queue.sh",
    "clone_job_with_d3.sh",
]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def relative_display(path: Path, base: Path | None = None) -> str:
    anchor = (base or Path.cwd()).expanduser().resolve()
    return os.path.relpath(str(path), str(anchor))


def write_text(path: Path, content: str, overwrite: bool) -> bool:
    if path.exists() and not overwrite:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def claim_ids(claims: list[str]) -> list[tuple[str, str]]:
    if not claims:
        claims = ["<fill in a scientific claim to test>"]
    return [(f"C{i:02d}", claim) for i, claim in enumerate(claims, start=1)]


def request_summary(system_name: str, claims: list[str], tasks: list[str]) -> str:
    lines = [
        "# Request Summary",
        "",
        f"- System: {system_name}",
        f"- Requested task families: {', '.join(tasks) if tasks else 'not yet specified'}",
        "- Goal: convert the user request or paper into a reproducible DFT workflow packet.",
        "- Literature basis: document the paper, notes, or input files here.",
        "- Output standard: planning packet first, launch packet second, verdict packet last.",
        "",
        "## Claims",
        "",
    ]
    for claim in claims or ["<fill in claim>"]:
        lines.append(f"- {claim}")
    lines.append("")
    return "\n".join(lines)


def knowledge_sources_md() -> str:
    return "\n".join(
        [
            "# Knowledge Sources",
            "",
            "| Source Type | Citation or Path | Role | Confidence | Notes |",
            "|---|---|---|---|---|",
            "| uploaded | | | | |",
            "| local | | | | |",
            "| RAG | | | | |",
            "| web | | | | |",
            "| model prior | | | | |",
            "",
            "Record how the theory basis was grounded before building the calculation packet.",
            "",
        ]
    )


def theory_packet_md(system_name: str, claims: list[str], tasks: list[str]) -> str:
    lines = [
        "# Theory Packet",
        "",
        f"- System: {system_name}",
        f"- Task families: {', '.join(tasks) if tasks else 'not yet specified'}",
        "",
        "## Candidate Mechanisms",
        "",
        "- <list paper claims, mechanistic pictures, and alternatives>",
        "",
        "## Candidate Theoretical Models",
        "",
        "- <band picture / defect thermodynamics / correlated oxide / interface transfer / kinetics proxy / etc.>",
        "",
        "## Chosen Working Model",
        "",
        "- <state the working model for the first production packet and why>",
        "",
        "## Model Ladder",
        "",
        "- Baseline: <PBE/PBEsol or other>",
        "- Correlation treatment: <DFT+U / hybrid / none>",
        "- Escalation path: <NEB / phonons / AIMD / GW / DMFT / etc.>",
        "",
        "## Observable Map",
        "",
    ]
    for claim in claims or ["<fill in claim>"]:
        lines.append(f"- Claim: {claim}")
        lines.append("  Observable: <energy / DOS / PDOS / optical / barrier / charge / structure>")
        lines.append("  Direct support: <fill in>")
        lines.append("  Indirect or unresolved part: <fill in>")
        lines.append("")
    lines.extend(
        [
            "## Open Theoretical Risks",
            "",
            "- <missing literature coverage, missing method level, finite-temperature caveat, etc.>",
            "",
        ]
    )
    return "\n".join(lines)


def claim_matrix_md(pairs: list[tuple[str, str]]) -> str:
    lines = [
        "# Claim Matrix",
        "",
        "| Claim ID | Claim Text | DFT-Testable? | Direct or Indirect | Required Controls | Status |",
        "|---|---|---|---|---|---|",
    ]
    for claim_id, claim_text in pairs:
        lines.append(f"| {claim_id} | {claim_text} | | | | planned |")
    lines.append("")
    return "\n".join(lines)


def method_guardrails_md() -> str:
    return "\n".join(
        [
            "# Method Guardrails",
            "",
            "- State the functional explicitly.",
            "- State whether `+U` is required and why.",
            "- State the magnetic order that was tested.",
            "- Keep convergence axes explicit: ENCUT, k-mesh, force threshold, and slab or supercell size when relevant.",
            "- Separate direct DFT evidence from indirect mechanistic support.",
            "- Do not launch production jobs without structure provenance and controls.",
            "",
        ]
    )


def copy_helpers(project_root: Path, overwrite: bool) -> list[str]:
    copied: list[str] = []
    source_root = Path(__file__).resolve().parent
    target_root = project_root / "scripts"
    ensure_dir(target_root)
    for name in HELPER_SCRIPTS:
        src = source_root / name
        dst = target_root / name
        if dst.exists() and not overwrite:
            continue
        shutil.copy2(src, dst)
        dst.chmod(0o755)
        copied.append(str(dst.relative_to(project_root)))
    return copied


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str], overwrite: bool) -> bool:
    if path.exists() and not overwrite:
        return False
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold a reproducible DFT project layout.")
    parser.add_argument("--project-root", type=Path, required=True, help="Project root to create.")
    parser.add_argument("--system-name", required=True, help="Human-readable system name.")
    parser.add_argument("--claim", action="append", default=[], help="Scientific claim to test.")
    parser.add_argument("--task", action="append", default=[], help="Requested task family.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing templates and helper scripts.")
    args = parser.parse_args()

    project_root = args.project_root.expanduser().resolve()
    for rel in [
        "workflow",
        "structures/raw_cif",
        "structures/poscar",
        "structures/slabs",
        "runs/00_bulk",
        "runs/01_surface",
        "runs/02_adsorption",
        "runs/03_defects",
        "runs/04_migration",
        "runs/05_optics",
        "joblists",
        "analysis",
        "logs",
        "scripts",
    ]:
        ensure_dir(project_root / rel)

    pairs = claim_ids(args.claim)
    created: list[str] = []

    if write_text(project_root / "workflow/request_summary.md", request_summary(args.system_name, args.claim, args.task), args.overwrite):
        created.append("workflow/request_summary.md")
    if write_text(project_root / "workflow/knowledge_sources.md", knowledge_sources_md(), args.overwrite):
        created.append("workflow/knowledge_sources.md")
    if write_text(project_root / "workflow/theory_packet.md", theory_packet_md(args.system_name, args.claim, args.task), args.overwrite):
        created.append("workflow/theory_packet.md")
    if write_text(project_root / "workflow/claim_matrix.md", claim_matrix_md(pairs), args.overwrite):
        created.append("workflow/claim_matrix.md")
    if write_text(project_root / "workflow/method_guardrails.md", method_guardrails_md(), args.overwrite):
        created.append("workflow/method_guardrails.md")

    experiment_rows = [
        {
            "claim_id": claim_id,
            "claim_text": claim_text,
            "claim_class": "",
            "model_system": "",
            "job_family": ";".join(args.task),
            "primary_observable": "",
            "reference_or_control": "",
            "sensitivity_axis": "",
            "method_risk": "",
            "pass_condition": "",
            "notes": "",
        }
        for claim_id, claim_text in pairs
    ]
    if write_csv(
        project_root / "workflow/experiment_matrix.csv",
        experiment_rows,
        [
            "claim_id",
            "claim_text",
            "claim_class",
            "model_system",
            "job_family",
            "primary_observable",
            "reference_or_control",
            "sensitivity_axis",
            "method_risk",
            "pass_condition",
            "notes",
        ],
        args.overwrite,
    ):
        created.append("workflow/experiment_matrix.csv")

    if write_csv(
        project_root / "analysis/energy_summary.csv",
        [],
        ["job_dir", "system", "status", "rc", "energy_ev", "converged"],
        args.overwrite,
    ):
        created.append("analysis/energy_summary.csv")
    if write_csv(
        project_root / "analysis/run_status.csv",
        [],
        ["job_dir", "status", "rc", "converged", "has_outcar", "has_contcar", "has_vasprun_xml"],
        args.overwrite,
    ):
        created.append("analysis/run_status.csv")
    if write_text(project_root / "analysis/claim_verdicts.md", "# Claim Verdicts\n\nMap claims to finished calculations here.\n", args.overwrite):
        created.append("analysis/claim_verdicts.md")
    if write_text(project_root / "analysis/open_questions.md", "# Open Questions\n\n- Fill unresolved method or interpretation risks here.\n", args.overwrite):
        created.append("analysis/open_questions.md")
    if write_text(
        project_root / "analysis/live_monitor_report.md",
        "# Live Monitor Report\n\nRun `python3 scripts/monitor_vasp_runs.py --project-root .` while jobs are active.\n",
        args.overwrite,
    ):
        created.append("analysis/live_monitor_report.md")
    if write_text(
        project_root / "joblists/bootstrap.txt",
        "# Add relative run directories here, one per line.\n# Example:\n# runs/00_bulk/example_relax\n",
        args.overwrite,
    ):
        created.append("joblists/bootstrap.txt")

    created.extend(copy_helpers(project_root, args.overwrite))

    print(
        json.dumps(
            {
                "project_root": relative_display(project_root),
                "system_name": args.system_name,
                "claims": [{"id": claim_id, "text": claim_text} for claim_id, claim_text in pairs],
                "created_or_updated": created,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
