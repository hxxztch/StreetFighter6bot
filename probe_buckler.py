import sys, asyncio, json, re
sys.path.insert(0, '.')
import httpx

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
SID = "4222666364"

async def probe():
    headers = {
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    # Try multiple approaches
    async with httpx.AsyncClient(headers=headers, timeout=30.0, follow_redirects=True) as client:

        # 1. Try fighter card page
        url = f"https://www.streetfighter.com/6/buckler/fighter_card/{SID}"
        try:
            resp = await client.get(url)
            print(f"[PAGE] {url} -> {resp.status_code} ({len(resp.text)} bytes)")
            # Check for Next.js data
            m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', resp.text, re.DOTALL)
            if m:
                data = json.loads(m.group(1))
                print(f"[NEXT_DATA] Found! Keys: {list(data.keys())}")
            else:
                # Check for any embedded JSON
                m2 = re.search(r'window\.__(?:NEXT|PRELOADED|INITIAL)__\w*\s*=\s*(.+?);\s*</script>', resp.text, re.DOTALL)
                if m2:
                    print(f"[EMBED] Found embedded state!")
                else:
                    print(f"[PAGE] No embedded data found. First 500 chars:")
                    print(resp.text[:500])
        except Exception as e:
            print(f"[PAGE ERROR] {type(e).__name__}: {e}")

        # 2. Try CFC API (Capcom Fighter Card)
        for api_path in [
            f"https://www.streetfighter.com/6/buckler/api/profile/{SID}",
            f"https://www.streetfighter.com/6/buckler/api/fighter/{SID}",
            f"https://www.streetfighter.com/6/buckler/api/fighter_card/{SID}",
            f"https://www.streetfighter.com/6/buckler/_next/data/build/fighter_card/{SID}.json",
        ]:
            try:
                resp = await client.get(api_path)
                print(f"[API] {api_path} -> {resp.status_code} ({len(resp.text)} bytes)")
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                        print(f"  JSON keys: {list(data.keys())[:10]}")
                    except:
                        print(f"  Text: {resp.text[:200]}")
            except Exception as e:
                print(f"[API ERROR] {api_path}: {type(e).__name__}")

asyncio.run(probe())
