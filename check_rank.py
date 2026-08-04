import json
with open("data/buckler_dumps/4222666364_nextdata.json", "r", encoding="utf-8") as f:
    data = json.load(f)
cli = data["props"]["pageProps"]["play"]["character_league_infos"]
found = False
for c in cli:
    li = c.get("league_info", {})
    lr = li.get("league_rank", 0)
    lp = li.get("league_point", 0)
    mr = li.get("master_rating", 0)
    if lr != 39 or lp != -1 or mr > 0:
        print(c["character_name"] + ": rank=" + str(lr) + " lp=" + str(lp) + " mr=" + str(mr))
        found = True
if not found:
    print("ALL 32 characters have default rank (39, -1)")
    print("This means character ranks are loaded client-side, not in SSR data")
