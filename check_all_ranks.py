import json
with open("data/buckler_dumps/4222666364_nextdata.json", "r", encoding="utf-8") as f:
    data = json.load(f)
cli = data["props"]["pageProps"]["play"]["character_league_infos"]
for c in cli:
    if c.get("is_played"):
        li = c.get("league_info", {})
        print(c["character_name"] + ": lp=" + str(li.get("league_point",0)) + " rank=" + str(li.get("league_rank",0)))
