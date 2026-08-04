path = r"bot2.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Find clearcache block
start = content.find('elif cmd == "clearcache":')
if start < 0:
    print("Not found")
else:
    # Find next elif after it
    next_elif = content.find("\n    elif", start + 1)
    if next_elif < 0:
        next_elif = content.find("\n    #", start + 1)
    # Find the newline before start
    prev_nl = content.rfind("\n", 0, start)
    content = content[:prev_nl] + content[next_elif:]
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("clearcache removed from bot2.py")
