# DFT, MLIP, And FEM Hierarchical Multiscale Workflow

## Engineering Intent

Use this case when DFT is needed for reference accuracy, MLIP-driven atomistic sampling is needed for scale, and FEM is needed for component or device response. This is the full hierarchical route; use it only when each layer changes the answer.

Read all four branch references: `references/aimd-workflows.md`, `references/mlip-workflows.md`, `references/fem-multiscale-coupling.md`, and `references/multiscale-validation.md`.

## Questions This Workflow Must Answer

- What information is lost and gained at every scale transition?
- Which atomistic states determine the continuum closure?
- Can the MLIP cover those states with a monitored safe domain?
- Which FEM states require adaptive feedback to DFT or MLIP active learning?
- Does combined uncertainty preserve the final decision margin?

## Minimum Inputs

- end-to-end claim, primary continuum observable, and evidence tier
- explicit stage DAG and handoff contracts
- DFT label protocol and MLIP deployment domain
- MLMD state grid, ensemble plan, and statistical estimator
- homogenization or constitutive fitting equation
- FEM equations, geometry, boundary conditions, and validation target
- compute and label budgets plus stopping rules

## Recommended Stage DAG

```text
S01 converged DFT references
S02 AIMD and targeted perturbation seed data
S03 MLIP baseline, active learning, and challenge validation
S04 production MLMD state grid
S05 statistical reduction and constitutive fit
S06 unit, tensor, and basis adapter
S07 FEM verification and coupled prediction
S08 DFT spot checks, experimental validation, and verdict
```

Do not force a linear chain when branches are independent. Use separate DFT property and MLIP-label branches that join only at a declared coupling stage.

## Cross-Scale Contracts

### DFT To MLIP

- consistent energies, forces, stresses, charge and spin conventions
- grouped splits and hard challenges
- configuration and method provenance
- explicit handling of multiple fidelity levels

### MLIP To MLMD

- frozen checkpoint and calculator
- state domain, uncertainty monitor, timestep, and abort rule
- DFT spot-check schedule

### MLMD To Constitutive Model

- converged ensemble and representative volume
- estimator, correlations, finite-size correction, and state interpolation
- fit uncertainty and held-out state points

### Constitutive Model To FEM

- units, tensor basis, sign, normalization, and validity range
- interpolation and phase-switch behavior
- conservation and round-trip tests

## Adaptive Feedback

Use feedback only when a gate triggers it:

- MLIP uncertainty or physical guardrail -> diverse DFT labels
- unconverged atomistic estimator -> larger cell, longer sampling, or more replicas
- poor constitutive fit -> new state points or better model form
- FEM sensitivity outside sampled domain -> targeted MLMD or DFT branch
- experiment mismatch -> diagnose parameter, model-form, boundary, and measurement error separately

## End-To-End Validation

- recover a DFT or MD limiting case from the reduced model
- verify MLIP errors on FEM-sensitive states rather than a generic average
- validate constitutive interpolation on held-out state points
- perform mesh, time, and parameter uncertainty propagation
- compare final output with an independent experiment or higher-fidelity benchmark
- test whether the decision changes across plausible model variants

## Frequent Failure Modes

- using every layer because it sounds comprehensive rather than because it is necessary
- passing mean values downstream while dropping state dependence and correlations
- validating the MLIP on bulk states while FEM failure is interface- or defect-controlled
- hiding empirical fit parameters in the homogenization step
- allowing downstream extrapolation to continue without upstream feedback

## Deliverables

- complete experiment manifest and stage DAG
- versioned DFT dataset, MLIP model card, and MLMD ensemble
- constitutive model with uncertainty and validity surface
- verified FEM model and end-to-end validation
- feedback ledger and compute or label budget
- claim verdict with layer-by-layer evidence and limitations
