path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Add battle log fetch after successful parse
old = """    if data:
        print(f\"[Buckler] REAL: {data.username} ({len(data.characters)} chars)\")
        return data"""

new = """    if data:
        print(f\"[Buckler] REAL: {data.username} ({len(data.characters)} chars)\")
        # Try to fetch battle log
        for bl_url in [f\"{url}/battlelog\", f\"{url}/history\", f\"{url}?tab=history\"]:
            print(f\"[Buckler] Trying battle log: {bl_url}\")
            bl_result = _fetch(bl_url, cookie)
            if bl_result and bl_result.get(\"StatusCode\", 0) == 200:
                bl_html = bl_result.get(\"Content\", \"\")
                bl_m = re.search(r'<script id=\"__NEXT_DATA__\" type=\"application/json\">(.+?)</script>', bl_html, re.DOTALL)
                if bl_m:
                    bl_raw = json.loads(bl_m.group(1))
                    bl_pp = bl_raw.get(\"props\", {}).get(\"pageProps\", {}) or {}
                    bl_play = bl_pp.get(\"play\", {}) or {}
                    battle_log = bl_play.get(\"battle_log\", []) or bl_play.get(\"battleLog\", []) or bl_pp.get(\"battleLog\", []) or []
                    if not battle_log:
                        blx = bl_pp.get(\"battleLog\")
                        if isinstance(blx, list): battle_log = blx
                    print(f\"[Buckler] Battle log: {len(battle_log)} entries\")
                    for bl in battle_log[:5]:
                        if isinstance(bl, dict):
                            data.recent_matches.append(RecentMatch(
                                date=str(bl.get(\"date\",\"\") or bl.get(\"playDate\",\"\") or \"\"),
                                opponent_name=str(bl.get(\"opponentName\",\"\") or bl.get(\"opponent_name\",\"\") or \"?\"),
                                opponent_char=CHAR_CN.get(bl.get(\"opponentCharacter\",\"\") or bl.get(\"opponent_character\",\"\") or \"\", str(bl.get(\"opponentCharacter\",\"\") or bl.get(\"opponent_character\",\"\") or \"?\")),
                                player_char=CHAR_CN.get(bl.get(\"playerCharacter\",\"\") or bl.get(\"player_character\",\"\") or \"\", str(bl.get(\"playerCharacter\",\"\") or bl.get(\"player_character\",\"\") or \"?\")),
                                result=\"win\" if str(bl.get(\"result\",\"\") or \"\").lower() in (\"win\",\"w\",\"1\") else \"lose\",
                                mode=str(bl.get(\"mode\",\"\") or bl.get(\"matchType\",\"\") or \"ranked\"),
                                rounds_won=int(bl.get(\"roundsWon\",0) or bl.get(\"rounds_won\",0) or 0),
                                rounds_lost=int(bl.get(\"roundsLost\",0) or bl.get(\"rounds_lost\",0) or 0),
                                lp_change=int(bl.get(\"lpChange\",0) or bl.get(\"lp_change\",0) or 0),
                            ))
                    break
                else:
                    print(f\"[Buckler] BL first 200: {bl_html[:200]}\")
            else:
                print(f\"[Buckler] BL status: {bl_result.get('StatusCode',0) if bl_result else 'None'}\")
        return data"""

content = content.replace(old, new)
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Battle log fetching added!")
