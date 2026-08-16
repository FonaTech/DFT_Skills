#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any

from sync_skill_to_platforms import apply_clouds_overlay


SKILL_NAME = "dft-workflow-orchestrator"
FRONTMATTER_PATTERN = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)


def read_overlay(skill_root: Path) -> dict[str, Any]:
    path = skill_root / "agents" / "clouds-coder.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Clouds overlay root must be an object.")
    return payload


def source_check(skill_root: Path) -> dict[str, Any]:
    errors: list[str] = []
    skill_path = skill_root / "SKILL.md"
    content = skill_path.read_text(encoding="utf-8")
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        errors.append("Standard SKILL.md frontmatter was not found.")
        header = ""
    else:
        header = match.group(1)
    if "name: dft-workflow-orchestrator" not in header:
        errors.append("Standard skill name is missing.")
    if "description:" not in header:
        errors.append("Standard skill description is missing.")
    for forbidden in ("entrypoints:", "attachments:", "clouds_coder:", "triggers:"):
        if forbidden in header:
            errors.append(f"Platform field leaked into standard frontmatter: {forbidden[:-1]}")
    return {"mode": "standard_source", "errors": errors, "frontmatter_lines": len(header.splitlines())}


def overlay_check(skill_root: Path) -> dict[str, Any]:
    errors: list[str] = []
    overlay = read_overlay(skill_root)
    if overlay.get("name") != SKILL_NAME:
        errors.append("Overlay name does not match the skill name.")
    entrypoints = overlay.get("entrypoints")
    if not isinstance(entrypoints, list) or not entrypoints:
        errors.append("Overlay has no entrypoints.")
        entrypoints = []
    missing = [path for path in entrypoints if not (skill_root / str(path)).is_file()]
    if missing:
        errors.append(f"Overlay entrypoints are missing: {missing}")
    attachments = overlay.get("attachments")
    if not isinstance(attachments, list) or not attachments:
        errors.append("Overlay has no attachment patterns.")
    clouds = overlay.get("clouds_coder")
    if not isinstance(clouds, dict):
        errors.append("Overlay has no clouds_coder object.")
        clouds = {}
    if "query_knowledge_library" not in clouds.get("preferred_tools", []):
        errors.append("query_knowledge_library is missing from preferred tools.")
    if not str(clouds.get("runtime_contract", "")).strip():
        errors.append("Clouds runtime contract is empty.")
    return {
        "mode": "clouds_overlay",
        "entrypoint_count": len(entrypoints),
        "attachment_count": len(attachments) if isinstance(attachments, list) else 0,
        "missing_entrypoints": missing,
        "errors": errors,
    }


def find_skill_row(store: Any) -> dict[str, Any] | None:
    for row in store.list_metadata():
        if row.get("name") == SKILL_NAME:
            return row
    return None


def runtime_check(rendered_skills_root: Path) -> dict[str, Any]:
    try:
        from Clouds_Coder import SkillStore
    except ImportError:
        return {
            "mode": "clouds_runtime",
            "available": False,
            "skipped": True,
            "errors": [],
            "notes": ["Clouds_Coder is not importable; static overlay and materialization checks were used."],
        }

    store = SkillStore(rendered_skills_root)
    row = find_skill_row(store)
    errors: list[str] = []
    if not row:
        errors.append("Rendered skill was not discovered by Clouds_Coder.SkillStore.")
        return {"mode": "clouds_runtime", "available": True, "skipped": False, "errors": errors}
    loaded = store.load(SKILL_NAME)
    compact = 'compact_mode="true"' in loaded
    if not compact:
        errors.append("Rendered Clouds skill did not enter compact mode.")
    if not row.get("entrypoints"):
        errors.append("Rendered Clouds metadata registered no entrypoints.")
    if not row.get("attachments"):
        errors.append("Rendered Clouds metadata registered no attachments.")
    return {
        "mode": "clouds_runtime",
        "available": True,
        "skipped": False,
        "compact_mode": compact,
        "entrypoint_count": len(row.get("entrypoints", [])),
        "attachment_count": len(row.get("attachments", [])),
        "errors": errors,
    }


def rendered_check(skill_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    with tempfile.TemporaryDirectory(prefix="clouds-skill-render-") as tmpdir:
        skills_root = Path(tmpdir) / "skills"
        rendered = skills_root / SKILL_NAME
        rendered.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(skill_root, rendered, ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"))
        apply_clouds_overlay(rendered)
        content = (rendered / "SKILL.md").read_text(encoding="utf-8")
        match = FRONTMATTER_PATTERN.match(content)
        errors: list[str] = []
        frontmatter: dict[str, Any] = {}
        if not match:
            errors.append("Rendered SKILL.md has no frontmatter.")
        else:
            try:
                frontmatter = json.loads(match.group(1))
            except json.JSONDecodeError as exc:
                errors.append(f"Rendered frontmatter is not the expected JSON-compatible YAML: {exc}")
        if frontmatter.get("entrypoints") is None:
            errors.append("Rendered frontmatter has no entrypoints.")
        if frontmatter.get("clouds_coder") is None:
            errors.append("Rendered frontmatter has no clouds_coder contract.")
        static = {
            "mode": "rendered_clouds_copy",
            "frontmatter_keys": sorted(frontmatter),
            "body_present": bool(match and content[match.end() :].strip()),
            "errors": errors,
        }
        return static, runtime_check(skills_root)


def main() -> int:
    skill_root = Path(__file__).resolve().parents[1]
    checks: list[dict[str, Any]] = []
    try:
        checks.append(source_check(skill_root))
        checks.append(overlay_check(skill_root))
        rendered, runtime = rendered_check(skill_root)
        checks.extend([rendered, runtime])
    except Exception as exc:
        checks.append({"mode": "unexpected_exception", "errors": [f"{type(exc).__name__}: {exc}"]})
    errors = [message for check in checks for message in check.get("errors", [])]
    payload = {
        "skill_name": SKILL_NAME,
        "skill_root": str(skill_root),
        "ok": not errors,
        "checks": checks,
        "errors": errors,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
