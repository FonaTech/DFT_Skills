#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path


SKILL_NAME = "dft-workflow-orchestrator"


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)


def copy_skill(src: Path, dst: Path, force: bool) -> None:
    if dst.exists() or dst.is_symlink():
        if not force:
            raise FileExistsError(f"Target already exists: {dst}")
        remove_path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"))


def symlink_skill(src: Path, dst: Path, force: bool) -> None:
    if dst.exists() or dst.is_symlink():
        if not force:
            raise FileExistsError(f"Target already exists: {dst}")
        remove_path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.symlink_to(src, target_is_directory=True)


def target_path(target: str, repo_root: Path) -> Path:
    if target == "clouds":
        return repo_root / "skills" / "generated" / SKILL_NAME
    if target == "claude-project":
        return repo_root / ".claude" / "skills" / SKILL_NAME
    if target == "opencode-project":
        return repo_root / ".opencode" / "skills" / SKILL_NAME
    if target == "agents-project":
        return repo_root / ".agents" / "skills" / SKILL_NAME
    if target == "claude-home":
        return Path.home() / ".claude" / "skills" / SKILL_NAME
    if target == "opencode-home":
        return Path.home() / ".config" / "opencode" / "skills" / SKILL_NAME
    if target == "agents-home":
        return Path.home() / ".agents" / "skills" / SKILL_NAME
    if target == "codex-home":
        return Path.home() / ".codex" / "skills" / SKILL_NAME
    raise ValueError(f"Unsupported target: {target}")


def display_path(path: Path, repo_root: Path) -> str:
    resolved = path.expanduser().resolve()
    repo_root = repo_root.expanduser().resolve()
    home = Path.home().resolve()
    if resolved == repo_root or repo_root in resolved.parents:
        return os.path.relpath(str(resolved), str(repo_root))
    if resolved == home or home in resolved.parents:
        return "~/" + os.path.relpath(str(resolved), str(home))
    return os.path.relpath(str(resolved), str(Path.cwd().resolve()))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Copy or link the DFT skill into platform-specific locations.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root for project-local targets.")
    parser.add_argument(
        "--targets",
        nargs="*",
        choices=[
            "clouds",
            "claude-project",
            "opencode-project",
            "agents-project",
            "claude-home",
            "opencode-home",
            "agents-home",
            "codex-home",
        ],
        help="Explicit targets to materialize.",
    )
    parser.add_argument("--mode", choices=["copy", "symlink"], default="copy", help="How to materialize the skill.")
    parser.add_argument("--force", action="store_true", help="Replace existing targets.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.expanduser().resolve()
    skill_root = Path(__file__).resolve().parents[1]
    targets = args.targets or ["clouds", "claude-project", "opencode-project", "agents-project"]

    materialized: list[dict[str, str]] = []
    for target in targets:
        dst = target_path(target, repo_root)
        if args.mode == "copy":
            copy_skill(skill_root, dst, args.force)
        else:
            symlink_skill(skill_root, dst, args.force)
        materialized.append({"target": target, "path": display_path(dst, repo_root)})

    print(json.dumps({"skill_root": display_path(skill_root, repo_root), "materialized": materialized}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
