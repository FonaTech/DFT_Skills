# Plasma Surface Reaction Proxy

## Engineering Intent

Use this case when the user needs DFT-guided insight into plasma-facing surface chemistry, radical impact, abstraction, or non-equilibrium feed-species interactions. The point is to construct a useful proxy workflow for the surface chemistry slice that DFT can treat, while keeping the plasma kinetics and sheath physics outside the DFT packet unless modeled separately.

Do not present this case as a full plasma simulation. It is a surface-reaction proxy workflow.

## Questions This Workflow Must Answer

- Which incoming species, fragments, or radicals are the chemically relevant plasma proxies?
- Which adsorption, abstraction, insertion, or surface-reconstruction events are energetically plausible?
- Which surface terminations remain reactive or stable under the chosen proxy species?
- Which outputs are suitable to hand off to a reduced plasma-surface reaction model?

## Theory And Modeling Boundary

- DFT can compare adsorption energies, abstraction endpoints, reaction energies, and selected barriers for explicitly defined plasma proxy species.
- DFT does not directly model the full plasma environment, sheath acceleration, energy distributions, or non-equilibrium population balance.
- Charged, radical, or electronically excited species require careful reference handling and often remain only approximate proxies.
- If bombardment energy or ion-impact dynamics are decisive, state clearly that static DFT screening is insufficient on its own.

## Minimum Inputs Before Launch

- the relevant feed-species set: radicals, neutrals, ions, or fragments
- the target surface termination and whether it is expected to evolve under plasma exposure
- whether the engineering question concerns passivation, etching, activation, or reaction selectivity
- approximate energy or reactivity regime that motivates the proxy species
- whether the output is for qualitative ranking or for downstream reduced-model parameterization

## Structure Strategy

- begin from a clean or pre-covered surface state that represents the intended plasma-facing condition
- define a small but chemically justified proxy set of incoming species
- include at least one control surface state or termination if the surface is not unique
- separate neutral and radical branches clearly in the workflow
- if abstraction or insertion is suspected, construct explicit product endpoints rather than waiting for spontaneous relaxation

## Recommended Job Ladder

1. bulk and surface reference preparation
2. clean or preconditioned surface relaxations
3. adsorption or encounter-state screening for the proxy species set
4. product-endpoint or abstraction-state relaxations for the leading events
5. optional barrier calculations for the steps that remain mechanistically decisive
6. optional charge-density or local DOS analysis to interpret the reactive surface state

## Primary Outputs And Decisions

- adsorption and reaction-energy ranking for the proxy species
- surface passivation, activation, or etching tendency under the modeled proxies
- qualitative map of which terminations are reactive, blocking, or self-limiting
- shortlist of events suitable for reduced-model handoff
- statement on what parts of the plasma problem remain unmodeled by the DFT proxy layer

## Controls And Sensitivity Axes

- compare at least one alternate surface termination or local site when ambiguity is real
- keep the radical or charge-state convention explicit for each proxy species
- test whether spin polarization changes the leading result for open-shell species
- document whether the result is endpoint screening only or includes explicit barriers
- if the surface is already reconstructed or covered, preserve that history in the structure provenance

## Analysis Checklist

- verify the proxy species set actually reflects the engineering question rather than every possible plasma fragment
- distinguish exothermic reaction endpoints from low-barrier accessible events
- tie each reactive trend back to a specific termination, site family, or local bonding motif
- keep radical, ionic, and neutral reference conventions separated
- state clearly which outputs can be used in a reduced reaction model and which remain qualitative only

## Frequent Failure Modes

- calling ordinary adsorption calculations a plasma model without any proxy logic
- mixing radicals, ions, and neutrals with inconsistent reference handling
- ignoring surface evolution and using one clean termination as though it were stationary
- treating a favorable endpoint as proof of accessible bombardment chemistry
- passing raw DFT energies downstream without reaction-family labels or validity notes

## Escalate Or Pair With

- pair with `01-catalytic-adsorption-and-dissociation.md` when the first uncertainty is still basic surface binding
- pair with `10-chemical-reaction-pathway-screening.md` if the plasma proxy network needs stepwise pathway screening
- pair with `11-ab-initio-molecular-dynamics-stability.md` when thermally or impact-driven rearrangements must be observed dynamically
- pair with `14-comsol-coupling-and-property-handoff.md` only after the DFT packet is reduced to a reaction or parameter set usable by a larger model

## Deliverables

- proxy-species definition table and reference conventions
- surface-reactivity ranking packet with explicit terminations and endpoints
- shortlist of reduced-model handoff candidates
- explicit note on plasma physics that remains outside the DFT scope
