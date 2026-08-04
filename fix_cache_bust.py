path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace "url" construction with cache-busting on retry
old = """    # Retry if page too small (search page instead of profile)
    import time as _t
    _retry = 0
    while len(html) < 50000 and _retry < 2:
        _retry += 1
        print(f"[Buckler] Small page ({len(html)}b), retry {_retry}/2...")
        _t.sleep(1.5)
        _r2 = _fetch(url, cookie)
        if _r2 and _r2.get("StatusCode",0) == 200 and len(_r2.get("Content","")) > len(html):
            html = _r2["Content"]
            print(f"[Buckler] Retry: {len(html)} bytes")"""

new = """    # Retry if page too small (search page instead of profile)
    import time as _t, random as _rnd
    _retry = 0
    while len(html) < 50000 and _retry < 2:
        _retry += 1
        print(f"[Buckler] Small page ({len(html)}b), retry {_retry}/2...")
        _t.sleep(1.5)
        # Try with cache-busting param
        _bu = url + (\"&\" if \"?\" in url else \"?\") + \"_t=\" + str(int(_t.time()))
        _r2 = _fetch(_bu, cookie)
        if not _r2 or _r2.get(\"StatusCode\",0) != 200:
            _r2 = _fetch(url, cookie)  # fallback to original
        if _r2 and _r2.get(\"StatusCode\",0) == 200 and len(_r2.get(\"Content\",\"\")) > len(html):
            html = _r2[\"Content\"]
            print(f\"[Buckler] Retry: {len(html)} bytes\")"""

content = content.replace(old, new)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Cache-busting retry added")
