# Finite-Temperature Free Energy And Phase Behavior

## Engineering Intent

Use this case when static total energies cannot resolve temperature-, pressure-, composition-, or entropy-dependent stability. Route among phonons, thermodynamic integration, enhanced sampling, cluster expansion, AIMD, or validated MLMD according to the phase and slow variables.

## Questions This Workflow Must Answer

- Which free-energy contributions control the phase decision?
- Are harmonic, quasiharmonic, anharmonic, configurational, magnetic, electronic, or interfacial terms required?
- What order parameter distinguishes candidate phases?
- Is the target an equilibrium boundary, metastability window, nucleation proxy, or kinetic transformation?

## Minimum Inputs

- candidate phases, compositions, magnetic or charge branches, and reference conventions
- temperature and pressure range and required boundary precision
- order parameters and expected transition class
- static DFT convergence and phonon or sampling feasibility
- experimental anchors, if calibration or validation is planned

## Route Selection

| Regime | Starting route | Escalation |
|---|---|---|
| dynamically stable crystal, moderate temperature | harmonic or quasiharmonic phonons | anharmonic force constants or thermodynamic integration |
| soft or strongly anharmonic crystal | AIMD or MLMD sampling | free-energy integration or self-consistent phonons |
| substitutional or occupational disorder | cluster expansion plus Monte Carlo | coupled lattice and vibrational free energies |
| liquid or amorphous phase | AIMD seed and validated MLMD | coexistence, integration, or enhanced sampling |
| magnetic or electronic entropy important | explicit model branch | higher-level electronic or spin treatment |

## Recommended Experiment Ladder

1. converge static phase energies and reference states
2. test dynamical stability and identify soft modes
3. choose the minimum free-energy decomposition that captures the decision
4. converge cell, supercell, k-mesh, state grid, and sampling estimator
5. compute phase free energies with independent references or thermodynamic cycles
6. locate crossings with propagated uncertainty
7. test hysteresis, finite-size, and alternative order parameters
8. validate selected state points against higher fidelity or experiment

## Controls And Sensitivity

- exchange-correlation, magnetic order, `+U`, and dispersion sensitivity
- supercell and commensurability
- integration path and reference free energy
- temperature and pressure grid density
- heating versus cooling and independent replicas
- finite-size scaling near transitions
- composition and defect ensemble assumptions

## Frequent Failure Modes

- using zero-K energy crossings as a finite-temperature phase boundary
- adding harmonic phonons to an unstable reference without repair
- calling hysteretic transformation points equilibrium boundaries
- fitting a smooth free-energy curve through insufficient or correlated samples
- omitting configurational, magnetic, or electronic entropy that changes the ordering

## Deliverables

- phase and reference-state matrix
- free-energy decomposition and integration protocol
- convergence and sampling diagnostics
- phase boundary with uncertainty and metastability caveats
- representative configurations or order-parameter distributions
- explicit statement of missing entropy or kinetic effects
