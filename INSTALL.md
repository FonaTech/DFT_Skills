# Installing DFT Skills For Clouds_Coder

This repository is optimized first for the [FonaTech/Clouds-Coder](https://github.com/FonaTech/Clouds-Coder) ecosystem and specifically for the loading behavior of `Clouds_Coder`, while remaining portable to Codex, Claude Code, and OpenCode.

GitHub quick link:

- Clouds-Coder repository: [FonaTech/Clouds-Coder](https://github.com/FonaTech/Clouds-Coder)

This repository is already laid out in a form that `Clouds_Coder` can discover:

- package root: `DFT_Skills/`
- native skill tree: `DFT_Skills/skills/dft-workflow-orchestrator/SKILL.md`

Repository-level docs:

- overview: [README.md](./README.md)
- license: [LICENSE](./LICENSE)
- third-party and copyright boundaries: [THIRD_PARTY_AND_COPYRIGHT.md](./THIRD_PARTY_AND_COPYRIGHT.md)

GitHub-friendly repository adapters:

- Claude Code metadata and notes: [`claude-plugin/`](./claude-plugin/)
- Codex install notes: [`codex/`](./codex/)
- OpenCode install notes: [`opencode/`](./opencode/)

Those repository folders are intentionally visible for GitHub upload and browsing. Actual platform installs still go to runtime-native paths such as `.claude/`, `.opencode/`, `~/.codex/`, and `~/.agents/`.

`Clouds_Coder.py` can see the portable source directly, while the generated mirror is the optimized compact-loading path.

## Mode 1: Direct Skills Root

Use `DFT_Skills/skills` as the active `skills_root`.

This is the cleanest portable mode if the repository itself is dedicated to this skill pack. It reads the standard source `SKILL.md`; use Mode 3 when Clouds-specific aliases, entrypoints, and compact metadata are required.

## Mode 2: External Library Auto-Discovery

Keep `DFT_Skills/` adjacent to the active `skills/` directory.

`Clouds_Coder.py` scans sibling directories of the active `skills_root` and auto-discovers external libraries that contain `skills/*/SKILL.md`.

That means a workspace like this is valid:

```text
workspace/
├── skills/
└── DFT_Skills/
    └── skills/
        └── dft-workflow-orchestrator/
            └── SKILL.md
```

## Mode 3: Project-Local Native Mirror

Mirror the skill into the standard Clouds project path:

```bash
python3 DFT_Skills/skills/dft-workflow-orchestrator/scripts/sync_skill_to_platforms.py \
  --repo-root "$(pwd)" \
  --targets clouds \
  --force
```

This creates:

- `skills/generated/dft-workflow-orchestrator/`

That path is the most predictable and recommended Clouds option when the main workspace already uses a `skills/` tree. The sync command must use copy mode because it applies the platform overlay only to the generated target.

## On-Demand Loading Alignment

The skill separates portable and Clouds-specific metadata:

- source `SKILL.md` frontmatter contains only standard `name` and `description`
- `agents/clouds-coder.json` contains aliases, triggers, attachments, entrypoints, preferred tools, and the runtime contract
- `sync_skill_to_platforms.py --targets clouds --mode copy` renders that overlay into the generated Clouds copy
- reusable resources are exposed through `attachments`
- the rendered copy can enter compact mode so the runtime shows the contract and resource manifest before deeper reads

## Verification

Run the built-in compatibility check:

```bash
python3 DFT_Skills/skills/dft-workflow-orchestrator/scripts/verify_clouds_compat.py
```

The verifier checks:

- standard source frontmatter
- the Clouds sidecar overlay and all entrypoints
- rendered project-local copy generation
- entrypoint presence
- Clouds compact-mode loading behavior when `Clouds_Coder` is importable

## Boundary Rules

- keep the skill bundle itself read-only during normal workflow execution
- keep generated structures, workflow files, run directories, logs, and analysis outputs in the user project root
- do not write calculation outputs back into `DFT_Skills/skills/...`
