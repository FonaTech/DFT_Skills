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
    "validate_integrated_research_plan.py",
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


def integrated_research_plan_md(system_name: str, pairs: list[tuple[str, str]], tasks: list[str]) -> str:
    primary_id, primary_claim = pairs[0]
    task_values = tasks or ["<define the first DFT task family>"]
    claim_lines = "\n".join(f"- `{claim_id}`: {claim_text}" for claim_id, claim_text in pairs)
    task_stages: list[str] = []
    for index, task in enumerate(task_values, 1):
        task_stages.extend(
            [
                f"### T{index:02d}: {task}",
                "",
                f"- Question and claims: state how this task tests {', '.join(claim_id for claim_id, _ in pairs)}.",
                "- Inputs and provenance: <structure, reference state, literature or user input, and versioned source>.",
                "- Method and reasoning: <explain why this calculation, approximation, and reference comparison can discriminate the claim>.",
                "- Controls and sensitivity axes: <functional, spin, charge, +U, dispersion, ENCUT, k-mesh, cell or slab size, and task-specific controls>.",
                "- Planned outputs: <observable, units, uncertainty estimate, and downstream consumer>.",
                "- Acceptance and escalation: <pass condition, negative result, retry, or observation that requires NEB, phonons, AIMD, MLIP/MD, or FEM>.",
                "",
            ]
        )

    return "\n".join(
        [
            f"# Integrated Research Plan: {system_name}",
            "",
            "- Plan status: draft",
            "- Planning authority: this document explains the route; workflow files below remain the operational control plane.",
            "",
            "## 1. Research Decision And Scope",
            "",
            f"- Primary claim: `{primary_id}` - {primary_claim}",
            "- Decision to inform: <state what changes if the claim is supported, contradicted, or inconclusive>.",
            "- System boundary and operating window: <composition, phase, defects, interfaces, charge, spin, temperature, pressure, field, strain, and environment>.",
            "- Non-goals: <state what is intentionally outside this packet>.",
            "",
            "## 2. Control Snapshot",
            "",
            f"- Objective: {primary_claim}",
            f"- Active claim: {primary_id}",
            "- Current gate: ground the scientific model and resolve launch-critical inputs",
            "- Next action: complete the model, structure, and convergence design before creating production jobs",
            "- Stop rule: <state when the decision is answered, the model is invalid, or the project must stop>",
            "",
            "## 3. Scientific Rationale And Scale Decision",
            "",
            "- Minimum route: DFT-only until a declared observable cannot be resolved at the electronic or local atomistic scale.",
            "- Why this route is sufficient: <connect the primary observable to a DFT-testable quantity and reference state>.",
            "- Deferred scales: <AIMD, MLIP/MD, FEM, or experimental calibration considered but not currently required>.",
            "- Escalation trigger: <specific fluctuation, time scale, size effect, geometry field, or failed gate that requires another method>.",
            "",
            "## 4. Evidence, Models, And Assumptions",
            "",
            "- Candidate mechanisms and alternatives: <record competing explanations rather than only the preferred story>.",
            "- Model ladder: <baseline functional, correlation treatment, dispersion, relativistic treatment, and task-specific escalation>.",
            "- Evidence and provenance: <user material, local files, literature, official documentation, or labeled model prior>.",
            "- Assumptions awaiting resolution: <assumption; risk if false; evidence or owner needed to resolve it; launch blocker yes/no>.",
            "",
            "## 5. Stage Roadmap",
            "",
            "### P0: Freeze the decision boundary and input provenance",
            "",
            "- Close: the claim, target observable, reference states, system variants, and constraints are explicit.",
            "- Output: a resolved request summary, source ledger, and named assumptions.",
            "- Gate: do not infer missing composition, charge, spin, or environmental conditions as facts.",
            "",
            "### P1: Select the scientific model and method ladder",
            "",
            "- Close: selected approximation can distinguish the stated mechanisms and has a documented limitation.",
            "- Output: theory packet with method rationale, controls, and escalation rule.",
            "- Gate: choose a higher method only when it changes the decision tolerance, not by habit.",
            "",
            "### P2: Build structures and reference states",
            "",
            "- Close: every structure has provenance, stoichiometry, charge, spin, cell, surface, defect, and reference-state definitions.",
            "- Output: normalized structures and a structure manifest.",
            "- Gate: no production job without a reproducible structure source and compatible references.",
            "",
            "### P3: Establish numerical and physical baselines",
            "",
            "- Close: basis, k-point, cell or slab, force, spin, and reference-state controls meet the required tolerance.",
            "- Output: a convergence record and a baseline result packet.",
            "- Gate: numerical convergence alone is not a mechanism or validation verdict.",
            "",
            *task_stages,
            "### P4: Integrate controls, uncertainty, and claim evidence",
            "",
            "- Close: each claim has direct evidence, indirect support, unresolved limits, and a counterfactual or sensitivity control.",
            "- Output: updated claim matrix and auditable analysis tables.",
            "- Gate: report inconclusive or contradictory results rather than forcing a rank or mechanism.",
            "",
            "### P5: Produce the decision-grade verdict",
            "",
            "- Close: the evidence package answers the stated decision within its declared validity domain.",
            "- Output: claim verdicts, reproducibility metadata, limits, and next recommended experiment.",
            "- Gate: separate completed calculations from planned extensions and proxies from measured engineering quantities.",
            "",
            "## 6. Stage Gates And Deliverables",
            "",
            "| Stage | Required deliverable | Acceptance or stop condition | Main-line effect |",
            "|---|---|---|---|",
            "| P0 | resolved decision and source ledger | unknown launch-critical inputs are labeled | sets scope |",
            "| P1 | theory and method packet | model limitations and escalation trigger stated | locks first route |",
            "| P2 | provenance-tracked structures | reference states are compatible | permits baseline jobs |",
            "| P3 | convergence and control packet | tolerances support the observable | permits task stages |",
            "| T## | claim-specific result | task-specific control and pass condition met | supports or challenges a claim |",
            "| P4-P5 | claim verdict and report | uncertainty and limits are explicit | closes, revises, or escalates the decision |",
            "",
            "## 7. Resource-Aware Execution Order",
            "",
            "1. Run the smallest representative structure and one decisive control before expanding variants.",
            "2. Resolve the dominant method or structure uncertainty before launching broad parameter sweeps.",
            "3. Add sensitivity axes only when they can change the claim or reduce the dominant uncertainty.",
            "4. Escalate to a new scale only after its trigger is observed and its downstream consumer is defined.",
            "",
            "## 8. Risks, Negative Results, And Escalation",
            "",
            "- A nonconverged, out-of-domain, or incompatible-reference result is a failed gate, not evidence.",
            "- If competing variants overlap within uncertainty, report them as unresolved rather than force a ranking.",
            "- If the required observable depends on finite-temperature events, long-time sampling, device geometry, or experimental calibration, record the limitation and activate only the justified escalation route.",
            "- Preserve a negative result when it rules out a mechanism, reference state, or method assumption.",
            "",
            "## 9. Research Spine Synchronization",
            "",
            "- Keep this plan's control snapshot synchronized with `workflow/request_summary.md`, `workflow/claim_matrix.md`, `workflow/experiment_matrix.csv`, and `analysis/claim_verdicts.md`.",
            "- For a branching or multiscale escalation, create the full control plane and synchronize this plan with `research_spine.md`, the manifest, branch register, decision log, and next-action queue.",
            "- Update the plan after a gate, route change, failed control, or new decision-critical evidence.",
            "",
            "## 10. Definition Of Done",
            "",
            "- [ ] The decision, claim IDs, observables, units, and pass conditions are explicit.",
            "- [ ] Structure and method provenance are recorded and launch-critical assumptions are resolved or bounded.",
            "- [ ] Every planned task has controls, acceptance, stop, and escalation conditions.",
            "- [ ] Results distinguish direct evidence, indirect support, and unresolved limits.",
            "- [ ] The final verdict is reproducible and states whether a new scale is actually required.",
            "",
            "## Claims",
            "",
            claim_lines,
            "",
        ]
    )


def request_summary(system_name: str, claims: list[str], tasks: list[str]) -> str:
    lines = [
        "# Request Summary",
        "",
        f"- System: {system_name}",
        f"- Requested task families: {', '.join(tasks) if tasks else 'not yet specified'}",
        "- Goal: convert the user request or paper into a reproducible DFT workflow packet.",
        "- Detailed planning authority: workflow/integrated_research_plan.md.",
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
            "- Keep workflow/integrated_research_plan.md current before production launch.",
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

    if write_text(
        project_root / "workflow/integrated_research_plan.md",
        integrated_research_plan_md(args.system_name, pairs, args.task),
        args.overwrite,
    ):
        created.append("workflow/integrated_research_plan.md")
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
                "planning_artifact": "workflow/integrated_research_plan.md",
                "planning_validation": "python3 scripts/validate_integrated_research_plan.py --plan workflow/integrated_research_plan.md --pretty",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
