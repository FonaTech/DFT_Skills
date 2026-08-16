# Pretrained MLIP Surrogate Screening

## Engineering Intent

Use this case to call a pretrained machine-learning interatomic potential for rapid energy, force, relaxation, or ranking experiments before targeted DFT confirmation. The goal is a bounded surrogate screen, not automatic replacement of first-principles evidence.

Read `references/mlip-workflows.md` and `references/engine-capability-matrix.md` before selecting a checkpoint or calculator.

## Questions This Workflow Must Answer

- What decision will the surrogate ranking or relaxation change?
- Does the checkpoint cover the target elements, bonding, phase, charge, spin, pressure, strain, and surface or defect environments?
- Which target-domain DFT configurations will validate it?
- What ranking error, force error, instability, or extrapolation signal stops the screen?

## Minimum Inputs

- candidate structures with provenance and stable IDs
- exact pretrained checkpoint, package version, checksum, license, device, and precision
- declared deployment domain and prohibited domain
- target-method DFT benchmark subset spanning ordinary and difficult candidates
- requested output and decision threshold

## Recommended Experiment Ladder

1. audit the local environment and model availability
2. inspect the official API for the installed package version
3. run one known-structure energy and force smoke test
4. benchmark unrelaxed target structures against consistent DFT labels
5. compare short surrogate relaxations to DFT-relaxed references
6. measure ranking quality and threshold sensitivity
7. screen candidates with runtime geometry and uncertainty guards
8. recompute finalists, boundary cases, and surprising outliers with DFT

## Validation Packet

- energy error per atom and relative-energy error within each comparison group
- force component, magnitude, and high-force-tail error
- stress error when cell relaxation or mechanics matters
- relaxation success, geometry deviation, and structure-order changes
- rank correlation, top-k recall, and false-negative rate near the selection threshold
- disaggregated errors for phases, compositions, defects, surfaces, and strained states
- throughput and memory on the actual deployment hardware

## Runtime Guardrails

- reject unsupported elements or malformed periodic cells before inference
- detect close contacts, extreme forces, implausible density, and failed optimizer steps
- monitor a calibrated uncertainty or conservative distance-to-training proxy when available
- quarantine rather than silently retain out-of-domain predictions
- keep raw input and output ordering stable through the screening table
- pin the checkpoint rather than using a moving `latest` alias

## Frequent Failure Modes

- assuming broad pretraining means target-domain accuracy
- benchmarking only equilibrium bulk structures before screening defects or surfaces
- selecting by global RMSE instead of ranking and decision performance
- allowing surrogate relaxation to change topology without a warning
- downloading an unnamed checkpoint and losing provenance
- reporting surrogate energies as DFT results

## Deliverables

- model card and exact invocation environment
- target-domain benchmark and hard challenge table
- complete candidate ranking with validity and warning columns
- DFT confirmation packet for finalists and disagreements
- safe-domain and prohibited-use statement
- verdict that distinguishes surrogate evidence from DFT evidence
