# Phonon And Thermal Transport

## Engineering Intent

Use this case when the main target is dynamical stability, phonon dispersion, vibrational mode analysis, or a lattice thermal transport handoff. The workflow should prove the structure is vibrationally well behaved before any thermal-transport interpretation is attempted.

Do not use this case alone to claim final thermal conductivity under realistic device conditions unless the scattering model, defects, and size effects are treated consistently.

## Questions This Workflow Must Answer

- Is the relaxed structure dynamically stable under the modeled phase and strain condition?
- Which phonon branches or mode families dominate the vibrational behavior near the engineering-relevant window?
- Are anharmonic or disorder effects likely large enough to invalidate a purely harmonic picture?
- Is the phonon packet mature enough for thermal-transport or continuum handoff?

## Theory And Modeling Boundary

- DFT can provide harmonic force constants, phonon dispersions, density of states, and in many workflows the upstream ingredients for lattice thermal transport models.
- Imaginary modes invalidate ordinary harmonic interpretations unless they are understood as numerical artifacts or symmetry-restoring soft modes under specific conditions.
- Harmonic phonons are not the same thing as full anharmonic thermal conductivity. Additional scattering and higher-order force-constant modeling may be required.
- If the structure is strongly disordered or highly anharmonic, AIMD or MLFF sampling may be the more honest next step.

## Minimum Inputs Before Launch

- whether the user needs dynamical stability only, mode assignment, or thermal-transport input
- structural phase, strain state, and magnetic order
- acceptable supercell size and force-convergence target for the force-constant workflow
- whether isotope, defect, interface, or finite-temperature effects must be reflected later
- whether the output is a trend screen or a quantitative transport handoff

## Structure Strategy

- start from a tightly relaxed reference structure with low residual forces
- use a supercell and displacement pattern appropriate to the intended force-constant cutoff
- if multiple phases or strain states are compared, keep them on the same convergence footing
- separate pristine harmonic analysis from later defect or alloy perturbations
- if a soft mode appears, preserve the snapshot or displaced branch for follow-up rather than hiding it

## Recommended Job Ladder

1. relaxed bulk reference with tight force criteria
2. static refinement for accurate forces
3. displaced-supercell or perturbative phonon workflow
4. phonon dispersion or vibrational DOS analysis
5. optional higher-order or transport-specific force-constant workflow if quantitative thermal transport is required
6. optional sensitivity checks on supercell size, displacement amplitude, and strain state

## Primary Outputs And Decisions

- phonon stability verdict with explicit note on any imaginary modes
- mode-resolved trends or branch assignments relevant to the engineering question
- vibrational density of states or related spectral summary
- thermal-transport handoff packet or proxy descriptors, if justified
- recommendation on whether harmonic analysis is sufficient or whether anharmonic follow-up is required

## Controls And Sensitivity Axes

- keep force convergence tighter than ordinary structural relaxations
- check supercell size and displacement amplitude sensitivity
- verify the same structural phase is used throughout the phonon workflow
- if soft modes appear, test whether they are numerical, symmetry-related, or physically meaningful
- if thermal transport is the goal, document which scattering channels are included and which are not

## Analysis Checklist

- confirm that any imaginary modes are interpreted before discussing transport
- identify which branches dominate the relevant frequency range or directional behavior
- separate harmonic stability from quantitative conductivity claims
- keep the relation between structural phase, strain, and phonon behavior explicit
- state clearly whether the result is a stability screen, a mode-analysis packet, or a transport handoff

## Frequent Failure Modes

- discussing thermal conductivity before checking for imaginary modes
- using too small a supercell or loose force convergence for delicate phonon branches
- treating harmonic results as though they already include strong anharmonic scattering
- hiding phase instability by showing only the stable part of the spectrum
- comparing different phases or strains with inconsistent displacement settings

## Escalate Or Pair With

- pair with `11-ab-initio-molecular-dynamics-stability.md` when strong anharmonicity or disorder undermines the harmonic approximation
- pair with `05-elastic-mechanical-stability.md` when mechanical softness and vibrational softness interact
- pair with `14-comsol-coupling-and-property-handoff.md` if thermal parameters are needed by a continuum model
- pair with `13-lammps-coupling-and-mlff-handoff.md` when larger-scale thermal sampling is needed beyond direct DFT reach

## Deliverables

- relaxed reference structure and phonon workflow definition
- phonon stability and mode-analysis packet
- transport handoff or proxy table, if justified
- explicit warning for missing anharmonic, defect, or finite-size physics
