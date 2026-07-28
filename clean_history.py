import json

with open("release_history.json", "r", encoding="utf-8-sig") as f:
    history = json.load(f)

cleaned = [
    h for h in history
    if "pokemon" in h["title"].lower() or "pokémon" in h["title"].lower()
]

removed = len(history) - len(cleaned)
print(f"Removed {removed} non-Pokemon entries")

with open("release_history.json", "w", encoding="utf-8") as f:
    json.dump(cleaned, f, indent=2)
