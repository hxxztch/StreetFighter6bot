import json
with open("data/buckler_dumps/4222666364_nextdata.json", "r", encoding="utf-8") as f:
    data = json.load(f)
pp = data["props"]["pageProps"]
play = pp["play"]
bi = play["base_info"]
ctl = bi.get("content_play_time_list", [])
total_sec = sum(c.get("play_time", 0) for c in ctl)
print("Total:", total_sec // 3600, "h", (total_sec % 3600) // 60, "m")
for c in ctl:
    nm = {1:"R",2:"C",3:"A",4:"T",5:"BH",6:"CR",7:"WT",8:"EB"}.get(c.get("content_type",0),"?" )
    pt = c.get("play_time", 0)
    print(nm, pt // 3600, "h", (pt % 3600) // 60, "m")
wrs = play.get("character_win_rates", [])
for c in sorted(wrs, key=lambda x: x.get("battle_count", 0), reverse=True)[:5]:
    print("CHAR:", c["character_name"], c["battle_count"], "b", c["win_count"], "w")
