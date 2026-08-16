#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import re
import shutil
from pathlib import Path
from typing import Any


STAGE_KINDS = (
    "dft",
    "aimd",
    "mlip",
    "md",
    "homogenization",
    "fem",
    "experiment",
    "analysis",
    "coupling",
)

HELPER_SCRIPTS = [
    "preflight_multiscale_env.py",
    "preflight_dft_env.py",
    "validate_integrated_research_plan.py",
    "validate_experiment_manifest.py",
    "maintain_research_spine.py",
    "audit_mlip_dataset.py",
    "run_ase_surrogate.py",
    "analyze_atomistic_trajectory.py",
    "fetch_structures.py",
    "scaffold_dft_project.py",
    "render_vasp_job.py",
    "monitor_vasp_runs.py",
    "summarize_vasp_runs.py",
    "run_one_vasp_job.sh",
    "run_vasp_queue.sh",
    "clone_job_with_d3.sh",
]

STAGE_DEFAULTS: dict[str, dict[str, Any]] = {
    "dft": {
        "purpose": "Generate converged electronic-structure reference labels and property controls.",
        "inputs": ["structures", "method_packet"],
        "outputs": ["dft_reference_labels", "dft_property_tables"],
        "controls": ["functional_or_method", "basis_or_cutoff", "kpoints", "spin_charge", "reference_state"],
        "validation": ["numerical_convergence", "method_sensitivity", "provenance"],
        "pass_condition": "Reference jobs converge and controls support the claim.",
    },
    "aimd": {
        "purpose": "Sample finite-temperature atomistic behavior with first-principles forces.",
        "inputs": ["relaxed_structures", "dft_method_packet"],
        "outputs": ["aimd_trajectories", "representative_snapshots"],
        "controls": ["ensemble", "temperature_pressure", "timestep", "replicas", "cell_size"],
        "validation": ["equilibration", "drift", "replica_consistency", "effective_sample_count"],
        "pass_condition": "The trajectory supports the declared qualitative or statistical observable.",
    },
    "mlip": {
        "purpose": "Validate, train, fine-tune, or actively improve a machine-learning interatomic potential.",
        "inputs": ["reference_labels", "deployment_domain", "model_or_architecture"],
        "outputs": ["validated_checkpoint", "model_card", "challenge_report"],
        "controls": ["grouped_split", "hard_challenge", "baseline", "checkpoint_hash", "domain_monitor"],
        "validation": ["energy_force_stress_error", "downstream_observable", "stability", "extrapolation"],
        "pass_condition": "Target-domain and challenge-set gates meet the declared decision tolerance.",
    },
    "md": {
        "purpose": "Run larger or longer atomistic sampling with a validated MLIP or classical potential.",
        "inputs": ["validated_checkpoint", "state_grid"],
        "outputs": ["md_trajectories", "ensemble_observables"],
        "controls": ["ensemble", "timestep", "replicas", "state_grid", "abort_threshold"],
        "validation": ["physical_invariants", "sampling", "finite_size", "dft_spot_checks"],
        "pass_condition": "Production sampling stays in-domain and derived observables converge.",
    },
    "homogenization": {
        "purpose": "Reduce atomistic ensembles to state-dependent constitutive parameters or closures.",
        "inputs": ["trajectories_or_snapshots", "estimator_definition"],
        "outputs": ["constitutive_table", "fit_and_uncertainty"],
        "controls": ["representative_volume", "averaging_window", "state_grid", "fit_family"],
        "validation": ["sampling_convergence", "held_out_state", "identifiability", "units"],
        "pass_condition": "The closure is identifiable and valid over the downstream state window.",
    },
    "fem": {
        "purpose": "Solve the device, component, field, transport, or multiphysics response.",
        "inputs": ["geometry", "boundary_conditions", "constitutive_table"],
        "outputs": ["continuum_response", "sensitivity_and_validation"],
        "controls": ["mesh", "time_step", "solver", "boundary_condition", "parameter_sensitivity"],
        "validation": ["benchmark", "mesh_time_convergence", "conservation", "limiting_case"],
        "pass_condition": "Verification passes and the simulated state remains inside constitutive validity.",
    },
    "experiment": {
        "purpose": "Calibrate or independently validate a simulation stage with measured data.",
        "inputs": ["protocol", "raw_measurements", "calibration_model"],
        "outputs": ["calibrated_parameters", "held_out_validation"],
        "controls": ["replicates", "instrument_uncertainty", "split", "protocol"],
        "validation": ["measurement_uncertainty", "held_out_prediction", "calibration_residual"],
        "pass_condition": "Calibration and independent validation meet the stated decision tolerance.",
    },
    "analysis": {
        "purpose": "Compute claim-specific observables and assemble an auditable verdict.",
        "inputs": ["upstream_artifacts", "claim_matrix"],
        "outputs": ["analysis_tables", "claim_verdicts"],
        "controls": ["estimator", "reference", "uncertainty", "units"],
        "validation": ["reproducible_parser", "independent_check", "claim_traceability"],
        "pass_condition": "Every verdict traces to validated artifacts and explicit limits.",
    },
    "coupling": {
        "purpose": "Transform, synchronize, or iterate between stages with an explicit handoff contract.",
        "inputs": ["producer_artifact", "consumer_schema", "mapping_equation"],
        "outputs": ["mapped_artifact", "coupling_diagnostics"],
        "controls": ["units", "basis", "state_mapping", "synchronization", "feedback"],
        "validation": ["round_trip", "conservation", "limiting_case", "failure_route"],
        "pass_condition": "The handoff passes schema, physics, unit, and conservation checks.",
    },
}

STAGE_SCALES = {
    "dft": "electronic",
    "aimd": "finite-temperature-atomistic",
    "mlip": "atomistic-surrogate",
    "md": "extended-atomistic",
    "homogenization": "statistical-scale-bridge",
    "fem": "continuum",
    "experiment": "experimental",
    "analysis": None,
    "coupling": None,
}

PLAN_REQUIRED_SECTIONS = [
    "Research Decision And Scope",
    "Control Snapshot",
    "Scientific Rationale And Scale Decision",
    "Evidence, Models, And Assumptions",
    "Stage Roadmap",
    "Stage Gates And Deliverables",
    "Resource-Aware Execution Order",
    "Risks, Negative Results, And Escalation",
    "Research Spine Synchronization",
    "Definition Of Done",
]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str, overwrite: bool) -> bool:
    if path.exists() and not overwrite:
        return False
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")
    return True


def write_json(path: Path, payload: Any, overwrite: bool) -> bool:
    return write_text(path, json.dumps(payload, indent=2, ensure_ascii=True) + "\n", overwrite)


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str], overwrite: bool) -> bool:
    if path.exists() and not overwrite:
        return False
    ensure_dir(path.parent)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return True


def slug(value: str) -> str:
    result = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return result or "multiscale-project"


def claim_pairs(claims: list[str]) -> list[tuple[str, str]]:
    values = claims or ["<fill in a falsifiable scientific or engineering claim>"]
    return [(f"C{index:02d}", value) for index, value in enumerate(values, 1)]


def scales_for_stages(stage_kinds: list[str]) -> list[str]:
    return list(dict.fromkeys(scale for kind in stage_kinds if (scale := STAGE_SCALES[kind])))


def stage_record(index: int, kind: str, depends_on: list[str], claim_ids: list[str]) -> dict[str, Any]:
    defaults = STAGE_DEFAULTS[kind]
    stage_id = f"S{index:02d}"
    return {
        "id": stage_id,
        "kind": kind,
        "name": f"{kind} stage {index:02d}",
        "purpose": defaults["purpose"],
        "depends_on": depends_on,
        "claim_ids": claim_ids,
        "inputs": list(defaults["inputs"]),
        "outputs": list(defaults["outputs"]),
        "controls": list(defaults["controls"]),
        "validation": list(defaults["validation"]),
        "pass_condition": defaults["pass_condition"],
        "resources": {"software": [f"<select {kind} software>"], "hardware": "<define resources>"},
        "failure_route": "<define stop, retry, or feedback behavior>",
        "status": "planned",
    }


def research_contract(system_name: str, stage_kinds: list[str], claims: list[tuple[str, str]]) -> str:
    claim_lines = "\n".join(f"- `{cid}`: {text}" for cid, text in claims)
    stages = " -> ".join(stage_kinds) if stage_kinds else "<define stages>"
    return f"""# Research Contract

- System: {system_name}
- Evidence tier: <design / smoke / pilot / production / decision-grade>
- Selected stage route: {stages}
- Minimum required scales: {", ".join(scales_for_stages(stage_kinds)) or "none; analysis or coupling only"}
- Deferred scales: <record scales considered but not required>
- Scale rationale: <why the selected scale is the smallest sufficient one>
- Escalation trigger: <observable or failed gate that would require another scale>
- Primary decision: <what decision changes if the claim is supported?>
- Primary observable: <quantity, estimator, and units>
- Pass condition: <numeric or qualitative threshold>
- Compute and license assumptions: <fill in>
- Stop rule: <fill in>

## Claims

{claim_lines}

## Route Rationale

- Why this stack can resolve the decisive physics: <fill in>
- Rejected or deferred alternatives: <fill in>
- Largest model-form risk: <fill in>
- Largest numerical or sampling risk: <fill in>
- Feedback path if an upstream gate fails: <fill in>
"""


def assumptions_md() -> str:
    return """# Assumptions

Record assumptions that are reversible or still awaiting user or literature confirmation.

| ID | Assumption | Reason | Risk if false | Resolution or owner | Status |
|---|---|---|---|---|---|
| A01 | <fill in> | <fill in> | <low / medium / high> | <fill in> | open |
"""


def decision_brief_md() -> str:
    return """# Complex-Task Design Brief

Complete this when route, depth, deliverables, or resource limits can change the workflow. For a routine single-scale task, mark it not required and record why.

| Decision | User choice | Agent assumption or consequence |
|---|---|---|
| Preferred technical route | <DFT-only / AIMD / MLIP-MD / FEM / staged coupling / other> | |
| Target depth | <design / smoke / pilot / production / decision-grade> | |
| Primary goal and final artifact | <fill in> | |
| Accuracy and uncertainty standard | <fill in> | |
| Independent validation | <fill in> | |
| Available data, checkpoints, solvers, licenses, and hardware | <fill in> | |
| Time, compute, and labeling budget | <fill in> | |
| Forbidden assumptions or substitutions | <fill in> | |
| Useful partial result if blocked | <fill in> | |

Status: <open / confirmed / not required>
Reason for status: <fill in>
"""


def research_spine_md(system_name: str, claims: list[tuple[str, str]], stage_kinds: list[str]) -> str:
    primary_id, primary_claim = claims[0]
    return f"""# Research Spine

- System: {system_name}
- Objective: {primary_claim}
- Active claim: {primary_id}
- Decision: <what decision must this project inform?>
- Decisive observable: <quantity, estimator, units, and pass threshold>
- Minimum route: {" -> ".join(stage_kinds)}
- Non-goals and deferred scales: <fill in>
- Evidence tier: <design / smoke / pilot / production / decision-grade>
- Current validated conclusion: no validated result yet
- Current gate: workflow design and strict manifest validation
- Next action: complete the design brief and resolve launch-critical placeholders
- Dominant uncertainty: <fill in>
- Stop rule: <define when the decision is answered or the project must stop>
- Last review: <ISO timestamp and reviewer>

Read this file first when resuming the project. Update it after every gate, failure, branch promotion, or change of goal.
"""


def integrated_research_plan_md(
    system_name: str, claims: list[tuple[str, str]], stages: list[dict[str, Any]], stage_kinds: list[str]
) -> str:
    primary_id, primary_claim = claims[0]
    route = " -> ".join(stage_kinds)
    claim_lines = "\n".join(f"- `{claim_id}`: {claim_text}" for claim_id, claim_text in claims)
    stage_blocks: list[str] = []
    for stage in stages:
        claim_refs = ", ".join(f"`{item}`" for item in stage["claim_ids"])
        dependencies = ", ".join(f"`{item}`" for item in stage["depends_on"]) or "none; entry stage"
        stage_blocks.extend(
            [
                f"### {stage['id']}: {stage['name']}",
                "",
                f"- Question and claims: {stage['purpose']} Claims: {claim_refs}.",
                f"- Dependencies and inputs: depends on {dependencies}; inputs: {', '.join(stage['inputs'])}.",
                f"- Method and reasoning: <explain why the {stage['kind']} model, approximation, and state grid can reduce the decision-critical uncertainty>.",
                f"- Controls and validation: controls: {', '.join(stage['controls'])}; independent checks: {', '.join(stage['validation'])}.",
                f"- Outputs and consumer: {', '.join(stage['outputs'])}; record schema, units, basis, validity domain, and downstream use.",
                f"- Acceptance and feedback: {stage['pass_condition']} Failure route: {stage['failure_route']}",
                "",
            ]
        )

    return "\n".join(
        [
            f"# Integrated Research Plan: {system_name}",
            "",
            "- Plan status: draft",
            "- Planning authority: this narrative explains the scientific route; the manifest and control files remain the operational source of truth.",
            "",
            "## 1. Research Decision And Scope",
            "",
            f"- Primary claim: `{primary_id}` - {primary_claim}",
            "- Decision to inform: <state the scientific or engineering decision that changes with the claim verdict>.",
            "- System boundary and operating window: <composition, phase, interfaces, defects, charge, spin, temperature, pressure, field, strain, geometry, and environment>.",
            "- Non-goals: <state intentionally excluded observables, scales, or decisions>.",
            "",
            "## 2. Control Snapshot",
            "",
            f"- Objective: {primary_claim}",
            f"- Active claim: {primary_id}",
            "- Current gate: workflow design and strict manifest validation",
            "- Next action: complete the design brief and resolve launch-critical placeholders",
            "- Stop rule: <define when the decision is answered or the project must stop>",
            "",
            "## 3. Scientific Rationale And Scale Decision",
            "",
            f"- Selected route: {route}",
            f"- Minimum required scales: {', '.join(scales_for_stages(stage_kinds)) or 'none; analysis or coupling only'}.",
            "- Why this route is sufficient: <connect each stage to the decisive observable and identify the information it adds>.",
            "- Deferred scales: <record plausible scales that are not currently needed>.",
            "- Escalation trigger: <state the observable, failed gate, or boundary condition that would justify another scale>.",
            "",
            "## 4. Evidence, Models, And Assumptions",
            "",
            "- Candidate mechanisms and alternatives: <record competing explanations and how the route can distinguish them>.",
            "- Model ladder: <state electronic-structure method, sampling model, MLIP family or checkpoint, continuum closure, and experimental calibration as applicable>.",
            "- Evidence and provenance: <user material, local files, literature, official documentation, databases, labels, checkpoints, and solver versions>.",
            "- Assumptions awaiting resolution: <assumption; risk if false; evidence or owner needed to resolve it; launch blocker yes/no>.",
            "",
            "## 5. Stage Roadmap",
            "",
            "### P0: Freeze the decision boundary and design brief",
            "",
            "- Close: primary claim, route, depth, deliverables, budget, validation standard, and forbidden substitutions are explicit.",
            "- Gate: no expensive route is committed while a route-changing user preference is unresolved.",
            "",
            "### P1: Establish sources, structures, reference states, and model controls",
            "",
            "- Close: every input has provenance and each model layer has a defined validity domain.",
            "- Gate: do not start a stage from an untracked structure, dataset, checkpoint, material parameter, or solver assumption.",
            "",
            *stage_blocks,
            "## 6. Stage Gates And Deliverables",
            "",
            "| Stage | Decision contribution | Required deliverable | Acceptance, stop, or feedback condition |",
            "|---|---|---|---|",
            "| P0 | bounds the research question | confirmed design brief | route-changing choices are resolved or explicitly assumed |",
            "| P1 | establishes valid inputs | provenance and method packet | input and validity gaps are visible |",
            *[
                f"| {stage['id']} | {stage['purpose']} | {', '.join(stage['outputs'])} | {stage['pass_condition']} |"
                for stage in stages
            ],
            "| Verdict | supports, contradicts, or retires a claim | claim verdict packet | direct evidence, uncertainty, and limits are explicit |",
            "",
            "## 7. Resource-Aware Execution Order",
            "",
            "1. Complete P0-P1 and the lowest-cost decisive stage before broad sweeps or downstream coupling.",
            "2. Resolve the dominant model-form, data, or numerical uncertainty before expanding state grids or branch count.",
            "3. Open a side branch only when its expected information gain can change the decision and it has a pass and kill criterion.",
            "4. Start a downstream stage only after the required upstream gate and handoff acceptance pass.",
            "",
            "## 8. Risks, Negative Results, And Escalation",
            "",
            "- A failed convergence, validation, domain, unit, tensor, or conservation check is a blocked gate rather than a result to carry downstream.",
            "- If alternatives overlap within uncertainty, report an inconclusive decision instead of forcing a ranking or mechanism.",
            "- If a new scale is necessary, state its decisive observable, consumer, validation gate, and feedback route before adding it.",
            "- Retain negative results that rule out a structure, mechanism, potential, closure, or boundary condition.",
            "",
            "## 9. Research Spine Synchronization",
            "",
            "- Keep the Control Snapshot synchronized with `workflow/research_spine.md` and the manifest `research_spine` block.",
            "- Keep claim IDs, stage IDs, dependencies, gates, and handoffs synchronized with `workflow/experiment_manifest.json` and `workflow/claim_matrix.csv`.",
            "- Keep branch scope and promotion rules synchronized with `workflow/branch_register.csv`, `workflow/decision_log.md`, and `workflow/next_action_queue.csv`.",
            "- Review this plan after every gate, failure, promotion, route change, or project resume; mark it stale rather than silently letting it drift.",
            "",
            "## 10. Definition Of Done",
            "",
            "- [ ] All claims have observables, units, pass conditions, and direct or explicitly indirect evidence.",
            "- [ ] Every completed stage has traceable inputs, controls, validation artifacts, validity limits, and a recorded result state.",
            "- [ ] Every handoff has compatible units, schema, basis, state variables, uncertainty, and rejection behavior.",
            "- [ ] The current plan, research spine, manifest, branch register, and next-action queue agree.",
            "- [ ] The final conclusion distinguishes completed work, planned work, negative results, inconclusive outcomes, and justified next steps.",
            "",
            "## Claims",
            "",
            claim_lines,
            "",
        ]
    )


def decision_log_md() -> str:
    return """# Decision Log

Append decisions; do not rewrite history.

| Date | Decision ID | Claim | Branch | Decision | Evidence artifact IDs | Alternatives considered | Consequence | Reviewer |
|---|---|---|---|---|---|---|---|---|
| | D001 | C01 | B000 | Initial route proposed | | <fill in> | Complete design brief before launch | |
"""


def knowledge_sources_md() -> str:
    return """# Knowledge Sources

| Source type | Citation, path, URL, or identifier | Role | Version or date | Confidence | Notes |
|---|---|---|---|---|---|
| user or local | | | | | |
| RAG | | | | | |
| official documentation | | | | | |
| literature | | | | | |
| model prior | | | | | |

Stop the source cascade when the current tier supports the model ladder, controls, and acceptance gates.
"""


def validation_plan(stage_kinds: list[str]) -> str:
    lines = [
        "# Validation Plan",
        "",
        "Use independent gates. Numerical convergence is not physical validation.",
        "",
        "| Stage kind | Verification | Validation or reference | Uncertainty | Stop condition | Status |",
        "|---|---|---|---|---|---|",
    ]
    for kind in stage_kinds:
        lines.append(f"| {kind} | <fill in> | <fill in> | <fill in> | <fill in> | planned |")
    lines.append("")
    return "\n".join(lines)


def risk_register() -> str:
    return """# Risk Register

| ID | Risk | Stage | Likelihood | Impact | Trigger | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|---|---|
| R01 | <method or model-form risk> | <stage> | <low / medium / high> | <low / medium / high> | <observable> | <control or fallback> | <owner> | open |
| R02 | <sampling, extrapolation, or coupling risk> | <stage> | <low / medium / high> | <low / medium / high> | <observable> | <control or fallback> | <owner> | open |
"""


def copy_helpers(project_root: Path, overwrite: bool) -> list[str]:
    source_root = Path(__file__).resolve().parent
    target_root = project_root / "scripts"
    ensure_dir(target_root)
    copied: list[str] = []
    for name in HELPER_SCRIPTS:
        source = source_root / name
        if not source.exists():
            continue
        target = target_root / name
        if target.exists() and not overwrite:
            continue
        shutil.copy2(source, target)
        target.chmod(0o755)
        copied.append(str(target.relative_to(project_root)))
    return copied


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scaffold a reproducible DFT, AIMD, MLIP, MD, FEM, or coupled project.")
    parser.add_argument("--project-root", type=Path, required=True, help="Project root to create or extend.")
    parser.add_argument("--system-name", required=True, help="Human-readable material, device, or process name.")
    parser.add_argument("--claim", action="append", default=[], help="Falsifiable claim; repeat for multiple claims.")
    parser.add_argument("--stage", action="append", choices=STAGE_KINDS, default=[], help="Stage kind in dependency order; repeat to build a route.")
    parser.add_argument("--independent-stages", action="store_true", help="Do not chain stages linearly; edit dependencies in the manifest.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite generated templates and copied helpers.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = args.project_root.expanduser().resolve()
    stage_kinds = args.stage or ["dft"]
    claims = claim_pairs(args.claim)
    claim_ids = [cid for cid, _ in claims]
    project_name = slug(args.system_name)
    created: list[str] = []

    directories = [
        "workflow",
        "structures/raw",
        "structures/normalized",
        "data/raw",
        "data/curated",
        "data/splits",
        "data/trajectories",
        "data/exchange",
        "models/checkpoints",
        "models/cards",
        "meshes",
        "runs",
        "analysis",
        "logs",
        "joblists",
        "scripts",
    ]
    directories.extend(f"runs/S{index:02d}_{kind}" for index, kind in enumerate(stage_kinds, 1))
    directories.extend(f"analysis/S{index:02d}_{kind}" for index, kind in enumerate(stage_kinds, 1))
    for rel in directories:
        ensure_dir(project_root / rel)

    stages: list[dict[str, Any]] = []
    for index, kind in enumerate(stage_kinds, 1):
        dependencies = [] if args.independent_stages or index == 1 else [f"S{index - 1:02d}"]
        stages.append(stage_record(index, kind, dependencies, claim_ids))

    handoffs: list[dict[str, Any]] = []
    if not args.independent_stages:
        for index in range(len(stages) - 1):
            source = stages[index]
            target = stages[index + 1]
            handoffs.append(
                {
                    "id": f"H{index + 1:02d}",
                    "from_stage": source["id"],
                    "to_stage": target["id"],
                    "artifact": f"<define {source['kind']} output consumed by {target['kind']}>",
                    "quantity_type": "<scalar, vector, tensor, dataset, checkpoint, mesh, or field>",
                    "schema": "<artifact schema and version>",
                    "mapping": "<equation, transformation, or adapter>",
                    "units": "<source and target units>",
                    "basis": "<coordinate or tensor basis; not applicable if scalar>",
                    "voigt_order": "<Voigt order and shear convention; not applicable if non-tensor>",
                    "sign_convention": "<sign or virial convention; not applicable if irrelevant>",
                    "state_variables": "<temperature, pressure, composition, strain, field, phase, or other state>",
                    "averaging_rule": "<none, ensemble, representative volume, fit, or homogenization>",
                    "validity": "<state, spatial, and temporal validity window>",
                    "acceptance": "<unit, basis, conservation, and physical acceptance test>",
                    "uncertainty": "<uncertainty and correlation treatment>",
                    "status": "planned",
                }
            )

    manifest = {
        "schema_version": "1.1",
        "project": {"name": project_name, "system": args.system_name, "root": "."},
        "user_preferences": {
            "route": "<record user route preference or agent-selected route>",
            "depth": "<design / smoke / pilot / production / decision-grade>",
            "deliverables": ["<record expected final artifacts>"],
            "constraints": ["<record accuracy, compute, license, and time constraints>"],
            "accepted_alternatives": ["<record permitted substitutions>"],
        },
        "research_spine": {
            "objective": claims[0][1],
            "active_claim_id": claims[0][0],
            "current_gate": "workflow design and strict manifest validation",
            "next_action": "complete the design brief and resolve launch-critical placeholders",
            "stop_rule": "<define when the decision is answered or the project must stop>",
            "non_goals": ["<record non-goals and intentionally deferred work>"],
        },
        "scale_decision": {
            "required_scales": scales_for_stages(stage_kinds),
            "deferred_scales": ["<record scales considered but not required>"],
            "rationale": "<explain why this is the smallest sufficient scale stack>",
            "escalation_trigger": "<observable or failed gate that requires another scale>",
        },
        "planning_artifact": {
            "path": "workflow/integrated_research_plan.md",
            "status": "draft",
            "required_sections": PLAN_REQUIRED_SECTIONS,
            "synchronizes": ["research_spine", "claims", "stages", "handoffs", "next_action_queue"],
            "last_reviewed": "",
        },
        "claims": [
            {
                "id": claim_id,
                "text": claim_text,
                "observable": "<define observable and units>",
                "pass_condition": "<define acceptance threshold>",
                "status": "planned",
            }
            for claim_id, claim_text in claims
        ],
        "stages": stages,
        "handoffs": handoffs,
        "resources": {"software": [], "hardware": {}, "licenses": [], "environment_file": "<pin environment>"},
        "metadata": {
            "created_by": "scaffold_multiscale_project.py",
            "created_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
            "notes": "Edit the manifest and validate it before expensive execution.",
        },
    }

    text_files = {
        "workflow/integrated_research_plan.md": integrated_research_plan_md(args.system_name, claims, stages, stage_kinds),
        "workflow/research_contract.md": research_contract(args.system_name, stage_kinds, claims),
        "workflow/decision_brief.md": decision_brief_md(),
        "workflow/research_spine.md": research_spine_md(args.system_name, claims, stage_kinds),
        "workflow/decision_log.md": decision_log_md(),
        "workflow/assumptions.md": assumptions_md(),
        "workflow/knowledge_sources.md": knowledge_sources_md(),
        "workflow/validation_plan.md": validation_plan(stage_kinds),
        "workflow/risk_register.md": risk_register(),
        "analysis/claim_verdicts.md": "# Claim Verdicts\n\nMap each claim to validated artifacts and limits.\n",
        "analysis/open_questions.md": "# Open Questions\n\n- Record unresolved physics, data, and coupling questions here.\n",
        "joblists/bootstrap.txt": "# Add project-relative run directories here, one per line.\n",
    }
    for rel, content in text_files.items():
        if write_text(project_root / rel, content, args.overwrite):
            created.append(rel)

    if write_json(project_root / "workflow/experiment_manifest.json", manifest, args.overwrite):
        created.append("workflow/experiment_manifest.json")

    claim_rows = [
        {
            "claim_id": claim_id,
            "claim_text": claim_text,
            "observable": "<define observable and units>",
            "pass_condition": "<define acceptance threshold>",
            "stages": ";".join(stage["id"] for stage in stages),
            "evidence_tier": "<design / smoke / pilot / production / decision-grade>",
            "status": "planned",
            "notes": "",
        }
        for claim_id, claim_text in claims
    ]
    if write_csv(
        project_root / "workflow/claim_matrix.csv",
        claim_rows,
        ["claim_id", "claim_text", "observable", "pass_condition", "stages", "evidence_tier", "status", "notes"],
        args.overwrite,
    ):
        created.append("workflow/claim_matrix.csv")

    handoff_rows = [
        {
            "handoff_id": item["id"],
            "from_stage": item["from_stage"],
            "to_stage": item["to_stage"],
            "artifact": item["artifact"],
            "quantity_type": item["quantity_type"],
            "schema": item["schema"],
            "mapping": item["mapping"],
            "units": item["units"],
            "basis": item["basis"],
            "voigt_order": item["voigt_order"],
            "sign_convention": item["sign_convention"],
            "state_variables": item["state_variables"],
            "averaging_rule": item["averaging_rule"],
            "validity": item["validity"],
            "acceptance": item["acceptance"],
            "uncertainty": item["uncertainty"],
            "status": item["status"],
        }
        for item in handoffs
    ]
    if write_csv(
        project_root / "workflow/handoff_register.csv",
        handoff_rows,
        [
            "handoff_id", "from_stage", "to_stage", "artifact", "quantity_type", "schema", "mapping", "units",
            "basis", "voigt_order", "sign_convention", "state_variables", "averaging_rule", "validity",
            "acceptance", "uncertainty", "status",
        ],
        args.overwrite,
    ):
        created.append("workflow/handoff_register.csv")

    started_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    branch_rows = [
        {
            "branch_id": "B000",
            "parent_branch": "ROOT",
            "claim_id": claims[0][0],
            "purpose": "Main research line",
            "hypothesis": claims[0][1],
            "method_or_scale": ";".join(stage_kinds),
            "expected_information_gain": "decision-critical",
            "inputs": "workflow/experiment_manifest.json",
            "planned_outputs": "validated claim verdict",
            "pass_condition": "<claim pass condition and all required gates pass>",
            "kill_criterion": "<budget, failed premise, or superseded objective>",
            "merge_rule": "ROOT remains the main line; promote only validated branch artifacts",
            "owner": "<owner>",
            "status": "active",
            "started_at": started_at,
            "closed_at": "",
            "artifact_ids": "",
            "notes": "Review before opening child branches.",
        }
    ]
    branch_headers = [
        "branch_id", "parent_branch", "claim_id", "purpose", "hypothesis", "method_or_scale",
        "expected_information_gain", "inputs", "planned_outputs", "pass_condition", "kill_criterion",
        "merge_rule", "owner", "status", "started_at", "closed_at", "artifact_ids", "notes",
    ]
    if write_csv(project_root / "workflow/branch_register.csv", branch_rows, branch_headers, args.overwrite):
        created.append("workflow/branch_register.csv")

    lineage_headers = [
        "artifact_id", "kind", "path_or_uri", "parent_artifact_ids", "producer_stage", "branch_id",
        "schema", "units", "basis", "checksum", "software_version", "method_or_checkpoint",
        "created_at", "status", "validity", "retention", "notes",
    ]
    if write_csv(project_root / "workflow/data_lineage.csv", [], lineage_headers, args.overwrite):
        created.append("workflow/data_lineage.csv")

    action_rows = [
        {
            "action_id": "A001",
            "claim_id": claims[0][0],
            "branch_id": "B000",
            "action": "Complete design brief and make the manifest strict-valid",
            "why_now": "The research route must be bounded before expensive execution.",
            "expected_information_gain": "high",
            "prerequisites": "workflow/decision_brief.md;workflow/research_contract.md",
            "cost": "low",
            "pass_condition": "strict manifest validation passes",
            "kill_criterion": "user changes the primary objective or route",
            "owner": "<owner>",
            "status": "ready",
            "due_or_review_date": "<date>",
        }
    ]
    action_headers = [
        "action_id", "claim_id", "branch_id", "action", "why_now", "expected_information_gain",
        "prerequisites", "cost", "pass_condition", "kill_criterion", "owner", "status", "due_or_review_date",
    ]
    if write_csv(project_root / "workflow/next_action_queue.csv", action_rows, action_headers, args.overwrite):
        created.append("workflow/next_action_queue.csv")

    created.extend(copy_helpers(project_root, args.overwrite))
    print(
        json.dumps(
            {
                "project_root": os.path.relpath(str(project_root), str(Path.cwd().resolve())),
                "project_name": project_name,
                "stage_kinds": stage_kinds,
                "claims": [{"id": cid, "text": text} for cid, text in claims],
                "manifest": str((project_root / "workflow/experiment_manifest.json").relative_to(project_root)),
                "planning_artifact": "workflow/integrated_research_plan.md",
                "created_or_updated": created,
                "next": "python3 scripts/validate_experiment_manifest.py --manifest workflow/experiment_manifest.json --handoff-register workflow/handoff_register.csv",
                "planning_validation": "python3 scripts/validate_integrated_research_plan.py --plan workflow/integrated_research_plan.md --pretty",
                "research_spine_next": "python3 scripts/maintain_research_spine.py --project-root . --pretty",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
