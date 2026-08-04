path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix dump path to use absolute
old = """DUMP_DIR / f"{sf6_id}_small_page.html""
new = """DUMP_DIR / f"{sf6_id}_small.html"

content = content.replace(old, new)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Dump path fixed")
