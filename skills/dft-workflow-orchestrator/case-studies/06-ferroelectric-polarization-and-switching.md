# Ferroelectric Polarization And Switching

## Engineering Intent

Use this case when the user needs spontaneous polarization, branch comparison, polar versus non-polar phase contrast, or a switching proxy tied to structural distortion. The objective is to map the polarization problem into a reproducible reference-state workflow rather than to treat one polar relaxation as self-evident proof.

Do not use this case alone to claim experimental coercive field, realistic domain-wall kinetics, or full switching dynamics.

## Questions This Workflow Must Answer

- Is the target phase polar relative to a justified centrosymmetric or non-polar reference?
- What is the magnitude and direction of the polarization under the chosen convention?
- How sensitive is the result to strain, mode amplitude, magnetic order, or correlation treatment?
- Does the user need a branch comparison, an energy double-well proxy, or just a structural polarization ranking?

## Theory And Modeling Boundary

- DFT can provide relaxed polar and reference structures, Berry-phase polarization, mode amplitudes, and energy differences between branches.
- Berry-phase results are branch dependent and meaningless without a reference path or branch-tracking logic.
- Static DFT does not give full switching kinetics, domain nucleation, or realistic coercive-field values.
- If the engineering claim depends on switching under finite temperature, defects, or domain walls, state that this case provides intrinsic crystal-level information only.

## Minimum Inputs Before Launch

- polar phase and justified non-polar or centrosymmetric reference phase
- crystallographic orientation and whether epitaxial strain is relevant
- whether the user wants polarization magnitude, switching proxy, or strain tuning
- magnetic order, SOC, and `+U` if the polar instability couples to correlated ions
- whether the system is bulk-like, layered, or interface-stabilized

## Structure Strategy

- relax both the polar and reference branches with comparable settings
- document the structural path connecting the branches if Berry-phase branch tracking will be used
- keep lattice constraints explicit, especially for strained or epitaxial variants
- if several polar distortions compete, treat them as separate branches rather than one blended state
- for thin-film or layered cases, record the out-of-plane reference convention and vacuum treatment

## Recommended Job Ladder

1. reference non-polar or centrosymmetric relaxation
2. polar branch relaxation with the same functional and convergence quality
3. static refinement for accurate charge density and Berry-phase evaluation
4. optional interpolation or mode-tracking calculations along the switching coordinate
5. optional strain or field-proxy sensitivity scans on the leading branches

## Primary Outputs And Decisions

- polarization vector and branch convention
- energy difference between reference and polar states
- structural distortion pattern tied to the polarization
- qualitative switching proxy such as a double-well trend or branch-connectivity note
- recommendation on whether a strain, interface, or defect follow-up is needed

## Controls And Sensitivity Axes

- compare at least one justified reference branch rather than using the polar state alone
- keep the cell constraint policy visible; polarization can move dramatically under epitaxial strain
- test whether the decisive result depends on `+U`, SOC, or magnetic order
- distinguish clamped-ion and relaxed-ion contributions when response coefficients are discussed
- if several nearly degenerate distortions exist, do not report one branch as unique without comment

## Analysis Checklist

- verify the chosen reference is symmetry justified and chemically meaningful
- report the polarization direction in a documented crystallographic basis
- track the branch logic so the Berry-phase number is not orphaned from its path
- connect polarization magnitude to the actual structural distortion, not just the final scalar value
- state clearly whether the result is an intrinsic polarization metric or a switching claim

## Frequent Failure Modes

- quoting a Berry-phase value without any reference branch or path
- treating one polar relaxation as proof of practical switchability
- hiding strain constraints that actually generate the polarization
- comparing polarization magnitudes across different cell conventions without normalization care
- ignoring competing non-polar distortions or antipolar branches

## Escalate Or Pair With

- pair with `15-piezoelectric-strain-coupling.md` when strain control is the engineering lever
- pair with `04-optical-and-dielectric-response.md` when dielectric or optical anisotropy follows the polar state
- pair with `07-heterointerface-band-alignment-and-charge-transfer.md` when interface stabilization or polarization discontinuity matters
- pair with `14-comsol-coupling-and-property-handoff.md` after the intrinsic polarization and tensor picture are stable enough for continuum use

## Deliverables

- polar and reference structures with a documented structural path
- Berry-phase or equivalent polarization packet with basis convention
- branch and strain sensitivity note
- explicit boundary statement separating intrinsic polarization from real switching kinetics
