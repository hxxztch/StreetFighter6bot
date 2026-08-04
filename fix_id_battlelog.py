path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Better ID->name mapping (include all sources)
old_id = """    id_to_name = {c.get("character_id"): c.get("character_name", "?") for c in cli if c.get("character_id")}"""
new_id = """    id_to_name = {}
    for c in cli:
        if c.get("character_id"):
            id_to_name[c["character_id"]] = c.get("character_name", "?")
    # Also add from character_win_rates (has all played chars)
    cwr = play.get("character_win_rates", []) or []
    for c in cwr:
        if c.get("character_id") and c.get("character_id") not in id_to_name:
            id_to_name[c["character_id"]] = c.get("character_name", "?")"""
content = content.replace(old_id, new_id)

# 2. Add battle log fetch after matchup parsing
old_return = """    return data if data.username and len(data.characters) > 0 else None"""

# Add battle log fetch in scrape function
old_scrape_end = """    parsed = _parse(data["raw"], sf6_id)
    if parsed: return parsed

    return None"""

new_scrape_end = """    # Try to fetch battle log for recent matches
    print("[Buckler] Fetching battle log...")
    bl_data = _fetch_and_parse(f"{base}/battlelog", cookie, sf6_id, "battlelog")
    if not bl_data:
        bl_data = _fetch_and_parse(f"{base}?tab=history", cookie, sf6_id, "battlelog")
    if not bl_data:
        bl_data = _fetch_and_parse(f"{base}/history", cookie, sf6_id, "battlelog")

    parsed = _parse(data["raw"], sf6_id)
    if parsed:
        # Merge battle log data if available
        if bl_data:
            bl_pp = bl_data.get("pp", {}) or {}
            bl_play = bl_pp.get("play", {}) or {}
            battle_log = bl_play.get("battle_log", []) or bl_play.get("battleLog", []) or bl_pp.get("battleLog", []) or bl_data.get("raw", {}).get("props", {}).get("pageProps", {}).get("battleLog", []) or []
            if battle_log:
                for bl in battle_log[:5]:
                    if isinstance(bl, dict):
                        parsed.recent_matches.append(RecentMatch(
                            date=bl.get("date","") or bl.get("playDate","") or "",
                            opponent_name=bl.get("opponentName","") or bl.get("opponent_name","") or "Unknown",
                            opponent_char=bl.get("opponentCharacter","") or bl.get("opponent_character","") or "?",
                            player_char=bl.get("playerCharacter","") or bl.get("player_character","") or "?",
                            result="win" if (bl.get("result","") or "").lower() in ("win","w","1") else "lose",
                            mode=bl.get("mode","") or bl.get("matchType","") or "?",
                            rounds_won=bl.get("roundsWon",0) or bl.get("rounds_won",0) or 0,
                            rounds_lost=bl.get("roundsLost",0) or bl.get("rounds_lost",0) or 0,
                            lp_change=bl.get("lpChange",0) or bl.get("lp_change",0) or 0,
                        ))
        return parsed

    return None"""

content = content.replace(old_scrape_end, new_scrape_end)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed: ID mapping includes all sources + battle log fetching added")
