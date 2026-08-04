path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Find the _parse function and replace it completely
old_parse = "def _parse(raw, sf6_id):"
next_func = content.find("def scrape(sf6_id):", content.find(old_parse))
new_parse = '''def _parse(raw, sf6_id):
    data = PlayerData(player_id=sf6_id)
    if not isinstance(raw, dict): return None
    pp = raw.get("props", {}).get("pageProps", {})
    if not isinstance(pp, dict) or not pp: return None

    # Fighter info from fighter_banner_info
    fbi = pp.get("fighter_banner_info", {}) or {}
    pi = fbi.get("personal_info", {}) or {}
    data.username = pi.get("fighter_id", "") or f"Player_{sf6_id}"
    data.platform = pi.get("platform_name", "") or "Unknown"

    # Play data
    play = pp.get("play", {}) or {}

    # Play time from base_info
    base = play.get("base_info", {}) or {}
    ctl = base.get("content_play_time_list", []) or []
    gt = GameModeTime(total_play_time=sum(item.get("play_time", 0) or 0 for item in ctl))
    for item in ctl:
        ct = item.get("content_type", -1)
        pt = item.get("play_time", 0) or 0
        if ct == 1: gt.ranked_time = pt
        elif ct == 2: gt.casual_time = pt
        elif ct == 5: gt.battle_hub_time = pt
        elif ct == 3: gt.arcade_time = pt
        elif ct == 4: gt.training_time = pt
    data.game_time = gt

    # Character data from character_league_infos + character_win_rates
    cli = play.get("character_league_infos", []) or []
    cwr = play.get("character_win_rates", []) or []

    # Build character name to wins/total mapping
    wr_map = {}
    for item in cwr:
        name = item.get("character_name", "")
        if name:
            bc = item.get("battle_count", 0) or 0
            wc = item.get("win_count", 0) or 0
            if bc > 0:
                wr_map[name] = (wc, bc)

    for item in cli:
        if item.get("is_played"):
            name = item.get("character_name", "Unknown")
            li = item.get("league_info", {}) or {}
            lp = li.get("league_point", 0) or 0
            mr = li.get("master_rating", 0) or 0
            rank_name = li.get("league_rank_name", "")
            lr = li.get("league_rank", 0)
            if mr > 0:
                rank_str = f"Master {mr}MR"
            elif rank_name:
                rank_str = f"{rank_name}"
            else:
                rank_str = "Unranked"

            w, t = wr_map.get(name, (0, 0))
            data.characters.append(CharacterStat(
                name=name, usage_count=t, wins=w, total=t,
                rank=rank_str, league_points=mr if mr > 0 else lp
            ))
    data.characters.sort(key=lambda x: x.usage_count, reverse=True)

    # Battle stats (technical)
    bs = play.get("battle_stats", {}) or {}
    data.tech_stats = TechStats(
        corner_pressure_time=bs.get("corner_time", 0) or 0,
        corner_pressured_time=bs.get("cornered_time", 0) or 0,
        throws_landed=bs.get("throw", 0) or 0,
        throw_escapes=bs.get("throw_escape", 0) or 0,
        perfect_parries=bs.get("perfect_parry", 0) or 0,
        drive_impacts=bs.get("drive_impact", 0) or 0,
        drive_impact_counters=bs.get("drive_impact_to_drive_impact", 0) or 0,
        drive_impacts_received=bs.get("receive_drive_impact", 0) or 0,
        punish_counters=bs.get("punish_counter", 0) or 0,
        punished_received=bs.get("receive_punish_counter", 0) or 0,
        super_arts=bs.get("super_arts_lv1", 0) or 0,
    )
    data.drive_usage = DriveUsage(
        drive_rush_cancel=bs.get("drive_rush_cancel", 0) or 0,
        overdrive=bs.get("overdrive_arts", 0) or 0,
        drive_reversal=bs.get("drive_reversal", 0) or 0,
        raw_drive_rush=bs.get("parry_drive_rush", 0) or 0,
        drive_parry=bs.get("drive_parry", 0) or 0,
        burnout_drain=bs.get("gauge_rate_ca", 0) or 0,
    )

    # Matchup data
    cwrbrc = play.get("character_win_rates_by_rival_character", []) or []
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
            ))

    return data if data.username and len(data.characters) > 0 else None

'''

content = content[:content.find(old_parse)] + new_parse + content[next_func:]
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Parser rewritten to match real Buckler data structure!")
