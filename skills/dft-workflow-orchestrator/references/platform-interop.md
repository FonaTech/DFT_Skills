# Platform Interop

This package keeps the scientific logic in one place and treats platform features as optional accelerators.

## Core Rule

The skill must still work when all you have is shell plus file access. Richer platform features are helpers, not dependencies.

## Clouds_Coder

Recommended entry:

- install or mirror into the local `skills/` tree so `SKILL.md` is auto-discovered
- preferred project-local path in this repository: `skills/generated/dft-workflow-orchestrator/`
- external-library discovery also works when `DFT_Skills/` is kept adjacent to the active `skills/` directory, because `Clouds_Coder.py` scans sibling directories for `skills/*/SKILL.md`

Preferred accelerators:

- `query_knowledge_library` for local RAG retrieval
- `load_skill` for chaining with research or PDF skills
- online search when local coverage is thin or the theory basis is incomplete

Grounding order on Clouds_Coder.py:

1. uploaded or local project materials
2. local RAG retrieval
3. online search
4. model knowledge as the final fallback

Stop at the first tier that already resolves the theory basis and experiment design.

Fallback:

- search workspace files directly
- use the bundled scripts for preflight, scaffolding, job rendering, and analysis

Native compatibility notes:

- keep the skill itself inside the active `skills_root`, because `Clouds_Coder.py` resolves writes with `safe_path(..., skills_root)`
- keep reusable assets inside the skill bundle only
- keep generated calculation work outside the skill bundle, in a user project root such as `project/workflow`, `project/structures`, `project/runs`, and `project/analysis`
- do not write run outputs, logs, or relaxed structures back into the skill directory during normal execution
- preserve `clouds_coder.preferred_tools`, `entrypoints`, and `runtime_contract` in frontmatter so the runtime can inject the right attachment set and boundary hints
- preserve enough body detail that `load_skill` enters compact-mode loading, so the runtime shows the contract plus resource manifest first and deeper files stay on demand
- use `query_knowledge_library` proactively on theory-heavy tasks, but only after uploaded and local materials have been checked first
- keep front-end monitoring alive with `scripts/monitor_vasp_runs.py` when queues are running in the background

Validation helper:

- run `python3 scripts/verify_clouds_compat.py` from the skill directory to check direct-root loading, sibling-library auto-discovery, project-local mirroring, and compact-mode behavior

## Claude Code

Supported local skill paths:

1. project local: `.claude/skills/dft-workflow-orchestrator/SKILL.md`
2. user level: `~/.claude/skills/dft-workflow-orchestrator/SKILL.md`

The local path is the safest default because the bundled scripts remain close to the working repository.
When Claude Code has web-capable tooling available, use uploaded files and local literature first, then web retrieval, then model prior. Stop when the current tier is already sufficient.

## OpenCode

OpenCode recognizes several routes:

1. project local: `.opencode/skills/dft-workflow-orchestrator/SKILL.md`
2. user level: `~/.config/opencode/skills/dft-workflow-orchestrator/SKILL.md`
3. Claude-compatible skill paths
4. Agent-standard paths under `.agents/skills/` or `~/.agents/skills/`

That means one copied bundle can serve both OpenCode and Claude-compatible loaders.
On OpenCode, prioritize uploaded or local sources first; use web retrieval when available; then use model knowledge with explicit uncertainty tags. Stop when the current tier is already sufficient.

## Codex

Portable contract:

- standard `SKILL.md`
- optional `agents/openai.yaml` UI metadata

Local install targets vary by Codex surface, so the sync script supports both:

1. `~/.codex/skills/dft-workflow-orchestrator/`
2. `~/.agents/skills/dft-workflow-orchestrator/`

If you do not know which surface is active, install both.
On Codex surfaces without a dedicated RAG tool, emulate the same policy with local files plus web retrieval before relying on model memory, and stop the collection chain once the current tier is sufficient.

## Portability Rules

- keep frontmatter conservative: `name`, `description`, `license`, `compatibility`, and flat-string `metadata`
- add platform-specific enhancement fields only as optional overlays, not as hard dependencies
- keep reusable automation in `scripts/`
- keep long methodology in `references/`
- never require proprietary platform-only tool names to complete the workflow
- prefer copied bundles over fragile fixed-path assumptions when distributing the skill
