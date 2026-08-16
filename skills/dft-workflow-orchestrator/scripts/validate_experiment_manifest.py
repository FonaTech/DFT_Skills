#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any

from validate_integrated_research_plan import ALLOWED_STATUSES as PLAN_STATUSES
from validate_integrated_research_plan import REQUIRED_SECTIONS as PLAN_REQUIRED_SECTIONS
from validate_integrated_research_plan import inspect_plan


ALLOWED_KINDS = {
    "dft",
    "aimd",
    "mlip",
    "md",
    "homogenization",
    "fem",
    "experiment",
    "analysis",
    "coupling",
}
ALLOWED_STATUSES = {
    "planned",
    "ready",
    "submitted",
    "running",
    "converged",
    "validated",
    "failed",
    "blocked",
    "skipped",
    "interpreted",
}
STAGE_SCALES = {
    "dft": "electronic",
    "aimd": "finite-temperature-atomistic",
    "mlip": "atomistic-surrogate",
    "md": "extended-atomistic",
    "homogenization": "statistical-scale-bridge",
    "fem": "continuum",
    "experiment": "experimental",
}
PLACEHOLDER_RE = re.compile(r"(?:\{\{[^{}]+\}\}|<[A-Za-z][^>]*>)")
REQUIRED_TOP_LEVEL = {"schema_version", "project", "claims", "stages", "handoffs", "resources", "metadata"}
SUPPORTED_SCHEMA_VERSIONS = {"1.0", "1.1"}
REQUIRED_PLAN_SYNCHRONIZATION = {"research_spine", "claims", "stages", "handoffs", "next_action_queue"}
REQUIRED_HANDOFF_HEADERS = {
    "handoff_id",
    "from_stage",
    "to_stage",
    "artifact",
    "mapping",
    "units",
    "validity",
    "acceptance",
}
RECOMMENDED_HANDOFF_HEADERS = {
    "quantity_type",
    "schema",
    "basis",
    "voigt_order",
    "sign_convention",
    "state_variables",
    "averaging_rule",
    "uncertainty",
    "status",
}


class Checker:
    def __init__(self, strict: bool = False) -> None:
        self.strict = strict
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.info: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)

    def required(self, condition: bool, message: str) -> None:
        if condition:
            return
        if self.strict:
            self.error(message)
        else:
            self.warning(message)


def load_json(path: Path, checker: Checker) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        checker.error(f"Manifest does not exist: {path}")
        return None
    except (OSError, json.JSONDecodeError) as exc:
        checker.error(f"Could not read JSON manifest {path}: {exc}")
        return None
    if not isinstance(payload, dict):
        checker.error("Manifest root must be a JSON object.")
        return None
    return payload


def as_list(value: Any, path: str, checker: Checker) -> list[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        checker.error(f"{path} must be a list.")
        return []
    return value


def check_unique_ids(items: list[Any], path: str, checker: Checker) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for position, item in enumerate(items):
        if not isinstance(item, dict):
            checker.error(f"{path}[{position}] must be an object.")
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id.strip():
            checker.error(f"{path}[{position}].id must be a non-empty string.")
            continue
        if item_id in index:
            checker.error(f"Duplicate {path} id: {item_id}")
        index[item_id] = item
    return index


def find_cycle(stage_map: dict[str, dict[str, Any]]) -> list[str] | None:
    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        state[node] = 1
        stack.append(node)
        for dep in stage_map[node].get("depends_on", []) or []:
            if dep not in stage_map:
                continue
            if state.get(dep, 0) == 0:
                cycle = visit(dep)
                if cycle:
                    return cycle
            elif state.get(dep) == 1:
                start = stack.index(dep)
                return stack[start:] + [dep]
        stack.pop()
        state[node] = 2
        return None

    for node in stage_map:
        if state.get(node, 0) == 0:
            cycle = visit(node)
            if cycle:
                return cycle
    return None


def depends_transitively(stage_map: dict[str, dict[str, Any]], source: str, target: str) -> bool:
    seen: set[str] = set()
    pending = list(stage_map.get(target, {}).get("depends_on", []) or [])
    while pending:
        item = pending.pop()
        if item == source:
            return True
        if item in seen:
            continue
        seen.add(item)
        pending.extend(stage_map.get(item, {}).get("depends_on", []) or [])
    return False


def check_placeholders(value: Any, path: str, checker: Checker) -> int:
    count = 0
    if isinstance(value, dict):
        for key, item in value.items():
            count += check_placeholders(item, f"{path}.{key}", checker)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            count += check_placeholders(item, f"{path}[{index}]", checker)
    elif isinstance(value, str) and PLACEHOLDER_RE.search(value):
        count += 1
        checker.required(False, f"Unresolved placeholder at {path}: {value}")
    return count


def check_stage_fields(stage: dict[str, Any], path: str, claim_ids: set[str], stage_ids: set[str], checker: Checker) -> None:
    kind = stage.get("kind")
    if kind not in ALLOWED_KINDS:
        checker.error(f"{path}.kind is unsupported: {kind!r}")
    status = stage.get("status")
    if status not in ALLOWED_STATUSES:
        checker.error(f"{path}.status is unsupported: {status!r}")
    dependencies = stage.get("depends_on", [])
    if not isinstance(dependencies, list) or not all(isinstance(item, str) for item in dependencies):
        checker.error(f"{path}.depends_on must be a list of stage IDs.")
    else:
        for dependency in dependencies:
            if dependency not in stage_ids:
                checker.error(f"{path}.depends_on references unknown stage: {dependency}")
    claim_refs = stage.get("claim_ids", [])
    if claim_refs is not None:
        if not isinstance(claim_refs, list) or not all(isinstance(item, str) for item in claim_refs):
            checker.error(f"{path}.claim_ids must be a list of claim IDs.")
        else:
            for claim_id in claim_refs:
                if claim_id not in claim_ids:
                    checker.error(f"{path}.claim_ids references unknown claim: {claim_id}")
    for field in ("inputs", "outputs", "controls", "validation"):
        value = stage.get(field)
        if not isinstance(value, list):
            checker.required(False, f"{path}.{field} must be a non-empty list.")
        elif not value:
            checker.required(False, f"{path}.{field} must not be empty.")
    checker.required(isinstance(stage.get("pass_condition"), str) and bool(stage["pass_condition"].strip()), f"{path}.pass_condition is required.")


def check_handoff_fields(
    handoff: dict[str, Any], path: str, stage_ids: set[str], stage_map: dict[str, dict[str, Any]], checker: Checker
) -> None:
    source = handoff.get("from_stage")
    target = handoff.get("to_stage")
    if source not in stage_ids:
        checker.error(f"{path}.from_stage references unknown stage: {source!r}")
    if target not in stage_ids:
        checker.error(f"{path}.to_stage references unknown stage: {target!r}")
    if source == target and source is not None:
        checker.error(f"{path} cannot hand off to itself: {source}")
    if source in stage_ids and target in stage_ids and not depends_transitively(stage_map, source, target):
        checker.required(False, f"{path} links {source} to {target}, but target does not depend on source.")
    for field in ("artifact", "mapping", "units", "validity", "acceptance"):
        value = handoff.get(field)
        checker.required(isinstance(value, str) and bool(value.strip()), f"{path}.{field} is required.")
    for field in ("quantity_type", "schema", "basis", "state_variables", "uncertainty"):
        value = handoff.get(field)
        checker.required(isinstance(value, str) and bool(value.strip()), f"{path}.{field} is required for strict handoff review.")


def check_handoff_csv(path: Path, manifest_handoffs: list[dict[str, Any]], checker: Checker) -> None:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            headers = set(reader.fieldnames or [])
            missing = sorted(REQUIRED_HANDOFF_HEADERS - headers)
            if missing:
                checker.error(f"Handoff register is missing headers: {', '.join(missing)}")
                return
            missing_recommended = sorted(RECOMMENDED_HANDOFF_HEADERS - headers)
            if missing_recommended:
                checker.required(False, f"Handoff register is missing strict-review headers: {', '.join(missing_recommended)}")
            rows = list(reader)
    except FileNotFoundError:
        checker.error(f"Handoff register does not exist: {path}")
        return
    except OSError as exc:
        checker.error(f"Could not read handoff register {path}: {exc}")
        return

    ids: set[str] = set()
    for index, row in enumerate(rows, 2):
        item_id = (row.get("handoff_id") or "").strip()
        if not item_id:
            checker.error(f"Handoff register row {index} has no handoff_id.")
        elif item_id in ids:
            checker.error(f"Duplicate handoff register id: {item_id}")
        ids.add(item_id)
        for field in REQUIRED_HANDOFF_HEADERS - {"handoff_id"}:
            value = (row.get(field) or "").strip()
            checker.required(bool(value), f"Handoff register row {index} has empty {field}.")
            if value and PLACEHOLDER_RE.search(value):
                checker.required(False, f"Handoff register row {index} has unresolved {field}: {value}")
        for field in RECOMMENDED_HANDOFF_HEADERS:
            value = (row.get(field) or "").strip()
            if field in headers:
                checker.required(bool(value), f"Handoff register row {index} has empty strict-review field {field}.")
                if value and PLACEHOLDER_RE.search(value):
                    checker.required(False, f"Handoff register row {index} has unresolved {field}: {value}")

    manifest_ids = {
        item.get("id")
        for item in manifest_handoffs
        if isinstance(item, dict) and isinstance(item.get("id"), str) and item.get("id")
    }
    if manifest_ids and ids != manifest_ids:
        checker.required(False, f"Manifest/register handoff IDs differ: manifest={sorted(manifest_ids)}, register={sorted(ids)}")


def check_planning_artifact(
    payload: dict[str, Any],
    project_root: Path,
    claim_ids: set[str],
    stage_ids: set[str],
    checker: Checker,
) -> dict[str, Any] | None:
    if payload.get("schema_version") != "1.1":
        return None

    artifact = payload.get("planning_artifact")
    if not isinstance(artifact, dict):
        checker.error("schema 1.1 requires a planning_artifact object.")
        return None

    raw_path = artifact.get("path")
    if not isinstance(raw_path, str) or not raw_path.strip():
        checker.error("planning_artifact.path must be a non-empty project-relative path.")
        return None
    candidate = Path(raw_path)
    if candidate.is_absolute():
        checker.error("planning_artifact.path must be project-relative, not absolute.")
        return None
    plan_path = (project_root / candidate).resolve()
    if plan_path != project_root and project_root not in plan_path.parents:
        checker.error("planning_artifact.path escapes the project root.")
        return None

    status = artifact.get("status")
    if status not in PLAN_STATUSES:
        checker.error("planning_artifact.status must be draft, current, stale, or superseded.")

    declared_sections = artifact.get("required_sections")
    if not isinstance(declared_sections, list) or not all(isinstance(item, str) for item in declared_sections):
        checker.error("planning_artifact.required_sections must be a list of section names.")
    else:
        missing_sections = sorted(set(PLAN_REQUIRED_SECTIONS) - set(declared_sections))
        if missing_sections:
            checker.error(f"planning_artifact.required_sections omits: {', '.join(missing_sections)}")

    synchronization = artifact.get("synchronizes")
    if not isinstance(synchronization, list) or not all(isinstance(item, str) for item in synchronization):
        checker.error("planning_artifact.synchronizes must be a list of control-plane names.")
    else:
        missing_sync = sorted(REQUIRED_PLAN_SYNCHRONIZATION - set(synchronization))
        if missing_sync:
            checker.error(f"planning_artifact.synchronizes omits: {', '.join(missing_sync)}")

    result = inspect_plan(
        plan_path,
        expected_claim_ids=sorted(claim_ids),
        expected_stage_ids=sorted(stage_ids),
        require_current=checker.strict,
        strict=checker.strict,
    )
    for message in result["errors"]:
        checker.error(f"Planning artifact: {message}")
    for message in result["warnings"]:
        checker.warning(f"Planning artifact: {message}")

    document_status = result.get("status")
    if isinstance(status, str) and isinstance(document_status, str) and status != document_status:
        checker.required(False, f"Planning artifact status drift: manifest={status!r}, document={document_status!r}")

    snapshot = result.get("snapshot")
    spine = payload.get("research_spine")
    if isinstance(snapshot, dict) and isinstance(spine, dict):
        for field in ("objective", "active_claim_id", "current_gate", "next_action", "stop_rule"):
            manifest_value = str(spine.get(field, "")).strip().strip("`")
            document_value = str(snapshot.get(field, "")).strip().strip("`")
            if manifest_value and document_value and manifest_value != document_value:
                checker.required(
                    False,
                    f"Planning artifact control-snapshot drift for {field}: manifest={manifest_value!r}, document={document_value!r}",
                )
    return result


def validate(
    payload: dict[str, Any],
    checker: Checker,
    handoff_register: Path | None = None,
    project_root: Path | None = None,
) -> dict[str, Any]:
    missing = sorted(REQUIRED_TOP_LEVEL - set(payload))
    if missing:
        checker.error(f"Manifest is missing top-level keys: {', '.join(missing)}")
    if payload.get("schema_version") not in SUPPORTED_SCHEMA_VERSIONS:
        checker.error(f"Unsupported schema_version: {payload.get('schema_version')!r}")
    if not isinstance(payload.get("project"), dict):
        checker.error("project must be an object.")

    scale_decision = payload.get("scale_decision")
    checker.required(isinstance(scale_decision, dict), "scale_decision is required for an auditable scale choice.")
    if isinstance(scale_decision, dict):
        required_scales = scale_decision.get("required_scales")
        deferred_scales = scale_decision.get("deferred_scales")
        checker.required(
            isinstance(required_scales, list) and all(isinstance(item, str) for item in required_scales),
            "scale_decision.required_scales must be a list of strings.",
        )
        if isinstance(required_scales, list) and len(required_scales) != len(set(required_scales)):
            checker.required(False, "scale_decision.required_scales contains duplicates.")
        checker.required(
            isinstance(deferred_scales, list) and all(isinstance(item, str) for item in deferred_scales),
            "scale_decision.deferred_scales must be a list of strings.",
        )
        for field in ("rationale", "escalation_trigger"):
            value = scale_decision.get(field)
            checker.required(isinstance(value, str) and bool(value.strip()), f"scale_decision.{field} is required.")

    research_spine = payload.get("research_spine")
    checker.required(isinstance(research_spine, dict), "research_spine is required for an auditable long-task orientation.")

    claims = as_list(payload.get("claims"), "claims", checker)
    claim_map = check_unique_ids(claims, "claims", checker)
    for item_id, item in claim_map.items():
        checker.required(isinstance(item.get("text"), str) and bool(item["text"].strip()), f"claims[{item_id}].text is required.")
        checker.required(isinstance(item.get("observable"), str) and bool(item["observable"].strip()), f"claims[{item_id}].observable is required.")
        checker.required(isinstance(item.get("pass_condition"), str) and bool(item["pass_condition"].strip()), f"claims[{item_id}].pass_condition is required.")
    if isinstance(research_spine, dict):
        for field in ("objective", "active_claim_id", "current_gate", "next_action", "stop_rule"):
            value = research_spine.get(field)
            checker.required(isinstance(value, str) and bool(value.strip()), f"research_spine.{field} is required.")
        active_claim = research_spine.get("active_claim_id")
        if active_claim and active_claim not in claim_map:
            checker.error(f"research_spine.active_claim_id references unknown claim: {active_claim}")

    stages = as_list(payload.get("stages"), "stages", checker)
    stage_map = check_unique_ids(stages, "stages", checker)
    stage_ids = set(stage_map)
    claim_ids = set(claim_map)
    for item_id, item in stage_map.items():
        check_stage_fields(item, f"stages[{item_id}]", claim_ids, stage_ids, checker)
    cycle = find_cycle(stage_map) if stage_map else None
    if cycle:
        checker.error(f"Stage dependency cycle detected: {' -> '.join(cycle)}")

    if isinstance(scale_decision, dict) and isinstance(scale_decision.get("required_scales"), list):
        declared_scales = {item for item in scale_decision["required_scales"] if isinstance(item, str)}
        expected_scales = {STAGE_SCALES[item["kind"]] for item in stage_map.values() if item.get("kind") in STAGE_SCALES}
        missing_scales = sorted(expected_scales - declared_scales)
        extra_scales = sorted(declared_scales - expected_scales)
        if missing_scales:
            checker.error(f"scale_decision omits scales required by stages: {', '.join(missing_scales)}")
        if extra_scales:
            checker.required(False, f"scale_decision declares scales with no matching stage: {', '.join(extra_scales)}")

    handoffs = as_list(payload.get("handoffs"), "handoffs", checker)
    handoff_map = check_unique_ids(handoffs, "handoffs", checker)
    for item_id, item in handoff_map.items():
        check_handoff_fields(item, f"handoffs[{item_id}]", stage_ids, stage_map, checker)
    handoff_edges = {
        (item.get("from_stage"), item.get("to_stage"))
        for item in handoff_map.values()
        if item.get("from_stage") in stage_ids and item.get("to_stage") in stage_ids
    }
    for target_id, stage in stage_map.items():
        for source_id in stage.get("depends_on", []) or []:
            if source_id not in stage_map:
                continue
            source_scale = STAGE_SCALES.get(stage_map[source_id].get("kind"))
            target_scale = STAGE_SCALES.get(stage.get("kind"))
            if source_scale and target_scale and source_scale != target_scale and (source_id, target_id) not in handoff_edges:
                checker.required(False, f"Cross-scale dependency {source_id} -> {target_id} has no explicit handoff.")
    if handoff_register:
        check_handoff_csv(handoff_register, handoffs, checker)

    planning_artifact = check_planning_artifact(
        payload,
        (project_root or Path.cwd()).resolve(),
        claim_ids,
        stage_ids,
        checker,
    )

    placeholder_count = check_placeholders(payload, "$", checker)
    return {
        "schema_version": payload.get("schema_version"),
        "scale_decision": scale_decision if isinstance(scale_decision, dict) else None,
        "research_spine": research_spine if isinstance(research_spine, dict) else None,
        "claims": len(claim_map),
        "stages": len(stage_map),
        "handoffs": len(handoff_map),
        "planning_artifact": planning_artifact,
        "placeholders": placeholder_count,
        "errors": checker.errors,
        "warnings": checker.warnings,
        "strict": checker.strict,
        "valid": not checker.errors,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a multiscale experiment manifest, integrated plan, and optional handoff register.")
    parser.add_argument("--manifest", type=Path, required=True, help="Path to workflow/experiment_manifest.json.")
    parser.add_argument("--handoff-register", type=Path, help="Optional path to workflow/handoff_register.csv.")
    parser.add_argument("--strict", action="store_true", help="Treat unresolved placeholders and incomplete templates as errors.")
    parser.add_argument("--pretty", action="store_true", help="Print a human-readable report.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    checker = Checker(strict=args.strict)
    manifest_path = args.manifest.expanduser().resolve()
    payload = load_json(manifest_path, checker)
    if payload is not None:
        result = validate(
            payload,
            checker,
            args.handoff_register.expanduser().resolve() if args.handoff_register else None,
            manifest_path.parent.parent,
        )
    else:
        result = {"errors": checker.errors, "warnings": checker.warnings, "valid": False, "strict": checker.strict}
    if args.pretty:
        print(f"Valid: {'yes' if result.get('valid') else 'no'}")
        print(f"Strict: {'yes' if result.get('strict') else 'no'}")
        for key in ("claims", "stages", "handoffs", "placeholders"):
            if key in result:
                print(f"{key}: {result[key]}")
        for message in result.get("errors", []):
            print(f"ERROR: {message}")
        for message in result.get("warnings", []):
            print(f"WARNING: {message}")
    else:
        json.dump(result, sys.stdout, indent=2)
        print()
    return 0 if result.get("valid") else 1


if __name__ == "__main__":
    raise SystemExit(main())
