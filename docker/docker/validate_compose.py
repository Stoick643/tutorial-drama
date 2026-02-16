#!/usr/bin/env python3
"""
ABOUTME: Validates docker-compose.yml content for tutorial challenges.
ABOUTME: Checks for required services, keys, and structure. Returns PASS/FAIL.
"""

import sys
import yaml


def validate(content, required_checks):
    """Validate docker-compose.yml content.
    
    Args:
        content: YAML content as string
        required_checks: Comma-separated list of checks to perform.
            Supported checks:
            - services: Must have 'services' top-level key
            - service:<name>: Must have a service with this name
            - image:<service>: Service must have 'image' key
            - build:<service>: Service must have 'build' key
            - ports:<service>: Service must have 'ports' key
            - volumes:<service>: Service must have 'volumes' key
            - environment:<service>: Service must have 'environment' key
            - depends_on:<service>: Service must have 'depends_on' key
            - min_services:<n>: Must have at least n services
    
    Returns:
        Tuple of (is_valid, message)
    """
    if not content.strip():
        return False, "FAIL: Compose file is empty"

    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        return False, f"FAIL: Invalid YAML syntax: {e}"

    if not isinstance(data, dict):
        return False, "FAIL: Compose file must be a YAML mapping"

    checks = [c.strip() for c in required_checks.split(',')]
    services = data.get('services', {})

    for check in checks:
        if check == 'services':
            if 'services' not in data:
                return False, "FAIL: Missing 'services' top-level key"

        elif check.startswith('service:'):
            service_name = check.split(':', 1)[1]
            if service_name not in services:
                return False, f"FAIL: Missing service '{service_name}'"

        elif check.startswith('min_services:'):
            min_count = int(check.split(':', 1)[1])
            if len(services) < min_count:
                return False, f"FAIL: Need at least {min_count} services, found {len(services)}"

        elif ':' in check:
            key, service_name = check.split(':', 1)
            if service_name not in services:
                return False, f"FAIL: Service '{service_name}' not found"
            if key not in services[service_name]:
                return False, f"FAIL: Service '{service_name}' is missing '{key}'"

    return True, "PASS"


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: validate_compose.py <file> <required_checks>")
        print("Example: validate_compose.py /tmp/user_input services,service:web,image:web,ports:web")
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
