---
name: dft-workflow-orchestrator
description: >
  Design, scaffold, execute, monitor, validate, and report reproducible atomistic-to-continuum materials simulations. Use for DFT or first-principles work with VASP, Quantum ESPRESSO, CP2K, GPAW, or related engines; ab initio molecular dynamics and enhanced sampling; machine-learning interatomic potentials or ML force fields including pretrained inference, fine-tuning, active learning, and production MD; finite-element or multiphysics studies with COMSOL, FEniCSx, MOOSE, Abaqus, or CalculiX; and coupled DFT-AIMD-MLIP-MD-FEM experiments. Also use for detailed integrated research plans, structures, adsorption, defects, NEB, electronic structure, optics, phonons, transport, mechanics, thermodynamics, interfaces, catalysis, uncertainty, provenance, literature-to-workflow planning, 第一性原理, 密度泛函, 从头算分子动力学, 机器学习势, 分子动力学, 有限元, 多物理场, 多尺度材料模拟, and 研究主线管理.
---

# Multiscale Materials Workflow Orchestrator

Turn a scientific question into a reproducible, scale-aware simulation project. Preserve the existing VASP execution path while selecting DFT, AIMD, MLIP, MD, FEM, or a validated combination according to the observable and scales actually required.

## Operating Rules

1. Start from the scientific decision and decisive observable, not from a favorite code.
2. Classify whether the claim is single-scale or genuinely cross-scale before adding a second method. Stop at the smallest scale that resolves the decision.
3. Preflight data, executables, Python packages, accelerators, licenses, and compute limits before promising execution.
4. Separate evidence layers: electronic-structure reference, atomistic sampling, surrogate prediction, homogenized constitutive law, continuum response, and experimental calibration.
5. Give every stage explicit inputs, outputs, controls, validation gates, units, provenance, and a validity domain.
6. Use sequential coupling by default. Use concurrent or adaptive coupling only when a supported implementation and a justified interface algorithm exist.
7. Treat pretrained MLIPs as hypotheses until validated on the target chemistry, phase, state variables, and observables.
8. Propagate uncertainty across handoffs; do not report only the final solver residual.
9. Never fabricate structures, pseudopotentials, checkpoints, licenses, API keys, convergence, model accuracy, or completed calculations.
10. Distinguish planning, scaffolding, dry-run, submitted, running, converged, validated, and interpreted states.
11. Keep generated projects and calculation outputs outside the skill directory.

## Intake

Resolve or explicitly mark assumptions for:

- scientific claim, decision, and primary observable
- composition, phase, defects, interfaces, charge, spin, environment, and operating window
- spatial and temporal scales that must be resolved
- required accuracy, uncertainty tolerance, budget, deadline, and available hardware
- available structures, trajectories, labels, checkpoints, experimental data, and solver licenses
- boundary conditions, loading paths, ensembles, rare events, and failure modes
- expected deliverable: plan, inputs, executable run, analysis, model, handoff table, or coupled prediction
- scale decision: smallest sufficient scale, scales deliberately deferred, and the observation that would force escalation

Ask only for missing choices that would materially change the experiment. For reversible details, proceed with labeled assumptions and expose them in `workflow/assumptions.md`.

### Complex-Task Design Brief

Before committing an expensive or multi-branch workflow, ask a short design brief when more than one scale or method is plausible, the requested depth is unclear, the output drives a consequential decision, or the route requires substantial compute, licensing, data generation, or model training. Confirm:

1. preferred technical route and acceptable alternatives (DFT-only, AIMD, MLIP/MLMD, FEM, or staged coupling)
2. target depth: design, smoke test, pilot, production, or decision-grade
3. primary goal and expected deliverables
4. accuracy, uncertainty, reproducibility, and independent-validation standard
5. available structures, labels, checkpoints, solvers, hardware, licenses, time, and budget
6. forbidden assumptions and what would count as a useful partial result

Keep questions concise and decision-oriented. If a noncritical detail is unanswered, choose a reversible default and record it. Do not block a routine single-scale scaffold on this brief.

## Mandatory Integrated Planning Artifact

Read [integrated-research-plan-contract.md](references/integrated-research-plan-contract.md). For any research-design, route-selection, methodology, roadmap, complex, branching, or consequential request, create or refresh `workflow/integrated_research_plan.md` before generating launch-ready inputs or starting work. This is a mandatory deliverable, not an optional explanation in chat.

The plan must be a detailed, coherent narrative rather than a list of generated files. It must contain the scientific decision, boundary and non-goals, model and scale rationale, assumptions, staged roadmap, each stage's method and derivation logic, inputs, outputs, controls, acceptance and stop gates, resource-aware sequence, negative conclusions, escalation triggers, and definition of done. Use stable phase or stage labels such as `P0`, `N0`, `S01`, or `A` through `G`.

Generate the artifact for DFT-only planning as well as coupled work. A detailed document does not authorize an unnecessary second scale: retain the smallest sufficient route and state the observable that would justify escalation. A narrow execution-only request may reuse a current plan, but must not proceed from a stale or conflicting plan.

Before calling a task complete, synchronize the plan's `Control Snapshot` with `workflow/research_spine.md`, `experiment_manifest.json`, the claim matrix, branch register, decision log, and next-action queue. Do not replace the integrated plan with placeholders after the user has provided enough information; unresolved facts must be explicit assumptions with a risk and resolution path.

## Phase 0: Preflight

Run the cross-stack probe:

```bash
python3 scripts/preflight_multiscale_env.py --workspace ../your-project --pretty
```

For a VASP-only request, retain the focused probe:

```bash
python3 scripts/preflight_dft_env.py --workspace ../your-project --pretty
```

Read [engine-capability-matrix.md](references/engine-capability-matrix.md) before selecting an engine or MLIP family. A detected package is not proof that a model, license, pseudopotential set, GPU build, or compatible checkpoint is available.

Downgrade honestly:

- no executable or license: produce a validated plan and scaffold
- no reference data or compatible MLIP: design data acquisition and validation, not production MLMD
- no FEM backend: produce a unit-checked handoff and solver-neutral weak-form specification
- inadequate compute: reduce scope without silently weakening the scientific claim

## Phase 1: Ground The Scientific Model

Read [literature-to-dft-outline.md](references/literature-to-dft-outline.md), [knowledge-grounding-protocol.md](references/knowledge-grounding-protocol.md), and [theory-model-selection.md](references/theory-model-selection.md).

Use sources in this order:

1. user-provided and local project files
2. local retrieval or RAG when available
3. authoritative online literature and official software documentation when available
4. model knowledge, clearly marked as an unverified prior

Stop collecting when the evidence is sufficient to choose the model ladder, controls, and pass criteria. Record contradictions and negative evidence rather than forcing consensus.

## Phase 2: Route The Experiment

Read [research-mode-router.md](references/research-mode-router.md). Then load only the branch references required by the route:

| Need | Primary route | Read |
|---|---|---|
| ground-state structure, energy, charge, spectra, barriers | DFT | [dft-task-router.md](references/dft-task-router.md), [vasp-methodology.md](references/vasp-methodology.md) |
| finite-temperature atomistic behavior at first-principles accuracy | AIMD | [aimd-workflows.md](references/aimd-workflows.md) |
| larger or longer atomistic sampling | MLIP or classical MD | [mlip-workflows.md](references/mlip-workflows.md) |
| device, component, field, fracture, transport, or reactor response | FEM or multiphysics | [fem-multiscale-coupling.md](references/fem-multiscale-coupling.md) |
| two or more linked scales | staged multiscale DAG | all relevant branch references plus [multiscale-validation.md](references/multiscale-validation.md) |

Open [case-studies/INDEX.md](case-studies/INDEX.md) and select the smallest case set that covers the decisive observable. Do not combine branches merely because they can produce additional plots.

### Single-Scale Stop Rule

Write a scale decision before opening a second branch:

- **electronic or local atomistic claim:** stop after the DFT gate when the requested observable is a ground-state or local response quantity
- **finite-temperature atomistic claim:** add AIMD only when static DFT cannot test the relevant fluctuation or rearrangement
- **large-cell or long-time atomistic claim:** add MLIP/MLMD only when validated sampling is the limiting factor
- **device or field claim:** add FEM only when geometry, boundary conditions, spatial fields, or component-scale response change the decision
- **cross-scale claim:** add a handoff only when an upstream state-dependent output is an input to a downstream equation and each layer has an independent acceptance test

Record rejected or deferred scales in `workflow/research_contract.md` and `experiment_manifest.json`. A workflow that ends at DFT, AIMD, MLIP, or FEM is complete when its own gate answers the claim.

## Phase 3: Create The Planning Authority

For routine DFT-only projects, use the DFT scaffold. It now creates the integrated plan by default; fill its stage narrative before materializing production jobs:

```bash
python3 scripts/scaffold_dft_project.py \
  --project-root ../your-project \
  --system-name "Material System" \
  --claim "Scientific claim" \
  --task bulk-relax \
  --task dos
```

For a complex or branching DFT-only project, use the full research control plane with `--stage dft` only. This does not create a multiscale chain or any handoff; it adds the integrated plan, design brief, research spine, branch register, lineage, and next-action queue.

For AIMD, MLIP, FEM, coupled work, or complex single-scale work, create the full packet. Its integrated plan is a required manifest-tracked artifact:

```bash
python3 scripts/scaffold_multiscale_project.py \
  --project-root ../your-project \
  --system-name "Material System" \
  --claim "Scientific claim" \
  --stage dft \
  --stage mlip \
  --stage md \
  --stage fem
```

Read [experiment-manifest-contract.md](references/experiment-manifest-contract.md). The project-level authority is:

- `workflow/integrated_research_plan.md`
- `workflow/research_contract.md`
- `workflow/decision_brief.md`
- `workflow/research_spine.md`
- `workflow/branch_register.csv`
- `workflow/data_lineage.csv`
- `workflow/next_action_queue.csv`
- `workflow/decision_log.md`
- `workflow/assumptions.md`
- `workflow/knowledge_sources.md`
- `workflow/claim_matrix.csv`
- `workflow/experiment_manifest.json`
- `workflow/handoff_register.csv`
- `workflow/validation_plan.md`
- `workflow/risk_register.md`

Validate before materializing expensive work:

```bash
python3 scripts/validate_experiment_manifest.py \
  --manifest ../your-project/workflow/experiment_manifest.json \
  --handoff-register ../your-project/workflow/handoff_register.csv
```

Use `--strict` only after placeholders are resolved and the workflow is launch-ready.

The validator enforces the integrated-plan structure for new schema `1.1` projects. Treat a missing plan, missing stage, or plan/spine disagreement as a planning defect before launch. A plan in `draft` is acceptable only for design work; change it to `current` once the route and gates are reconciled.

Keep the research spine current while work branches: after each run, update the current gate, claim verdict, branch status, and one prioritized next action. Refresh it with:

```bash
python3 scripts/maintain_research_spine.py \
  --project-root ../your-project \
  --pretty
```

Do not launch a branch that has no claim, purpose, kill criterion, or expected information gain. Close, merge, or explicitly defer branches before opening more.

## Phase 4: Acquire Structures And Data

Use this priority:

1. user-provided, curated structures and datasets
2. versioned institutional or public databases with stable identifiers
3. documented reconstruction from literature
4. generated configurations with a recorded algorithm, seed, parent, and constraints

For structure presets:

```bash
python3 scripts/fetch_structures.py --list-presets
python3 scripts/fetch_structures.py \
  --project-root ../your-project \
  --preset bulk-property-bootstrap
```

Write provenance for structures, labels, trajectories, train/validation/test splits, pretrained weights, descriptor statistics, meshes, constitutive fits, and experimental calibration data. Prevent leakage by grouping related frames, trajectories, compositions, or parent structures before splitting.

## DFT Lane

Retain the established VASP path and quality gates:

1. justify the functional, pseudopotentials, spin, charge, `+U`, dispersion, relativistic treatment, cell, and reference states
2. converge basis, k-points, cell or slab dimensions, force criteria, and method-sensitive axes
3. acquire and normalize structures with provenance
4. render VASP jobs only after method choices are documented
5. require real `INCAR`, `KPOINTS`, `POSCAR`, and licensed local `POTCAR` before launch
6. run through `run_one_vasp_job.sh` or `run_vasp_queue.sh`
7. monitor through `monitor_vasp_runs.py`
8. summarize through `summarize_vasp_runs.py`
9. map every result back to a claim, control, sensitivity axis, and method limit

Example materialization:

```bash
python3 scripts/render_vasp_job.py \
  --structure <structure-file> \
  --job-dir <job-dir> \
  --preset correlated-relax \
  --system "Example system" \
  --species-order Sm Ni O \
  --u-element Ni \
  --u-value 2.0 \
  --afm-element Ni
```

Do not translate settings mechanically between VASP, Quantum ESPRESSO, CP2K, GPAW, CASTEP, ABINIT, or other engines. Match physical approximations, pseudopotential or basis families, reference energies, smearing, stress conventions, and convergence criteria.

## AIMD Lane

Follow [aimd-workflows.md](references/aimd-workflows.md):

1. converge the static electronic setup and starting structure
2. justify the ensemble, thermostat or barostat, time step, cell size, temperature or pressure ladder, equilibration, production length, and replicas
3. monitor conserved quantities, drift, SCF failures, cell pathologies, and the claim-specific structural observables
4. separate equilibration from production and estimate autocorrelation or effective sample size
5. use enhanced sampling only with a declared collective variable, reweighting plan, and independent validation
6. quench or recompute representative and event snapshots when mechanistic interpretation matters

Generate reproducible trajectory diagnostics instead of relying on visual inspection:

```bash
python3 scripts/analyze_atomistic_trajectory.py \
  --input data/trajectories/production.extxyz \
  --timestep-fs 1.0 \
  --equilibration-frames 1000 \
  --distance-pair 0,7 \
  --output analysis/trajectory_report.json \
  --csv-output analysis/trajectory_timeseries.csv \
  --pretty
```

Short AIMD trajectories can falsify obvious stability claims or reveal candidate events. They do not establish long-time rates, equilibrium phase boundaries, or converged transport without adequate sampling.

## MLIP And MLMD Lane

Follow [mlip-workflows.md](references/mlip-workflows.md):

1. define the deployment domain before selecting a model
2. inventory elements, charge and spin states, phases, surfaces, defects, temperatures, pressures, strains, and reaction classes
3. prefer a validated pretrained model for in-domain screening; fine-tune or train when target-domain error is unacceptable
4. record model family, package and version, checkpoint identifier and checksum, license, precision, device, cutoffs, and calculator settings
5. validate energies, forces, stresses, geometries, phonons or elastic response, and use-case observables on grouped holdouts and hard challenge sets
6. compare against at least one simple baseline and targeted DFT spot checks
7. use committee disagreement, calibrated uncertainty, descriptor distance, or explicit challenge detection to trigger new labels
8. freeze a model only after active-learning convergence and rerun final holdouts once
9. monitor extrapolation and physical invariants during production MD; stop rather than integrate through out-of-domain states

Use the installed package's official API for the exact version. Prefer a supported ASE or LAMMPS calculator interface when available. Never invent checkpoint names or silently download large weights.

For a trusted ASE-compatible calculator, run bounded proxy inference or relaxation through the generic runner after building a version-checked factory or project adapter:

```bash
python3 scripts/run_ase_surrogate.py \
  --input structures.extxyz \
  --output analysis/surrogate.extxyz \
  --factory package.module:CalculatorClass \
  --config workflow/calculator_config.json \
  --mode single-point \
  --allow-code-execution
```

Start with one frame. The runner records input, output, adapter, and config hashes but does not certify the model domain or silently manage model licensing.

## FEM And Multiphysics Lane

Follow [fem-multiscale-coupling.md](references/fem-multiscale-coupling.md):

1. state governing equations, geometry, dimensionality, initial and boundary conditions, sources, constitutive laws, and coupling terms
2. classify parameters as direct atomistic outputs, statistically homogenized values, fitted closures, experimental calibrations, or assumptions
3. record units, tensor rank, basis, symmetry, sign convention, normalization, validity window, and uncertainty for every handoff
4. verify tensor rotations and energy or flux consistency before import
5. perform mesh, time-step, domain-size, nonlinear-solver, and stabilization studies
6. validate the uncoupled FEM model before enabling multiphysics feedback
7. distinguish numerical convergence from physical validation

Support COMSOL, FEniCSx, MOOSE, Abaqus, CalculiX, or a solver-neutral weak form. Generate engine-specific files only when the local version and interface are known.

## Coupled Lane

Represent the workflow as a directed acyclic graph of stages and handoffs. A common hierarchy is:

```text
DFT references -> AIMD or configuration generation -> MLIP validation
-> MLIP-MD sampling -> statistical reduction or homogenization
-> FEM constitutive model -> device-scale prediction
```

At every arrow, define:

- producer artifact and consumer requirement
- mapping equation or transformation code
- units, tensor basis, averaging volume, and state variables
- interpolation and extrapolation policy
- uncertainty and correlation treatment
- acceptance test, rejection behavior, and feedback destination

Use DFT spot checks or new labels when MLMD leaves its validated domain. Refit continuum closures when atomistic sampling changes their state dependence. Do not hide empirical calibration inside an apparently first-principles chain.

## Validation And Verdict

Read [multiscale-validation.md](references/multiscale-validation.md). Require independent gates:

- DFT: numerical convergence, reference-state consistency, and method sensitivity
- AIMD: equilibration, drift, replica consistency, finite-size and sampling checks
- MLIP: grouped holdouts, hard challenges, physical invariants, stability, and domain detection
- FEM: verification, mesh/time convergence, conservation, benchmark recovery, and parameter sensitivity
- coupled: unit and tensor checks, end-to-end conservation, uncertainty propagation, and feedback-loop tests

Report:

- what ran and what was only planned
- exact software, versions, inputs, seeds, hardware-relevant precision, and model or data identifiers
- observables with controls, uncertainty, and validity domains
- failed or inconclusive branches
- direct support, indirect support, contradiction, and unresolved claims
- next experiment chosen by information value, not by convenience

## Resource Map

Load only what the task needs:

- core routing: [research-mode-router.md](references/research-mode-router.md)
- DFT theory and execution: [dft-task-router.md](references/dft-task-router.md), [theory-model-selection.md](references/theory-model-selection.md), [vasp-methodology.md](references/vasp-methodology.md)
- AIMD and enhanced sampling: [aimd-workflows.md](references/aimd-workflows.md)
- MLIP selection, training, inference, active learning, and MLMD: [mlip-workflows.md](references/mlip-workflows.md)
- FEM and atomistic-continuum coupling: [fem-multiscale-coupling.md](references/fem-multiscale-coupling.md)
- validation and uncertainty: [multiscale-validation.md](references/multiscale-validation.md)
- detailed planning artifact and stage narrative: [integrated-research-plan-contract.md](references/integrated-research-plan-contract.md)
- long-task orientation, branch governance, and lineage: [research-spine-and-state.md](references/research-spine-and-state.md)
- engine and ecosystem selection: [engine-capability-matrix.md](references/engine-capability-matrix.md)
- project schema: [experiment-manifest-contract.md](references/experiment-manifest-contract.md), [project-layout.md](references/project-layout.md)
- background VASP runs: [live-run-monitoring.md](references/live-run-monitoring.md)
- platform behavior: [platform-interop.md](references/platform-interop.md)
- applied study templates: [case-studies/INDEX.md](case-studies/INDEX.md)
- structure templates: [presets/INDEX.md](presets/INDEX.md)

## Hard Stops

- Do not claim a calculation ran when only inputs were generated.
- Do not use an MLIP outside its validated domain because an inference call succeeded.
- Do not infer rates from isolated barriers without a kinetic model and prefactor treatment.
- Do not infer continuum constants from one atomistic state without a defined homogenization and validity window.
- Do not compare energies, forces, stresses, tensors, or trajectories produced with incompatible conventions without reconciliation.
- Do not continue a coupled chain after an upstream validation gate fails.
- Do not add AIMD, MLIP, MD, homogenization, or FEM merely to make a project look comprehensive; name the scale-specific bottleneck first.
- Do not substitute a collection of templates, a manifest, or a chat summary for `workflow/integrated_research_plan.md` when the planning-artifact contract applies.
