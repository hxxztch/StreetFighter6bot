import sys, json, re
sys.path.insert(0, ".")
from src.buckler.client import _fetch, _load_cookie
cookie = _load_cookie()
url = "https://www.streetfighter.com/6/buckler/profile/4222666364/battlelog"
r = _fetch(url, cookie)
if r and r.get("StatusCode", 0) == 200:
    html = r.get("Content", "")
    with open("data/buckler_dumps/bl_dump.html", "w", encoding="utf-8") as f:
        f.write(html)
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', html, re.DOTALL)
    if m:
        raw = json.loads(m.group(1))
        pp = raw.get("props", {}).get("pageProps", {})
        print("pageProps keys:", list(pp.keys()))
        for k in pp.keys():
            if "battle" in k.lower() or "log" in k.lower():
                v = pp.get(k)
                print(k, type(v).__name__, len(v) if isinstance(v, (list, dict)) else str(v)[:100])
        play = pp.get("play", {})
        if play:
            print("play keys:", list(play.keys())[:15])
            for k in play.keys():
                if "battle" in k.lower():
                    v = play.get(k)
                    print("play." + k, type(v).__name__, len(v) if isinstance(v, (list, dict)) else str(v)[:100])
    else:
        print("No __NEXT_DATA__")
else:
    print("Fetch failed:", r.get("StatusCode", 0) if r else "None")
