# DFT Task Router

Map each scientific claim to the smallest DFT packet that can actually test it.

## Core Rules

- One claim, one primary observable.
- One production claim must have at least one control or reference.
- If a claim needs structure, magnetism, and chemistry sensitivity, split those axes instead of hiding them in one job.

## Claim Routing Table

| Claim type | Minimum calculation family | Typical controls | Main outputs | Common failure mode |
|---|---|---|---|---|
| bulk phase stability | bulk relax plus static energy | polymorphs, competing oxides, alternate cell branch | total energy, volume, relaxed cell | comparing unconverged cells |
| strain response or epitaxy | constrained-cell relax series | unstrained bulk, alternate branch | stress, lattice trend, bond lengths | mixing strained and unstrained settings |
| correlated-insulator trend | `DFT+U` branch and spin scan | `U=0`, alternate `U`, alternate magnetic order | gap trend, local moments, bond disproportionation | treating one `U` value as universal truth |
| H insertion or intercalation | supercell defect or interstitial relax | pristine bulk, multiple sites, concentration series | insertion energy, site preference, local structure | ignoring supercell concentration |
| adsorption strength | slab plus adsorbate relax | clean slab, gas-phase adsorbate, alternate adsorption site | adsorption energy, binding geometry | skipping clean-slab reference |
| surface work function | slab static with vacuum analysis | clean vs modified slab | vacuum level, Fermi level, work function | asymmetric slab without dipole handling |
| interface charge transfer | interface relax plus charge analysis | separated slabs or bulks | interface energy, charge transfer, projected DOS | unrelaxed interface geometry |
| catalytic dissociation | adsorption intermediates plus TS or NEB | initial molecular state, final dissociated state | reaction energy, barrier | endpoints not fully relaxed |
| diffusion or proton transfer | endpoint relaxations plus NEB | both end states | migration barrier, image energies | running NEB before endpoint cleanup |
| defect formation | defect supercell relax | pristine cell, chemical-potential references | formation energy, local distortion | undefined chemical potentials |
| electronic reconstruction | static DOS, PDOS, charge analysis | pristine, doped, strained, or interface reference | DOS, PDOS, charge partition | DOS on unrelaxed structures |
| optical response | optics static on converged structure | reference phase or composition | dielectric function, absorption proxy | claiming quantitative optics from loose settings |

## Required Columns For `workflow/experiment_matrix.csv`

1. `claim_id`
2. `claim_text`
3. `claim_class`
4. `model_system`
5. `job_family`
6. `primary_observable`
7. `reference_or_control`
8. `sensitivity_axis`
9. `method_risk`
10. `pass_condition`
11. `notes`

## Quick Heuristics

### Bulk systems

- Relax before DOS, optics, or Bader analysis.
- Do not compare energies from mismatched pseudopotentials or cutoffs.

### Surfaces and interfaces

- Relax the clean slab first.
- State Miller index, termination, slab thickness, and vacuum explicitly.
- State whether dispersion is included and why.

### Defects and dopants

- Compare more than one candidate site whenever chemistry permits.
- Record the concentration implied by the chosen supercell.
- Keep chemical potentials explicit if formation energies are discussed.

### Correlated materials

- Split structure branch, `U`, and magnetic order into separate axes.
- Treat plain GGA or PBEsol as a baseline, not the final word.

## What Not To Do

- Do not say "DFT proves the experiment" without controls.
- Do not use one structure and one `U` value for a strongly correlated oxide.
- Do not present DOS, PDOS, or Bader results without stating which relaxed structure produced them.
