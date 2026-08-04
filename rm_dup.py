path = "bot2.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()
old = """
    elif cmd == "help":
    elif cmd == "help":"""
new = """
    elif cmd == "help":"""
content = content.replace(old, new)
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Duplicate elif removed")
