import json, sys
sys.path.insert(0, ".")
with open("data/buckler_dumps/4222666364_nextdata.json", "r", encoding="utf-8") as f:
    data = json.load(f)
cli = data["props"]["pageProps"]["play"]["character_league_infos"]
for c in cli:
    name = c.get("character_name", "")
    cid = c.get("character_id")
    if "bison" in name.lower() or "yasmine" in name.lower() or "yasmin" in name.lower() or "Elena" in name:
        print("ID=" + str(cid) + ": " + name)
# Show all names to find M.Bison
for c in cli:
    name = c.get("character_name", "")
    cid = c.get("character_id")
    if cid in [18, 19, 20, 21, 22, 23, 24, 25, 26, 27]:
        print("ID=" + str(cid) + ": " + name + " (tool=" + c.get("character_tool_name","?") + ")")
