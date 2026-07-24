# Integrated Research Plan Contract

`workflow/integrated_research_plan.md` is the human-readable planning authority for a research project. It is the narrative complement to the machine-readable manifest and the short research spine. It must explain why the proposed work can answer the decision, not merely list files or solver commands.

## When The Artifact Is Required

Create or refresh the plan before creating a new experiment packet when the request includes any of:

- a research plan, technical route, methodology, roadmap, or experimental design
- a new scientific claim, nontrivial model choice, or consequential engineering decision
- more than one plausible method, scale, mechanism, or interpretation
- an AIMD, MLIP, MD, FEM, experimental, or coupled route
- a branching DFT project, even when it remains single-scale

The bundled DFT and multiscale scaffolders always create the file so the default project has a planning authority. A narrowly scoped execution-only request may reuse a current plan; it does not need a new long document solely because another job is being launched.

Do not treat a detailed plan as evidence that a task is multiscale. A DFT-only plan can still be decision-grade. Add a second scale only when its observable or boundary condition is required to resolve the decision.

## Lifecycle And Status

The plan lives at:

```text
workflow/integrated_research_plan.md
```

Use one status near the top of the document and in the manifest:

- `draft`: route is proposed and assumptions remain open
- `current`: route, gates, and next action agree with the control plane
- `stale`: a decision, gate, or route changed and the narrative has not been reconciled
- `superseded`: retain history but point to the replacement plan or decision record

Before an expensive launch, update the plan to `current`. Never silently overwrite a materially different technical route; record the decision and why the old route was retired.

## Required Sections

Use these exact top-level section names. The validator checks them for projects using schema `1.1`.

1. `Research Decision And Scope`
2. `Control Snapshot`
3. `Scientific Rationale And Scale Decision`
4. `Evidence, Models, And Assumptions`
5. `Stage Roadmap`
6. `Stage Gates And Deliverables`
7. `Resource-Aware Execution Order`
8. `Risks, Negative Results, And Escalation`
9. `Research Spine Synchronization`
10. `Definition Of Done`

The `Control Snapshot` must contain bullet fields named `Objective`, `Active claim`, `Current gate`, `Next action`, and `Stop rule`. Their values must agree with the manifest's `research_spine` block and `workflow/research_spine.md`.

## Required Narrative Content

The plan must state, in concrete terms:

- the scientific or engineering decision and the claim that could change it
- system boundary, state variables, operating window, non-goals, and intentionally deferred scales
- candidate mechanisms or hypotheses and why the selected model ladder can distinguish them
- the observable, estimator, units, uncertainty target, and acceptance rule for each claim
- what is directly supported by the planned method and what remains a proxy, extrapolation, or unresolved question
- source quality, known missing inputs, and explicit labeled assumptions
- resource constraints, minimum viable route, optional extensions, and a prioritization order
- credible negative, inconclusive, and stop outcomes rather than only a success narrative

Do not replace this material with generic placeholders in a plan marked `current`. When information is unavailable, write a labeled assumption, its risk, the evidence needed to resolve it, and whether it blocks launch.

## Stage Grammar

Give every roadmap item a stable identifier such as `P0`, `P1`, `S01`, or `N0`. A plan may use a single DFT stage or a multi-stage DAG. For each stage, include:

1. the question or gate it closes and the claim IDs it informs
2. inputs and provenance requirements
3. the model, method, and reasoning for choosing them
4. controls, sensitivity axes, and independent checks
5. planned outputs, units, and the downstream consumer
6. acceptance, kill, retry, or escalation condition
7. its dependency and relationship to the main research line

For a cross-scale handoff, also record the producer, consumer, mapping equation or adapter, units, tensor basis, state variables, validity domain, uncertainty, and rejection route. For a single-scale plan, explicitly say why an added scale is not currently needed and what observation would change that decision.

## Synchronization Rules

The planning artifact is the detailed explanation; these files remain the operational sources of truth:

- `workflow/research_spine.md`: short current orientation
- `workflow/experiment_manifest.json`: machine-readable claims, stages, dependencies, and scale choice
- `workflow/claim_matrix.csv`: claim-to-evidence mapping
- `workflow/branch_register.csv`: side-branch scope and promotion rules
- `workflow/next_action_queue.csv`: one prioritized action per active claim
- `workflow/decision_log.md`: append-only route and promotion decisions

At project creation, after every gate, before opening a material branch, and before an expensive launch, reconcile the plan's control snapshot, roadmap, gates, and execution order with those files. Use `maintain_research_spine.py` to detect drift. Treat conflicting versions as a review blocker, not a reason to choose whichever file is most convenient.

## Validation

For multiscale or branching projects, `validate_experiment_manifest.py` enforces the plan contract for schema `1.1`:

- the declared artifact exists inside the project root
- all required sections exist
- every manifest claim and stage appears in the plan
- the control snapshot agrees with the manifest research spine
- strict validation rejects a non-current plan and unresolved placeholders

This is a structural and traceability check, not a certification that the scientific reasoning is correct. The branch-specific validation gates still decide scientific adequacy.
