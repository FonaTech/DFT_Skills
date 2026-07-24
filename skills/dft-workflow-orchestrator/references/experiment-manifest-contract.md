# Experiment Manifest Contract

The manifest is the machine-readable control plane for DFT, AIMD, MLIP, MD, FEM, and coupled projects. It describes intent and dependencies; it does not pretend to be an engine input deck.

## Contents

1. Required files
2. Manifest schema
3. Stage contract
4. Handoff contract
5. Validation rules
6. Example

## Required Files

The multiscale scaffold creates:

```text
workflow/
├── integrated_research_plan.md
├── research_contract.md
├── decision_brief.md
├── research_spine.md
├── branch_register.csv
├── data_lineage.csv
├── next_action_queue.csv
├── decision_log.md
├── assumptions.md
├── knowledge_sources.md
├── claim_matrix.csv
├── experiment_manifest.json
├── handoff_register.csv
├── validation_plan.md
└── risk_register.md
```

Keep the existing DFT files (`request_summary.md`, `theory_packet.md`, `claim_matrix.md`, `experiment_matrix.csv`, and `method_guardrails.md`) when the project includes a VASP lane. The two schemas can coexist; the multiscale manifest is the dependency authority.

## Manifest Schema

Top-level keys:

```json
{
  "schema_version": "1.1",
  "project": {"name": "...", "system": "...", "root": "..."},
  "user_preferences": {"route": "...", "depth": "...", "deliverables": [], "constraints": [], "accepted_alternatives": []},
  "research_spine": {"objective": "...", "active_claim_id": "C01", "current_gate": "...", "next_action": "...", "stop_rule": "...", "non_goals": []},
  "scale_decision": {"required_scales": ["..."], "deferred_scales": ["..."], "rationale": "...", "escalation_trigger": "..."},
  "planning_artifact": {"path": "workflow/integrated_research_plan.md", "status": "draft", "required_sections": ["..."], "synchronizes": ["research_spine", "claims", "stages", "handoffs", "next_action_queue"], "last_reviewed": ""},
  "claims": [{"id": "C01", "text": "...", "observable": "...", "pass_condition": "..."}],
  "stages": [{"id": "S01", "kind": "dft", "name": "...", "depends_on": [], "inputs": [], "outputs": [], "controls": [], "validation": [], "status": "planned"}],
  "handoffs": [{"id": "H01", "from_stage": "S01", "to_stage": "S02", "artifact": "...", "quantity_type": "...", "schema": "...", "mapping": "...", "units": "...", "basis": "...", "voigt_order": "...", "sign_convention": "...", "state_variables": "...", "averaging_rule": "...", "uncertainty": "...", "validity": "...", "acceptance": "..."}],
  "resources": {"software": [], "hardware": {}, "licenses": []},
  "metadata": {"created_by": "...", "created_at": "...", "notes": "..."}
}
```

Allowed stage `kind` values are `dft`, `aimd`, `mlip`, `md`, `homogenization`, `fem`, `experiment`, `analysis`, and `coupling`. Use `coupling` for an explicit adapter or iterative feedback stage, not as a vague label.

Allowed status values are `planned`, `ready`, `submitted`, `running`, `converged`, `validated`, `failed`, `blocked`, `skipped`, and `interpreted`.

## Stage Contract

Every stage must declare:

- unique ID and kind
- human-readable name and scientific purpose
- upstream dependencies
- input artifacts and their required schema or units
- output artifacts and provenance fields
- controls and sensitivity axes
- validation tests and pass conditions
- compute, software, license, and resource assumptions
- failure behavior and retry or feedback route
- status and optional execution metadata

The top-level `scale_decision` should declare the minimum sufficient scales, deliberately deferred scales, the rationale, and the observable trigger for escalation. It is optional for legacy DFT-only packets but required for a strict multiscale review.

The top-level `research_spine` is the live orientation record. Keep its objective, active claim, current gate, next action, and stop rule synchronized with `workflow/research_spine.md` and the `Control Snapshot` in `workflow/integrated_research_plan.md`. Use `workflow/branch_register.csv` to govern side branches, `workflow/data_lineage.csv` to trace artifacts, `workflow/next_action_queue.csv` to limit work in progress, and `workflow/decision_log.md` for append-only promotion decisions. Read [research-spine-and-state.md](research-spine-and-state.md) and [integrated-research-plan-contract.md](integrated-research-plan-contract.md) for the full protocol.

## Integrated Planning Artifact

New multiscale scaffold projects use schema `1.1` and must declare `planning_artifact`. It points to the detailed, human-readable `workflow/integrated_research_plan.md`; it is not a replacement for the manifest.

The plan must contain the required planning-contract sections, every claim ID, every stage ID, and a control snapshot that matches `research_spine`. Use `draft` while design assumptions are open, `current` before an expensive launch, `stale` when the route has drifted, and `superseded` only when a decision log points to a replacement. Schema `1.0` remains accepted by the validator for existing projects, but new scaffolded projects must use `1.1`.

Stage-specific minimums:

| Kind | Minimum additional declaration |
|---|---|
| dft | engine, method ladder, structure and reference states |
| aimd | ensemble, state points, timestep, equilibration, production, replicas |
| mlip | family or checkpoint, domain, precision, calculator, model validation |
| md | driver, potential, ensemble, timestep, sampling and stop rules |
| homogenization | ensemble or representative volume, estimator, weighting, fit and error |
| fem | equations, fields, geometry, boundary conditions, constitutive inputs, verification |
| experiment | measurement, protocol, calibration, uncertainty and data location |
| analysis | source artifacts, estimator, units and acceptance criteria |
| coupling | mapping, transformation, synchronization and conservation test |

## Handoff Contract

Every handoff must answer:

1. Which artifact is produced and consumed?
2. What schema, units, basis, sign, and normalization does it use?
3. What state variables and validity window travel with it?
4. What transformation or fitting equation is applied?
5. What uncertainty and parameter correlations travel with it?
6. What acceptance test rejects the handoff?
7. Where does a failed or out-of-domain query go?

Use `workflow/handoff_register.csv` for row-level records. Keep raw source values and transformed values distinct.

## Validation Rules

The bundled validator checks:

- required top-level keys and schema version
- unique claim, stage, and handoff IDs
- supported kinds and statuses
- dependency existence and acyclicity
- stage-to-claim references when present
- handoff source and destination existence
- required handoff fields and register headers
- duplicate IDs and unresolved template placeholders
- strict-mode completeness for controls, outputs, validation, and pass conditions
- for schema `1.1`, the integrated plan location, required sections, claim and stage coverage, status, and control-snapshot synchronization

It deliberately does not certify scientific correctness, units, executable availability, or numerical convergence. Those require the branch-specific gates.

## Example

```json
{
  "schema_version": "1.1",
  "project": {"name": "oxide-coupled-device", "system": "proton conductor", "root": "."},
  "user_preferences": {"route": "DFT to MLIP-MD to FEM", "depth": "production", "deliverables": ["validated conductivity closure", "device response"], "constraints": ["target-domain validation required"], "accepted_alternatives": ["AIMD pilot before MLIP"]},
  "research_spine": {"objective": "Decide whether proton transport changes device response", "active_claim_id": "C01", "current_gate": "validate the MLIP on transport-relevant states", "next_action": "DFT-label challenge configurations", "stop_rule": "stop when propagated uncertainty no longer changes the device decision", "non_goals": ["electrode degradation"]},
  "scale_decision": {"required_scales": ["electronic", "atomistic-surrogate", "extended-atomistic", "continuum"], "deferred_scales": [], "rationale": "Transport needs atomistic sampling and device geometry changes the decision.", "escalation_trigger": "MLIP or constitutive validity failure sends the workflow upstream."},
  "planning_artifact": {"path": "workflow/integrated_research_plan.md", "status": "current", "required_sections": ["Research Decision And Scope", "Control Snapshot", "Scientific Rationale And Scale Decision", "Evidence, Models, And Assumptions", "Stage Roadmap", "Stage Gates And Deliverables", "Resource-Aware Execution Order", "Risks, Negative Results, And Escalation", "Research Spine Synchronization", "Definition Of Done"], "synchronizes": ["research_spine", "claims", "stages", "handoffs", "next_action_queue"], "last_reviewed": "2026-01-01T00:00:00Z"},
  "claims": [{
    "id": "C01",
    "text": "Proton mobility changes the device response across temperature.",
    "observable": "temperature-dependent effective conductivity",
    "pass_condition": "held-out FEM curve remains within declared uncertainty"
  }],
  "stages": [
    {"id": "S01", "kind": "dft", "name": "defect and barrier references", "depends_on": [], "claim_ids": ["C01"], "inputs": ["structures"], "outputs": ["dft_labels"], "controls": ["site", "charge", "method"], "validation": ["convergence", "reference_state"], "status": "planned"},
    {"id": "S02", "kind": "mlip", "name": "target-domain validation", "depends_on": ["S01"], "claim_ids": ["C01"], "inputs": ["dft_labels"], "outputs": ["validated_checkpoint"], "controls": ["held_out", "challenge"], "validation": ["force_error", "stability"], "status": "planned"},
    {"id": "S03", "kind": "md", "name": "state-grid sampling", "depends_on": ["S02"], "claim_ids": ["C01"], "inputs": ["validated_checkpoint"], "outputs": ["diffusion_ensemble"], "controls": ["replica", "temperature"], "validation": ["autocorrelation", "finite_size"], "status": "planned"},
    {"id": "S04", "kind": "homogenization", "name": "conductivity closure", "depends_on": ["S03"], "claim_ids": ["C01"], "inputs": ["diffusion_ensemble"], "outputs": ["conductivity_table"], "controls": ["volume", "fit"], "validation": ["held_out_state"], "status": "planned"},
    {"id": "S05", "kind": "fem", "name": "device response", "depends_on": ["S04"], "claim_ids": ["C01"], "inputs": ["conductivity_table"], "outputs": ["device_curve"], "controls": ["mesh", "time_step"], "validation": ["benchmark", "conservation"], "status": "planned"}
  ],
  "handoffs": [{"id": "H01", "from_stage": "S04", "to_stage": "S05", "artifact": "conductivity_table", "quantity_type": "rank-2 tensor state table", "schema": "conductivity-v1", "mapping": "tensor-to-solver basis rotation", "units": "S/m", "basis": "crystal to device coordinates", "voigt_order": "not applicable", "sign_convention": "positive flux follows positive driving force convention in the governing equation", "state_variables": "temperature and composition", "averaging_rule": "replica mean with correlated uncertainty", "uncertainty": "bootstrap covariance by state", "validity": "T=300..800 K, composition=x range", "acceptance": "round-trip units and held-out state"}],
  "resources": {"software": ["DFT", "MLIP", "MD", "FEM"], "hardware": {}, "licenses": []},
  "metadata": {"created_by": "scaffold_multiscale_project.py", "created_at": "", "notes": ""}
}
```
