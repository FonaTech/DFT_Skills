# AIMD And Finite-Temperature Atomistic Workflows

Use ab initio molecular dynamics when electronic-structure forces are needed during finite-temperature sampling. Design it as a statistical experiment, not as an animated relaxation.

## Contents

1. Experiment contract
2. Static prerequisites
3. Ensemble and integrator design
4. Sampling ladders
5. Enhanced sampling and rare events
6. Analysis and statistical sufficiency
7. Handoff to MLIP
8. Failure and stopping rules

## Experiment Contract

Record before launch:

- hypothesis and trajectory-level observable
- phase, composition, charge, spin, cell, constraints, and environment
- ensemble, target temperature and pressure, thermostat or barostat, and coupling constants
- integration time step and its convergence evidence
- equilibration length, production length, output cadence, restart cadence, and replica count
- electronic convergence, smearing, basis, k-point, dispersion, and spin policy inherited from static work
- analysis estimator, block size or autocorrelation treatment, uncertainty, and pass condition
- escalation path if the event is too rare for direct AIMD

## Static Prerequisites

Complete these gates first:

1. Relax a physically meaningful starting structure.
2. Converge electronic settings for forces, not only total energies.
3. Verify the chosen supercell permits the relevant disorder, diffusion, wavelength, or reconstruction.
4. Confirm the timestep resolves the fastest important motion with an energy-drift test.
5. Check that constraints and frozen layers do not suppress the target mechanism.
6. Establish reference states for comparisons across temperature, composition, phase, or surface coverage.

For metallic, magnetic, charged, or strongly correlated systems, monitor electronic-state changes during dynamics. A static setup that converges once may fail repeatedly on distorted frames.

## Ensemble And Integrator Design

| Goal | Typical starting ensemble | Required cautions |
|---|---|---|
| thermal stability at fixed cell | NVT | thermostat should not erase the target dynamics |
| energy conservation check | NVE after equilibration | quantify drift and remove center-of-mass motion appropriately |
| thermal expansion or pressure response | NPT or staged cell sampling | cell fluctuations, Pulay stress, barostat timescale, finite-size effects |
| surface or interface dynamics | NVT with fixed or constrained regions | vacuum, dipole, slab momentum, thermostat region |
| diffusion comparison | NVT or NPT, depending on physics | multiple origins, unwrap positions, finite-size and correlation effects |
| liquid structure | NVT/NPT melt-equilibrate-production ladder | density, equilibration, composition, and cell-size convergence |

Do not select thermostat and barostat parameters by habit. Compare them to the characteristic vibrational and structural relaxation times and verify that the measured observable is insensitive within the declared tolerance.

## Sampling Ladders

### Stability Screen

```text
static relax -> gentle heating -> target-temperature equilibration
-> replicated short production -> structural metrics -> quenched snapshots
```

Use to detect rapid reconstruction or obvious instability. Keep conclusions limited to the sampled cell and time window.

### Temperature Or Pressure Ladder

```text
shared reference -> independently equilibrated state points
-> production at every state -> distributions and hysteresis check
```

Avoid reusing a single continuously heated trajectory as independent equilibrium evidence. Use both heating and cooling or independent starts when hysteresis matters.

### Diffusion Or Transport

```text
equilibration -> long production or replicas -> unwrapped trajectories
-> mean-squared displacement and correlation analysis -> regime fit
```

Require a diffusive regime before fitting a diffusion coefficient. Report dimensionality, mobile species count, correlation window, finite-size limits, and confidence interval. Use Green-Kubo or collective formulations when single-particle Einstein relations do not match the requested transport coefficient.

### Liquid, Amorphous, Or Melt-Quench

```text
validated initial density -> melt -> liquid equilibration
-> controlled quench with documented rate -> anneal -> independent samples
```

One quenched cell is a realization, not a material ensemble. Compare structural factors, coordination, density, ring or motif statistics, and relevant experimental observables when available.

## Enhanced Sampling And Rare Events

Use umbrella sampling, metadynamics, adaptive biasing, constrained dynamics, replica exchange, or transition-path methods only after defining:

- the collective variable and why it resolves the slow mode
- bias parameters and convergence diagnostics
- reweighting or unbiased estimator
- orthogonal hidden barriers to test
- independent starts or recrossing checks
- a reference calculation or static path for validation

Do not infer a complete mechanism from a visually plausible collective variable. If alternative pathways are possible, include competing variables or seed separate path families.

## Analysis And Statistical Sufficiency

Separate equilibration from production. Analyze at least:

- temperature, pressure, conserved quantity, and total-energy drift as appropriate
- SCF iteration count and failed or low-quality force steps
- cell volume and shape when variable-cell dynamics is used
- claim-specific bonds, angles, coordination, order parameters, or species populations
- radial, angular, or structure factors when phase or liquid structure matters
- mean-squared displacement, velocity autocorrelation, or Green-Kubo integrands when transport matters
- replica-to-replica variation
- autocorrelation time, block uncertainty, and effective independent sample count

Use block averaging, bootstrap over independent blocks or replicas, or another estimator suited to correlated trajectories. Frame count is not independent sample count.

Use `scripts/analyze_atomistic_trajectory.py` for a first reproducible pass over ASE-readable AIMD or MLMD trajectories. It reports energy, kinetic-temperature, volume, MSD, selected pair distances, drift slopes, missing labels, and non-finite frames. Its MSD unwrapping assumes a fixed atom count and fully periodic cells with modest cell changes; use domain-specific transport analysis for variable-cell, reactive, constrained, collective, or charge-transport estimators.

## Representative Snapshot Policy

Select snapshots by a declared rule:

- uniform time blocks for unbiased state coverage
- clustering or farthest-point sampling for diverse environments
- extrema of a claim-specific order parameter
- event windows before, during, and after a transition
- uncertainty or disagreement for MLIP labeling

Recompute selected frames with consistent high-quality static settings when their energies, forces, stresses, or electronic structure support a mechanistic claim.

## Handoff To MLIP

When AIMD seeds MLIP training:

1. preserve trajectory and parent identifiers
2. remove failed or unconverged electronic steps
3. avoid splitting adjacent frames across train and test
4. add targeted off-equilibrium, strained, defect, interface, and reaction configurations required by deployment
5. label all selected frames with one consistent reference method or a documented delta-learning scheme
6. retain a hard challenge set that active learning cannot consume

## Failure And Stopping Rules

Stop or repair when:

- persistent SCF failures make forces unreliable
- energy drift exceeds the declared tolerance in the conservation test
- the thermostat or barostat drives unphysical oscillation
- atoms cross boundaries incorrectly because trajectories are wrapped or cells malformed
- an event is caused by an artificial constraint, small cell, excessive timestep, or abrupt initialization
- independent replicas disagree beyond the expected statistical uncertainty
- no effective independent samples are obtained for the requested estimator

Escalate to a validated MLIP when AIMD cannot reach the required scale. Escalate to free-energy or path methods when direct dynamics cannot sample the event. Narrow the claim when neither is feasible.
