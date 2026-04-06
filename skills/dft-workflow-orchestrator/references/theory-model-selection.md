# Theory Model Selection

Choose the working model before choosing the INCAR.

## Core Rule

The theoretical picture determines the method ladder. Do not let the first runnable calculation become the theory by accident.

## Model Ladder

| Problem class | Working picture | Minimum method | Common escalation | Typical warning sign |
|---|---|---|---|---|
| weakly correlated bulk crystal | band picture, elastic or structural response | PBE or PBEsol relax | hybrid or phonons if gap or lattice dynamics matter | energy trends flip with tiny setup changes |
| correlated oxide or nickelate | charge-transfer or ligand-hole picture, bond disproportionation, magnetic order | DFT+U with branch and spin scan | hybrid, DMFT, larger magnetic cell | one `U` value is doing all the physics |
| proton insertion in oxide | defect thermodynamics plus local bonding and charge redistribution | supercell relax plus insertion-energy scan | multiple sites, concentration series, finite-T sampling | only one insertion site tested |
| surface adsorption | slab thermodynamics plus surface chemistry | clean slab plus adsorption relax | D3(BJ), ab initio thermodynamics, NEB | clean slab reference missing |
| interface-assisted transfer | interface charge redistribution and bond rearrangement | interface relax plus charge analysis | NEB, constrained pathways, larger interface cell | transfer claim based only on isolated bulks |
| migration or reaction barrier | path problem between two relaxed minima | endpoint relaxations plus NEB | better image count, climbing image, alternative path | endpoints not relaxed |
| optical proxy | qualitative dielectric or interband trend | static optics on converged structure | hybrid or GW for quantitative spectra | optics used on unconverged or metallic artifacts |
| finite-temperature phase behavior | entropic competition, lattice dynamics, disorder | static DFT is only baseline support | phonons, AIMD, cluster expansion, DMFT | static zero-K result used as full thermal proof |
| charge localization or polarons | local symmetry breaking and trapped carrier picture | enlarged cell plus spin-polarized relax | hybrid, constrained DFT, non-adiabatic methods | charge stays delocalized because cell is too small |

## Nickelate-Specific Guidance

For rare-earth nickelates, do not collapse the theory to "simple Mott insulator".

Keep active:

- charge-transfer or ligand-hole character
- bond disproportionation or breathing distortion
- magnetic-order approximation
- strain sensitivity
- proton-induced local bond and valence redistribution

This means the minimum defensible packet often includes:

- structural branch scan
- magnetic-order scan
- `U` scan
- local-structure metrics and DOS or PDOS

## Working Questions To Answer

Before launch, answer these explicitly in `workflow/theory_packet.md`:

1. What is the paper's mechanistic claim?
2. What is the simplest model that can test that claim?
3. What physical effect is missing from that model?
4. What result would only count as indirect support, not proof?

## Observable Map

| Observable | What it usually supports | What it does not automatically prove |
|---|---|---|
| total energy | relative stability within the chosen model | experimental phase abundance |
| insertion energy | relative favorability of sites or concentrations | true kinetics or uptake rate |
| DOS or PDOS | qualitative redistribution of states | transport coefficient by itself |
| Bader or charge partition | heuristic charge transfer trend | unique oxidation state |
| optical dielectric function | qualitative absorption or screening trend | exact measured spectrum |
| NEB barrier | path-dependent activation proxy | macroscopic rate in a real film |

## Escalation Rule

If the claim depends on physics beyond static DFT or DFT+U, say so early and keep the escalation path visible:

- hybrid functional
- phonons
- AIMD
- GW or Bethe-Salpeter
- DMFT
- constrained or non-adiabatic methods

Do not hide these behind a polished but overconfident workflow.
