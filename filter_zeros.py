path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = "data.characters.sort(key=lambda x: (x.league_points if hasattr(x,\"league_points\") else -1, x.usage_count), reverse=True)"
new = "data.characters = [c for c in data.characters if c.total > 0]\n    data.characters.sort(key=lambda x: (x.league_points if hasattr(x,\"league_points\") else -1, x.usage_count), reverse=True)"
content = content.replace(old, new)
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Zero-battle characters filtered out")
