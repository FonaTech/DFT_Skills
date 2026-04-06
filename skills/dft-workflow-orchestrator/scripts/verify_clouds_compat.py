#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from Clouds_Coder import SkillStore


SKILL_NAME = "dft-workflow-orchestrator"


def rel(path: Path, base: Path) -> str:
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except Exception:
        return path.resolve().as_posix()


def find_skill_row(store: SkillStore, name: str = SKILL_NAME) -> dict | None:
    for row in store.list_metadata():
        if row.get("name") == name:
            return row
    return None


def validate_store(store: SkillStore, *, require_compact: bool) -> dict:
    row = find_skill_row(store)
    if not row:
        return {
            "skill_present": False,
            "compact_mode": False,
            "provider_id": "",
            "entrypoint_count": 0,
            "attachment_count": 0,
            "errors": [f"Skill '{SKILL_NAME}' was not discovered."],
        }

    load_text = store.load(SKILL_NAME)
    compact_mode = 'compact_mode="true"' in load_text
    errors: list[str] = []
    if require_compact and not compact_mode:
        errors.append("Clouds compact-mode loading was not triggered.")
    if not row.get("entrypoints"):
        errors.append("No entrypoints were registered.")
    if not row.get("attachments"):
        errors.append("No attachments were registered.")
    runtime_contract = row.get("meta", {}).get("clouds_coder", {}).get("runtime_contract", "")
    if not str(runtime_contract).strip():
        errors.append("clouds_coder.runtime_contract is missing.")
    preferred_tools = row.get("meta", {}).get("clouds_coder", {}).get("preferred_tools", [])
    if "query_knowledge_library" not in preferred_tools:
        errors.append("query_knowledge_library is missing from clouds_coder.preferred_tools.")
    return {
        "skill_present": True,
        "compact_mode": compact_mode,
        "provider_id": row.get("provider_id", ""),
        "entrypoint_count": len(row.get("entrypoints", [])),
        "attachment_count": len(row.get("attachments", [])),
        "errors": errors,
    }


def direct_root_check(package_root: Path) -> dict:
    skills_root = package_root / "skills"
    store = SkillStore(skills_root)
    result = validate_store(store, require_compact=True)
    result["mode"] = "direct_skills_root"
    result["skills_root"] = rel(skills_root, Path.cwd())
    skill_dir = skills_root / SKILL_NAME
    missing_entrypoints = []
    row = find_skill_row(store)
    if row:
        for entry in row.get("entrypoints", []):
            if not (skill_dir / entry).exists():
                missing_entrypoints.append(entry)
    result["missing_entrypoints"] = missing_entrypoints
    if missing_entrypoints:
        result["errors"].append("Some entrypoints do not exist on disk.")
    return result


def external_discovery_check(package_root: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix="clouds-skill-ext-") as tmpdir:
        workspace = Path(tmpdir)
        (workspace / "skills").mkdir(parents=True, exist_ok=True)
        linked_package = workspace / package_root.name
        linked_package.symlink_to(package_root.resolve(), target_is_directory=True)
        store = SkillStore(workspace / "skills")
        result = validate_store(store, require_compact=True)
        result["mode"] = "external_library_auto_discovery"
        result["skills_root"] = "skills"
        result["external_package"] = package_root.name
        return result


def mirrored_project_check(package_root: Path) -> dict:
    sync_script = package_root / "skills" / SKILL_NAME / "scripts" / "sync_skill_to_platforms.py"
    with tempfile.TemporaryDirectory(prefix="clouds-skill-mirror-") as tmpdir:
        workspace = Path(tmpdir)
        (workspace / "skills").mkdir(parents=True, exist_ok=True)
        target = workspace / "skills" / "generated" / SKILL_NAME
        if target.exists():
            shutil.rmtree(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(package_root / "skills" / SKILL_NAME, target, ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"))
        store = SkillStore(workspace / "skills")
        result = validate_store(store, require_compact=True)
        result["mode"] = "project_local_clouds_mirror"
        result["skills_root"] = "skills"
        result["mirrored_skill"] = f"skills/generated/{SKILL_NAME}"
        result["sync_script"] = rel(sync_script, Path.cwd())
        return result


def main() -> int:
    package_root = Path(__file__).resolve().parents[3]
    checks = [
        direct_root_check(package_root),
        external_discovery_check(package_root),
        mirrored_project_check(package_root),
    ]
    ok = all(not item.get("errors") for item in checks)
    payload = {
        "package_root": rel(package_root, Path.cwd()),
        "skill_name": SKILL_NAME,
        "ok": ok,
        "checks": checks,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
