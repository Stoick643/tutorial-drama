#!/usr/bin/env python3
"""
ABOUTME: Dispatcher for LLM tutorial grading.
ABOUTME: Reads /tmp/llm_mode to determine which tool to run on /tmp/user_input.
Modes: call-llm, tokenize, similarity, echo
"""

import sys
import os

def main():
    mode_file = "/tmp/llm_mode"
    # Check both paths: Docker uses /tmp/user_input, subprocess uses /tmp/grader-user-input
    input_file = "/tmp/user_input"
    if not os.path.exists(input_file):
        input_file = "/tmp/grader-user-input"

    if not os.path.exists(mode_file):
        print("Error: No mode set. Missing /tmp/llm_mode")
        sys.exit(1)

    if not os.path.exists(input_file):
        print("Error: No input. Missing /tmp/user_input")
        sys.exit(1)

    mode = open(mode_file).read().strip()
    user_input = open(input_file).read().strip()

    if mode == "call-llm":
        from call_llm import call_llm
        result = call_llm(user_input)
        print(result)

    elif mode == "tokenize":
        from tokenize_text import tokenize
        result = tokenize(user_input)
        print(result)

    elif mode == "similarity":
        from compute_similarity import compute
        result = compute(user_input)
        print(result)

    elif mode == "echo":
        # Just echo back the input (for validation-only lessons)
        print(user_input)

    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)

if __name__ == "__main__":
    main()
