path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old_bl = """                bl_pp = bl_raw.get(\"props\", {}).get(\"pageProps\", {}) or {}
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
                    break"""

new_bl = """                bl_pp = bl_raw.get(\"props\", {}).get(\"pageProps\", {}) or {}
                    replay_list = bl_pp.get(\"replay_list\", []) or []
                    if not replay_list:
                        bl_play = bl_pp.get(\"play\", {}) or {}
                        replay_list = bl_play.get(\"replay_list\", []) or bl_play.get(\"battleLog\", []) or []
                    print(f\"[Buckler] Battle log: {len(replay_list)} entries\")
                    for entry in replay_list[:5]:
                        if not isinstance(entry, dict): continue
                        p1 = entry.get(\"player1_info\", {}) or {}
                        p2 = entry.get(\"player2_info\", {}) or {}
                        p1_sid = str((p1.get(\"player\", {}) or {}).get(\"short_id\", \"\"))
                        p2_sid = str((p2.get(\"player\", {}) or {}).get(\"short_id\", \"\"))
                        target_id = str(sf6_id)
                        # Determine which side is the user
                        if p2_sid == target_id:
                            user_side = p2; opp_side = p1
                        elif p1_sid == target_id:
                            user_side = p1; opp_side = p2
                        else:
                            user_side = p2; opp_side = p1  # guess
                        user_rr = user_side.get(\"round_results\", []) or []
                        opp_rr = opp_side.get(\"round_results\", []) or []
                        user_won = sum(1 for r in user_rr if r == 1)
                        opp_won = sum(1 for r in opp_rr if r == 1)
                        result = \"win\" if user_won > opp_won else \"lose\"
                        user_char = CHAR_CN.get(user_side.get(\"character_name\", \"\"), user_side.get(\"character_name\", \"?\"))
                        opp_char = CHAR_CN.get(opp_side.get(\"character_name\", \"\"), opp_side.get(\"character_name\", \"?\"))
                        opp_name = (opp_side.get(\"player\", {}) or {}).get(\"fighter_id\", \"?\")
                        mode = entry.get(\"replay_battle_type_name\", \"?\")
                        date_ts = entry.get(\"uploaded_at\", 0) or 0
                        if date_ts:
                            import datetime
                            date_str = datetime.datetime.fromtimestamp(date_ts).strftime(\"%m/%d %H:%M\")
                        else:
                            date_str = \"?\"
                        data.recent_matches.append(RecentMatch(
                            date=date_str,
                            opponent_name=str(opp_name),
                            opponent_char=str(opp_char),
                            player_char=str(user_char),
                            result=result,
                            mode=str(mode),
                            rounds_won=user_won,
                            rounds_lost=opp_won,
                            lp_change=0,
                        ))
                    break"""

content = content.replace(old_bl, new_bl)
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Battle log parser updated for replay_list structure!")
