#!/usr/bin/env python3
"""
ABOUTME: Tokenizes text using tiktoken and shows splits, IDs, and count.
ABOUTME: Used for lesson 01 — real tokenization demonstration.
"""

import sys
import tiktoken


def tokenize(text):
    """Tokenize text and return formatted output showing splits, IDs, and count."""
    # Use cl100k_base encoding (used by GPT-4, similar to what most modern LLMs use)
    enc = tiktoken.get_encoding("cl100k_base")

    tokens = enc.encode(text)
    decoded = [enc.decode([t]) for t in tokens]

    output = f"Input text: \"{text}\"\n\n"
    output += f"Token splits:\n"
    for i, (token_id, token_text) in enumerate(zip(tokens, decoded)):
        # Show the token text with visible representation of spaces
        visible = token_text.replace(" ", "\u2581")  # Use underscore for spaces
        output += f"  [{i}] \"{visible}\" (ID: {token_id})\n"

    output += f"\nTotal tokens: {len(tokens)}\n"
    output += f"Characters: {len(text)}\n"
    output += f"Ratio: {len(text)/len(tokens):.1f} chars per token\n"

    # Fun facts
    output += f"\n--- Token Insights ---\n"
    if len(tokens) == 1:
        output += f"Your entire input is a single token!\n"
    elif len(tokens) > len(text.split()):
        output += f"More tokens ({len(tokens)}) than words ({len(text.split())}) — some words were split into subwords.\n"
    elif len(tokens) < len(text.split()):
        output += f"Fewer tokens ({len(tokens)}) than words ({len(text.split())}) — some words merged with adjacent spaces.\n"
    else:
        output += f"Token count matches word count — each word maps to roughly one token.\n"

    return output


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: tokenize-text <input_file>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        text = f.read().strip()

    print(tokenize(text))
