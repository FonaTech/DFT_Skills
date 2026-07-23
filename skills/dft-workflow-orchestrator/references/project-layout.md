# Project Layout Contract

The scaffold script assumes this layout:

```text
project/
├── workflow/
│   ├── request_summary.md
│   ├── knowledge_sources.md
│   ├── theory_packet.md
│   ├── claim_matrix.md
│   ├── experiment_matrix.csv
│   ├── method_guardrails.md
│   └── structure_manifest.<preset>.json
├── structures/
│   ├── raw_cif/
│   ├── poscar/
│   ├── slabs/
│   └── provenance.json
├── runs/
│   ├── 00_bulk/
│   ├── 01_surface/
│   ├── 02_adsorption/
│   ├── 03_defects/
│   ├── 04_migration/
│   └── 05_optics/
├── joblists/
├── analysis/
├── logs/
└── scripts/
```

For AIMD, MLIP, MD, FEM, or coupled work, `scaffold_multiscale_project.py` extends the contract:

```text
project/
├── workflow/
│   ├── research_contract.md
│   ├── decision_brief.md
│   ├── research_spine.md
│   ├── decision_log.md
│   ├── claim_matrix.csv
│   ├── experiment_manifest.json
│   ├── branch_register.csv
│   ├── data_lineage.csv
│   ├── next_action_queue.csv
│   ├── handoff_register.csv
│   ├── validation_plan.md
│   └── risk_register.md
├── data/{raw,curated,splits,trajectories,exchange}/
├── models/{checkpoints,cards}/
├── meshes/
├── runs/S##_kind/
├── analysis/S##_kind/
├── structures/{raw,normalized}/
├── logs/
├── joblists/
└── scripts/
```

## Rules

- `workflow/` is the planning authority.
- `workflow/research_spine.md` is the first-read north-star for long or resumed tasks.
- `workflow/branch_register.csv` bounds side branches and records merge or kill decisions.
- `workflow/data_lineage.csv` traces structures, labels, trajectories, datasets, models, meshes, handoffs, and verdicts.
- `workflow/next_action_queue.csv` keeps work aligned with the current gate and information value.
- `workflow/structure_manifest.*.json` is the optional landing zone for preset-derived structure intake templates.
- `structures/` stores source and normalized models.
- `runs/` contains only executable job directories.
- `joblists/` defines queue order and grouping.
- `analysis/` contains machine-readable summaries and verdict drafts.
- `analysis/live_status.csv`, `analysis/live_status.json`, `analysis/queue_status.json`, and `analysis/live_monitor_report.md` are refreshed while jobs are running.
- `logs/` stores queue or batch logs, not scientific conclusions.
- `scripts/` contains copied project-local helpers so later execution does not depend on remembering the original skill path.

## Minimum Files Before Launch

Do not start production calculations until these exist:

- `workflow/request_summary.md`
- `workflow/knowledge_sources.md`
- `workflow/theory_packet.md`
- `workflow/claim_matrix.md`
- `workflow/experiment_matrix.csv`
- `workflow/method_guardrails.md`
- at least one resolved structure under `structures/`

For a multiscale or branching project, also require:

- a confirmed or explicitly design-tier `workflow/decision_brief.md`
- a current `workflow/research_spine.md`
- a non-orphaned `workflow/branch_register.csv`
- a manifest that passes `validate_experiment_manifest.py --strict`
- a `workflow/next_action_queue.csv` entry tied to the active claim and gate
- lineage rows for any artifact consumed by a downstream stage

## Minimum Files Per VASP Job

- `INCAR`
- `KPOINTS`
- `POSCAR`
- `POTCAR`

Recommended after execution:

- `.heartbeat`
- `.status`
- `vasp.out`
- `OUTCAR`
- `CONTCAR`

## Naming Rules

Use names that encode the scientific axis, for example:

- `runs/00_bulk/sno_u2_relax`
- `runs/00_bulk/sno_u4_relax`
- `runs/01_surface/pt111_clean_relax`
- `runs/02_adsorption/h_on_o_top`
- `runs/04_migration/h_transfer_neb`

Avoid opaque names like `test1`, `run-final`, or `new-folder`.
