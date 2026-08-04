path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Find and replace the entire scrape function
old_start = "def scrape(sf6_id):"
next_start = content.find("\ndef _gen_mock")

new_scrape = """def scrape(sf6_id):
    cookie = _load_cookie()
    if not cookie:
        print("[Buckler] No cookie")
        return None
    print(f"[Buckler] Cookie: {len(cookie)} chars")
    base = f"{BUCKLER_BASE_URL}/profile/{sf6_id}"
    print(f"[Buckler] Fetching profile...")
    data = _fetch_and_parse(base, cookie, sf6_id, "current")
    if not data:
        print("[Buckler] Profile fetch failed")
        return None
    raw = data["raw"]
    (DUMP_DIR / f"{sf6_id}_nextdata.json").write_text(json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8")
    sc = raw.get("props", {}).get("pageProps", {}).get("common", {}).get("statusCode", 0)
    print(f"[Buckler] statusCode: {sc}")
    if sc != 200 and sc != 0:
        print(f"[Buckler] Non-OK status: {sc}")
        return None
    parsed = _parse(raw, sf6_id)
    if parsed:
        print(f"[Buckler] REAL: {parsed.username} ({len(parsed.characters)} chars, {len(parsed.ranked_matchups)} matchups)")
        # Try battle log
        print("[Buckler] Fetching battle log...")
        bl_data = _fetch_and_parse(f"{base}/battlelog", cookie, sf6_id, "battlelog")
        if bl_data:
            bl_pp = bl_data.get("pp", {}) or {}
            bl_play = bl_pp.get("play", {}) or {}
            battle_log = bl_play.get("battle_log", []) or bl_play.get("battleLog", []) or bl_pp.get("battleLog", []) or []
            if not battle_log:
                bl_raw = bl_data.get("raw", {}) or {}
                bl_props = bl_raw.get("props", {}).get("pageProps", {}) or {}
                battle_log = bl_props.get("battleLog", []) or []
            print(f"[Buckler] Battle log entries: {len(battle_log)}")
            for bl in battle_log[:5]:
                if isinstance(bl, dict):
                    parsed.recent_matches.append(RecentMatch(
                        date=str(bl.get("date","") or bl.get("playDate","") or ""),
                        opponent_name=str(bl.get("opponentName","") or bl.get("opponent_name","") or "?"),
                        opponent_char=str(bl.get("opponentCharacter","") or bl.get("opponent_character","") or "?"),
                        player_char=str(bl.get("playerCharacter","") or bl.get("player_character","") or "?"),
                        result="win" if str(bl.get("result","") or "").lower() in ("win","w","1") else "lose",
                        mode=str(bl.get("mode","") or bl.get("matchType","") or "?"),
                        rounds_won=int(bl.get("roundsWon",0) or bl.get("rounds_won",0) or 0),
                        rounds_lost=int(bl.get("roundsLost",0) or bl.get("rounds_lost",0) or 0),
                        lp_change=int(bl.get("lpChange",0) or bl.get("lp_change",0) or 0),
                    ))
        return parsed
    print("[Buckler] Parse returned None")
    return None"""

content = content[old_start:next_start] = ""  # Remove old scrape
# Actually, let me find the scrape function and replace it properly
idx_start = content.find(old_start)
idx_end = content.find("\ndef _gen_mock", idx_start)
if idx_end < 0:
    idx_end = content.find("\ndef _fetch_and_parse", idx_start)

content = content[:idx_start] + new_scrape + content[idx_end:]

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Scrape function simplified - current season + battle log only")
