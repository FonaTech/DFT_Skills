# Case Study Index

This folder contains reusable engineering case templates for the DFT workflow skill. Each case is meant to be a working planning packet, not a one-line reminder. Open one case first, extract the relevant workflow logic, and only combine cases when the science question genuinely spans two domains.

## What Each Case Now Provides

Each case file is expected to give:

- the engineering intent and the decision boundary for when that case is the right one
- the theory and modeling boundary, including what plain DFT can support and what must remain qualified
- the minimum information that should be collected before job launch
- a structure-model strategy, not just a property name
- a recommended job ladder so the workflow can be materialized into `workflow/experiment_matrix.csv`
- the primary outputs, controls, sensitivity axes, and analysis checks
- common failure modes, escalation triggers, and cross-case handoff guidance

## How To Use This Folder

1. Match the user's decisive observable, not the most attractive figure type.
2. Open only the single most relevant case file first.
3. Add a second case only if the workflow truly crosses domains, for example interface plus optics, or DFT plus COMSOL handoff.
4. Translate the chosen case into `workflow/request_summary.md`, `workflow/theory_packet.md`, `workflow/claim_matrix.md`, and `workflow/experiment_matrix.csv`.
5. Keep all generated structures, runs, and analysis in the project root rather than inside the skill bundle.

## Routing Table

| Domain | Use when the user asks for | Primary outputs | Case file |
|---|---|---|---|
| Catalysis | adsorption energies, dissociation trends, site competition | adsorption energy, reaction energy, geometry set | `01-catalytic-adsorption-and-dissociation.md` |
| Electrocatalysis | potential-dependent surface chemistry, reaction ladders, overpotential proxies | free-energy ladder, site trend, sensitivity packet | `02-electrocatalysis-and-surface-potential.md` |
| Band engineering | band edges, effective mass, anisotropy, transport proxy | band structure, DOS, band-edge and mass packet | `03-band-structure-and-carrier-transport.md` |
| Optics and dielectric | dielectric constant, optical absorption, refractive response | dielectric tensor, optical trend packet | `04-optical-and-dielectric-response.md` |
| Mechanics | stiffness, modulus, strain response, stability criteria | elastic tensor, modulus and stability packet | `05-elastic-mechanical-stability.md` |
| Polarization | ferroelectricity, Berry phase, switching proxy | polarization branches, mode and strain comparison | `06-ferroelectric-polarization-and-switching.md` |
| Interfaces | band alignment, charge transfer, interface stability | interface-energy and lineup packet | `07-heterointerface-band-alignment-and-charge-transfer.md` |
| Defects | vacancy, substitution, trap states, dopant activation | formation-energy and localization packet | `08-defect-chemistry-and-trap-states.md` |
| Migration | ionic transport, proton hopping, vacancy diffusion | NEB barrier and pathway comparison | `09-ionic-migration-and-neb.md` |
| Chemical reaction | elementary-step screening, pathway ranking, intermediate competition | endpoint ladder, barrier ladder, route comparison | `10-chemical-reaction-pathway-screening.md` |
| AIMD | finite-temperature stability, disorder, rapid reconstruction | trajectory diagnostics and stability packet | `11-ab-initio-molecular-dynamics-stability.md` |
| Plasma | radical impact, plasma-facing reactivity, non-equilibrium surface proxy | adsorption and abstraction proxy set | `12-plasma-surface-reaction-proxy.md` |
| LAMMPS coupling | force-field fitting, MLFF training, larger-scale handoff | training packet, validation packet, safe-domain note | `13-lammps-coupling-and-mlff-handoff.md` |
| COMSOL coupling | device or reactor scale constitutive parameters | property handoff table and validity window | `14-comsol-coupling-and-property-handoff.md` |
| Piezoelectric coupling | strain-electric response, electromechanical tensors | piezo tensor and strain-response packet | `15-piezoelectric-strain-coupling.md` |
| Thermal transport | phonons, dynamical stability, lattice thermal transport | phonon and force-constant packet | `16-phonon-and-thermal-transport.md` |

## Selection Rules

- If the user asks for a mechanism, start from the case tied to the decisive observable, not from the visually richest plot.
- If the user asks for several properties at once, separate the bootstrap case from the downstream cases instead of merging every target into one launch packet.
- If the user asks for continuum, reactor, or long-time behavior, first finish the DFT packet, then open the corresponding handoff or scale-bridging case.
- If one case reveals that the current DFT level is insufficient, record the limit explicitly and stop pretending the case file alone resolves the scientific question.
