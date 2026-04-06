# VASP Methodology Notes

This reference is a decision guide. It is not a universal parameter table.

## 1. Functional Choice

### Plain GGA or PBEsol is usually enough when:

- the system is weakly correlated
- the task is geometry screening or reference bulk optimization
- the observable is not dominated by localized `d` or `f` electrons

### `+U` is usually required when:

- transition-metal `d` states dominate the physics
- rare-earth or actinide compounds are involved
- the target observable depends on localization, magnetism, or gap opening

For correlated oxides, always state:

- which element receives `U`
- which `Ueff` values were tested
- whether the conclusion changes across the scan

## 2. Magnetic Order

Do not default blindly to non-magnetic calculations for magnetic oxides.

Minimum screening:

- one `FM` pattern
- one simple `AFM` pattern

Production claims should move toward a physically motivated ordered approximation if the literature suggests one.

## 3. Convergence Axes

At minimum validate:

1. `ENCUT`
2. k-point mesh
3. energy and force thresholds
4. slab thickness or supercell size when relevant

Never mix loose settings across compared systems unless you explain the asymmetry.

## 4. Surfaces, Adsorption, and Interfaces

Track explicitly:

- Miller index
- termination
- slab thickness
- vacuum size
- frozen layers if any
- dipole correction if asymmetry exists

Dispersion:

- use D3 or D3(BJ) for adsorption, layered materials, weak interfaces, or molecular binding
- do not confuse dispersion correction with strong-correlation treatment

## 5. Correlated-Oxide Guardrails

For nickelates and related materials:

- treat `U` as a sensitivity axis, not a magic switch
- keep structural branch explicit
- keep magnetic order explicit
- do not overclaim finite-temperature metal-insulator physics from static zero-K DFT or DFT+U

## 6. Common Job Families

### Relaxation

Use for:

- bulk cell or ionic optimization
- clean slab or interface cleanup
- endpoint structures before static analysis

Typical tags:

- `IBRION = 2`
- `NSW > 0`
- `ISIF = 2` or `3` depending on whether cell degrees of freedom should move

### Static DOS or PDOS

Use only after relaxation.

Typical changes:

- tighter electronic convergence
- `NSW = 0`
- denser k-mesh than geometry optimization if needed

### Optics

Use only after a structurally converged reference is available.

Track:

- whether the system is metallic or insulating
- k-point sensitivity
- whether the result is a qualitative comparison or a quantitative benchmark

### NEB

Required:

- fully converged initial state
- fully converged final state
- chemically meaningful interpolation

Do not run NEB on endpoints that were never relaxed.

## 7. Required Method Summary

Every final packet should include:

- code version
- pseudopotential family
- functional
- `U` scheme and values
- magnetic setup
- cutoff
- k-mesh
- relaxation thresholds
- whether dispersion was used
- structure provenance
