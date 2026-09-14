import json

with open("data/processed/chunks.json", encoding="utf-8") as f:
    data = json.load(f)

suspicious = []
for c in data:
    text = c["text"]
    # crude heuristic: lots of short fragment-like lines close together
    short_lines = sum(1 for line in text.split("\n") if 0 < len(line.strip()) < 15)
    if short_lines >= 4:
        suspicious.append(c)

print(f"Flagged {len(suspicious)} out of {len(data)} chunks as possibly garbled")
for c in suspicious[:5]:
    print(f"\n--- {c['act']} ({c['id']}) ---")
    print(c["text"][:200])