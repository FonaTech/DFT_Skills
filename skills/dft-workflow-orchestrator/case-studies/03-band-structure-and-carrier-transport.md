# Band Structure And Carrier Transport

## Engineering Intent

Use this case when the user wants band edges, band dispersion, effective masses, or carrier-transport proxies that depend primarily on the bulk electronic structure. This case converts "show me the band structure" into a workflow that is explicit about symmetry, spin treatment, and the limitations of semilocal DFT for transport claims.

Do not present this case as a full mobility prediction unless scattering physics, defect chemistry, and temperature dependence are handled separately.

## Questions This Workflow Must Answer

- What is the qualitative band topology near the relevant band edges?
- Are the decisive states direct or indirect, isotropic or anisotropic, and strongly orbital selective or not?
- Does spin-orbit coupling, magnetic order, or `+U` materially change the edge physics?
- Is the result stable enough to be used for transport proxy comparisons or interface lineup input?

## Theory And Modeling Boundary

- DFT can provide band dispersion, DOS, orbital character, and effective-mass proxies near the band edges.
- Semilocal DFT may misplace absolute band gaps and sometimes reorder edge states. If the claim is gap sensitive, document whether hybrid, meta-GGA, `+U`, or scissor correction is needed.
- A favorable band structure does not by itself prove high mobility. Carrier lifetime, phonon scattering, defects, and microstructure remain outside this case unless explicitly added.
- For magnetic or heavy-element systems, SOC and spin order are not optional details. They can redefine the whole answer.

## Minimum Inputs Before Launch

- whether the engineering target is band gap, carrier anisotropy, effective mass, or qualitative edge composition
- magnetic order, correlated elements, and whether SOC is expected to matter
- the required cell choice: primitive for band path, conventional for reporting, or both
- whether the user needs absolute alignment to vacuum, an interface, or only relative dispersion
- whether transport conclusions are only qualitative or intended for later Boltzmann or device-level workflows

## Structure Strategy

- begin from a fully relaxed bulk cell with the final magnetic and structural order
- use the primitive cell for the band-path workflow unless another convention is justified
- if polymorphs or strain states are being compared, keep the structural lineage and normalization explicit
- prepare a static high-quality charge density before final band and DOS runs
- keep any defected or doped variants separate from the pristine reference rather than blending them into one narrative

## Recommended Job Ladder

1. bulk relaxation with the intended magnetic and correlation settings
2. static self-consistent run with tighter electronic settings and a converged k-mesh
3. high-symmetry band-path calculation using the same underlying method
4. DOS or PDOS run for orbital attribution near the decisive edges
5. optional SOC, `+U`, hybrid, or strain sensitivity reruns on the leading candidate systems

## Primary Outputs And Decisions

- band structure referenced to the documented Fermi or valence-band maximum convention
- DOS and PDOS near the transport-relevant edges
- effective-mass or curvature proxies along the decisive directions
- statement on whether edge physics is dominated by one sublattice, orbital family, or spin channel
- explicit note on whether the present level is sufficient for the user's transport claim

## Controls And Sensitivity Axes

- compare at least one methodological axis when the system is correlated, magnetic, or heavy-element dominated
- test k-path and k-mesh convergence separately; they are not the same issue
- keep smearing small enough that edge-state interpretation remains meaningful
- track whether structural strain or internal distortion changes the band ordering
- if absolute alignment matters, add a slab or interface workflow instead of inferring it from bulk alone

## Analysis Checklist

- verify the relaxed structure and magnetic state match the one used for the final band run
- identify the actual band-edge k-points and whether the gap is direct or indirect
- annotate the orbital character of the decisive valence and conduction states
- report effective-mass trends only in the directions actually analyzed
- separate a robust qualitative trend from any quantitative gap number that is method sensitive

## Frequent Failure Modes

- showing one band plot without documenting spin order, SOC, or `+U`
- treating DOS broadening artifacts as real edge features
- inferring absolute transport performance from dispersion alone
- using a non-converged structure or inconsistent static setup for the final band run
- comparing strained, doped, and pristine systems without a clear reference convention

## Escalate Or Pair With

- pair with `07-heterointerface-band-alignment-and-charge-transfer.md` when lineup or contact physics is the real target
- pair with `08-defect-chemistry-and-trap-states.md` if carrier trapping or dopant compensation dominates the transport claim
- pair with `04-optical-and-dielectric-response.md` when the same edge physics feeds optical transitions
- pair with `14-comsol-coupling-and-property-handoff.md` only after the band-level outputs are converted into clearly defined continuum parameters

## Deliverables

- pristine bulk reference structure and static-charge-density job
- band, DOS, and orbital-character packet with documented method choices
- effective-mass or anisotropy note with directional conventions
- explicit limit statement on what transport claims remain outside the present workflow
