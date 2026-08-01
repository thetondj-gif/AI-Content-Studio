#!/usr/bin/env python3
"""Offline acceptance for DAWN-native media production pattern specs."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
ALLOWED_STAGES = {
    "research", "script", "scene_segmentation", "captions", "chapters",
    "thumbnail_spec", "ffmpeg_plan", "publishing_metadata",
}
EXISTING_DAWN_SERVICES = {"comfyui", "postiz", "google-flow", "ffmpeg", "drive"}


def validate(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if plan.get("schema_version") != 1:
        errors.append("schema_version")
    stages = plan.get("stages")
    if not isinstance(stages, list) or not stages or not set(stages).issubset(ALLOWED_STAGES):
        errors.append("stage_allowlist")
    if plan.get("provider_neutral") is not True:
        errors.append("provider_neutral_required")
    if plan.get("direct_publish") is not False:
        errors.append("direct_publish_prohibited")
    if plan.get("production_credentials_present") is not False:
        errors.append("credentials_prohibited")
    if plan.get("network_execution") is not False:
        errors.append("offline_gate_only")
    if plan.get("copy_upstream_implementation") is not False:
        errors.append("implementation_copy_prohibited")
    output = str(plan.get("output_root", ""))
    if not output.startswith("dawn-integration/evidence/"):
        errors.append("output_boundary")
    mappings = plan.get("existing_service_mappings")
    if not isinstance(mappings, dict) or not mappings:
        errors.append("service_mapping_required")
    else:
        unknown = {str(value) for value in mappings.values()} - EXISTING_DAWN_SERVICES
        if unknown:
            errors.append("unknown_service_mapping")
    if plan.get("duplication_reviewed") is not True:
        errors.append("duplication_review")
    return errors


def evaluate(plan: dict[str, Any]) -> dict[str, Any]:
    errors = validate(plan)
    return {
        "schema_version": 1,
        "capability": "dawn-media-production-patterns",
        "operation": "validate-pattern-spec",
        "status": "blocked" if errors else "success",
        "evidence": ["policy:original-dawn-specification", "policy:no-direct-publish"],
        "data": {"pattern_spec_accepted": not errors, "media_generated": False, "published": False},
        "warnings": errors,
        "cost": {"currency": "USD", "estimated": 0},
        "external_actions_performed": False,
    }


def main() -> int:
    valid = json.loads((ROOT / "fixtures" / "valid-plan.json").read_text())
    invalid = json.loads((ROOT / "fixtures" / "invalid-plan.json").read_text())
    accepted = evaluate(valid)
    refused = evaluate(invalid)
    assertions = [
        accepted["status"] == "success",
        accepted["data"]["media_generated"] is False,
        accepted["data"]["published"] is False,
        accepted["external_actions_performed"] is False,
        refused["status"] == "blocked",
        "direct_publish_prohibited" in refused["warnings"],
        "implementation_copy_prohibited" in refused["warnings"],
        "duplication_review" in refused["warnings"],
    ]
    report = {
        "capability": "dawn-media-production-patterns",
        "status": "passed" if all(assertions) else "failed",
        "tests": len(assertions),
        "passed": sum(assertions),
        "network_used": False,
        "credentials_required": False,
        "media_generated": False,
        "published": False,
        "external_actions_performed": False,
    }
    print(json.dumps(report, indent=2))
    return 0 if all(assertions) else 1


if __name__ == "__main__":
    sys.exit(main())
