# MLIP Selection, Validation, Active Learning, And MLMD

Treat a machine-learning interatomic potential as a bounded surrogate for a declared atomistic deployment domain. A successful calculator call is only a smoke test.

## Contents

1. Choose the operating mode
2. Define the deployment domain
3. Select a model family
4. Build and split reference data
5. Validate a pretrained model
6. Train or fine-tune
7. Run active learning
8. Gate production MLMD
9. Monitor and report

## Choose The Operating Mode

| Mode | Use when | Minimum gate |
|---|---|---|
| pretrained inference | target appears close to the checkpoint domain | target-domain DFT benchmark and stability checks |
| pretrained relaxation or screening | ranking many candidates | rank correlation, top-candidate recall, DFT confirmation |
| fine-tuning | broad representations exist but target error is too high | leakage-safe split and frozen base comparison |
| training from scratch | domain is specialized and enough labels exist | baseline comparison, learning curve, challenge set |
| delta learning | a lower-cost physical baseline is available | baseline consistency and correction transferability |
| committee or ensemble | uncertainty proxy is required | calibration against observed target-domain errors |
| active learning | deployment exploration can be iteratively labeled | acquisition rule, budget, convergence and immutable test set |
| production MLMD | validation passes for the exact state window | runtime domain monitor and abort policy |

## Define The Deployment Domain

Write a machine-readable domain statement covering:

- elements, compositions, charge states, spin assumptions, phases, and bonding classes
- bulk, surface, interface, defect, molecule, liquid, or amorphous environments
- temperature, pressure, density, strain, field, and reaction windows
- cell sizes and boundary conditions
- required outputs: energy, force, stress, dipole, charge, or higher response
- production tasks: relaxation, NPT MD, fracture, diffusion, free energy, phonons, thermal transport, or screening
- unacceptable failure modes and the runtime stop condition

Use the deployment domain to construct the dataset and challenges. Do not infer the domain from whatever data happens to be available.

## Select A Model Family

Evaluate candidates on:

- supported elements and chemical or charge representation
- locality cutoff and whether long-range electrostatics or dispersion is represented
- rotational, translational, permutation, parity, and periodic invariances or equivariances
- energy, force, stress, and optional property heads
- memory, precision, GPU or CPU, distributed-training, and MD throughput requirements
- integration path for ASE, LAMMPS, i-PI, or the selected driver
- checkpoint provenance, training-domain disclosure, version, checksum, and license
- fine-tuning support and reproducibility of the installed release

Read [engine-capability-matrix.md](engine-capability-matrix.md) for ecosystem families. Confirm exact APIs from official documentation for the installed version.

## Reference Data Contract

For every configuration, preserve:

- stable configuration ID, parent ID, trajectory ID, and frame index
- species, positions, cell, periodicity, constraints, charge, and spin state
- total energy and energy convention
- forces with units and sign convention
- stress or virial with rank, ordering, units, sign, and extensive or intensive convention
- DFT engine, version, functional, pseudopotentials or basis, cutoffs, k-points, smearing, spin, `+U`, and convergence status
- generation method, state variables, and selection reason
- data-license and source provenance

Reject or quarantine inconsistent labels. If multiple fidelity levels are intentional, encode fidelity explicitly and use a documented multi-fidelity or delta-learning objective.

## Split Without Leakage

Group before splitting by the correlation source that matters:

- adjacent frames from one trajectory
- distortions from one parent structure
- symmetry-equivalent configurations
- same composition, phase, defect family, surface termination, or reaction path
- active-learning batch

Use three distinct evaluation roles:

1. validation set for model selection and early stopping
2. immutable in-domain test set for final error estimation
3. hard challenge set for deployment edges and failure discovery

Random frame splits are rarely sufficient for MD-derived data.

## Validate A Pretrained Model

Before any production use:

1. Load only a named, versioned, licensed checkpoint and record its checksum.
2. Run a minimal energy-force smoke test on a known configuration.
3. Compare against target-method DFT on representative equilibrium and off-equilibrium structures.
4. Include the difficult environments relevant to deployment: strained cells, defects, surfaces, liquids, transition regions, or close contacts.
5. Test structural relaxations and short MD for physical stability.
6. Evaluate the actual downstream observable, not only aggregate component errors.
7. Compare to a simple baseline and the decision tolerance.

For screening, measure ranking and decision performance: rank correlation, top-k recall, false-negative rate near the selection threshold, and DFT confirmation of finalists.

## Metrics

Report disaggregated metrics by chemistry and state:

- energy error per atom and relative-energy error within relevant groups
- force component and force-magnitude errors, including high-force tails
- stress or virial component errors
- calibration of ensemble disagreement or another uncertainty proxy
- geometry, equation of state, elastic, phonon, defect, barrier, or adsorption errors as required
- MD stability, distribution shift, and conservation behavior
- speed and memory on the deployment hardware

A low global RMSE can hide a failed rare environment. Show error distributions and worst relevant cases.

## Train Or Fine-Tune

Record:

- code, version, commit if relevant, environment lock, device, and precision
- data manifest and immutable split hashes
- architecture, cutoff, radial or angular basis, loss terms, weights, optimizer, schedule, batch construction, seed, and stopping rule
- energy referencing and per-species offsets
- normalization and stress or virial convention
- checkpoint selection rule and full learning curves

Train at least one simple or frozen-pretrained baseline. Use learning curves to distinguish data shortage from model or optimization limitations. Do not tune on the immutable test or challenge set.

## Active Learning Loop

Use a closed loop:

```text
seed labels -> fit committee or uncertainty model -> explore deployment states
-> detect risk -> diversify candidates -> DFT label -> quality control
-> append versioned batch -> refit -> revalidate -> convergence decision
```

Candidate acquisition may combine:

- committee disagreement or calibrated uncertainty
- descriptor or embedding distance from training data
- physical guardrails such as minimum distance, energy, force, density, or coordination
- diversity selection to avoid redundant labels
- task-specific value, such as proximity to a transition or failure boundary

Never label every high-uncertainty frame blindly. First remove integration artifacts, cluster candidates, cap selection per trajectory or state, and preserve chemical diversity.

Stop active learning only when all are satisfied:

- target-domain acquisition rate has plateaued below a declared threshold
- no new failure class appears in independent exploration
- relevant holdout and challenge metrics meet decision tolerances
- short production-like MD remains stable across replicas and state points
- the remaining uncertainty no longer changes the downstream decision

Freeze the final model, then evaluate the untouched test and challenge sets exactly once.

## Production MLMD Gate

Record and enforce:

- frozen checkpoint hash, calculator settings, precision, device, and neighbor-list behavior
- ensemble, timestep, thermostat or barostat, state ladder, replicas, and seeds
- energy, force, stress, minimum-distance, density, temperature, and uncertainty monitors
- checkpoint and restart cadence
- abort thresholds and quarantine policy for suspicious frames
- DFT spot-check schedule, especially at state-space boundaries

Do not integrate through severe extrapolation. Stop, select representative frames, label with DFT, retrain, and repeat validation.

## Physical Validation For MLMD

Choose checks tied to use:

- energy conservation in NVE and thermostat behavior in NVT
- equation of state and elastic stability
- phonons or vibrational density of states
- radial and angular distributions and structure factor
- phase stability and transition hysteresis
- diffusion, viscosity, conductivity, or thermal-transport estimator convergence
- defect, surface, interface, fracture, or reaction challenge trajectories

Compare distributions and derived observables with DFT, experiment, or a trusted baseline within an explicit validity window.

## Model Invocation Policy

- Inspect the installed package and official docs before constructing the calculator.
- Prefer the package's supported ASE or LAMMPS adapter.
- Pin checkpoint and package versions; never use an ambiguous alias such as `latest` in a reproducible run.
- Do not silently fetch large or restricted weights. State download size, source, license, and cache location first.
- Start with one structure and one force call, then a short constrained relaxation, then short MD.
- Preserve raw calculator output and model metadata with the trajectory.

The bundled `scripts/run_ase_surrogate.py` provides a stable execution shell for single-point inference and bounded relaxation. Use either:

- `--factory MODULE:CALLABLE` when the installed package exposes a calculator constructor whose keyword arguments fit in JSON
- `--adapter trusted_adapter.py` when version-specific setup is more complex; define `build_calculator(config)` and optionally `model_metadata(config)`

Pass `--allow-code-execution` only for a trusted installed package or reviewed local adapter. Keep credentials out of the config. Record checkpoint path, version, checksum, license, precision, and deployment domain in the adapter's model metadata or project model card. The runner writes `extxyz` labels and a metadata sidecar; it does not replace target-domain validation.

## Deliverables

- deployment-domain statement
- dataset manifest with grouped splits and provenance
- model card with checkpoint hash and license
- in-domain and challenge validation report
- active-learning ledger when used
- production MLMD protocol and runtime stop rules
- safe-domain and prohibited-use statement
