# DFT To FEM Electro-Chemo-Mechanical Coupling

## Engineering Intent

Use this case when atomistic defect, transport, elastic, dielectric, or reaction information must drive a continuum model with coupled concentration, electric, thermal, and mechanical fields. Typical targets include batteries, ionic conductors, memristive oxides, corrosion, catalytic devices, and electroactive solids.

Read `references/fem-multiscale-coupling.md`, `references/multiscale-validation.md`, and the property-specific DFT case.

## Questions This Workflow Must Answer

- Which governing equations and fields define the continuum decision?
- Which coefficients are direct DFT quantities and which require kinetics, homogenization, or experimental calibration?
- How do temperature, composition, phase, field, and strain change those coefficients?
- Does continuum feedback move the material outside the atomistic validity window?

## Minimum Inputs

- continuum geometry, dimensionality, equations, boundary and initial conditions, and loading history
- required property list with units, tensor basis, state variables, and accuracy targets
- structures and DFT reference states for each relevant phase, defect, charge, and strain branch
- constitutive mapping equations and any experimental calibration data
- FEM engine, version, mesh strategy, solver choices, and benchmark cases

## Recommended Stage DAG

```text
S01 DFT structures and reference energies
S02 DFT elastic, dielectric, defect, and migration property grid
S03 kinetic or constitutive reduction
S04 unit and tensor coupling adapter
S05 single-physics FEM verification
S06 coupled electro-chemo-mechanical FEM
S07 uncertainty and held-out validation
```

## Atomistic Property Grid

Generate only coefficients needed by the continuum equations. Candidate families include:

- elastic, chemical-expansion, dielectric, piezoelectric, and polarization tensors
- defect formation, charge-state, migration, and reaction energetics
- diffusivity or mobility model parameters with explicit prefactor treatment
- phase free-energy anchors and composition or strain derivatives
- surface and interface energies or exchange-current proxies

Use a state grid when a coefficient is not constant. Record interpolation and prohibited extrapolation.

## Coupling Checks

- rotate tensors from crystal to device basis with a round-trip test
- distinguish eV/atom, eV/cell, and energy density
- distinguish stress from virial and declare sign conventions
- verify electrochemical potential and flux units in every equation
- check mechanical work, heat, charge, and mass conservation
- keep intrinsic, homogenized, and fitted parameters separate

## FEM Verification And Validation

1. recover analytic diffusion, elasticity, electrostatics, or heat limits separately
2. perform mesh, time-step, nonlinear tolerance, and domain-size studies
3. activate one coupling term at a time
4. compare against a manufactured or reduced-dimensional benchmark
5. propagate the atomistic parameter uncertainty through the decisive output
6. validate on held-out state points or independent experiment

## Feedback Rules

If FEM reaches an unsampled temperature, composition, phase, strain, or field, stop or request a targeted upstream calculation. If sensitivity shows one poorly constrained coefficient dominates the output, compute that branch before expanding low-impact DFT work.

## Frequent Failure Modes

- inserting a zero-temperature DFT value as a universal continuum constant
- deriving a rate from one barrier without prefactor, concentration, or site population
- mixing crystal and device coordinates
- calibrating and validating on the same experimental curve
- accepting a converged FEM solve despite invalid constitutive extrapolation

## Deliverables

- equation and parameter requirement sheet
- DFT state-grid and provenance packet
- machine-readable handoff register with transformations
- verified single-physics and coupled FEM models
- propagated uncertainty and sensitivity report
- feedback requests, validity window, and final claim verdict
