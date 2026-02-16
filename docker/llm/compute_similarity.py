#!/usr/bin/env python3
"""
ABOUTME: Computes cosine similarity between pre-computed sentence embeddings.
ABOUTME: Used for lesson 02 — demonstrates how LLMs understand meaning through vectors.

Students pick two sentences by number and see the similarity score.
Input format: "1 5" (two sentence numbers) or "1,5"
"""

import sys
import json
import numpy as np
import os

EMBEDDINGS_FILE = "/data/embeddings.json"


def load_embeddings():
    """Load pre-computed sentence embeddings."""
    with open(EMBEDDINGS_FILE) as f:
        return json.load(f)


def cosine_similarity(a, b):
    """Compute cosine similarity between two vectors."""
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def compute(user_input):
    """Parse user input, look up sentences, compute similarity."""
    data = load_embeddings()
    sentences = data["sentences"]

    # Show available sentences if input is "list" or empty
    if not user_input or user_input.strip().lower() == "list":
        output = "Available sentences:\n"
        for i, s in enumerate(sentences):
            output += f"  [{i}] \"{s['text']}\"\n"
        output += f"\nType two numbers to compare, e.g.: 0 3"
        return output

    # Parse two numbers from input
    import re
    numbers = re.findall(r'\d+', user_input)

    if len(numbers) < 2:
        output = "Please enter two sentence numbers to compare.\n\n"
        output += "Available sentences:\n"
        for i, s in enumerate(sentences):
            output += f"  [{i}] \"{s['text']}\"\n"
        output += f"\nExample: 0 3"
        return output

    idx_a, idx_b = int(numbers[0]), int(numbers[1])

    if idx_a >= len(sentences) or idx_b >= len(sentences) or idx_a < 0 or idx_b < 0:
        return f"Error: Sentence numbers must be between 0 and {len(sentences)-1}"

    sent_a = sentences[idx_a]
    sent_b = sentences[idx_b]

    sim = cosine_similarity(sent_a["embedding"], sent_b["embedding"])

    output = f"Sentence A [{idx_a}]: \"{sent_a['text']}\"\n"
    output += f"Sentence B [{idx_b}]: \"{sent_b['text']}\"\n\n"
    output += f"Cosine similarity: {sim:.4f}\n\n"

    if sim > 0.85:
        output += f"Very similar! These sentences express closely related meanings.\n"
    elif sim > 0.6:
        output += f"Moderately similar. Some shared meaning or topic.\n"
    elif sim > 0.3:
        output += f"Somewhat related, but different topics or perspectives.\n"
    else:
        output += f"Very different meanings. These sentences are far apart in vector space.\n"

    output += f"\n--- How This Works ---\n"
    output += f"Each sentence is converted to a vector of {len(sent_a['embedding'])} numbers.\n"
    output += f"Cosine similarity measures the angle between vectors.\n"
    output += f"1.0 = identical meaning, 0.0 = completely unrelated, -1.0 = opposite.\n"
    output += f"This is how search engines and RAG systems find relevant documents."

    return output


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: compute-similarity <input_file>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        text = f.read().strip()

    print(compute(text))
