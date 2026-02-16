#!/usr/bin/env python3
"""
ABOUTME: Validates Dockerfile content for tutorial challenges.
ABOUTME: Checks for required instructions and returns PASS/FAIL with details.
"""

import sys
import re

VALID_INSTRUCTIONS = {
    'FROM', 'RUN', 'CMD', 'LABEL', 'MAINTAINER', 'EXPOSE', 'ENV',
    'ADD', 'COPY', 'ENTRYPOINT', 'VOLUME', 'USER', 'WORKDIR', 'ARG',
    'ONBUILD', 'STOPSIGNAL', 'HEALTHCHECK', 'SHELL'
}


def parse_dockerfile(content):
    """Parse Dockerfile content and extract instructions."""
    instructions = []
    for line in content.strip().split('\n'):
        line = line.strip()
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue
        # Extract instruction name
        parts = line.split(None, 1)
        if parts:
            instruction = parts[0].upper()
            value = parts[1] if len(parts) > 1 else ''
            instructions.append((instruction, value))
    return instructions


def validate(content, required_instructions):
    """Validate Dockerfile against required instructions.
    
    Args:
        content: Dockerfile content as string
        required_instructions: Comma-separated list of required instructions
    
    Returns:
        Tuple of (is_valid, message)
    """
    if not content.strip():
        return False, "FAIL: Dockerfile is empty"

    instructions = parse_dockerfile(content)
    found_instructions = [inst[0] for inst in instructions]

    # Check for valid Dockerfile structure
    if not instructions:
        return False, "FAIL: No valid instructions found"

    # Check that first instruction is FROM
    if found_instructions[0] != 'FROM':
        return False, "FAIL: Dockerfile must start with FROM instruction"

    # Check required instructions
    required = [r.strip().upper() for r in required_instructions.split(',')]
    missing = [r for r in required if r not in found_instructions]

    if missing:
        return False, f"FAIL: Missing required instructions: {', '.join(missing)}"

    return True, "PASS"


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: validate_dockerfile.py <file> <required_instructions>")
        print("Example: validate_dockerfile.py /tmp/user_input FROM,RUN,CMD")
        sys.exit(1)

    filepath = sys.argv[1]
    required = sys.argv[2]

    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("FAIL: No input provided")
        sys.exit(1)

    is_valid, message = validate(content, required)
    print(message)
    sys.exit(0 if is_valid else 1)
