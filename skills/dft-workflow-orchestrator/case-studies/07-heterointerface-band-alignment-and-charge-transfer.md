# Heterointerface Band Alignment And Charge Transfer

## Engineering Intent

Use this case when the engineering question depends on interface stability, band lineup, built-in fields, contact quality, or charge transfer across two materials. The target is an explicit interface packet, not a guess from isolated bulk properties alone.

Do not use this case as a shortcut for transport or device performance claims unless the interface model and the downstream constitutive interpretation are both documented.

## Questions This Workflow Must Answer

- Which interface termination and registry are plausible and energetically competitive?
- What strain, stoichiometry, and polarity choices are built into the interface model?
- How large is the charge-transfer or electrostatic-lineup trend under those assumptions?
- Is the interface stable enough to justify downstream transport, dielectric, or device-level modeling?

## Theory And Modeling Boundary

- DFT can compare interface formation energies, charge redistribution trends, local electrostatic offsets, and local DOS or PDOS signatures.
- Bulk band edges alone do not define the final interface lineup once dipoles, reconstruction, and charge redistribution appear.
- A band alignment proxy does not automatically yield contact resistance, carrier injection efficiency, or full device performance.
- If the claim depends on defect-rich, amorphous, or chemically reacting interfaces, this crystalline interface case is only a first approximation.

## Minimum Inputs Before Launch

- the identities and phases of both constituents
- likely surface terminations, polarity, and orientation relationship
- whether the user needs thermodynamic stability, lineup, charge transfer, or all three
- commensuration tolerance and how strain will be distributed between the two sides
- whether the interface is expected to be abrupt, reconstructed, defective, or chemistry modified

## Structure Strategy

- begin from relaxed bulk references for both constituents
- generate clean surface references when termination energetics or vacuum alignment matter
- build one or more commensurate interface supercells with documented strain allocation
- compare at least one alternate registry or termination if the interface is not unique
- keep stoichiometry, cell dipole, and vacuum or periodic boundary conventions explicit

## Recommended Job Ladder

1. relaxed bulk references for each constituent
2. isolated slab or vacuum-reference calculations if lineup or termination energy is needed
3. interface construction with explicit registry and termination labels
4. full interface relaxation with convergence checks on layer thickness and in-plane strain
5. charge-density difference, planar potential, and local DOS analyses
6. optional sensitivity runs for alternate terminations, strain states, or chemical environments

## Primary Outputs And Decisions

- interface formation or adhesion-energy metric under the documented stoichiometry convention
- electrostatic lineup or band-offset proxy
- charge transfer trend and its spatial localization
- structural reconstruction or rumpling markers that materially affect the conclusion
- recommendation on whether the interface packet is stable enough for device or continuum handoff

## Controls And Sensitivity Axes

- compare at least one alternate registry, termination, or interfacial composition when ambiguity is real
- keep slab or layer thickness convergence visible on both sides of the interface
- track how much artificial strain is imposed and to which constituent
- test whether magnetism, `+U`, or SOC changes the interface-localized states
- if vacuum alignment is used, document whether it comes from isolated slabs or local potential analysis

## Analysis Checklist

- verify that the final interface geometry is chemically plausible and not a trapped artificial overlap
- separate interface-specific charge transfer from bulk reference alignment arguments
- record which offset is a direct lineup metric and which remains a proxy
- keep the influence of strain and stoichiometry visible in the final verdict
- state clearly whether the interface is modeled as abrupt, idealized, and defect free

## Frequent Failure Modes

- inferring interface physics from pristine bulk band edges only
- using one arbitrary registry and presenting it as representative
- hiding severe mismatch strain that dominates the final result
- mixing isolated-slab and interface potentials without a consistent alignment logic
- ignoring termination polarity or stoichiometric imbalance at the boundary

## Escalate Or Pair With

- pair with `03-band-structure-and-carrier-transport.md` if the decisive uncertainty is still bulk edge physics
- pair with `08-defect-chemistry-and-trap-states.md` when interface traps or dopants dominate the junction behavior
- pair with `04-optical-and-dielectric-response.md` when optical or dielectric response depends on the lineup
- pair with `14-comsol-coupling-and-property-handoff.md` only after the interface constitutive assumptions are reduced to a stable parameter set

## Deliverables

- bulk, surface, and interface structure packet with registry labels
- interface-energy and alignment table with strain conventions
- charge-transfer and local-potential analysis packet
- explicit note on which parts are ideal-interface results and which real-device effects remain out of scope
