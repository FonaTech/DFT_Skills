#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Sequence


REQUIRED_SECTIONS = (
    "Research Decision And Scope",
    "Control Snapshot",
    "Scientific Rationale And Scale Decision",
    "Evidence, Models, And Assumptions",
    "Stage Roadmap",
    "Stage Gates And Deliverables",
    "Resource-Aware Execution Order",
    "Risks, Negative Results, And Escalation",
    "Research Spine Synchronization",
    "Definition Of Done",
)
ALLOWED_STATUSES = {"draft", "current", "stale", "superseded"}
PLACEHOLDER_RE = re.compile(r"(?:\{\{[^{}]+\}\}|<[A-Za-z][^>]*>)")
HEADING_RE = re.compile(r"^#{1,6}\s+(?:\d+[.)]\s+)?(.+?)\s*$", re.MULTILINE)
SNAPSHOT_RE = re.compile(r"^- (Objective|Active claim|Current gate|Next action|Stop rule):\s*(.*)$", re.MULTILINE | re.IGNORECASE)
STATUS_RE = re.compile(r"^- Plan status:\s*(.+?)\s*$", re.MULTILINE | re.IGNORECASE)
SNAPSHOT_KEYS = ("objective", "active_claim_id", "current_gate", "next_action", "stop_rule")
SNAPSHOT_LABELS = {
    "objective": "objective",
    "active claim": "active_claim_id",
    "current gate": "current_gate",
    "next action": "next_action",
    "stop rule": "stop_rule",
}


def normalize_heading(value: str) -> str:
    return " ".join(value.casefold().split())


def normalize_value(value: str) -> str:
    return value.strip().strip("`")


def read_snapshot(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for label, value in SNAPSHOT_RE.findall(text):
        key = SNAPSHOT_LABELS[label.strip().casefold()]
        values[key] = normalize_value(value)
    return values


def inspect_plan(
    path: Path,
    *,
    expected_claim_ids: Sequence[str] = (),
    expected_stage_ids: Sequence[str] = (),
    require_current: bool = False,
    strict: bool = False,
) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "path": str(path),
            "valid": False,
            "errors": [f"Planning artifact does not exist: {path}"],
            "warnings": [],
            "sections": [],
            "snapshot": {},
            "status": None,
            "placeholders": 0,
        }
    except OSError as exc:
        return {
            "path": str(path),
            "valid": False,
            "errors": [f"Could not read planning artifact {path}: {exc}"],
            "warnings": [],
            "sections": [],
            "snapshot": {},
            "status": None,
            "placeholders": 0,
        }

    sections = {normalize_heading(item) for item in HEADING_RE.findall(text)}
    missing_sections = [item for item in REQUIRED_SECTIONS if normalize_heading(item) not in sections]
    if missing_sections:
        errors.append(f"Planning artifact is missing required sections: {', '.join(missing_sections)}")

    snapshot = read_snapshot(text)
    missing_snapshot = [key for key in SNAPSHOT_KEYS if not snapshot.get(key)]
    if missing_snapshot:
        errors.append(f"Planning artifact control snapshot is missing: {', '.join(missing_snapshot)}")

    status_match = STATUS_RE.search(text)
    status = normalize_value(status_match.group(1)).casefold() if status_match else None
    if status not in ALLOWED_STATUSES:
        errors.append("Planning artifact must declare Plan status as draft, current, stale, or superseded.")
    elif require_current and status != "current":
        errors.append(f"Planning artifact must be current for strict validation; found {status!r}.")
    elif status != "current":
        warnings.append(f"Planning artifact status is {status!r}; reconcile it before launch.")

    for claim_id in expected_claim_ids:
        if not re.search(rf"(?<![A-Za-z0-9_]){re.escape(claim_id)}(?![A-Za-z0-9_])", text):
            errors.append(f"Planning artifact does not mention manifest claim {claim_id}.")
    for stage_id in expected_stage_ids:
        if not re.search(rf"(?<![A-Za-z0-9_]){re.escape(stage_id)}(?![A-Za-z0-9_])", text):
            errors.append(f"Planning artifact does not mention manifest stage {stage_id}.")

    placeholders = len(PLACEHOLDER_RE.findall(text))
    if placeholders:
        message = f"Planning artifact contains {placeholders} unresolved placeholder value(s)."
        (errors if strict else warnings).append(message)

    return {
        "path": str(path),
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "sections": sorted(sections),
        "snapshot": snapshot,
        "status": status,
        "placeholders": placeholders,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the required structure of an integrated research plan.")
    parser.add_argument("--plan", type=Path, required=True, help="Path to workflow/integrated_research_plan.md.")
    parser.add_argument("--claim-id", action="append", default=[], help="Claim ID that must appear in the plan; repeat as needed.")
    parser.add_argument("--stage-id", action="append", default=[], help="Stage ID that must appear in the plan; repeat as needed.")
    parser.add_argument("--strict", action="store_true", help="Require status=current and reject unresolved placeholders.")
    parser.add_argument("--pretty", action="store_true", help="Print a human-readable report.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = inspect_plan(
        args.plan.expanduser().resolve(),
        expected_claim_ids=args.claim_id,
        expected_stage_ids=args.stage_id,
        require_current=args.strict,
        strict=args.strict,
    )
    if args.pretty:
        print(f"Valid: {'yes' if result['valid'] else 'no'}")
        print(f"Status: {result['status'] or '<missing>'}")
        print(f"Placeholders: {result['placeholders']}")
        for message in result["errors"]:
            print(f"ERROR: {message}")
        for message in result["warnings"]:
            print(f"WARNING: {message}")
    else:
        json.dump(result, sys.stdout, indent=2)
        print()
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
