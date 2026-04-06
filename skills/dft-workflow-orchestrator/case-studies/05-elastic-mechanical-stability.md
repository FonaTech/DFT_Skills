# Elastic Mechanical Stability

## Engineering Intent

Use this case when the main decision is whether a structure is mechanically stable and what elastic response window it offers under small strain. The target outputs are elastic constants, modulus trends, anisotropy indicators, and stability criteria that can feed screening or handoff workflows.

Do not stretch this case into fracture, plasticity, grain-boundary failure, or long-time deformation claims. Those live outside ordinary small-strain DFT elasticity.

## Questions This Workflow Must Answer

- Is the relaxed phase mechanically stable under the chosen pressure and symmetry condition?
- What are the principal elastic constants and modulus trends?
- Is the response isotropic enough for scalar reporting, or does tensor anisotropy matter?
- Do strain-sensitive properties need a follow-up piezoelectric, phonon, or COMSOL handoff workflow?

## Theory And Modeling Boundary

- DFT can provide the small-strain elastic tensor and derived quantities such as bulk, shear, and Young's modulus under the stated approximation.
- Mechanical stability conclusions depend on the actual relaxed structure, magnetic state, and pressure condition.
- A stable elastic tensor does not prove resistance to fracture, creep, fatigue, or finite-temperature microstructural degradation.
- If the user asks about large deformation or failure, mark this case as a constitutive baseline only.

## Minimum Inputs Before Launch

- the target phase and whether zero-pressure or finite-pressure stability is relevant
- crystal symmetry and whether the user needs full tensor reporting or only aggregate moduli
- whether the material is layered, low-dimensional, soft, or likely to undergo internal relaxations under strain
- whether electromechanical or thermal couplings are expected to matter downstream
- acceptable strain amplitude for the finite-difference workflow

## Structure Strategy

- begin from a well-relaxed bulk structure with tight force and stress convergence
- preserve the correct magnetic and correlated state before any strain perturbation
- use symmetry-aware strain sets when possible, but keep the full applied strain list documented
- for low-symmetry cells, check that the deformation set spans all required independent tensor components
- for layered or 2D-like systems, keep vacuum conventions and thickness interpretation explicit

## Recommended Job Ladder

1. bulk relaxation to a low-stress reference state
2. static refinement at the reference geometry
3. a finite set of positive and negative strain perturbations around the reference
4. stress or total-energy extraction for tensor fitting
5. post-processing into elastic constants, mechanical stability criteria, and directional moduli
6. optional strain-sensitivity follow-up for the property that actually matters downstream

## Primary Outputs And Decisions

- elastic tensor in the stated crystallographic basis
- derived bulk, shear, and Young's modulus under the chosen averaging convention
- anisotropy indicators or compliance trends
- explicit mechanical stability verdict using the symmetry-appropriate criteria
- recommendation on whether scalar reporting is adequate or tensor handoff is required

## Controls And Sensitivity Axes

- verify the strain amplitude is small enough for linear elasticity but large enough to beat numerical noise
- keep ENCUT, k-mesh, and stress convergence tighter than ordinary relaxation settings
- check whether internal atomic relaxation under fixed strain changes the conclusions
- test the sensitivity to magnetic order or `+U` if those choices affect bonding stiffness
- if pressure matters, do not reuse zero-pressure criteria without adjustment

## Analysis Checklist

- confirm the reference cell is at or very near the intended stress state
- fit the tensor from symmetric strain branches rather than one-sided perturbations only
- use the correct symmetry-dependent stability criteria
- state the averaging convention for isotropic moduli
- separate intrinsic elastic response from device or microstructure assumptions

## Frequent Failure Modes

- using a poorly converged reference cell and then blaming noisy elastic constants on the material
- applying strains that are too large for linear elasticity
- quoting scalar modulus values without acknowledging strong tensor anisotropy
- mixing clamped and internally relaxed strain states without distinction
- interpreting low-dimensional materials with bulk-style volume normalization and no caveat

## Escalate Or Pair With

- pair with `15-piezoelectric-strain-coupling.md` when electromechanical response is the real target
- pair with `16-phonon-and-thermal-transport.md` if dynamical stability remains uncertain
- pair with `14-comsol-coupling-and-property-handoff.md` when the tensor becomes a continuum input
- pair with `11-ab-initio-molecular-dynamics-stability.md` if soft structures appear only marginally stable at zero temperature

## Deliverables

- reference bulk structure and strain set definition
- elastic tensor table with basis and averaging convention
- mechanical stability verdict with the exact criteria used
- note on what this small-strain workflow does not establish
