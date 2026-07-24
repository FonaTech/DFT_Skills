# Research Spine And State Control

Use this reference to keep a long or branching materials project aligned with its original decision. It is a project-control protocol, not a replacement for scientific analysis.

## Contents

1. North-star contract
2. Claim and gate state
3. Branch governance
4. Data and model lineage
5. Next-action queue
6. Review cadence
7. Recovery from drift

## North-Star Contract

Maintain one short `workflow/research_spine.md` with:

- decision the project must inform
- primary claim and decisive observable
- non-goals and deliberately deferred scales
- evidence tier and acceptable uncertainty
- current validated conclusion
- current blocking gate
- one prioritized next action
- conditions for stopping, merging, or escalating
- last review time and reviewer

Keep this file readable without opening raw trajectories, logs, or every branch. It is the first file to read when a task resumes after interruption or context compaction.

Maintain `workflow/integrated_research_plan.md` alongside it. The spine is deliberately short; the integrated plan is the detailed narrative of the decision boundary, method rationale, staged gates, resource order, negative outcomes, and definition of done. Its `Control Snapshot` must match the spine and manifest. Read [integrated-research-plan-contract.md](integrated-research-plan-contract.md) before creating or revising it.

## Claim And Gate State

Use stable claim IDs (`C01`, `C02`, ...) and stage IDs (`S01`, `S02`, ...). A claim can be:

`planned -> in_progress -> supported | indirectly_supported | contradicted | inconclusive | blocked | retired`

A stage can be:

`planned -> ready -> submitted -> running -> converged -> validated -> interpreted`

or `failed`, `blocked`, or `skipped` with a reason. Do not infer a claim verdict from a stage status alone.

For every claim, record:

- current verdict and confidence
- evidence artifacts and controls
- unresolved assumptions and dominant uncertainty
- next gate and pass condition
- branch IDs that support or challenge it
- decision impact if the verdict changes

## Branch Governance

Create a row in `workflow/branch_register.csv` before starting a nontrivial variant. Required columns:

```text
branch_id,parent_branch,claim_id,purpose,hypothesis,method_or_scale,
expected_information_gain,inputs,planned_outputs,pass_condition,
kill_criterion,merge_rule,owner,status,started_at,closed_at,artifact_ids,notes
```

Allowed branch statuses are `proposed`, `active`, `paused`, `passed`, `failed`, `merged`, `killed`, and `deferred`.

Branch rules:

1. Every branch has one parent (`ROOT` for the main line) and at least one claim.
2. State the uncertainty or decision that the branch is meant to reduce.
3. Define a kill criterion before launch: method failure, low information value, budget cap, or contradiction.
4. Define a merge rule: what result is promoted to the main line and where it is recorded.
5. Keep branch scope bounded by a budget, state grid, number of jobs, or review date.
6. Do not open a child branch from a failed or unvalidated parent unless the failure itself is the hypothesis being repaired.
7. Close or defer completed branches; do not leave ambiguous `active` rows.
8. Keep exploratory plots and scratch files attached to a branch, not mixed into the main verdict directory.

Use expected information gain to prioritize. A branch that cannot change a decision, reduce a dominant uncertainty, or repair a failed gate should be deferred or killed.

## Main-Line Promotion

Promote a result only when:

- the branch pass condition is met
- the artifact is validated and traceable
- controls and uncertainty are recorded
- the result changes or confirms the claim matrix
- the main-line next action is updated

Record promotion in `workflow/decision_log.md` with date, evidence, alternatives considered, and reviewer. Never silently replace a main-line result with a branch result.

## Data And Model Lineage

Track each meaningful artifact in `workflow/data_lineage.csv`:

```text
artifact_id,kind,path_or_uri,parent_artifact_ids,producer_stage,branch_id,
schema,units,basis,checksum,software_version,method_or_checkpoint,
created_at,status,validity,retention,notes
```

Artifact kinds include `structure`, `label`, `trajectory`, `dataset`, `split`, `checkpoint`, `mesh`, `parameter_table`, `solver_result`, `analysis`, and `decision_record`.

Lineage rules:

- raw inputs are immutable; derived files point to parents
- a split records its grouping rule and source dataset
- a model records its training split, checkpoint parent, and configuration
- a handoff records transformed units and basis, not only the destination file
- a verdict cites artifact IDs, not vague directory names
- checksums are added for files that can be rerun or transferred
- invalid or superseded artifacts remain visible with status and reason

## Next-Action Queue

Maintain one queue ordered by decision value, not by convenience. Each row should include:

```text
action_id,claim_id,branch_id,action,why_now,expected_information_gain,
prerequisites,cost,pass_condition,kill_criterion,owner,status,due_or_review_date
```

At most one action per claim should be `ready` unless parallel execution is explicitly justified. The active action must name the gate it will close. When a job finishes, update the queue before submitting another job.

Good actions:

- a method sensitivity run that resolves the dominant model-form uncertainty
- a DFT spot check of an MLMD extrapolation frame
- a missing state point that determines constitutive interpolation
- a mesh or timestep test that separates numerical from physical disagreement
- an independent control that could falsify the current mechanism

Bad actions:

- another plot with no pass condition
- expanding a branch after its claim is already decided
- collecting more correlated frames after effective sample size has plateaued
- training a larger model without a deployment-domain failure

## Review Cadence

Refresh the spine:

- before the first expensive run
- after every gate, failure, or surprising observation
- before opening a new branch
- before promoting a result
- at the end of each evidence tier
- before handing data to another person, solver, or platform

The refresh command is:

```bash
python3 scripts/maintain_research_spine.py --project-root . --pretty
```

The generated report should expose:

- drift between `workflow/research_spine.md` and the manifest's `research_spine` block
- drift between the integrated plan's `Control Snapshot` and the manifest's `research_spine` block
- missing required integrated-plan sections, claim IDs, or stage IDs
- current claim and stage counts
- active, orphaned, stale, and unbounded branches
- missing or invalid lineage references
- blocked gates and unresolved placeholders
- the next ready action and why it is prioritized

## Recovery From Drift

When a project has become difficult to follow:

1. stop new branch creation
2. read `research_spine.md`, `integrated_research_plan.md`, `claim_matrix.csv`, and the latest decision log
3. inventory stages and artifacts from the manifest and lineage table
4. mark orphaned or duplicate branches as deferred, merged, or killed
5. choose one current claim and one next gate
6. archive or quarantine outputs that cannot be traced
7. update assumptions and uncertainty before resuming execution

Do not attempt to recover direction by reading every raw output first. Reconstruct the control plane, then inspect only artifacts referenced by the next gate.

## Drift Warnings

Escalate to the user when:

- the primary goal has changed but the manifest still encodes the old decision
- a branch's output is being used outside its declared validity window
- downstream work continues after an upstream gate failed
- the project has multiple conflicting "final" results
- data or checkpoints cannot be traced to a source or license
- the requested depth has increased beyond the original evidence tier

Ask the user to reconfirm route, depth, goal, and acceptable partial result rather than silently rewriting the main line.
