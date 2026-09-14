import json
import random

with open("data/processed/chunks.json", encoding="utf-8") as f:
    data = json.load(f)

random.seed(42)
sample = random.sample(data, 8)

for c in sample:
    print(f"--- {c['act']} ({c['id']}) ---")
    print(c["text"][:250])
    print()