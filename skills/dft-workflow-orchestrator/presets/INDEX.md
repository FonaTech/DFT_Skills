# Structure Preset Library

These preset manifests are portable engineering templates for `scripts/fetch_structures.py`.
They bootstrap structure intake for a workflow family without hardcoding any specific material system.

## How To Use

List the available presets:

```bash
python3 scripts/fetch_structures.py --list-presets
```

Write a project-local template from a preset:

```bash
python3 scripts/fetch_structures.py \
  --project-root ../your-project \
  --preset catalytic-surface-screening
```

If the preset still contains placeholders such as `{{surface_source}}`, the script writes a template into
`workflow/structure_manifest.<preset>.json` and exits cleanly.

After filling the template, run the manifest directly:

```bash
python3 scripts/fetch_structures.py \
  --project-root ../your-project \
  --manifest ../your-project/workflow/structure_manifest.catalytic-surface-screening.json
```

You can also export a template explicitly:

```bash
python3 scripts/fetch_structures.py \
  --project-root ../your-project \
  --preset bulk-property-bootstrap \
  --write-template ../your-project/workflow/structure_manifest.bulk.json
```

## Source Rules

- Set each `source` to one of `file`, `mp`, `cod`, or `url`.
- Use uploaded or local structure files first when they are available.
- Keep all manifest paths relative to the project when possible.
- Treat these presets as starting points and edit slab thickness, vacuum, supercell size, and normalization as needed.

## Presets

- [bulk-property-bootstrap.json](bulk-property-bootstrap.json): one bulk reference cell for relax, DOS, PDOS, dielectric, or validation work.
- [catalytic-surface-screening.json](catalytic-surface-screening.json): one parent bulk plus a clean slab seed for adsorption or dissociation studies.
- [electrocatalysis-surface-ladder.json](electrocatalysis-surface-ladder.json): slab-oriented intake tuned for charged-interface and potential-dependent screening.
- [reaction-pathway-surface-bootstrap.json](reaction-pathway-surface-bootstrap.json): catalyst slab plus gas or molecular seed for surface reaction mapping.
- [band-transport-bulk.json](band-transport-bulk.json): primitive-cell intake for band dispersion and carrier-transport workflows.
- [optics-dielectric-bulk.json](optics-dielectric-bulk.json): bulk structure intake for dielectric tensor and optical spectra calculations.
- [elastic-mechanics-bulk.json](elastic-mechanics-bulk.json): bulk reference for elastic tensor, stress-strain, and mechanical stability studies.
- [ferroelectric-polarization-bootstrap.json](ferroelectric-polarization-bootstrap.json): paired polar and non-polar references for polarization analysis.
- [heterointerface-alignment-bootstrap.json](heterointerface-alignment-bootstrap.json): film and substrate constituents with slab seeds for interface construction.
- [defect-supercell-screening.json](defect-supercell-screening.json): pristine bulk plus a reusable supercell seed for vacancy or substitution studies.
- [migration-neb-bootstrap.json](migration-neb-bootstrap.json): migration host plus supercell seed for NEB endpoint preparation.
- [aimd-stability-seed.json](aimd-stability-seed.json): bulk plus moderate supercell seed for ab initio molecular dynamics.
- [plasma-surface-proxy.json](plasma-surface-proxy.json): surface parent and feedstock intake for plasma-surface proxy calculations.
- [lammps-mlff-handoff.json](lammps-mlff-handoff.json): structure intake for DFT-to-MLFF or LAMMPS handoff preparation.
- [comsol-property-handoff.json](comsol-property-handoff.json): bulk reference for property extraction to continuum or multiphysics models.
- [phonon-thermal-transport.json](phonon-thermal-transport.json): bulk plus supercell seed for phonons and thermal transport.
- [oxide-protonation-supercell.json](oxide-protonation-supercell.json): oxide supercell plus protonated seed for insertion or local-bonding studies.
