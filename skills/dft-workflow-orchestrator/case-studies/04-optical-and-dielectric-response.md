# Optical And Dielectric Response

## Engineering Intent

Use this case when the main engineering target is dielectric response, optical absorption trends, refractive behavior, or polarization-dependent screening. The goal is to turn a generic request for "optical properties" into a workflow that distinguishes static dielectric constants, independent-particle spectra, and the higher-level physics that DFT may not capture directly.

Do not use this case to make excitonic or device-quantum-efficiency claims unless the required many-body or experimental calibration layer is included separately.

## Questions This Workflow Must Answer

- Which dielectric quantity is actually needed: static electronic, ionic contribution, or frequency-dependent response?
- Are the key transitions polarization dependent or nearly isotropic?
- Is semilocal DFT sufficient for the intended trend, or will band-gap error dominate the interpretation?
- Which outputs are direct calculations and which are post-processed or corrected proxies?

## Theory And Modeling Boundary

- DFT can provide static dielectric tensors, independent-particle optical response, and electronic-structure context for major transitions.
- Ionic and electronic contributions must be distinguished explicitly when both are relevant.
- Independent-particle spectra from plain DFT do not automatically include excitonic effects, strong electron-hole interaction, or realistic finite-temperature broadening.
- If the application depends on an absolute onset energy, document whether a hybrid functional, scissor correction, or beyond-DFT method is required.

## Minimum Inputs Before Launch

- the decisive property: static dielectric constant, anisotropic tensor, absorption onset, refractive trend, or energy-loss proxy
- crystal symmetry, polarization directions of interest, and whether the material is metallic or insulating
- whether phonon or ionic polarization contributions are needed
- whether the user wants trend screening, semi-quantitative comparison, or publication-level spectral interpretation
- whether SOC, magnetism, or strong correlation is expected to reshape the near-gap states

## Structure Strategy

- start from a well-relaxed bulk cell with the correct structural phase
- use a static, well-converged electronic density before response calculations
- if anisotropy matters, keep the crystallographic orientation explicit in the workflow packet
- separate pristine, strained, doped, and defected variants into their own response branches
- for metallic systems, confirm that the requested optical observable is meaningful under the chosen smearing and intraband treatment

## Recommended Job Ladder

1. bulk relaxation and static refinement with converged ENCUT and k-mesh
2. dielectric-tensor workflow, electronic only or electronic plus ionic as required
3. optical response calculation with sufficient empty bands and documented broadening
4. DOS and band analysis to assign the transitions that dominate the decisive spectral range
5. optional sensitivity reruns with SOC, `+U`, hybrid, strain, or symmetry-broken variants

## Primary Outputs And Decisions

- dielectric tensor components and the convention used to report them
- optical absorption or dielectric-function trend in the energy window relevant to the user
- directional anisotropy or polarization selection rule proxy
- mapping between the main spectral features and the underlying band transitions
- recommendation on whether the present DFT level is suitable for trend screening only or for stronger quantitative claims

## Controls And Sensitivity Axes

- check convergence with respect to empty bands, k-mesh density, and smearing
- keep the broadening width documented because it can reshape the apparent onset
- separate static dielectric, optical dielectric, and ionic contributions instead of merging them
- test whether the decisive spectral features shift under a better gap treatment
- if comparing strained or ferroelectric states, keep cell shape and polarization state explicit

## Analysis Checklist

- verify the system is insulating if a conventional dielectric interpretation is being used
- identify whether the requested quantity is tensorial and direction dependent
- relate the main peaks or onsets to specific band-edge transitions or orbital characters
- state clearly whether the reported onset is raw DFT, corrected, or qualitative only
- keep the link between structure phase and optical response visible in the final summary

## Frequent Failure Modes

- presenting a raw semilocal absorption onset as though it were a final experimental prediction
- mixing ionic and electronic dielectric contributions without stating the distinction
- using too few empty bands and then interpreting artificial spectral truncation
- comparing spectra produced with different broadening or smearing settings as if they were commensurate
- ignoring SOC or magnetic order in systems where the near-gap states depend on them

## Escalate Or Pair With

- pair with `03-band-structure-and-carrier-transport.md` when band-edge physics needs a separate focused treatment
- pair with `06-ferroelectric-polarization-and-switching.md` if polarization state controls the dielectric response
- pair with `14-comsol-coupling-and-property-handoff.md` when the goal is a tensor handoff to a continuum solver
- pair with `16-phonon-and-thermal-transport.md` if vibrational contributions or instability change the usable phase

## Deliverables

- converged dielectric and optical job set with orientation notes
- table separating raw DFT outputs from derived or corrected observables
- spectral interpretation note tied to band and DOS features
- explicit warning for any missing excitonic, many-body, or finite-temperature physics
