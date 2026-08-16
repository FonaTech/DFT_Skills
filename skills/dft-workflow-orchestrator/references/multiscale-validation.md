# Multiscale Validation And Uncertainty

Use independent gates at every stage and propagate only artifacts that pass. A smooth end-to-end result cannot compensate for an invalid upstream model.

## Contents

1. Evidence ledger
2. Stage gates
3. Uncertainty budget
4. End-to-end tests
5. Decision and stopping rules

## Evidence Ledger

For each claim, maintain:

| Field | Required content |
|---|---|
| claim | falsifiable scientific or engineering statement |
| observable | measured quantity and estimator |
| stage | DFT, AIMD, MLIP, MD, homogenization, FEM, or experiment |
| reference | control, benchmark, or independent data |
| method | code, version, settings, checkpoint, seed, and artifact hash |
| uncertainty | numerical, statistical, model, mapping, and calibration components |
| validity | state, spatial, temporal, and parameter domain |
| verdict | supported, indirectly supported, contradicted, inconclusive, or not run |
| next action | highest-information follow-up and stop condition |

Do not collapse “not run” and “failed” into “inconclusive”.

## Stage Gates

### DFT Gate

Pass only when:

- structure and reference states are traceable
- energy, force, cell, k-point, and method-sensitive convergence meet declared tolerances
- pseudopotential or basis and functional choices are consistent across comparisons
- magnetic, charge, correlation, dispersion, and finite-size axes are addressed when relevant
- controls support the claim and no unresolved fatal warning remains

### AIMD Gate

Pass only when:

- starting electronic and structural setup passed the DFT gate
- timestep, thermostat or barostat, and conservation behavior are acceptable
- equilibration is separated from production
- replicas or state points are consistent within uncertainty
- effective sample count supports the estimator or the claim is explicitly qualitative
- event snapshots are independently refined when interpreted mechanistically

### MLIP Gate

Pass only when:

- deployment domain and prohibited domain are written
- grouped validation and hard challenge sets are held out
- energies, forces, stresses, structures, and downstream observables meet tolerances
- uncertainty or extrapolation detection is calibrated or conservatively bounded
- physical invariants and short production-like trajectories are stable
- checkpoint, package, license, and checksum are frozen

### Homogenization Or Fit Gate

Pass only when:

- the representative volume or state ensemble is converged
- estimator, weighting, and boundary conditions are documented
- fit residuals, identifiability, and held-out states are reported
- parameter correlations and uncertainty are retained
- fitted closures are not mislabeled as direct atomistic outputs

### FEM Gate

Pass only when:

- unit, tensor, and basis transformations are tested
- analytic or trusted benchmarks pass
- mesh, time, nonlinear, and domain convergence are demonstrated
- conservation and limiting cases hold
- the constitutive validity window contains the simulated state

### Coupled Gate

Pass only when:

- each handoff contract is satisfied
- end-to-end units, signs, and state variables are consistent
- uncertainty is propagated without double counting
- feedback and extrapolation behavior are tested
- an independent benchmark, experiment, or higher-fidelity spot check supports the final observable

## Uncertainty Budget

Classify uncertainty separately:

1. numerical: basis, mesh, timestep, SCF, optimizer, solver tolerance
2. statistical: finite trajectory, replicas, bootstrap, autocorrelation
3. model-form: functional, magnetic order, MLIP architecture, constitutive law, continuum assumption
4. mapping: averaging volume, tensor rotation, interpolation, reduced kinetics, boundary transfer
5. calibration: experimental noise, parameter fit, measurement bias

For a derived quantity, state the propagation method and correlations. A practical first pass is a sensitivity matrix or Monte Carlo over the full staged pipeline; use a more formal Bayesian or polynomial-chaos treatment when the decision warrants it.

## End-To-End Tests

Use at least one test from each applicable class:

- limiting case where the coupled model reduces to a known DFT, MD, or FEM result
- manufactured solution or analytic benchmark for the continuum solver
- round-trip unit and tensor conversion
- duplicate input with different file ordering to test invariance
- held-out state point or composition
- DFT spot check of MLMD-selected configurations
- conservation test across atomistic-to-continuum flux or energy transfer
- perturbation test to verify expected monotonicity or symmetry
- restart test for trajectories and coupled solver checkpoints

## Decision And Stopping Rules

Stop the chain when:

- the decision tolerance is met with margin and further work has low information value
- a fatal upstream failure cannot be repaired within scope
- uncertainty dominates the decision and a higher-fidelity or new-data request is required
- the model is outside its validity domain and no safe fallback exists

Choose follow-ups by expected information value:

- method branch when model-form uncertainty dominates
- larger cell, longer trajectory, or more replicas when statistical uncertainty dominates
- active-learning labels when MLIP extrapolation dominates
- new state-grid points when interpolation dominates
- mesh or solver refinement when numerical uncertainty dominates
- experiment calibration when continuum closure is non-identifiable

## Report Format

Every final report should include:

- a one-paragraph verdict with evidence tier
- a stage-by-stage gate table
- uncertainty components and dominant driver
- validity and prohibited extrapolation domains
- artifact identifiers and reproducibility metadata
- failed, skipped, and planned work
- the next action and its expected information value
