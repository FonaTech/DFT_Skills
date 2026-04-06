# Piezoelectric Strain Coupling

## Engineering Intent

Use this case when the user needs piezoelectric response, electromechanical coupling, or strain-controlled polarization change. The aim is to connect structure, symmetry, elastic response, and polarization into a tensor-level workflow instead of treating one strained calculation as a piezoelectric result.

Do not use this case for nonlinear device actuation, domain-wall motion, or extrinsic composite effects unless those are modeled separately.

## Questions This Workflow Must Answer

- Is the phase symmetry compatible with a nonzero piezoelectric response?
- Which tensor components are relevant for the intended loading and measurement geometry?
- How strongly does strain couple to polarization or internal distortion?
- Are clamped-ion and relaxed-ion responses both needed for the engineering question?

## Theory And Modeling Boundary

- DFT can provide piezoelectric tensors through finite differences or perturbative methods, along with related elastic and dielectric context.
- Symmetry, structural phase, and strain convention determine which tensor components can be nonzero.
- Intrinsic piezoelectric tensors do not include domain motion, microcracking, porosity, or device-level electromechanical amplification.
- If the engineering claim depends on large-field switching or extrinsic mechanisms, this case is only the intrinsic baseline.

## Minimum Inputs Before Launch

- the loading direction, electrical direction, and coordinate convention required by the user
- whether the goal is tensor extraction, comparative strain trend, or constitutive handoff
- structural phase and whether it is already polar or only strain induced
- whether clamped-ion versus relaxed-ion contributions matter
- any expected coupling to magnetism, correlation, or epitaxial constraints

## Structure Strategy

- start from a well-relaxed phase with symmetry consistent with the targeted response
- document the crystallographic basis used for tensor reporting
- if strain engineering is part of the question, prepare a small family of strained states rather than one arbitrary distortion
- keep the polarization reference and elastic response tied to the same structural branch
- for layered or thin-film-like systems, make vacuum and effective thickness conventions explicit

## Recommended Job Ladder

1. relaxed reference structure with confirmed symmetry
2. static refinement for charge density and stress quality
3. piezoelectric response calculation by finite difference or perturbative method
4. optional elastic and dielectric companion calculations if the full electromechanical packet is required
5. strain-family reruns if the user asks how coupling evolves under epitaxial or mechanical constraint

## Primary Outputs And Decisions

- piezoelectric tensor in the documented basis
- relation between strain, polarization change, and internal structural distortion
- distinction between clamped-ion and relaxed-ion response where applicable
- recommendation on which tensor components matter for the engineering geometry
- decision on whether the intrinsic tensor is ready for continuum handoff or still too sensitive

## Controls And Sensitivity Axes

- verify the symmetry really permits the reported tensor components
- keep strain amplitude small and consistent if finite differences are used
- test whether the decisive tensor components depend strongly on the structural phase or strain state
- track the interplay with elastic softness and dielectric response instead of reporting the piezo tensor in isolation
- if low-dimensional normalization is used, document the effective thickness convention explicitly

## Analysis Checklist

- report tensor components in a clearly named coordinate frame
- identify whether the response is dominated by ionic relaxation, electronic response, or both
- connect the largest tensor components to the underlying structural motif or polar mode
- separate intrinsic response from any device or microstructure amplification
- state clearly whether the result is a zero-field intrinsic tensor or part of a larger switching narrative

## Frequent Failure Modes

- reporting nonzero components forbidden by the actual symmetry
- mixing coordinate conventions between different strained states
- hiding the difference between clamped-ion and relaxed-ion response
- treating one strained polarization calculation as a full piezoelectric tensor
- applying bulk normalization to layered systems with no thickness caveat

## Escalate Or Pair With

- pair with `06-ferroelectric-polarization-and-switching.md` when the response is tied to polar branch changes
- pair with `05-elastic-mechanical-stability.md` when elastic softness or anisotropy controls the response
- pair with `14-comsol-coupling-and-property-handoff.md` when the tensor will be exported to a continuum solver
- pair with `04-optical-and-dielectric-response.md` if electromechanical and dielectric anisotropy are being co-analyzed

## Deliverables

- symmetry-checked piezoelectric tensor packet
- strain-response note with coordinate conventions
- clamped-ion versus relaxed-ion interpretation note
- explicit boundary statement distinguishing intrinsic electromechanical response from device-level behavior
