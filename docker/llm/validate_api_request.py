#!/usr/bin/env python3
"""
ABOUTME: Validates LLM API request JSON structure.
ABOUTME: Used for lessons 03 and 05 — checks for required fields and valid values.

Checks can include:
  - basic: valid JSON, has model, has messages
  - roles: messages include system and user roles
  - params: has temperature (0-2) and max_tokens (>0)
  - context: system message contains provided context string
"""

import sys
import json


def validate(content, checks):
    """Validate API request JSON.
    
    Args:
        content: JSON string
        checks: Comma-separated list of checks to perform
    
    Returns:
        Tuple of (is_valid, message)
    """
    if not content.strip():
        return False, "FAIL: Empty input"

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        return False, f"FAIL: Invalid JSON syntax — {e}"

    if not isinstance(data, dict):
        return False, "FAIL: Request must be a JSON object"

    check_list = [c.strip() for c in checks.split(",")]

    for check in check_list:
        if check == "basic":
            if "model" not in data:
                return False, "FAIL: Missing 'model' field"
            if not isinstance(data["model"], str) or not data["model"]:
                return False, "FAIL: 'model' must be a non-empty string"
            if "messages" not in data:
                return False, "FAIL: Missing 'messages' array"
            if not isinstance(data["messages"], list) or len(data["messages"]) == 0:
                return False, "FAIL: 'messages' must be a non-empty array"

        elif check == "roles":
            messages = data.get("messages", [])
            roles_found = set()
            for msg in messages:
                if not isinstance(msg, dict):
                    return False, "FAIL: Each message must be an object with 'role' and 'content'"
                if "role" not in msg:
                    return False, "FAIL: Each message must have a 'role' field"
                if "content" not in msg:
                    return False, "FAIL: Each message must have a 'content' field"
                roles_found.add(msg["role"])

            if "system" not in roles_found:
                return False, "FAIL: Missing message with role 'system'"
            if "user" not in roles_found:
                return False, "FAIL: Missing message with role 'user'"

        elif check == "params":
            if "temperature" not in data:
                return False, "FAIL: Missing 'temperature' parameter"
            temp = data["temperature"]
            if not isinstance(temp, (int, float)):
                return False, "FAIL: 'temperature' must be a number"
            if temp < 0 or temp > 2:
                return False, "FAIL: 'temperature' must be between 0 and 2"

            if "max_tokens" not in data:
                return False, "FAIL: Missing 'max_tokens' parameter"
            mt = data["max_tokens"]
            if not isinstance(mt, int) or mt <= 0:
                return False, "FAIL: 'max_tokens' must be a positive integer"

        elif check.startswith("context:"):
            # Check that system message contains a specific string
            required_text = check.split(":", 1)[1]
            messages = data.get("messages", [])
            system_content = ""
            for msg in messages:
                if msg.get("role") == "system":
                    system_content = msg.get("content", "")
                    break
            if required_text not in system_content:
                return False, f"FAIL: System message must include the provided context about '{required_text}'"

    return True, "PASS"


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: validate-api-request <file> <checks>")
        print("Example: validate-api-request /tmp/user_input basic,roles,params")
        sys.exit(1)

    filepath = sys.argv[1]
    checks = sys.argv[2]

    try:
        with open(filepath) as f:
            content = f.read()
    except FileNotFoundError:
        print("FAIL: No input provided")
        sys.exit(1)

    is_valid, message = validate(content, checks)
    print(message)
    sys.exit(0 if is_valid else 1)
