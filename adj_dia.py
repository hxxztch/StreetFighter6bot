path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()
content = content.replace(
    "(25000, \"Master\", \"M\"),\n        (20000, \"Diamond 5\", \"D5\"),",
    "(25000, \"Master\", \"M\"),\n        (22000, \"Diamond 5\", \"D5\"),")
content = content.replace("(19000, \"Diamond 4\", \"D4\"),", "(20000, \"Diamond 4\", \"D4\"),")
content = content.replace("(18000, \"Diamond 3\", \"D3\"),", "(19000, \"Diamond 3\", \"D3\"),")
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Diamond thresholds: D5>=22000 D4>=20000 D3>=19000")
