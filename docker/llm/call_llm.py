#!/usr/bin/env python3
"""
ABOUTME: Makes real API calls to Moonshot LLM.
ABOUTME: Used for lessons 00, 04, 05 — real LLM responses.
"""

import json
import os
import sys
import urllib.request
import urllib.error


MOONSHOT_URL = "https://api.moonshot.cn/v1/chat/completions"
DEFAULT_MODEL = "moonshot-v1-8k"


def call_llm(user_input, system_prompt=None):
    """Call Moonshot API with user input and return response text."""
    api_key = os.environ.get("LLM_API_KEY", "")

    if not api_key:
        return "Error: No API key configured. Please set LLM_API_KEY environment variable."

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_input})

    payload = {
        "model": DEFAULT_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 500
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(MOONSHOT_URL, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            content = result["choices"][0]["message"]["content"]
            
            # Also show some metadata for educational purposes
            usage = result.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", "?")
            completion_tokens = usage.get("completion_tokens", "?")
            total_tokens = usage.get("total_tokens", "?")
            model = result.get("model", DEFAULT_MODEL)
            
            output = f"{content}\n\n"
            output += f"--- API Response Metadata ---\n"
            output += f"Model: {model}\n"
            output += f"Prompt tokens: {prompt_tokens}\n"
            output += f"Response tokens: {completion_tokens}\n"
            output += f"Total tokens: {total_tokens}"
            return output

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.readable() else ""
        return f"API Error ({e.code}): {error_body}"
    except urllib.error.URLError as e:
        return f"Connection Error: {e.reason}"
    except Exception as e:
        return f"Error: {str(e)}"


def call_llm_from_json(json_input):
    """Call Moonshot API from a full JSON request (for lessons 04/05)."""
    api_key = os.environ.get("LLM_API_KEY", "")

    if not api_key:
        return "Error: No API key configured. Please set LLM_API_KEY environment variable."

    try:
        payload = json.loads(json_input)
    except json.JSONDecodeError as e:
        return f"Invalid JSON: {e}"

    # Override model if not provided
    if "model" not in payload:
        payload["model"] = DEFAULT_MODEL

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(MOONSHOT_URL, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            return json.dumps(result, indent=2)

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.readable() else ""
        return f"API Error ({e.code}): {error_body}"
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: call-llm <input_file> [--json]")
        sys.exit(1)

    filepath = sys.argv[1]
    as_json = "--json" in sys.argv

    with open(filepath) as f:
        content = f.read().strip()

    if as_json:
        print(call_llm_from_json(content))
    else:
        print(call_llm(content))
