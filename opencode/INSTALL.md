# Installing DFT Skills For OpenCode

Run the sync script from the repository root to materialize OpenCode-compatible copies of the skill.

## Project-local install

```bash
python3 DFT_Skills/skills/dft-workflow-orchestrator/scripts/sync_skill_to_platforms.py \
  --repo-root "$(pwd)" \
  --targets opencode-project claude-project agents-project \
  --force
```

This creates:

- `.opencode/skills/dft-workflow-orchestrator`
- `.claude/skills/dft-workflow-orchestrator`
- `.agents/skills/dft-workflow-orchestrator`

OpenCode recognizes all three routes.

## User-level install

```bash
python3 DFT_Skills/skills/dft-workflow-orchestrator/scripts/sync_skill_to_platforms.py \
  --repo-root "$(pwd)" \
  --targets opencode-home claude-home agents-home \
  --force
```

Restart OpenCode after installation.
