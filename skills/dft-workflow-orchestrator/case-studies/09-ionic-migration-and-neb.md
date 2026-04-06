# Ionic Migration And NEB

## Engineering Intent

Use this case when the decisive quantity is a migration barrier or pathway ranking for ions, protons, vacancies, or small mobile species. This workflow is about constructing defensible initial and final states and then using NEB or a related method to test the barrier, not about hoping that one relaxation reveals transport.

Do not turn this case into a diffusion-coefficient claim unless the barrier model, prefactor logic, and defect thermodynamics are all documented.

## Questions This Workflow Must Answer

- Which lattice sites or local motifs are connected by the proposed migration event?
- Are the initial and final states true local minima under the same method?
- What is the barrier ordering among the plausible migration pathways?
- Is the path sensitive to local chemistry, supercell size, charge state, or correlation treatment?

## Theory And Modeling Boundary

- DFT plus NEB can provide a minimum-energy-path proxy and activation barrier for a specific migration event.
- The barrier depends on the chosen initial and final states, supercell, and defect environment.
- One barrier does not produce a full macroscopic diffusion coefficient without population, topology, and prefactor information.
- If the material exhibits strong disorder, concerted motion, or finite-temperature path switching, a static NEB alone may be insufficient.

## Minimum Inputs Before Launch

- the migrating species and its likely site network
- whether the event is vacancy mediated, interstitial, exchange-like, or proton-transfer like
- supercell size target and defect concentration implications
- charge state or oxidation-state assumptions if they affect the local environment
- whether the user needs one illustrative barrier or a pathway comparison for screening

## Structure Strategy

- start from a pristine or defected host structure that is already converged
- relax the initial and final states independently until both are genuine minima
- if several sites are plausible, generate parallel initial-final pairs rather than forcing one path
- keep the local environment around the moving species comparable between pathways
- use a large enough supercell that the migrating species does not interact strongly with its own periodic image

## Recommended Job Ladder

1. host bulk or defect supercell relaxation
2. initial-state relaxation
3. final-state relaxation
4. interpolation and NEB image generation with a documented image count
5. NEB or climbing-image NEB run to barrier convergence
6. optional static refinement of the decisive images and sensitivity reruns for competing paths

## Primary Outputs And Decisions

- migration barrier for each explicitly defined pathway
- pathway ordering and geometric description of the transition state region
- qualitative local-bonding or coordination change along the path
- note on whether the result supports a simple site-to-site hopping picture or suggests more complex transport physics
- recommendation on whether larger cells, more images, or finite-temperature sampling are required

## Controls And Sensitivity Axes

- compare at least two plausible paths if the migration network is not unique
- verify the initial and final endpoints are converged with the same method and charge state
- test image count and spring settings if the barrier shape is jagged or unstable
- keep the supercell size and defect concentration explicit
- check whether spin, `+U`, or local charge redistribution changes the decisive barrier ordering

## Analysis Checklist

- confirm no NEB image is simply a failed relaxation into an unrelated state
- verify the barrier is referenced to the proper initial-state energy
- inspect whether the highest image is localized in one saddle region or split across multiple unresolved events
- state whether the path is a direct minimum-energy path or only one plausible screened path
- distinguish barrier comparison from macroscopic transport prediction

## Frequent Failure Modes

- launching NEB from poorly relaxed endpoints
- using one arbitrary path and presenting it as the global transport answer
- ignoring supercell concentration effects for interstitial or proton migration
- claiming conductivity or diffusion coefficients from a barrier with no population model
- failing to check whether the charge state or local magnetic configuration changes along the path

## Escalate Or Pair With

- pair with `08-defect-chemistry-and-trap-states.md` when defect thermodynamics determine which mobile species actually exists
- pair with `10-chemical-reaction-pathway-screening.md` when the motion is one step in a broader reaction network
- pair with `11-ab-initio-molecular-dynamics-stability.md` when correlated or disordered motion makes a single-path NEB too rigid
- pair with `13-lammps-coupling-and-mlff-handoff.md` if many pathways or long-time diffusion statistics are needed later

## Deliverables

- initial and final state structures with provenance
- NEB path table with image count and convergence note
- barrier comparison note for the decisive pathways
- explicit statement of what remains unresolved without topology, prefactors, or finite-temperature sampling
