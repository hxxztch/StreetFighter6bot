path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Detect search pages
old = """    data = _parse(raw, sf6_id)
    if not data:
        print("[Buckler] Parse failed - page may be incomplete or player has no data")
        raise Exception("数据解析失败")"""

new = """    # Check if this is a search page (no play data)
    pp = raw.get("props", {}).get("pageProps", {})
    if not pp.get("play"):
        print("[Buckler] Search page detected, profile not available")
        raise Exception("玩家未公开数据或未注册Buckler")
    data = _parse(raw, sf6_id)
    if not data:
        print("[Buckler] Parse failed - page may be incomplete or player has no data")
        raise Exception("数据解析失败")"""

content = content.replace(old, new)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Added search page detection")
