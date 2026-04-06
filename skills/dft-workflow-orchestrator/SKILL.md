---
name: dft-workflow-orchestrator
aliases:
  - dft
  - vasp
  - ab-initio
  - first-principles
  - materials-dft
keywords:
  - dft
  - vasp
  - density functional theory
  - first principles
  - ab initio
  - materials simulation
  - computational physics
  - cif
  - poscar
  - adsorption
  - defect
  - migration barrier
  - band structure
  - optical dielectric
  - aimd
  - phonon
  - lammps coupling
  - comsol coupling
runtime_compat:
  - clouds_coder.py
  - codex
  - claude-code
  - opencode
triggers:
  - DFT
  - VASP
  - density functional theory
  - first-principles
  - ab initio
  - CIF
  - POSCAR
  - slab
  - interface
  - adsorption
  - defect
  - migration
  - NEB
  - DOS
  - PDOS
  - Bader
  - band structure
  - optical property
  - dielectric
  - ferroelectric
  - polarization
  - AIMD
  - phonon
  - thermal transport
  - piezoelectric
  - LAMMPS
  - COMSOL
  - 计算物理
  - 第一性原理
  - 密度泛函
  - 结构下载
  - 掺氢
  - 过渡态
  - 能带
  - 光学
  - 介电
  - 缺陷
  - 迁移势垒
  - 分子动力学
  - 声子
  - 热输运
  - 压电
description: >
  Portable DFT and VASP workflow skill for literature-grounded materials simulation.
  Use this skill whenever the user asks about DFT, VASP, density functional theory,
  first-principles or ab initio modeling, 第一性原理, structure download, CIF/POSCAR
  generation, DFT+U, magnetic order, slabs, interfaces, adsorption, defects, NEB,
  DOS, PDOS, Bader analysis, optical properties, or wants to convert a paper claim
  or experimental mechanism into a reproducible computational workflow across
  Clouds_Coder, Codex, Claude Code, or OpenCode.
license: MIT
compatibility: >
  Agent Skills compatible. Best with shell and file tools. Optional acceleration:
  local VASP plus pseudopotentials, pymatgen, ase, mp_api, fitz, and RAG retrieval
  on platforms that expose it.
metadata:
  category: materials-simulation
  domain: materials-simulation
  engine: vasp
  workflow: literature-to-runs
  portability: cross-platform
  keywords:
    - density functional theory
    - vasp workflow
    - structure acquisition
    - adsorption and catalysis
    - defect chemistry
    - migration barrier
    - band structure
    - optical dielectric response
    - aimd monitoring
    - phonon thermal transport
attachments:
  - references/*.md
  - case-studies/*.md
  - presets/*.md
  - presets/*.json
  - scripts/*.py
  - scripts/*.sh
  - agents/*.yaml
clouds_coder:
  aliases:
    - density-functional-theory
    - first-principles-workflow
    - computational-physics-dft
  triggers:
    - catalytic adsorption
    - electrocatalysis
    - optical response
    - defect chemistry
    - trap state
    - ab initio molecular dynamics
    - plasma reaction
    - lammps handoff
    - comsol handoff
  preferred_tools:
    - query_knowledge_library
    - load_skill
    - bash
    - read_file
    - write_file
    - TodoWrite
  entrypoints:
    - references/literature-to-dft-outline.md
    - references/knowledge-grounding-protocol.md
    - references/theory-model-selection.md
    - references/dft-task-router.md
    - references/live-run-monitoring.md
    - references/vasp-methodology.md
    - references/project-layout.md
    - references/platform-interop.md
    - case-studies/INDEX.md
    - presets/INDEX.md
    - scripts/preflight_dft_env.py
    - scripts/fetch_structures.py
    - scripts/scaffold_dft_project.py
    - scripts/render_vasp_job.py
    - scripts/monitor_vasp_runs.py
    - scripts/summarize_vasp_runs.py
    - scripts/run_one_vasp_job.sh
    - scripts/run_vasp_queue.sh
    - scripts/clone_job_with_d3.sh
    - scripts/sync_skill_to_platforms.py
  runtime_contract: |
    1. Probe the runtime and workspace before promising calculations.
    2. On Clouds_Coder.py, ground theory in this exact order: uploaded or local source files, local RAG, online search, then model knowledge as the final fallback.
    3. On platforms other than Clouds_Coder.py, ground theory in this exact order: uploaded or local source files, online search if available, then model knowledge as the fallback.
    4. Stop the collection chain as soon as the current information tier is sufficient to justify model selection and experiment routing.
    5. Convert the user's request or paper into explicit claims, controls, observables, and method limits.
    6. Acquire or normalize structures before generating jobs, and always write provenance.
    7. Keep the planning authority inside workflow/*.md and workflow/*.csv before launch.
    8. For correlated, magnetic, or strongly method-sensitive systems, scan at least one sensitivity axis instead of assuming plain GGA is enough.
    9. When jobs run in the background, keep a live monitoring loop active via queue logs, runtime files, and analysis/live_status.* outputs.
    10. Never fabricate POTCAR, API keys, Materials Project access, or convergence evidence.
entrypoints:
  - references/literature-to-dft-outline.md
  - references/knowledge-grounding-protocol.md
  - references/theory-model-selection.md
  - references/dft-task-router.md
  - references/live-run-monitoring.md
  - references/vasp-methodology.md
  - references/project-layout.md
  - references/platform-interop.md
  - case-studies/INDEX.md
  - presets/INDEX.md
  - scripts/preflight_dft_env.py
  - scripts/fetch_structures.py
  - scripts/scaffold_dft_project.py
  - scripts/render_vasp_job.py
  - scripts/monitor_vasp_runs.py
  - scripts/summarize_vasp_runs.py
  - scripts/run_one_vasp_job.sh
  - scripts/run_vasp_queue.sh
  - scripts/clone_job_with_d3.sh
  - scripts/sync_skill_to_platforms.py
---

# DFT Workflow Orchestrator

Turn a scientific question into a reproducible DFT workspace. Do not stop at vague advice if the environment can support actual scaffolding.

## Use This Skill For

- literature-to-calculation planning
- VASP project bootstrapping
- structure retrieval or normalization
- correlated oxides, magnetic materials, and DFT+U decisions
- slabs, interfaces, adsorption, defects, migration, DOS, optics, and charge analysis
- background-run monitoring, convergence triage, and queue-state interpretation
- project packets that need explicit claims, controls, and method boundaries

## Do Not Use This Skill For

- chemistry trivia or one-line definitions
- pretending static DFT proves finite-temperature kinetics or growth dynamics
- fabricating `POTCAR`, API keys, Materials Project access, or convergence evidence

## Runtime Contract

Always follow this order:

1. Preflight the environment before promising calculations.
2. Build a knowledge packet and theory packet before detailed experiment routing.
3. On Clouds_Coder.py, ground theory in this exact order: uploaded or local source files, local RAG, online search, then model knowledge as the final fallback.
4. On platforms other than Clouds_Coder.py, use uploaded or local source files first, then online search if available, then model knowledge as the fallback.
5. Stop the collection chain as soon as the current information tier is sufficient to justify theory selection and experiment routing.
6. Translate the user request or paper into a claim matrix.
7. Acquire or normalize structures before job creation.
8. Write the workflow packet before launching runs.
9. Materialize only defensible jobs.
10. Keep a front-end monitoring loop active while jobs run in the background.
11. Summarize outcomes with explicit method limits.
12. Keep all generated calculation outputs in a user project root, not inside the skill directory itself.

## Clouds_Coder Native Loading

This skill is intentionally structured for `Clouds_Coder.py` lazy loading.

When `load_skill('dft-workflow-orchestrator')` is called in a Clouds session, the runtime should treat this file as a gateway and the entrypoints as the authoritative low-cost resource map.

Use this read pattern instead of bulk-reading the whole bundle:

1. for theory intake and source hierarchy, read `references/literature-to-dft-outline.md` and `references/knowledge-grounding-protocol.md`
2. for workflow routing, read `references/dft-task-router.md` and then only one case from `case-studies/`
3. for structure intake, read `presets/INDEX.md` and `scripts/fetch_structures.py`
4. for method settings, read `references/vasp-methodology.md`
5. for active jobs, read `references/live-run-monitoring.md` and `scripts/monitor_vasp_runs.py`
6. only open the full `case-studies/` or `presets/` tree when the current task truly expands into that branch

Clouds-specific discovery and install routes that stay aligned with the loader:

- direct skills-root mode: point the active `skills_root` at `DFT_Skills/skills`
- external-library mode: keep `DFT_Skills` adjacent to the active `skills/` directory so `Clouds_Coder.py` can auto-discover `skills/*/SKILL.md`
- project-local native mode: mirror the skill into `skills/generated/dft-workflow-orchestrator/` with `scripts/sync_skill_to_platforms.py --targets clouds`

Boundary rules for native Clouds use:

- keep the skill bundle read-only during normal execution
- keep generated workflow packets, structures, runs, logs, and analysis outside the skill bundle
- prefer `query_knowledge_library` only after uploaded or local materials have been checked
- treat `case-studies/INDEX.md`, `presets/INDEX.md`, and the runtime contract as the first on-demand control plane, not as files to bypass

## Phase 0: Preflight

From the skill root, run:

```bash
python3 scripts/preflight_dft_env.py --workspace ../your-project --pretty
```

Check:

- `vasp_std`, `vasp_gam`, `mpirun`, `pdftotext`, and Python availability
- pseudopotential roots and Materials Project API keys
- Python packages: `pymatgen`, `ase`, `mp_api`, `numpy`, `scipy`, `fitz`
- whether literature PDFs and local structure files already exist

If prerequisites are missing, downgrade to planning or partial scaffolding instead of bluffing.

## Phase 1: Knowledge Grounding and Theory Intake

Use [references/literature-to-dft-outline.md](references/literature-to-dft-outline.md),
[references/knowledge-grounding-protocol.md](references/knowledge-grounding-protocol.md), and
[references/theory-model-selection.md](references/theory-model-selection.md).

Build three layers:

1. User objective: target system, observable, and required rigor.
2. Literature claim set: what the paper actually claims, what is merely interpretation, and what controls exist.
3. Source-grounding stack: select sources in platform order and stop escalating as soon as the current tier is sufficient.

Platform-specific grounding rule:

- On `Clouds_Coder.py`, use this exact order: uploaded or local project files, then local `query_knowledge_library` retrieval, then online or web literature search, then model knowledge as the final fallback.
- On other platforms, use uploaded or local project files first, then online or web retrieval if available, then model knowledge as the fallback.
- If the current source tier already resolves the theory basis, method choice, and control design, do not continue to the next tier just to accumulate citations.

When the theory model is unclear or obscure, explicitly write:

- candidate mechanism families
- candidate theoretical models
- why the current DFT level is sufficient or insufficient
- what higher-level method would be needed if the present result is only indirect support

Separate every statement into:

- directly supported by source or input files
- DFT-testable hypothesis
- non-DFT claim that must remain qualified

## Phase 2: Claim Routing

Use [references/dft-task-router.md](references/dft-task-router.md).

If the request matches a standard engineering workflow, open [case-studies/INDEX.md](case-studies/INDEX.md) and load only the single most relevant case file instead of reading the full case library.

Minimum required workflow files:

- `workflow/request_summary.md`
- `workflow/knowledge_sources.md`
- `workflow/theory_packet.md`
- `workflow/claim_matrix.md`
- `workflow/experiment_matrix.csv`
- `workflow/method_guardrails.md`

Every claim must map to:

- a model system
- a job family
- a primary observable
- a control or reference
- a method risk
- a pass condition

## Phase 3: Structure Acquisition

Use the bundled structure script:

```bash
python3 scripts/fetch_structures.py --help
```

List the bundled engineering presets with:

```bash
python3 scripts/fetch_structures.py --list-presets
```

Preset templates live in [presets/INDEX.md](presets/INDEX.md). If a preset still contains unresolved placeholders, the script writes a project-local template into `workflow/structure_manifest.<preset>.json` and exits so the user can fill the remaining fields before any structure download happens.

Preferred order:

1. user-provided `CIF`, `POSCAR`, `CONTCAR`, or curated structure folder
2. Materials Project when API access exists
3. COD or direct public URLs
4. documented reconstruction from literature cell data

Always record provenance in `structures/provenance.json`.

## Phase 4: Method Selection

Use [references/vasp-methodology.md](references/vasp-methodology.md).

Decide explicitly:

- functional
- whether `+U` is required
- magnetic order and spin treatment
- slab thickness, vacuum, and dipole correction when relevant
- dispersion treatment for weak binding
- convergence targets for `ENCUT`, k-mesh, and force criteria

Never summarize this phase as "standard VASP settings".

## Phase 5: Project Scaffolding

Create the reproducible project packet:

```bash
python3 scripts/scaffold_dft_project.py \
  --project-root ../your-project \
  --system-name "Material System" \
  --claim "Claim one" \
  --task bulk-relax \
  --task dos
```

The scaffold creates the contract described in [references/project-layout.md](references/project-layout.md) and copies execution helpers into the project `scripts/` directory.

Boundary rule:

- use the skill directory as read-only knowledge and tooling
- use the project root as the only place for generated workflow files, structures, runs, logs, and analysis outputs

## Phase 6: Job Materialization

Render job folders with:

```bash
python3 scripts/render_vasp_job.py \
  --structure <structure-file> \
  --job-dir <job-dir> \
  --preset correlated-relax \
  --system "Example system" \
  --species-order Sm Ni O \
  --u-element Ni \
  --u-value 2.0 \
  --afm-element Ni
```

Use only after the structure and method choices are already justified.

Do not start a run until the job directory contains real:

- `INCAR`
- `KPOINTS`
- `POSCAR`
- `POTCAR`

If `POTCAR` cannot be resolved from the local pseudopotential root, stop and report it.

## Phase 7: Execution

Use the bundled project-safe runners:

- `run_one_vasp_job.sh`
- `run_vasp_queue.sh`
- `clone_job_with_d3.sh`

Typical examples:

```bash
cd your-project
zsh scripts/run_one_vasp_job.sh runs/00_bulk/example_relax 8
```

```bash
cd your-project
zsh scripts/run_vasp_queue.sh joblists/bootstrap.txt 8
```

If the front-end must stay interactive while jobs run, launch the queue in the background and keep monitoring active:

```bash
cd your-project
nohup zsh scripts/run_vasp_queue.sh joblists/bootstrap.txt 8 \
  > logs/bootstrap/launcher.out 2>&1 &
```

## Phase 8: Live Monitoring and Course Correction

Use [references/live-run-monitoring.md](references/live-run-monitoring.md).

While jobs are active, run:

```bash
cd your-project
python3 scripts/monitor_vasp_runs.py \
  --project-root . \
  --interval-seconds 120 \
  --iterations 0 \
  --pretty
```

This keeps these front-end artifacts fresh:

- `analysis/live_status.csv`
- `analysis/live_status.json`
- `analysis/queue_status.json`
- `analysis/live_monitor_report.md`

On each cycle:

- compare converged jobs against `workflow/experiment_matrix.csv`
- decide whether the next queued jobs still cover the required controls and sensitivity axes
- stop queue expansion if a stale or failed job suggests a method problem
- for correlated systems, never treat one converged bootstrap job as the whole physics packet

## Phase 9: Analysis and Verdict

Use:

```bash
cd your-project
python3 scripts/summarize_vasp_runs.py --project-root .
```

Minimum deliverables:

- `analysis/energy_summary.csv`
- `analysis/run_status.csv`
- `analysis/claim_verdicts.md`
- `analysis/open_questions.md`

Every conclusion must include:

- which relaxed structure supports it
- which method settings produced it
- which control calculation it was compared against
- which uncertainty remains

## Platform Router

See [references/platform-interop.md](references/platform-interop.md).

Short version:

- Clouds_Coder: prefer `query_knowledge_library` or `load_skill` if available, otherwise use local files plus the bundled scripts.
- Claude Code: install under `.claude/skills/<name>/` or `~/.claude/skills/<name>/`.
- OpenCode: install under `.opencode/skills/<name>/`, `~/.config/opencode/skills/<name>/`, or Claude/Agent-compatible paths.
- Codex: use the Agent Skills package plus `agents/openai.yaml`; the installer supports both `~/.codex/skills/<name>/` and `~/.agents/skills/<name>/` targets.

## Quality Gates

- Always document structure provenance.
- Always write the claim matrix before production runs.
- Keep `analysis/live_monitor_report.md` current while background jobs are active.
- For correlated or magnetic systems, scan at least one sensitivity axis instead of pretending one setup is universal.
- For adsorption, defects, NEB, work functions, or optics, make the reference state explicit.
- Keep method limits visible. Plain DFT or DFT+U cannot prove every experimental mechanism.
- If the platform exposes a RAG interface and it returns nothing useful, say so and continue with local files and literature.
