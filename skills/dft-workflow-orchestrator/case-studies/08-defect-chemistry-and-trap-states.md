# Defect Chemistry And Trap States

## Engineering Intent

Use this case when vacancies, substitutions, interstitials, or trap states control the engineering question. The goal is to build a defect workflow that makes supercell size, chemical potentials, localization, and charge-state assumptions explicit instead of hiding them behind one defect relaxation.

Do not use this case to claim final defect concentrations or device reliability without a proper thermodynamic and kinetic framework.

## Questions This Workflow Must Answer

- Which defect species and lattice sites are plausibly relevant?
- What is the formation-energy ordering under the chosen chemical-potential convention?
- Do localized in-gap or near-edge states appear, and are they robust to methodology?
- Is the defect likely to act as a trap, compensator, or structural destabilizer under the modeled conditions?

## Theory And Modeling Boundary

- DFT can compare relaxed defect geometries, formation energies under explicit reference conventions, and localization proxies from DOS, PDOS, charge density, or spin density.
- Defect formation energies depend on chemical potentials, supercell size, and sometimes charge-correction methodology.
- One neutral supercell calculation is not a complete defect thermodynamics study if charged states matter.
- Trap behavior inferred from orbital localization is still not identical to device capture cross section or kinetic lifetime.

## Minimum Inputs Before Launch

- the defect family: vacancy, substitution, interstitial, antisite, or complex
- whether neutral-only screening is acceptable or charged states must be considered
- chemical-potential environment or at least the bounding synthesis conditions
- supercell size target and acceptable defect concentration proxy
- whether the main observable is formation energy, trap level, compensation trend, or local distortion

## Structure Strategy

- relax the pristine bulk reference with the same production method intended for defects
- build a supercell large enough that image-image interaction is visibly controlled
- create separate defect branches for each unique candidate site rather than overloading one representative site
- preserve charge, spin, and symmetry labels clearly in the folder names
- if a defect complex is being studied, keep the single-defect references available for decomposition analysis

## Recommended Job Ladder

1. pristine bulk relaxation and supercell generation
2. pristine supercell static refinement as the direct reference
3. defect supercell relaxations for the key candidate sites
4. optional charged-state or alternative-spin reruns where the physics demands them
5. DOS, PDOS, spin density, charge density, or local structure analysis for the decisive candidates
6. optional chemical-potential or correction sensitivity table

## Primary Outputs And Decisions

- defect formation-energy ranking under the documented reference convention
- local structural distortion and coordination response
- in-gap, near-edge, or spin-polarized state indicators tied to the defect
- statement on whether the defect is likely benign, compensating, trap-forming, or stabilizing
- recommendation on which defect branches deserve migration, interface, or transport follow-up

## Controls And Sensitivity Axes

- record the concentration implied by the chosen supercell
- compare at least one alternate site if site ambiguity exists
- keep chemical-potential assumptions visible in the final tables
- test whether localization or defect-level ordering changes under `+U`, hybrid, or spin-state sensitivity
- if charged states matter, state explicitly whether image-charge or potential-alignment corrections were applied

## Analysis Checklist

- verify the pristine supercell reference is converged and stored alongside the defect jobs
- separate defect formation energy from trap-level interpretation
- inspect whether the defect state is genuinely localized or merely folded bulk character
- document any symmetry breaking induced by the defect
- state clearly whether the workflow supports relative defect ranking only or a more complete thermodynamic argument

## Frequent Failure Modes

- quoting a defect number without any chemical-potential convention
- using a supercell so small that the result is mostly an artificial concentration effect
- showing one DOS peak and calling it a device-relevant trap without localization analysis
- comparing neutral and charged defects without correction or alignment notes
- hiding the pristine supercell reference or using inconsistent methods between reference and defect runs

## Escalate Or Pair With

- pair with `09-ionic-migration-and-neb.md` when the decisive defect is also the migrating species
- pair with `03-band-structure-and-carrier-transport.md` if edge-state renormalization controls the interpretation
- pair with `07-heterointerface-band-alignment-and-charge-transfer.md` when defects are interfacial rather than bulk-like
- pair with `11-ab-initio-molecular-dynamics-stability.md` if defect-induced disorder or temperature stability is a concern

## Deliverables

- pristine and defect supercell packet with site labels
- formation-energy table with chemical-potential conventions
- localization or trap-analysis note tied to actual electronic-structure evidence
- explicit statement of what remains unresolved without charge corrections, larger cells, or kinetics
