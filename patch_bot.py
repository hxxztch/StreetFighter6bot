# 1. Delete old database
import os
try:
    os.remove(r"E:\Study\sf6-qq-bot\data\sf6bot2.db")
    print("DB deleted")
except:
    print("DB not found (OK)")

# 2. Update bot2.py to skip cache and always fetch fresh
path = r"bot2.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Disable cache - always fetch fresh
old = """            try:
                cached = await get_cached_stats(sid)
                if cached:
                    data = _reconstruct(cached)
                else:
                    data = await fetch_player_data(sid)
                    await set_cached_stats(sid, dataclasses.asdict(data))"""

new = """            try:
                data = await fetch_player_data(sid)
                try:
                    await set_cached_stats(sid, dataclasses.asdict(data))
                except:
                    pass"""

content = content.replace(old, new)
print("Cache disabled - always fetches fresh")

# 3. Update Buckler client with more verbose error logging
cpath = r"src\buckler\client.py"
with open(cpath, "r", encoding="utf-8") as f:
    ccontent = f.read()

# Add traceback to scrape_fighter_card error handler
old_err = """        print(f"[Buckler] Scrape error: {e}")
        import traceback; traceback.print_exc()"""
new_err = """        print(f"[Buckler] Scrape error [{type(e).__name__}]: {e}")
        import traceback; traceback.print_exc()"""
ccontent = ccontent.replace(old_err, new_err)

# Add response body preview for non-200 responses
old_status = """            print(f"[Buckler] Fighter card: {r.status_code} ({len(r.text)} bytes)")"""
new_status = """            print(f"[Buckler] Fighter card: {r.status_code} ({len(r.text)} bytes)")
            if r.status_code != 200:
                print(f"[Buckler] Response headers: {dict(r.headers)}")"""
ccontent = ccontent.replace(old_status, new_status)

with open(cpath, "w", encoding="utf-8") as f:
    f.write(ccontent)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("All fixes applied!")
print("Run: python bot2.py")
print("Then in QQ: !bind 4222666364 -> !sf6")
