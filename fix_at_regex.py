path = r"bot2.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix the _parse_at function - make regex more flexible
old = "m = re.search(r'\\[CQ:at,qq=(\\d+)\\]', text)"
new = "m = re.search(r'\\[CQ:at,qq=(\\d+)', text)"
content = content.replace(old, new)

# Also add debug logging
old2 = """at_qq = _parse_at(arg)
            if at_qq:
                sid = await get_binding(at_qq)"""

new2 = """at_qq = _parse_at(arg)
            if at_qq:
                print("[AT] Parsed QQ: " + str(at_qq))
                sid = await get_binding(at_qq)
                print("[AT] Bound SF6 ID: " + str(sid))"""

# Replace both dashboard and card handlers
content = content.replace(old2, new2)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed @ regex + added debug logging")
