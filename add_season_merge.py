path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Add multi-season LP merge after _parse call
old = """    data = _parse(raw, sf6_id)
    if not data:
        print("[Buckler] Parse failed")
        return _gen_mock(sf6_id)
    print(f"[Buckler] REAL: {data.username} ({len(data.characters)} chars)")"""

new = """    data = _parse(raw, sf6_id)
    if not data:
        print("[Buckler] Parse failed")
        return _gen_mock(sf6_id)
    
    # Multi-season LP merge - try to get highest LP for each character
    pp = raw.get("props", {}).get("pageProps", {})
    play = pp.get("play", {})
    seasons = play.get("season_ids", [])
    if seasons:
        current = play.get("current_season_id", seasons[0] if seasons else 0)
        season_data = {}  # char_name -> (lp, mr, league_rank)
        # Collect LP from current season first
        cli = play.get("character_league_infos", []) or []
        for c in cli:
            if c.get("is_played"):
                name = CHAR_CN.get(c.get("character_name",""), c.get("character_name",""))
                li = c.get("league_info", {}) or {}
                lp = li.get("league_point", 0) or 0
                mr = li.get("master_rating", 0) or 0
                if lp > 0 or mr > 0:
                    season_data[name] = (lp, mr)
        # Try previous seasons
        for sid in [s for s in seasons if s != current]:
            su = f"{BUCKLER_BASE_URL}/profile/{sf6_id}?season={sid}"
            print(f"[Buckler] Season {sid}: {su}")
            sr = _fetch(su, cookie)
            if not sr or sr.get("StatusCode",0) != 200:
                continue
            sm = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', sr.get("Content",""), re.DOTALL)
            if not sm:
                continue
            sd = json.loads(sm.group(1))
            spp = sd.get("props", {}).get("pageProps", {})
            scli = (spp.get("play", {}) or {}).get("character_league_infos", []) or []
            for c in scli:
                if c.get("is_played"):
                    name = CHAR_CN.get(c.get("character_name",""), c.get("character_name",""))
                    li = c.get("league_info", {}) or {}
                    lp = li.get("league_point", 0) or 0
                    mr = li.get("master_rating", 0) or 0
                    if lp > 0 or mr > 0:
                        old_lp, old_mr = season_data.get(name, (-1, 0))
                        if lp > old_lp or mr > old_mr:
                            season_data[name] = (lp, mr)
        # Update character data with highest LP found
        for c in data.characters:
            cn = c.name
            if cn in season_data:
                lp, mr = season_data[cn]
                if mr > 0:
                    c.league_points = mr * 100  # Make MR sort above LP
                    c.rank = f"Master {mr}MR"
                elif lp > c.league_points:
                    c.league_points = lp
                    tn, ts = _lp_to_tier(lp)
                    c.rank = f"{ts} {lp}LP"
        data.characters.sort(key=lambda x: (x.league_points if x.league_points > 0 else -1, x.usage_count), reverse=True)
    
    print(f"[Buckler] REAL: {data.username} ({len(data.characters)} chars)")"""

content = content.replace(old, new)
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Multi-season LP merge added!")
