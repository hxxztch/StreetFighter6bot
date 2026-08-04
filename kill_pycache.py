path = r"bot2.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Add dont_write_bytecode right after imports
old = "import asyncio, json, sys, traceback"
new = "import asyncio, json, sys, traceback\nsys.dont_write_bytecode = True"
content = content.replace(old, new)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("sys.dont_write_bytecode added to bot2.py")
