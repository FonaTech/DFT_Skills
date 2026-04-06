# Catalytic Adsorption And Dissociation

## Engineering Intent

Use this case when the main decision is whether a surface binds, activates, or dissociates a reactant strongly enough to matter for catalyst screening. The decisive outputs are endpoint energetics and geometry changes on a defined surface model, not generic statements that a material is "active."

Avoid using this case alone when the claim actually depends on reaction barriers, electrolyte effects, or plasma kinetics. In those situations this case is the first screening layer, not the full answer.

## Questions This Workflow Must Answer

- Which adsorption site or motif is preferred at the target coverage?
- Does the molecular state remain intact, partially activated, or fully dissociate after relaxation?
- Is the energetic preference robust to facet, site, spin, and dispersion choices?
- Is the result strong enough to justify escalation to NEB, electrocatalysis, or finite-temperature checks?

## Theory And Modeling Boundary

- Static DFT can compare adsorption energies, dissociated endpoint energies, bond elongation, charge redistribution proxies, and local DOS changes.
- Static DFT does not by itself prove turnover, selectivity, or steady-state catalytic rate.
- A dissociated endpoint lower in energy than the molecular endpoint does not guarantee a low barrier.
- If the engineering claim is about kinetics, explicitly mark this case as an endpoint-screening workflow and queue NEB or reaction-pathway work afterward.

## Minimum Inputs Before Launch

- target facet or a justified list of candidate facets
- adsorbate identity, reference stoichiometry, and spin state assumptions
- surface composition, magnetic state, and whether the slab is polar
- coverage convention and whether adsorbate-adsorbate interaction is expected to matter
- reference state definition for gas, isolated molecule, or competing fragments

## Structure Strategy

- start from a bulk-relaxed parent before any slab is trusted
- generate a clean slab with explicit thickness, vacuum, and termination choices
- enumerate at least two chemically distinct adsorption sites or orientations
- if dissociation matters, prepare one or more dissociated endpoints rather than relying on spontaneous relaxation only
- keep the surface cell size large enough that the chosen coverage is interpretable

## Recommended Job Ladder

1. bulk reference relaxation with the method intended for the surface work
2. clean slab relaxation with frozen-bottom or fully relaxed policy documented
3. gas-phase or isolated reference relaxation using a consistent functional
4. molecular adsorption relaxations for the leading site and at least one control site
5. dissociated endpoint relaxations for the chemically plausible fragment placements
6. optional static refinement, charge analysis, DOS or PDOS, and dipole-corrected reruns if needed

## Primary Outputs And Decisions

- adsorption energy referenced to the documented free or isolated state
- reaction energy between intact and dissociated endpoints
- bond lengths, adsorption height, key surface reconstruction markers, and coordination changes
- qualitative charge redistribution or bonding proxy from Bader, charge-density difference, or projected DOS
- ranking of sites, motifs, or facets that should move forward

## Controls And Sensitivity Axes

- compare at least one alternate site, orientation, or adsorption registry
- test whether dispersion changes the ranking when weak binding is plausible
- keep slab thickness, vacuum, dipole correction, and bottom-layer constraints visible
- check spin polarization or magnetic order if the surface or adsorbate may be open-shell
- record whether the chosen supercell implies a realistic or artificially high coverage

## Analysis Checklist

- verify the clean slab remains stable and not accidentally reconstructed into another termination
- confirm the relaxed adsorption motif is chemically interpretable and not a numerical artifact
- separate strong adsorption from mere short contact distances by checking energy and geometry together
- compare intact and dissociated states on the same reference footing
- state clearly whether the conclusion is "preferred endpoint" or "demonstrated accessible pathway"

## Frequent Failure Modes

- claiming catalysis from one relaxed geometry without any energetic comparison
- forgetting the isolated adsorbate or using an inconsistent gas reference
- comparing different slab sizes or k-mesh settings as though they were directly commensurate
- using only one adsorption site and presenting it as a global conclusion
- overlooking charged, radical, or spin-sensitive adsorbates that need a different reference treatment

## Escalate Or Pair With

- pair with `09-ionic-migration-and-neb.md` or `10-chemical-reaction-pathway-screening.md` when a barrier determines the claim
- pair with `02-electrocatalysis-and-surface-potential.md` if the relevant environment is potential dependent
- pair with `12-plasma-surface-reaction-proxy.md` when radicals or non-equilibrium feed species dominate
- pair with `11-ab-initio-molecular-dynamics-stability.md` if the adsorbate state is thermally labile

## Deliverables

- clean slab and adsorbate reference structures with provenance
- adsorption and dissociation job matrix with site labels
- endpoint energy table with explicit references
- short analysis note on what DFT does support and what still requires a barrier or finite-temperature workflow
