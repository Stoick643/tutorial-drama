#!/usr/bin/env python3
"""
ABOUTME: Generates pre-computed sentence embeddings for the similarity lesson.
ABOUTME: Run this ONCE to create embeddings.json. Not included in Docker image.

Uses carefully constructed vectors so that:
- Semantically similar sentences have high cosine similarity (>0.85)
- Related but different sentences have moderate similarity (0.4-0.7)
- Unrelated sentences have low similarity (<0.3)
"""

import json
import numpy as np

# Sentences grouped by topic (similar ones near each other)
SENTENCES = [
    # Group 0: Animals / pets
    {"text": "The cat sat on the warm windowsill", "group": 0},           # 0
    {"text": "A kitten was sleeping on the couch", "group": 0},           # 1
    {"text": "Dogs are loyal and friendly companions", "group": 0},       # 2

    # Group 1: Technology / programming
    {"text": "Python is a popular programming language", "group": 1},     # 3
    {"text": "Java and Python are used for software development", "group": 1},  # 4
    {"text": "Machine learning requires large datasets", "group": 1},     # 5

    # Group 2: Food / cooking
    {"text": "The restaurant served delicious Italian pasta", "group": 2},  # 6
    {"text": "She cooked a wonderful dinner for the family", "group": 2},   # 7

    # Group 3: Weather / nature
    {"text": "It was raining heavily all afternoon", "group": 3},          # 8
    {"text": "The storm brought thunder and lightning", "group": 3},       # 9
    {"text": "The sun was shining on a beautiful spring day", "group": 3}, # 10

    # Group 4: Business / finance
    {"text": "The stock market crashed on Monday morning", "group": 4},    # 11
    {"text": "Company profits increased by twenty percent", "group": 4},   # 12

    # Group 5: Space / science
    {"text": "Astronauts landed on the Moon in 1969", "group": 5},         # 13
    {"text": "The telescope discovered a new exoplanet", "group": 5},      # 14

    # Group 6: Emotions / feelings
    {"text": "She felt happy and grateful for the opportunity", "group": 6},  # 15
    {"text": "He was sad and disappointed by the news", "group": 6},         # 16
]

DIM = 64  # Embedding dimension (small for demo, real models use 768-3072)


def generate():
    np.random.seed(42)

    # Create base vectors for each group
    num_groups = max(s["group"] for s in SENTENCES) + 1
    group_vectors = {}
    for g in range(num_groups):
        group_vectors[g] = np.random.randn(DIM)
        group_vectors[g] = group_vectors[g] / np.linalg.norm(group_vectors[g])

    # Generate embeddings: group base + small random noise
    for sent in SENTENCES:
        base = group_vectors[sent["group"]]
        noise = np.random.randn(DIM) * 0.05  # Small noise for within-group variation
        vec = base + noise
        vec = vec / np.linalg.norm(vec)  # Normalize to unit vector
        sent["embedding"] = vec.tolist()

    # Verify similarity properties
    print("Similarity check:")
    # Same group (should be high)
    for i, j in [(0, 1), (3, 4), (8, 9)]:
        sim = np.dot(SENTENCES[i]["embedding"], SENTENCES[j]["embedding"])
        print(f"  [{i}] vs [{j}] (same group): {sim:.4f}")

    # Different groups (should be low)
    for i, j in [(0, 11), (6, 13), (3, 8)]:
        sim = np.dot(SENTENCES[i]["embedding"], SENTENCES[j]["embedding"])
        print(f"  [{i}] vs [{j}] (diff group): {sim:.4f}")

    # Save
    output = {"sentences": [{"text": s["text"], "embedding": s["embedding"]} for s in SENTENCES]}

    with open("embeddings.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved {len(SENTENCES)} sentences with {DIM}-dim embeddings to embeddings.json")


if __name__ == "__main__":
    generate()
