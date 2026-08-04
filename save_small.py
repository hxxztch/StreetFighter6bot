path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Save small pages separately
old = """    (DUMP_DIR / f"{sf6_id}_page.html").write_text(html, encoding="utf-8")"""

new = """    if len(html) < 50000:
        (DUMP_DIR / f"{sf6_id}_small_page.html").write_text(html, encoding="utf-8")
        print("[Buckler] Small page saved as _small_page.html")
    (DUMP_DIR / f"{sf6_id}_page.html").write_text(html, encoding="utf-8")"""

content = content.replace(old, new)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Small pages saved separately")
