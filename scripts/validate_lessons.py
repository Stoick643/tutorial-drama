#!/usr/bin/env python3
"""Validate all lesson JSON files have required fields.

Run: python scripts/validate_lessons.py
"""

import json
import sys
import os
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

REQUIRED_FIELDS = ["tutorial", "module", "scene", "technical_concept", "challenge", "styles"]
REQUIRED_CHALLENGE_FIELDS = ["task", "check_logic"]
REQUIRED_CHECK_LOGIC_FIELDS = ["expected_result"]
REQUIRED_STYLE_FIELDS = ["name", "title", "dialogue"]
VALID_RESULT_TYPES = [
    "exact_match",
    "user_output_exact_match",
    "user_output_contains",
    "user_output_contains_all",
    "integer_greater_than",
    "set_contains",
]

def validate_lesson(path: Path) -> list[str]:
    """Validate a single lesson file. Returns list of errors."""
    errors = []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {e}"]

    # Top-level fields
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    # Challenge validation
    challenge = data.get("challenge", {})
    for field in REQUIRED_CHALLENGE_FIELDS:
        if field not in challenge:
            errors.append(f"Missing challenge.{field}")

    check_logic = challenge.get("check_logic", {})
    if check_logic:
        for field in REQUIRED_CHECK_LOGIC_FIELDS:
            if field not in check_logic:
                errors.append(f"Missing challenge.check_logic.{field}")

        expected = check_logic.get("expected_result", {})
        if "type" not in expected:
            errors.append("Missing challenge.check_logic.expected_result.type")
        elif expected["type"] not in VALID_RESULT_TYPES:
            errors.append(f"Unknown result type: {expected['type']}")

        if "value" not in expected:
            errors.append("Missing challenge.check_logic.expected_result.value")

    # Styles validation
    styles = data.get("styles", [])
    if not styles:
        errors.append("No styles defined")
    for i, style in enumerate(styles):
        for field in REQUIRED_STYLE_FIELDS:
            if field not in style:
                errors.append(f"Style [{i}] missing: {field}")
        if "dialogue" in style and not style["dialogue"]:
            errors.append(f"Style [{i}] ({style.get('name', '?')}): empty dialogue")

    return errors


def main():
    base = Path(__file__).resolve().parent.parent / "tutorials"
    total_errors = 0
    total_files = 0

    for topic_dir in sorted(base.iterdir()):
        if not topic_dir.is_dir():
            continue
        for lesson_file in sorted(topic_dir.glob("*.json")):
            total_files += 1
            errors = validate_lesson(lesson_file)
            if errors:
                print(f"\n❌ {topic_dir.name}/{lesson_file.name}:")
                for err in errors:
                    print(f"   - {err}")
                total_errors += len(errors)
            else:
                print(f"✅ {topic_dir.name}/{lesson_file.name}")

    print(f"\n{'='*40}")
    print(f"Files: {total_files}, Errors: {total_errors}")

    if total_errors > 0:
        sys.exit(1)
    else:
        print("All lessons valid! ✅")


if __name__ == "__main__":
    main()
