import json, re
with open("data/buckler_dumps/bl_dump.html", "r", encoding="utf-8") as f:
    html = f.read()
m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', html, re.DOTALL)
raw = json.loads(m.group(1))
pp = raw["props"]["pageProps"]
print("replay_list:", len(pp.get("replay_list", [])))
print("total_page:", pp.get("total_page"))
rl = pp.get("replay_list", [])
if rl:
    print(json.dumps(rl[0], indent=2, ensure_ascii=False))
    print("---")
    print(json.dumps(rl[1], indent=2, ensure_ascii=False))
