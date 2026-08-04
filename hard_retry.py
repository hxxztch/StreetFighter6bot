path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Add retry for small pages RIGHT before the __NEXT_DATA__ check  
old = """    (DUMP_DIR / f"{sf6_id}_page.html").write_text(html, encoding="utf-8")
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', html, re.DOTALL)"""

new = """    # Retry if page too small (search page instead of profile)
    import time as _t
    _retry = 0
    while len(html) < 50000 and _retry < 2:
        _retry += 1
        print(f"[Buckler] Small page ({len(html)}b), retry {_retry}/2...")
        _t.sleep(1.5)
        _r2 = _fetch(url, cookie)
        if _r2 and _r2.get("StatusCode",0) == 200 and len(_r2.get("Content","")) > len(html):
            html = _r2["Content"]
            print(f"[Buckler] Retry: {len(html)} bytes")
    
    (DUMP_DIR / f"{sf6_id}_page.html").write_text(html, encoding="utf-8")
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', html, re.DOTALL)"""

content = content.replace(old, new)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Added 2x retry for small pages")
