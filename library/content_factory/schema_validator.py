#!/usr/bin/env python3
"""
Schema Validator for Papercraft Content Factory Artifacts.
Validates all structured JSON artifacts against formal JSON schemas.
"""

import os
import json
from typing import Dict, Any, Tuple, List, Optional
import jsonschema

SCHEMA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schemas")

SCHEMA_MAP = {
    "dossier": "dossier_schema.json",
    "hook_matrix": "hook_matrix_schema.json",
    "audience_plan": "audience_plan_schema.json",
    "script": "script_schema.json",
    "storyboard": "storyboard_schema.json",
    "asset_plan": "asset_plan_schema.json",
    "audio_plan": "audio_plan_schema.json",
    "workflow_state": "workflow_state_schema.json",
    "qa_report": "qa_report_schema.json",
    "trends": "trends_schema.json",
    "trend_intelligence": "trend_intelligence_schema.json",
    "publishing_kit": "publishing_kit_schema.json",
    "captions": "captions_schema.json"
}


def load_schema(artifact_type: str) -> Dict[str, Any]:
    if artifact_type not in SCHEMA_MAP:
        raise ValueError(f"Unknown artifact type: '{artifact_type}'. Known: {list(SCHEMA_MAP.keys())}")
    schema_path = os.path.join(SCHEMA_DIR, SCHEMA_MAP[artifact_type])
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_artifact(artifact_type: str, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate data dictionary against specified artifact type schema.
    Returns (is_valid, list_of_error_messages).
    """
    try:
        schema = load_schema(artifact_type)
    except Exception as e:
        return False, [f"Could not load schema for '{artifact_type}': {e}"]

    validator = jsonschema.Draft7Validator(schema)
    errors = []
    for err in sorted(validator.iter_errors(data), key=lambda e: e.path):
        loc = ".".join(str(p) for p in err.path) or "root"
        errors.append(f"[{loc}] {err.message}")

    return len(errors) == 0, errors


def validate_artifact_file(artifact_type: str, file_path: str) -> Tuple[bool, List[str]]:
    """Validate JSON file on disk against schema."""
    if not os.path.exists(file_path):
        return False, [f"File not found: {file_path}"]
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return False, [f"Malformed JSON in {file_path}: {e}"]

    return validate_artifact(artifact_type, data)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python3 schema_validator.py <artifact_type> <json_file_path>")
        sys.exit(2)
    t, p = sys.argv[1], sys.argv[2]
    valid, errs = validate_artifact_file(t, p)
    if valid:
        print(f"[OK] {p} conforms to {t} schema.")
        sys.exit(0)
    else:
        print(f"[FAIL] {p} failed {t} validation:")
        for err in errs:
            print(f"  - {err}")
        sys.exit(1)
