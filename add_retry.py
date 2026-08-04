path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Add retry for small pages after fetch
old = """    print(f"[Buckler] Status: {status}, Size: {len(html)} bytes")
    if status != 200:
        print("[Buckler] Non-200: " + str(status))
        raise Exception("Buckler返回HTTP " + str(status) + "，数据不可用")"""

new = """    print(f"[Buckler] Status: {status}, Size: {len(html)} bytes")
    if status == 200 and len(html) < 50000:
        print("[Buckler] Page too small, retrying after 2s...")
        import time as _time
        _time.sleep(2)
        result2 = _fetch(url, cookie)
        if result2 and result2.get("StatusCode", 0) == 200:
            html2 = result2.get("Content", "")
            if len(html2) > len(html):
                print(f"[Buckler] Retry: {len(html2)} bytes (larger, using this)")
                html = html2
                status = 200
    if status != 200:
        print("[Buckler] Non-200: " + str(status))
        raise Exception("Buckler返回HTTP " + str(status) + "，数据不可用")"""

content = content.replace(old, new)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Added retry for small page responses")
