#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any


BRANCH_STATUSES = {"proposed", "active", "paused", "passed", "failed", "merged", "killed", "deferred"}
ACTION_STATUSES = {"proposed", "ready", "active", "blocked", "done", "killed", "deferred"}
PLACEHOLDER_RE = re.compile(r"(?:\{\{[^{}]+\}\}|<[A-Za-z][^>]*>)")
BRANCH_HEADERS = {
    "branch_id",
    "parent_branch",
    "claim_id",
    "purpose",
    "hypothesis",
    "method_or_scale",
    "expected_information_gain",
    "inputs",
    "planned_outputs",
    "pass_condition",
    "kill_criterion",
    "merge_rule",
    "owner",
    "status",
    "started_at",
    "closed_at",
    "artifact_ids",
    "notes",
}
LINEAGE_HEADERS = {
    "artifact_id",
    "kind",
    "path_or_uri",
    "parent_artifact_ids",
    "producer_stage",
    "branch_id",
    "schema",
    "units",
    "basis",
    "checksum",
    "software_version",
    "method_or_checkpoint",
    "created_at",
    "status",
    "validity",
    "retention",
    "notes",
}
QUEUE_HEADERS = {
    "action_id",
    "claim_id",
    "branch_id",
    "action",
    "why_now",
    "expected_information_gain",
    "prerequisites",
    "cost",
    "pass_condition",
    "kill_criterion",
    "owner",
    "status",
    "due_or_review_date",
}


def read_json(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"Missing manifest: {path}")
        return None
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"Cannot read manifest {path}: {exc}")
        return None
    if not isinstance(payload, dict):
        errors.append("Manifest root is not an object.")
        return None
    return payload


def read_csv(path: Path, required_headers: set[str], warnings: list[str], errors: list[str]) -> list[dict[str, str]]:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            headers = set(reader.fieldnames or [])
            missing = sorted(required_headers - headers)
            if missing:
                errors.append(f"{path.name} is missing headers: {', '.join(missing)}")
            return list(reader)
    except FileNotFoundError:
        warnings.append(f"Control file is missing: {path}")
    except OSError as exc:
        errors.append(f"Cannot read {path}: {exc}")
    return []


def read_spine_markdown(path: Path, strict: bool, warnings: list[str], errors: list[str]) -> dict[str, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        (errors if strict else warnings).append(f"Research spine file is missing: {path}")
        return {}
    except OSError as exc:
        errors.append(f"Cannot read research spine {path}: {exc}")
        return {}
    values: dict[str, str] = {}
    labels = {
        "objective": "objective",
        "active claim": "active_claim_id",
        "current gate": "current_gate",
        "next action": "next_action",
        "stop rule": "stop_rule",
    }
    for label, value in re.findall(r"^- ([^:]+):\s*(.*)$", text, flags=re.MULTILINE):
        key = labels.get(label.strip().lower())
        if key:
            values[key] = value.strip().strip("`")
    missing = sorted(set(labels.values()) - set(values))
    if missing:
        (errors if strict else warnings).append(f"Research spine file is missing synchronized fields: {', '.join(missing)}")
    return values


def compare_spine_sources(
    manifest_spine: dict[str, Any], markdown_spine: dict[str, str], strict: bool, warnings: list[str], errors: list[str]
) -> None:
    for field in ("objective", "active_claim_id", "current_gate", "next_action", "stop_rule"):
        manifest_value = str(manifest_spine.get(field, "")).strip().strip("`")
        markdown_value = markdown_spine.get(field, "").strip().strip("`")
        if manifest_value and markdown_value and manifest_value != markdown_value:
            (errors if strict else warnings).append(
                f"Research spine drift for {field}: manifest={manifest_value!r}, markdown={markdown_value!r}"
            )


def split_ids(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in re.split(r"[;,]", value) if item.strip()]


def placeholder_count(value: Any) -> int:
    if isinstance(value, dict):
        return sum(placeholder_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(placeholder_count(item) for item in value)
    return 1 if isinstance(value, str) and PLACEHOLDER_RE.search(value) else 0


def filled(value: str | None) -> bool:
    text = (value or "").strip()
    return bool(text) and not PLACEHOLDER_RE.search(text)


def parse_timestamp(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def status_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        status = str(item.get("status", "<missing>"))
        counts[status] = counts.get(status, 0) + 1
    return dict(sorted(counts.items()))


def choose_next_actions(queue_rows: list[dict[str, str]], stage_rows: list[dict[str, Any]], claim_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ready = [row for row in queue_rows if (row.get("status") or "").strip().lower() in {"ready", "active"}]
    if ready:
        def rank(row: dict[str, str]) -> tuple[int, str]:
            raw = row.get("expected_information_gain", "")
            try:
                score = -int(raw)
            except (TypeError, ValueError):
                score = {"high": -3, "medium": -2, "low": -1}.get(str(raw).strip().lower(), 0)
            return score, row.get("action_id", "")

        return sorted(ready, key=rank)

    blocked = [row for row in stage_rows if row.get("status") in {"failed", "blocked"}]
    if blocked:
        return [
            {
                "action_id": "DERIVED-REPAIR",
                "action": f"Repair or explicitly retire blocked stage {row.get('id')}",
                "why_now": "An upstream gate is blocked.",
                "status": "derived",
            }
            for row in blocked
        ]
    planned = [row for row in stage_rows if row.get("status") in {"planned", "ready"}]
    if planned:
        row = planned[0]
        return [
            {
                "action_id": "DERIVED-NEXT-STAGE",
                "action": f"Define and execute gate for {row.get('id')} ({row.get('kind')})",
                "why_now": "No explicit action queue entry exists for the next planned stage.",
                "status": "derived",
            }
        ]
    if claim_rows:
        return [{"action_id": "DERIVED-REVIEW", "action": "Review claim verdicts and decide whether to stop or open a bounded branch", "status": "derived"}]
    return []


def audit_spine(
    project_root: Path,
    manifest: dict[str, Any],
    branch_rows: list[dict[str, str]],
    lineage_rows: list[dict[str, str]],
    queue_rows: list[dict[str, str]],
    stale_days: int,
    strict: bool,
    warnings: list[str],
    errors: list[str],
) -> dict[str, Any]:
    claims = [item for item in manifest.get("claims", []) if isinstance(item, dict)]
    stages = [item for item in manifest.get("stages", []) if isinstance(item, dict)]
    claim_ids = {str(item.get("id")) for item in claims}
    stage_ids = {str(item.get("id")) for item in stages}
    branch_ids = {(row.get("branch_id") or "").strip() for row in branch_rows if (row.get("branch_id") or "").strip()}
    now = dt.datetime.now(dt.timezone.utc)
    orphan_branches: list[str] = []
    unbounded_branches: list[str] = []
    stale_branches: list[str] = []
    duplicate_artifacts: list[str] = []
    artifact_ids = {(row.get("artifact_id") or "").strip() for row in lineage_rows if (row.get("artifact_id") or "").strip()}
    seen_artifacts: set[str] = set()

    for row in lineage_rows:
        artifact_id = (row.get("artifact_id") or "").strip()
        if not artifact_id:
            warnings.append("A lineage row has no artifact_id.")
        elif artifact_id in seen_artifacts:
            duplicate_artifacts.append(artifact_id)
        seen_artifacts.add(artifact_id)
        producer_stage = (row.get("producer_stage") or "").strip()
        if producer_stage and producer_stage not in stage_ids:
            warnings.append(f"Lineage artifact {artifact_id} references unknown producer stage {producer_stage}.")
        branch_id = (row.get("branch_id") or "").strip()
        if branch_id and branch_id not in branch_ids:
            (errors if strict else warnings).append(f"Lineage artifact {artifact_id} references unknown branch {branch_id}.")
        parent_ids = split_ids(row.get("parent_artifact_ids"))
        for parent_id in parent_ids:
            if parent_id not in artifact_ids:
                (errors if strict else warnings).append(f"Lineage artifact {artifact_id} references unknown parent: {parent_id}.")
        if (row.get("status") or "").strip().lower() in {"validated", "frozen", "final"} and not (row.get("checksum") or "").strip():
            (errors if strict else warnings).append(f"Validated or frozen artifact {artifact_id} has no checksum.")

    seen_branches: set[str] = set()
    for row in branch_rows:
        branch_id = (row.get("branch_id") or "").strip()
        if not branch_id:
            errors.append("A branch row has no branch_id.")
            continue
        if branch_id in seen_branches:
            errors.append(f"Duplicate branch_id: {branch_id}")
        seen_branches.add(branch_id)
        parent = (row.get("parent_branch") or "").strip()
        claim_id = (row.get("claim_id") or "").strip()
        if not parent:
            (errors if strict else warnings).append(f"Branch {branch_id} has no parent_branch.")
        elif parent != "ROOT" and parent not in branch_ids:
            orphan_branches.append(branch_id)
        if not claim_id:
            (errors if strict else warnings).append(f"Branch {branch_id} has no claim_id.")
        elif claim_id not in claim_ids:
            orphan_branches.append(branch_id)
        status = (row.get("status") or "").strip().lower()
        if status not in BRANCH_STATUSES:
            warnings.append(f"Branch {branch_id} has unsupported status {status!r}.")
        if status in {"active", "proposed"}:
            if not filled(row.get("purpose")) or not filled(row.get("pass_condition")) or not filled(row.get("kill_criterion")):
                unbounded_branches.append(branch_id)
            started = parse_timestamp(row.get("started_at"))
            if started is None:
                (errors if strict else warnings).append(f"Active branch {branch_id} has no valid started_at timestamp.")
            if started and (now - started).days >= stale_days:
                stale_branches.append(branch_id)
        if status in {"passed", "failed", "merged", "killed"} and not parse_timestamp(row.get("closed_at")):
            (errors if strict else warnings).append(f"Closed branch {branch_id} has no valid closed_at timestamp.")
        for artifact_id in split_ids(row.get("artifact_ids")):
            if lineage_rows and artifact_id not in artifact_ids:
                warnings.append(f"Branch {branch_id} references unknown artifact {artifact_id}.")

    if orphan_branches:
        errors.append(f"Orphaned branch references: {sorted(set(orphan_branches))}")
    if duplicate_artifacts:
        errors.append(f"Duplicate artifact IDs in lineage: {sorted(set(duplicate_artifacts))}")
    if unbounded_branches:
        message = f"Active or proposed branches lack a bounded purpose/pass/kill rule: {sorted(set(unbounded_branches))}"
        (errors if strict else warnings).append(message)
    if stale_branches:
        warnings.append(f"Branches active for at least {stale_days} days without closure: {sorted(set(stale_branches))}")

    spine = manifest.get("research_spine")
    if not isinstance(spine, dict):
        message = "Manifest has no research_spine block; use workflow/research_spine.md as the source of direction."
        (errors if strict else warnings).append(message)
    else:
        for field in ("objective", "active_claim_id", "current_gate", "next_action", "stop_rule"):
            if not isinstance(spine.get(field), str) or not spine[field].strip():
                (errors if strict else warnings).append(f"research_spine.{field} is empty.")
        active_claim = spine.get("active_claim_id")
        if active_claim and active_claim not in claim_ids:
            errors.append(f"research_spine.active_claim_id is unknown: {active_claim}")

    placeholders = placeholder_count(manifest)
    if placeholders:
        warnings.append(f"Manifest contains {placeholders} unresolved placeholder value(s).")

    seen_actions: set[str] = set()
    ready_by_claim: dict[str, int] = {}
    for row in queue_rows:
        action_id = (row.get("action_id") or "").strip()
        claim_id = (row.get("claim_id") or "").strip()
        branch_id = (row.get("branch_id") or "").strip()
        status = (row.get("status") or "").strip().lower()
        if not action_id:
            errors.append("An action queue row has no action_id.")
        elif action_id in seen_actions:
            errors.append(f"Duplicate action_id: {action_id}")
        seen_actions.add(action_id)
        if not claim_id:
            (errors if strict else warnings).append(f"Action {action_id} has no claim_id.")
        elif claim_id not in claim_ids:
            errors.append(f"Action {action_id} references unknown claim {claim_id}.")
        if not branch_id:
            (errors if strict else warnings).append(f"Action {action_id} has no branch_id.")
        elif branch_id not in branch_ids:
            errors.append(f"Action {action_id} references unknown branch {branch_id}.")
        if status not in ACTION_STATUSES:
            warnings.append(f"Action {action_id} has unsupported status {status!r}.")
        if status in {"ready", "active"}:
            ready_by_claim[claim_id] = ready_by_claim.get(claim_id, 0) + 1
            for field in ("action", "why_now", "pass_condition", "kill_criterion"):
                if not filled(row.get(field)):
                    (errors if strict else warnings).append(f"Ready action {action_id} has no resolved {field}.")

    next_actions = choose_next_actions(queue_rows, stages, claims)
    for claim_id, count in ready_by_claim.items():
        if count > 1:
            warnings.append(f"Claim {claim_id or '<missing>'} has {count} ready/active actions; justify parallel work or keep one.")

    blockers = [
        {"stage_id": row.get("id"), "kind": row.get("kind"), "status": row.get("status"), "name": row.get("name")}
        for row in stages
        if row.get("status") in {"failed", "blocked"}
    ]
    health = "red" if errors else "amber" if warnings else "green"
    return {
        "project_root": str(project_root),
        "generated_at": now.isoformat(),
        "health": health,
        "research_spine": spine if isinstance(spine, dict) else {},
        "counts": {
            "claims": len(claims),
            "stages": len(stages),
            "branches": len(branch_rows),
            "artifacts": len(lineage_rows),
            "actions": len(queue_rows),
        },
        "claim_status": status_counts(claims),
        "stage_status": status_counts(stages),
        "branch_status": status_counts(branch_rows),
        "blockers": blockers,
        "orphaned_branches": sorted(set(orphan_branches)),
        "unbounded_branches": sorted(set(unbounded_branches)),
        "stale_branches": sorted(set(stale_branches)),
        "next_actions": next_actions,
        "placeholder_count": placeholders,
        "errors": errors,
        "warnings": warnings,
    }


def markdown_report(report: dict[str, Any]) -> str:
    spine = report.get("research_spine", {})
    lines = [
        "# Research Status",
        "",
        f"- Health: **{report['health']}**",
        f"- Generated: {report['generated_at']}",
        f"- Objective: {spine.get('objective', '<not recorded>')}",
        f"- Active claim: {spine.get('active_claim_id', '<not recorded>')}",
        f"- Current gate: {spine.get('current_gate', '<not recorded>')}",
        f"- Next action: {spine.get('next_action', '<not recorded>')}",
        "",
        "## Counts",
        "",
        "| Entity | Count | Status counts |",
        "|---|---:|---|",
        f"| claims | {report['counts']['claims']} | {report['claim_status']} |",
        f"| stages | {report['counts']['stages']} | {report['stage_status']} |",
        f"| branches | {report['counts']['branches']} | {report['branch_status']} |",
        f"| artifacts | {report['counts']['artifacts']} | lineage rows |",
        f"| actions | {report['counts']['actions']} | queue rows |",
        "",
        "## Blockers",
        "",
    ]
    if report["blockers"]:
        lines.extend(f"- {item['stage_id']} ({item['kind']}): {item['status']} - {item['name']}" for item in report["blockers"])
    else:
        lines.append("- None recorded in the manifest.")
    lines.extend(["", "## Branch Warnings", ""])
    for key, label in (("orphaned_branches", "orphaned"), ("unbounded_branches", "unbounded"), ("stale_branches", "stale")):
        values = report[key]
        lines.append(f"- {label}: {', '.join(values) if values else 'none'}")
    lines.extend(["", "## Next Actions", "", "| ID | Action | Why now | Status |", "|---|---|---|---|"])
    if report["next_actions"]:
        for item in report["next_actions"]:
            lines.append(f"| {item.get('action_id', '')} | {item.get('action', '')} | {item.get('why_now', '')} | {item.get('status', '')} |")
    else:
        lines.append("| | No next action recorded | Review the spine before continuing | |")
    lines.extend(["", "## Errors", ""])
    lines.extend(f"- {message}" for message in report["errors"] or ["None"])
    lines.extend(["", "## Warnings", ""])
    lines.extend(f"- {message}" for message in report["warnings"] or ["None"])
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh a research-spine status report for a branching simulation project.")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root containing workflow/ and analysis/.")
    parser.add_argument("--manifest", type=Path, help="Override workflow manifest path.")
    parser.add_argument("--branch-register", type=Path, help="Override branch register path.")
    parser.add_argument("--lineage", type=Path, help="Override data lineage path.")
    parser.add_argument("--action-queue", type=Path, help="Override next-action queue path.")
    parser.add_argument("--spine-file", type=Path, help="Override workflow/research_spine.md path.")
    parser.add_argument("--stale-days", type=int, default=14, help="Age in days after which an active branch is warned as stale.")
    parser.add_argument("--strict", action="store_true", help="Treat missing spine and unbounded branches as errors.")
    parser.add_argument("--no-write", action="store_true", help="Print the report without writing analysis/research_status files.")
    parser.add_argument("--pretty", action="store_true", help="Print a compact human-readable report.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.stale_days < 1:
        raise SystemExit("--stale-days must be at least 1.")
    root = args.project_root.expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []
    manifest_path = (args.manifest or root / "workflow" / "experiment_manifest.json").expanduser().resolve()
    manifest = read_json(manifest_path, errors) or {}
    branch_path = (args.branch_register or root / "workflow" / "branch_register.csv").expanduser().resolve()
    lineage_path = (args.lineage or root / "workflow" / "data_lineage.csv").expanduser().resolve()
    queue_path = (args.action_queue or root / "workflow" / "next_action_queue.csv").expanduser().resolve()
    spine_path = (args.spine_file or root / "workflow" / "research_spine.md").expanduser().resolve()
    branch_rows = read_csv(branch_path, BRANCH_HEADERS, warnings, errors)
    lineage_rows = read_csv(lineage_path, LINEAGE_HEADERS, warnings, errors)
    queue_rows = read_csv(queue_path, QUEUE_HEADERS, warnings, errors)
    markdown_spine = read_spine_markdown(spine_path, args.strict, warnings, errors)
    report = audit_spine(root, manifest, branch_rows, lineage_rows, queue_rows, args.stale_days, args.strict, warnings, errors)
    manifest_spine = manifest.get("research_spine")
    if isinstance(manifest_spine, dict):
        compare_spine_sources(manifest_spine, markdown_spine, args.strict, warnings, errors)
    report["spine_file"] = str(spine_path)
    report["spine_markdown"] = markdown_spine
    report["errors"] = errors
    report["warnings"] = warnings
    report["health"] = "red" if errors else "amber" if warnings else "green"

    if not args.no_write:
        analysis_dir = root / "analysis"
        analysis_dir.mkdir(parents=True, exist_ok=True)
        (analysis_dir / "research_status.json").write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        (analysis_dir / "research_status.md").write_text(markdown_report(report), encoding="utf-8")

    if args.pretty:
        print(f"Health: {report['health']}")
        print(f"Claims={report['counts']['claims']} stages={report['counts']['stages']} branches={report['counts']['branches']} artifacts={report['counts']['artifacts']}")
        next_action = (report["next_actions"] or [{"action": "<none>"}])[0].get("action")
        print(f"Next: {next_action}")
        for message in report["errors"]:
            print(f"ERROR: {message}")
        for message in report["warnings"]:
            print(f"WARNING: {message}")
    else:
        json.dump(report, sys.stdout, indent=2)
        print()
    return 0 if not report["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
