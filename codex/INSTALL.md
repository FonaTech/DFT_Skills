# Installing DFT Skills For Codex

This package is distributed as an Agent Skills bundle and also includes `agents/openai.yaml` metadata for Codex-compatible surfaces.

## Recommended install

Install both Codex-facing targets if you are unsure which local surface is active:

```bash
python3 DFT_Skills/skills/dft-workflow-orchestrator/scripts/sync_skill_to_platforms.py \
  --repo-root "$(pwd)" \
  --targets codex-home agents-home \
  --force
```

This creates:

- `~/.codex/skills/dft-workflow-orchestrator`
- `~/.agents/skills/dft-workflow-orchestrator`

## Project-local compatibility copy

If your Codex surface uses agent-standard project paths, also create:

```bash
python3 DFT_Skills/skills/dft-workflow-orchestrator/scripts/sync_skill_to_platforms.py \
  --repo-root "$(pwd)" \
  --targets agents-project \
  --force
```

Restart Codex after installation.
