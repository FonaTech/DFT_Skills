# Electrocatalysis And Surface Potential

## Engineering Intent

Use this case when the engineering question is tied to potential-dependent surface chemistry, adsorbate ladders, or descriptor-based overpotential proxies. The aim is to turn a catalytic question into a documented electrochemical approximation rather than to hide electrolyte assumptions behind ordinary adsorption calculations.

Do not use this case to claim full electrochemical kinetics unless the workflow includes the required free-energy corrections, potential convention, and environment model.

## Questions This Workflow Must Answer

- Which intermediates become limiting along the intended reaction ladder?
- How does site preference change under the chosen electrochemical reference convention?
- Which step controls the qualitative thermodynamic bottleneck?
- How sensitive is the conclusion to solvation proxy, spin treatment, and surface coverage?

## Theory And Modeling Boundary

- DFT can provide electronic energies, adsorption trends, and geometry information for intermediate ladders.
- The electrochemical interpretation usually depends on an additional thermodynamic framework such as the computational hydrogen electrode or another explicit reference convention.
- Implicit solvent, explicit water, surface charging, and constant-potential methods are not interchangeable. Record which approximation is actually used.
- A low free-energy step does not guarantee fast kinetics, and a simple CHE ladder is not a full constant-potential treatment.

## Minimum Inputs Before Launch

- the target electrochemical reaction family and the required elementary intermediates
- pH, potential convention, and whether the user expects thermodynamic screening or kinetic analysis
- surface termination, facet, and magnetic state
- environment approximation: vacuum only, implicit solvent, explicit water, or a staged combination
- whether proton-coupled electron transfer steps are represented through CHE or another formalism

## Structure Strategy

- start from a clean slab and document the chosen reference termination
- define the intermediate set before launching calculations so the ladder is closed
- place each adsorbate at at least one chemically plausible site and one control site
- if co-adsorption or water stabilization is believed to be decisive, include that explicitly instead of leaving it implicit
- keep surface cell size large enough to avoid meaningless crowding when several intermediates are compared

## Recommended Job Ladder

1. bulk and clean-slab relaxations with the production method
2. baseline adsorption calculations for the core intermediates
3. optional solvent or water-assisted variants for the most sensitive states
4. static refinement for final energies, charge analysis, and local DOS where needed
5. free-energy assembly step with zero-point, entropy, and potential bookkeeping clearly separated from raw DFT energy
6. optional NEB only for the step that remains mechanistically decisive after ladder screening

## Primary Outputs And Decisions

- free-energy ladder under the stated approximation
- limiting thermodynamic step or overpotential proxy
- site dependence of the decisive intermediates
- qualitative electronic indicators such as charge redistribution, band filling, or adsorbate-state hybridization
- recommendation on whether a more explicit environment model is required

## Controls And Sensitivity Axes

- compare at least one alternate adsorption site for the key intermediates
- track coverage sensitivity when neighboring adsorbates are likely to interact
- test whether dispersion or solvent stabilization reorders the limiting step
- keep the reference hydrogen, water, or proton-electron bookkeeping explicit
- record whether the surface is neutral, implicitly charged, or simply treated as a neutral vacuum slab

## Analysis Checklist

- distinguish raw adsorption energies from electrochemical free energies
- verify that the chosen intermediate ladder is stoichiometrically closed
- report which step is limiting and why, not just which intermediate binds strongly
- separate robust conclusions from those that flip under small methodological changes
- state clearly if the workflow supports thermodynamic ranking only

## Frequent Failure Modes

- mixing gas-phase references, solvent-corrected states, and CHE terms without a consistent table
- claiming potential dependence from neutral-vacuum calculations without stating the approximation
- overlooking adsorbate coverage effects on the limiting step
- using one intermediate geometry and assuming the whole ladder is under control
- presenting a descriptor trend as if it were a full microkinetic prediction

## Escalate Or Pair With

- pair with `10-chemical-reaction-pathway-screening.md` when one elementary barrier controls the engineering decision
- pair with `01-catalytic-adsorption-and-dissociation.md` when endpoint binding is still the first uncertainty
- pair with `07-heterointerface-band-alignment-and-charge-transfer.md` when support or junction effects shift the surface electronic structure
- pair with `14-comsol-coupling-and-property-handoff.md` only after the DFT packet has a defensible reduced constitutive form

## Deliverables

- intermediate definition table and reference convention note
- adsorption and free-energy ladder tables with explicit correction columns
- shortlist of decisive steps and the sensitivity axes that could overturn the ranking
- clear statement of whether the case supports thermodynamic screening, kinetic inference, or only qualitative trends
