# Installing DFT Skills For Claude Code

Use the sync script to place the skill into Claude-compatible directories.

## Project-local install

```bash
python3 DFT_Skills/skills/dft-workflow-orchestrator/scripts/sync_skill_to_platforms.py \
  --repo-root "$(pwd)" \
  --targets claude-project \
  --force
```

This creates:

- `.claude/skills/dft-workflow-orchestrator`

## User-level install

```bash
python3 DFT_Skills/skills/dft-workflow-orchestrator/scripts/sync_skill_to_platforms.py \
  --repo-root "$(pwd)" \
  --targets claude-home \
  --force
```

This creates:

- `~/.claude/skills/dft-workflow-orchestrator`

## Optional plugin-style metadata

The package also ships `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`.
Treat those as metadata helpers only. The `.claude/skills/...` install path is the compatibility baseline.
