import os
BASE = r"E:\Study\sf6-qq-bot"
def w(path, content):
    fpath = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(fpath), exist_ok=True)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK: {path}")

w(r"src\buckler\client.py", r'''"""Buckler Boot Camp API client - real scraping + mock fallback"""
import json, random, re, httpx
from pathlib import Path
from src.config import BUCKLER_BASE_URL, BUCKLER_COOKIE_FILE, DATA_DIR
from src.buckler.models import (PlayerData, GameModeTime, CharacterStat, TechStats, DriveUsage, MatchupStat, RecentMatch)

SF6_CHARS = ["隆","肯","春丽","古烈","布兰卡","桑吉尔夫","达尔西姆","本田","迪杰","金佰莉","杰米","卢克","朱莉","玛丽莎","曼侬","莉莉","JP","嘉米","拉希德","阿鬼","爱德","豪鬼","维加","特瑞","舞","艾琳娜"]
RANKS = ["Rookie 1","Rookie 2","Iron 1","Iron 2","Iron 3","Bronze 1","Bronze 2","Bronze 3","Silver 1","Silver 2","Silver 3","Gold 1","Gold 2","Gold 3","Platinum 1","Platinum 2","Platinum 3","Diamond 1","Diamond 2","Diamond 3","Master"]
MODES = ["ranked","casual","battle_hub"]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

DUMP_DIR = DATA_DIR / "buckler_dumps"
DUMP_DIR.mkdir(parents=True, exist_ok=True)

def _load_cookie():
    """Load Buckler cookie from file"""
    try:
        path = Path(BUCKLER_COOKIE_FILE)
        if path.exists():
            cookie = path.read_text(encoding="utf-8").strip()
            if cookie and not cookie.startswith("#"):
                return cookie
    except Exception:
        pass
    return None

async def _scrape_fighter_card(client, sf6_id):
    """Scrape fighter card page for embedded data"""
    url = f"{BUCKLER_BASE_URL}/fighter_card/{sf6_id}"
    resp = await client.get(url, follow_redirects=True)
    resp.raise_for_status()
    html = resp.text

    # Try to find embedded JSON data (Next.js __NEXT_DATA__ pattern)
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', html, re.DOTALL)
    if m:
        raw = json.loads(m.group(1))
        DUMP_DIR.mkdir(parents=True, exist_ok=True)
        (DUMP_DIR / f"{sf6_id}_nextdata.json").write_text(json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8")
        return raw

    # Try to find page-level state
    for pattern in [r'window\.__PRELOADED_STATE__\s*=\s*({.+?});', r'window\.__INITIAL_STATE__\s*=\s*({.+?});']:
        m = re.search(pattern, html, re.DOTALL)
        if m:
            raw = json.loads(m.group(1))
            (DUMP_DIR / f"{sf6_id}_preload.json").write_text(json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8")
            return raw

    # Try to find fighter data in script tags
    for pattern in [r'"fighterName"\s*:\s*"(.+?)"', r'"fighter_name"\s*:\s*"(.+?)"']:
        m = re.search(pattern, html)
        if m:
            # Found fighter name, try to extract more
            pass

    # Save raw HTML for debugging
    (DUMP_DIR / f"{sf6_id}_page.html").write_text(html, encoding="utf-8")
    return None

async def _api_fetch(client, sf6_id):
    """Try bucket API endpoints"""
    endpoints = [
        f"{BUCKLER_BASE_URL}/api/profile/{sf6_id}",
        f"{BUCKLER_BASE_URL}/api/fighter/{sf6_id}",
        f"{BUCKLER_BASE_URL}/api/fighter_card/{sf6_id}",
    ]
    for url in endpoints:
        try:
            resp = await client.get(url, follow_redirects=True)
            resp.raise_for_status()
            data = resp.json()
            DUMP_DIR.mkdir(parents=True, exist_ok=True)
            (DUMP_DIR / f"{sf6_id}_api.json").write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            return data
        except Exception:
            continue
    return None

def _parse_response(raw, sf6_id):
    """Parse raw Buckler response into PlayerData"""
    # Try multiple parsing strategies
    data = PlayerData(player_id=sf6_id)

    # Strategy 1: Next.js page props
    if isinstance(raw, dict):
        props = raw.get("props", {}).get("pageProps", {})
        if not props:
            props = raw

        # Fighter info
        fighter = props.get("fighter") or props.get("fighterData") or props.get("data") or {}
        if not fighter and isinstance(props, dict):
            fighter = props

        data.username = fighter.get("fighterName") or fighter.get("fighter_name") or fighter.get("name") or f"Player_{sf6_id[-8:]}"
        data.platform = fighter.get("platform") or "Unknown"

        # Character data
        chars_raw = fighter.get("characterData") or fighter.get("characters") or fighter.get("fighterCharacterData") or []
        if not chars_raw:
            chars_raw = fighter.get("data", [])
        for c in chars_raw:
            if isinstance(c, dict):
                cname = c.get("characterName") or c.get("character_name") or "Unknown"
                data.characters.append(CharacterStat(
                    name=cname,
                    usage_count=c.get("usageCount", 0) or c.get("usage_count", 0) or c.get("playCount", 0) or 0,
                    wins=c.get("wins", 0) or c.get("win", 0) or 0,
                    total=c.get("totalGames", 0) or c.get("total_games", 0) or max(1, c.get("playCount", 0) or 0),
                    rank=c.get("rank") or c.get("leagueRank") or c.get("league_rank") or "N/A",
                    league_points=c.get("leaguePoints", 0) or c.get("league_points", 0) or c.get("lp", 0) or 0,
                ))
        data.characters.sort(key=lambda x: x.usage_count, reverse=True)

        # Game time
        play = fighter.get("playData") or fighter.get("play_data") or {}
        gt = GameModeTime(
            total_play_time=play.get("totalPlayTime", 0) or play.get("total_play_time", 0) or 0,
            ranked_time=play.get("rankedMatchPlayTime", 0) or play.get("ranked_match_play_time", 0) or 0,
            casual_time=play.get("casualMatchPlayTime", 0) or play.get("casual_match_play_time", 0) or 0,
            battle_hub_time=play.get("battleHubPlayTime", 0) or play.get("battle_hub_play_time", 0) or 0,
            training_time=play.get("trainingModePlayTime", 0) or play.get("training_mode_play_time", 0) or 0,
            arcade_time=play.get("arcadeModePlayTime", 0) or play.get("arcade_mode_play_time", 0) or 0,
            custom_room_time=play.get("customRoomPlayTime", 0) or play.get("custom_room_play_time", 0) or 0,
            world_tour_time=play.get("worldTourPlayTime", 0) or play.get("world_tour_play_time", 0) or 0,
            extreme_battle_time=play.get("extremeBattlePlayTime", 0) or play.get("extreme_battle_play_time", 0) or 0,
        )
        data.game_time = gt

        # Technical stats
        tech_raw = fighter.get("technicalStats") or fighter.get("technical_stats") or {}
        data.tech_stats = TechStats(
            games_played=tech_raw.get("gamesPlayed", 0) or tech_raw.get("games_played", 0) or 0,
            corner_pressure_time=tech_raw.get("cornerPressureTime", 0) or tech_raw.get("corner_pressure_time", 0) or 0,
            corner_pressured_time=tech_raw.get("cornerPressuredTime", 0) or tech_raw.get("corner_pressured_time", 0) or 0,
            throws_landed=tech_raw.get("throwsLanded", 0) or tech_raw.get("throws_landed", 0) or 0,
            throw_escapes=tech_raw.get("throwEscapes", 0) or tech_raw.get("throw_escapes", 0) or 0,
            perfect_parries=tech_raw.get("perfectParries", 0) or tech_raw.get("perfect_parries", 0) or 0,
            drive_impacts=tech_raw.get("driveImpacts", 0) or tech_raw.get("drive_impacts", 0) or 0,
            drive_impact_counters=tech_raw.get("driveImpactCounters", 0) or tech_raw.get("drive_impact_counters", 0) or 0,
            drive_impacts_received=tech_raw.get("driveImpactsReceived", 0) or tech_raw.get("drive_impacts_received", 0) or 0,
            punish_counters=tech_raw.get("punishCounters", 0) or tech_raw.get("punish_counters", 0) or 0,
            punished_received=tech_raw.get("punishedReceived", 0) or tech_raw.get("punished_received", 0) or 0,
            super_arts=tech_raw.get("superArts", 0) or tech_raw.get("super_arts", 0) or 0,
            combos_max_damage=tech_raw.get("combosMaxDamage", 0) or tech_raw.get("combos_max_damage", 0) or 0,
            combos_avg_damage=tech_raw.get("combosAvgDamage", 0) or tech_raw.get("combos_avg_damage", 0) or 0,
        )

        # Drive usage
        dr_raw = tech_raw.get("driveUsage", {}) or tech_raw.get("drive_usage", {})
        data.drive_usage = DriveUsage(
            drive_rush_cancel=dr_raw.get("driveRushCancel", 0) or dr_raw.get("drive_rush_cancel", 0) or 0,
            overdrive=dr_raw.get("overdrive", 0) or 0,
            drive_reversal=dr_raw.get("driveReversal", 0) or dr_raw.get("drive_reversal", 0) or 0,
            raw_drive_rush=dr_raw.get("rawDriveRush", 0) or dr_raw.get("raw_drive_rush", 0) or 0,
            drive_parry=dr_raw.get("driveParry", 0) or dr_raw.get("drive_parry", 0) or 0,
            burnout_drain=dr_raw.get("burnoutDrain", 0) or dr_raw.get("burnout_drain", 0) or 0,
        )

        # Matchup data
        ranked = fighter.get("rankedMatchData") or fighter.get("ranked_match_data") or []
        casual = fighter.get("casualMatchData") or fighter.get("casual_match_data") or []
        bh = fighter.get("battleHubMatchData") or fighter.get("battle_hub_match_data") or []
        for m in ranked:
            data.ranked_matchups.append(MatchupStat(
                opponent_char=m.get("characterName","") or m.get("character_name","") or "Unknown",
                wins=m.get("wins",0) or m.get("win",0) or 0,
                total=m.get("totalGames",0) or m.get("total_games",0) or 0,
                mode="ranked"
            ))
        for m in casual:
            data.casual_matchups.append(MatchupStat(
                opponent_char=m.get("characterName","") or m.get("character_name","") or "Unknown",
                wins=m.get("wins",0) or m.get("win",0) or 0,
                total=m.get("totalGames",0) or m.get("total_games",0) or 0,
                mode="casual"
            ))
        for m in bh:
            data.battle_hub_matchups.append(MatchupStat(
                opponent_char=m.get("characterName","") or m.get("character_name","") or "Unknown",
                wins=m.get("wins",0) or m.get("win",0) or 0,
                total=m.get("totalGames",0) or m.get("total_games",0) or 0,
                mode="battle_hub"
            ))

        # Recent matches
        recent_raw = fighter.get("battleLog") or fighter.get("battle_log") or fighter.get("recentMatches") or fighter.get("recent_matches") or []
        for m in recent_raw:
            data.recent_matches.append(RecentMatch(
                date=m.get("date","") or m.get("playDate","") or "",
                opponent_name=m.get("opponentName","") or m.get("opponent_name","") or "Unknown",
                opponent_char=m.get("opponentCharacter","") or m.get("opponent_character","") or "Unknown",
                player_char=m.get("playerCharacter","") or m.get("player_character","") or "",
                result="win" if (m.get("result","") or "").lower() in ("win","w","1") else "lose",
                mode=m.get("mode","") or m.get("matchType","") or "ranked",
                rounds_won=m.get("roundsWon",0) or m.get("rounds_won",0) or 0,
                rounds_lost=m.get("roundsLost",0) or m.get("rounds_lost",0) or 0,
                lp_change=m.get("lpChange",0) or m.get("lp_change",0) or m.get("mrChange",0) or 0,
            ))

    if data.username == "" or len(data.characters) == 0:
        return None
    return data

async def fetch_player_data(sf6_id):
    """Get player data: try real API first, then mock"""
    cookie = _load_cookie()
    headers = {
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": f"{BUCKLER_BASE_URL}/",
    }
    if cookie:
        headers["Cookie"] = cookie
        print(f"[Buckler] Loaded cookie ({len(cookie)} chars)")

    async with httpx.AsyncClient(headers=headers, timeout=30.0, follow_redirects=True) as client:
        # Try scraping fighter card page
        raw = await _scrape_fighter_card(client, sf6_id)
        if raw:
            data = _parse_response(raw, sf6_id)
            if data and data.username and len(data.characters) > 0:
                print(f"[Buckler] Scraped: {data.username} ({len(data.characters)} chars)")
                return data

        # Try direct API calls
        raw = await _api_fetch(client, sf6_id)
        if raw:
            data = _parse_response(raw, sf6_id)
            if data and data.username and len(data.characters) > 0:
                print(f"[Buckler] API: {data.username} ({len(data.characters)} chars)")
                return data

    # Fallback to mock
    print(f"[Buckler] No real data, using mock for {sf6_id}")
    return _gen_mock(sf6_id)

# Keep mock generator (same as before)
def _gen_mock(sf6_id):
    rng = random.Random(sf6_id)
    nc = rng.choice([1,1,2,2,3,4])
    pool = rng.sample(SF6_CHARS, nc)
    tm = rng.randint(200, 3500)
    wts = [rng.uniform(0.3,1.0) for _ in range(nc)]
    ws = sum(wts)
    fracs = [w/ws for w in wts]
    fracs[0] = max(fracs[0], 0.4)
    diff = sum(fracs) - 1.0
    fracs[1:] = [f - diff/(len(fracs)-1) for f in fracs[1:]]
    chars = []
    for i, name in enumerate(pool):
        count = max(5, round(tm*fracs[i]))
        wr = min(0.75, max(0.35, rng.uniform(0.35,0.75)))
        wins = round(count*wr)
        ri = rng.randint(8, 19)
        rank = RANKS[ri]
        lp = rng.randint(1300,2100) if rank=="Master" else rng.randint(8000,25000)
        chars.append(CharacterStat(name=name,usage_count=count,wins=wins,total=count,rank=f"{rank} {lp}{'MR' if rank=='Master' else 'LP'}",league_points=lp))
    chars.sort(key=lambda c: c.usage_count, reverse=True)
    games = max(1, sum(c.total for c in chars))
    ts = TechStats(games_played=games, corner_pressure_time=round(rng.uniform(2.5,8.0),1), corner_pressured_time=round(rng.uniform(2.0,7.5),1), throws_landed=round(rng.uniform(1.0,4.5),1), throw_escapes=round(rng.uniform(0.5,3.5),1), perfect_parries=round(rng.uniform(0.1,1.2),2), drive_impacts=round(rng.uniform(1.5,5.0),1), drive_impact_counters=round(rng.uniform(0.3,2.0),1), drive_impacts_received=round(rng.uniform(1.0,4.5),1), punish_counters=round(rng.uniform(0.5,3.0),1), punished_received=round(rng.uniform(0.4,2.8),1), super_arts=round(rng.uniform(0.8,2.5),1), combos_max_damage=rng.randint(2000,7000), combos_avg_damage=round(rng.uniform(800,3200),0))
    du = DriveUsage(drive_rush_cancel=rng.randint(400,3500), overdrive=rng.randint(500,4000), drive_reversal=rng.randint(50,600), raw_drive_rush=rng.randint(200,2000), drive_parry=rng.randint(300,3000), burnout_drain=rng.randint(100,1500))
    tot_sec = rng.randint(36000, 500000)
    gt = GameModeTime(total_play_time=tot_sec, ranked_time=round(tot_sec*rng.uniform(0.25,0.55)), casual_time=round(tot_sec*rng.uniform(0.05,0.20)), battle_hub_time=round(tot_sec*rng.uniform(0.05,0.20)), training_time=round(tot_sec*rng.uniform(0.05,0.20)), arcade_time=round(tot_sec*rng.uniform(0.02,0.10)), custom_room_time=round(tot_sec*rng.uniform(0.02,0.10)), world_tour_time=round(tot_sec*rng.uniform(0.02,0.15)), extreme_battle_time=round(tot_sec*rng.uniform(0.01,0.05)))
    gt.other_time = max(0, tot_sec - sum([gt.ranked_time, gt.casual_time, gt.battle_hub_time, gt.training_time, gt.arcade_time, gt.custom_room_time, gt.world_tour_time, gt.extreme_battle_time]))
    def _mu(mode, n):
        res = []
        for name in rng.sample(SF6_CHARS, min(n, len(SF6_CHARS))):
            t = rng.randint(5,80)
            w = round(t * rng.uniform(0.30,0.80))
            res.append(MatchupStat(opponent_char=name, wins=w, total=t, mode=mode))
        res.sort(key=lambda m: m.total, reverse=True)
        return res
    rmu = _mu("ranked", rng.randint(4,8))
    cmu = _mu("casual", rng.randint(2,5))
    bmu = _mu("battle_hub", rng.randint(2,5))
    recent = []
    for i in range(rng.randint(10,20)):
        oc = rng.choice(SF6_CHARS)
        pc = pool[0] if rng.random()<0.7 else rng.choice(pool)
        mode = rng.choice(MODES)
        won = rng.random()<0.52
        rw = rng.choice([1,2]) if won else rng.choice([0,1])
        rl = 2-rw if won else 2-rng.choice([0,1])
        recent.append(RecentMatch(date=f"2026-{rng.randint(7,8):02d}-{rng.randint(1,28):02d} {rng.randint(10,23)}:{rng.randint(0,59):02d}", opponent_name=f"Player_{rng.randint(1000,9999)}", opponent_char=oc, player_char=pc, result="win" if won else "lose", mode=mode, rounds_won=rw, rounds_lost=rl, lp_change=rng.randint(0,65) if won else -rng.randint(0,65)))
    recent.sort(key=lambda m: m.date, reverse=True)
    return PlayerData(username=f"Fighter_{sf6_id[-8:]}", player_id=sf6_id, platform=rng.choice(["Steam","PS5","Xbox"]), game_time=gt, characters=chars, tech_stats=ts, drive_usage=du, ranked_matchups=rmu, casual_matchups=cmu, battle_hub_matchups=bmu, recent_matches=recent)
''')

print("Phase 2: real client done!")
