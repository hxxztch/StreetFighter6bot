path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the matchup parsing code
old_mu = """    cwrbrc = play.get("character_win_rates_by_rival_character", []) or []
    from collections import defaultdict
    mu_map = defaultdict(lambda: {"wins": 0, "total": 0, "mode": "ranked"})
    for item in cwrbrc:
        opp_name = item.get("rival_character_name", "")
        if opp_name:
            mu_map[opp_name]["wins"] += item.get("win_count", 0) or 0
            mu_map[opp_name]["total"] += item.get("battle_count", 0) or 0
    for opp_name, vals in sorted(mu_map.items(), key=lambda x: x[1]["total"], reverse=True):
        if vals["total"] > 0:
            data.ranked_matchups.append(MatchupStat(
                opponent_char=opp_name, wins=vals["wins"], total=vals["total"], mode="ranked"
            ))"""

new_mu = """    # Build ID->name map from character_league_infos
    cli = play.get("character_league_infos", []) or []
    id_to_name = {c.get("character_id"): c.get("character_name", "?") for c in cli if c.get("character_id")}
    
    cwrbrc = play.get("character_win_rates_by_rival_character", []) or []
    mu_agg = {}
    for char_entry in cwrbrc:
        rival_list = char_entry.get("rival_character_win_rates", []) or []
        for item in rival_list:
            opp_id = item.get("rival_character_id")
            opp_name = id_to_name.get(opp_id, f"ID{opp_id}")
            if opp_name:
                key = opp_name
                if key not in mu_agg:
                    mu_agg[key] = {"wins": 0, "total": 0}
                mu_agg[key]["wins"] += item.get("win_count", 0) or 0
                mu_agg[key]["total"] += item.get("battle_count", 0) or 0
    for opp_name, vals in sorted(mu_agg.items(), key=lambda x: x[1]["total"], reverse=True):
        if vals["total"] > 0:
            data.ranked_matchups.append(MatchupStat(
                opponent_char=opp_name, wins=vals["wins"], total=vals["total"], mode="ranked"
            ))"""

content = content.replace(old_mu, new_mu)
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Matchup parser fixed for nested rival_character_win_rates structure")
