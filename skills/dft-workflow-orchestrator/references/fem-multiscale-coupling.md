# DFT, MLIP, And FEM Multiscale Coupling

Use this reference when atomistic calculations supply parameters, closures, source terms, or local models to a finite-element or multiphysics calculation. The central artifact is a traceable constitutive contract, not a table of unqualified numbers.

## Contents

1. Define the continuum problem
2. Classify the atomistic input
3. Map state and scale
4. Extract and homogenize properties
5. Implement and verify the FEM model
6. Sequential and concurrent coupling
7. Feedback and uncertainty
8. Handoff checklist

## Define The Continuum Problem

Before atomistic calculations, record:

- domains, geometry, dimensionality, coordinate systems, and representative volume
- unknown fields and governing strong or weak forms
- initial and boundary conditions, loading path, sources, sinks, interfaces, and contact laws
- constitutive variables and their state dependence on temperature, composition, phase, damage, field, strain, or history
- coupling terms, conservation laws, and required outputs
- mesh, time integration, nonlinear solver, stabilization, tolerances, and benchmark cases
- parameter sensitivity and the uncertainty the downstream decision can tolerate

If the continuum model is not specified, produce a solver-neutral requirement sheet before computing DFT properties.

## Classify The Atomistic Input

Label every handoff as one of:

| Class | Examples | Extra work required |
|---|---|---|
| direct | relaxed lattice, dielectric tensor, elastic tensor | unit, basis, phase, and method verification |
| state-grid | property versus temperature, composition, strain, field, defect fraction | sampling, interpolation, uncertainty and phase boundaries |
| homogenized | effective modulus, conductivity, diffusivity, permeability | representative volume, ensemble, weighting, convergence |
| fitted closure | reaction rate, damage law, plasticity parameter, phase-field coefficient | fitting objective, identifiability, calibration and held-out validation |
| empirical-calibrated | atomistic prior adjusted with experiment | explicit likelihood or fitting rule and independent test |
| local surrogate | MLIP or reduced model queried inside a larger solver | interface stability, energy consistency, extrapolation detection |

Do not call fitted or calibrated quantities direct DFT outputs.

## Map State And Scale

Create a state map for every parameter:

```text
continuum state -> atomistic state variables -> sampling protocol
-> estimator or constitutive fit -> interpolation or averaging
-> FEM coefficient and validity window
```

Record:

- temperature, pressure, composition, phase, defect or dopant concentration
- strain, stress, electric, magnetic, chemical, or reaction fields
- orientation, texture, grain or interface assumptions
- atomistic cell size and time window
- averaging volume and temporal window
- interpolation, extrapolation, and phase-switch policy

When the continuum grid crosses a phase boundary or a model's safe domain, switch models or stop. Do not smooth through a discontinuity without physical justification.

## Property Extraction Patterns

### Elasticity And Mechanics

- compute a converged stress-strain or energy-strain response with symmetry-appropriate perturbations
- use multiple strain amplitudes and verify linearity range
- rotate the tensor from crystal basis to continuum basis explicitly
- distinguish single-crystal, polycrystal, porous, defected, and effective properties
- propagate fitting and orientation uncertainty

### Dielectric, Piezoelectric, And Electrochemical Response

- define electronic versus ionic, clamped versus relaxed, static versus optical response
- maintain polarization branch and sign conventions
- include field, charge, and boundary-condition assumptions
- distinguish intrinsic tensors from effective porous or composite values

### Thermal Transport

- identify whether the FEM needs conductivity, heat capacity, source, or interface resistance
- obtain state-dependent values from phonons, Green-Kubo, or validated MLMD with converged sampling
- separate lattice, electronic, and radiative contributions
- record finite-size and directionality corrections

### Diffusion And Reaction

- map DFT or MLMD barriers and diffusivities to a kinetic law with prefactor, concentration, and occupancy assumptions
- keep site populations and charge states explicit
- use temperature and field dependence only within the sampled regime
- validate the reduced law against atomistic trajectories or independent data

### Damage, Fracture, And Plasticity

- use atomistic calculations to identify cohesive, defect, dislocation, or phase-transition behavior
- fit a continuum law to a defined loading path and state range
- include rate, temperature, size, and history effects when relevant
- do not infer macroscopic fracture toughness from one cleavage energy without a crack model

## Units, Tensors, And Conservation

Build a machine-readable `workflow/handoff_register.csv` with at least:

```text
handoff_id,from_stage,to_stage,artifact,quantity_type,schema,mapping,units,
basis,voigt_order,sign_convention,state_variables,averaging_rule,
uncertainty,validity,acceptance,status
```

For every transfer:

1. convert units once in a named transformation
2. document tensor rank and coordinate basis
3. document Voigt ordering and shear convention
4. test dimensional consistency of the governing equation
5. test energy, mass, charge, and flux conservation where applicable
6. retain the unconverted source value and transformation log

Common traps include eV/atom versus J/m3, Angstrom versus meter, bar versus pascal, stress versus virial sign, engineering versus tensorial shear, and conductivity versus diffusivity conventions.

## Implement And Verify The FEM Model

Use a staged implementation:

1. unit test constitutive and transformation functions
2. verify a single-physics benchmark with an analytic or trusted solution
3. perform mesh and time-step convergence
4. test nonlinear and stabilization settings independently
5. validate parameter interpolation on held-out state points
6. enable coupling terms one at a time
7. compare end-to-end conservation and limiting cases
8. only then run the full geometry and parameter sweep

Numerical residual reduction is verification. Agreement with experiment, atomistic benchmarks, or an accepted reference is validation. Report them separately.

## Sequential Coupling

Use sequential coupling when scale separation is reasonable:

```text
DFT -> property or barrier table
MLIP/MD -> state-dependent ensemble or closure
homogenization -> FEM coefficient field or law
FEM -> fields and state history
```

Version each artifact and preserve the state mapping. Use interpolation only inside the sampled domain. For feedback, iterate through a declared fixed-point or staggered algorithm with convergence and relaxation criteria.

## Concurrent Or Adaptive Coupling

Use concurrent coupling only when:

- the interface has an energy, force, flux, or weak-form consistency argument
- overlapping regions, buffer zones, and boundary transfer are defined
- time integration and load transfer are stable
- each solver can checkpoint and recover
- a manufactured-solution or limiting-case test exists

Examples include QM/MM, atomistic-continuum domain decomposition, adaptive crack-tip refinement, and local MLIP/DFT correction. A file exchange between independent solvers is not automatically concurrent coupling.

## Feedback And Uncertainty

At each downstream query, check:

- state within the atomistic sampling envelope
- interpolation distance and phase identity
- uncertainty from labels, surrogate, sampling, fit, and numerical solver
- whether parameter correlations matter for the output

Use ensembles, bootstrap, polynomial chaos, Gaussian-process surrogates, or Monte Carlo when appropriate. Preserve correlated uncertainty between parameters generated from the same DFT or trajectory ensemble. Do not add independent error bars blindly.

If FEM sensitivity identifies a state or parameter that controls the decision but is poorly constrained, send a targeted request upstream: new DFT method branch, AIMD state point, MLIP active-learning batch, or experiment. Document the feedback edge in the manifest.

## Handoff Checklist

- continuum equations and units are versioned
- every parameter traces to a source artifact and method
- direct, homogenized, fitted, and calibrated quantities are distinct
- tensor basis, ordering, signs, and transformations are tested
- state and validity windows are explicit
- mesh, timestep, solver, and constitutive verification passed
- parameter and model uncertainty reached the downstream decision
- prohibited extrapolation and failure behavior are defined
- a reproducible import or solver-neutral table exists
