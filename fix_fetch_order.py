path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Swap fetch order: urllib first, PS second
old = """for name, fn in [("PS", lambda: _ps_fetch(url, cookie)), ("urllib", lambda: _urllib_fetch(url, cookie)), ("requests", lambda: _req_fetch(url, cookie))]:"""

new = """for name, fn in [("urllib", lambda: _urllib_fetch(url, cookie)), ("PS", lambda: _ps_fetch(url, cookie)), ("requests", lambda: _req_fetch(url, cookie))]:"""

content = content.replace(old, new)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Fetch order: urllib first, PS second")
