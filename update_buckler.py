import os
BASE = r"E:\Study\sf6-qq-bot"
def w(path, content):
    fpath = os.path.join(BASE, path)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK: {path}")

w(r"src\buckler\client.py", r'''"""Buckler client - uses requests (sync) for max compatibility"""
import json, random, re, time, sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent.parent.parent))
import requests
from pathlib import Path
from src.config import BUCKLER_BASE_URL, DATA_DIR
from src.buckler.models import (PlayerData, GameModeTime, CharacterStat, TechStats, DriveUsage, MatchupStat, RecentMatch)

SF6_CHARS = ["隆","肯","春丽","古烈","布兰卡","桑吉尔夫","达尔西姆","本田","迪杰","金佰莉","杰米","卢克","朱莉","玛丽莎","曼侬","莉莉","JP","嘉米","拉希德","阿鬼","爱德","豪鬼","维加","特瑞","舞","艾琳娜"]
RANKS = ["Rookie 1","Rookie 2","Iron 1","Iron 2","Iron 3","Bronze 1","Bronze 2","Bronze 3","Silver 1","Silver 2","Silver 3","Gold 1","Gold 2","Gold 3","Platinum 1","Platinum 2","Platinum 3","Diamond 1","Diamond 2","Diamond 3","Master"]
MODES = ["ranked","casual","battle_hub"]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
DUMP_DIR = DATA_DIR / "buckler_dumps"
DUMP_DIR.mkdir(parents=True, exist_ok=True)

def _get_session(headers_extra=None):
    s = requests.Session()
    s.headers.update({
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Sec-Ch-Ua": '"Chromium";v="126", "Google Chrome";v="126"',
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
    })
    if headers_extra:
        s.headers.update(headers_extra)
    s.verify = False
    requests.packages.urllib3.disable_warnings()
    return s

def scrape_fighter_card(sf6_id):
    """Scrape Buckler fighter card page - synchronous version"""
    s = _get_session({"Referer": "https://www.streetfighter.com/6/buckler/"})

    # Step 1: Visit main page to get any session cookies
    try:
        r = s.get(f"{BUCKLER_BASE_URL}/", timeout=15)
        print(f"[Buckler] Main page: {r.status_code}")
    except Exception as e:
        print(f"[Buckler] Main page: {e}")

    # Step 2: Get fighter card page
    url = f"{BUCKLER_BASE_URL}/fighter_card/{sf6_id}"
    try:
        r = s.get(url, timeout=15)
        print(f"[Buckler] Fighter card: {r.status_code} ({len(r.text)} bytes)")
        html = r.text

        # Save for debugging
        (DUMP_DIR / f"{sf6_id}_page.html").write_text(html, encoding="utf-8")

        # Try __NEXT_DATA__
        m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', html, re.DOTALL)
        if m:
            data = json.loads(m.group(1))
            (DUMP_DIR / f"{sf6_id}_nextdata.json").write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            return _parse_next_data(data, sf6_id)

        # Try __PRELOADED_STATE__
        for pat in [r'__NEXT_DATA__\s*=', r'__PRELOADED_STATE__\s*=', r'window\.__data\s*=']:
            m = re.search(pat + r'\s*({.+?});', html, re.DOTALL)
            if m:
                raw = json.loads(m.group(1))
                (DUMP_DIR / f"{sf6_id}_state.json").write_text(json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8")
                result = _parse_next_data(raw, sf6_id)
                if result:
                    return result

        # Try API endpoint
        r2 = s.get(f"{BUCKLER_BASE_URL}/api/profile/{sf6_id}", timeout=15)
        if r2.status_code == 200:
            data = r2.json()
            (DUMP_DIR / f"{sf6_id}_api.json").write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            result = _parse_next_data(data, sf6_id)
            if result:
                return result

        print(f"[Buckler] Content preview: {html[:300]}")
    except Exception as e:
        print(f"[Buckler] Scrape error: {e}")
        import traceback; traceback.print_exc()

    return None

def _parse_next_data(raw, sf6_id):
    """Extract PlayerData from raw JSON"""
    data = PlayerData(player_id=sf6_id)
    props = raw.get("props", {}).get("pageProps", raw) if isinstance(raw, dict) else raw
    fighter = (props.get("fighter") or props.get("fighterData") or props.get("data") or props) if isinstance(props, dict) else {}
    if not isinstance(fighter, dict):
        return None
    data.username = (fighter.get("fighterName") or fighter.get("fighter_name") or fighter.get("name") or "")
    data.platform = fighter.get("platform") or ""
    chars_raw = fighter.get("characterData") or fighter.get("characters") or fighter.get("fighterCharacterData") or []
    for c in chars_raw:
        if isinstance(c, dict):
            data.characters.append(CharacterStat(
                name=c.get("characterName") or c.get("character_name") or "Unknown",
                usage_count=c.get("usageCount") or c.get("usage_count") or c.get("playCount") or 0,
                wins=c.get("wins") or c.get("win") or 0,
                total=c.get("totalGames") or c.get("total_games") or max(1, c.get("playCount") or 0),
                rank=c.get("rank") or c.get("leagueRank") or c.get("league_rank") or "N/A",
                league_points=c.get("leaguePoints") or c.get("league_points") or c.get("lp") or 0,
            ))
    data.characters.sort(key=lambda x: x.usage_count, reverse=True)
    if data.username and len(data.characters) > 0:
        return data
    return None

def _gen_mock(sf6_id):
    rng = random.Random(sf6_id)
    nc = rng.choice([1,1,2,2,3,4]); pool = rng.sample(SF6_CHARS, nc)
    tm = rng.randint(200,3500); wts = [rng.uniform(0.3,1.0) for _ in range(nc)]
    ws = sum(wts); fracs = [w/ws for w in wts]; fracs[0] = max(fracs[0], 0.4)
    diff = sum(fracs)-1.0; fracs[1:] = [f - diff/(len(fracs)-1) for f in fracs[1:]]
    chars = []
    for i, name in enumerate(pool):
        count = max(5, round(tm*fracs[i])); wr = min(0.75, max(0.35, rng.uniform(0.35,0.75)))
        wins = round(count*wr); ri = rng.randint(8, 19); rank = RANKS[ri]
        lp = rng.randint(1300,2100) if rank=="Master" else rng.randint(8000,25000)
        chars.append(CharacterStat(name=name,usage_count=count,wins=wins,total=count,rank=f"{rank} {lp}{'MR' if rank=='Master' else 'LP'}",league_points=lp))
    chars.sort(key=lambda c: c.usage_count, reverse=True)
    games = max(1, sum(c.total for c in chars))
    ts = TechStats(games_played=games, corner_pressure_time=round(rng.uniform(2.5,8.0),1), corner_pressured_time=round(rng.uniform(2.0,7.5),1), throws_landed=round(rng.uniform(1.0,4.5),1), throw_escapes=round(rng.uniform(0.5,3.5),1), perfect_parries=round(rng.uniform(0.1,1.2),2), drive_impacts=round(rng.uniform(1.5,5.0),1), drive_impact_counters=round(rng.uniform(0.3,2.0),1), drive_impacts_received=round(rng.uniform(1.0,4.5),1), punish_counters=round(rng.uniform(0.5,3.0),1), punished_received=round(rng.uniform(0.4,2.8),1), super_arts=round(rng.uniform(0.8,2.5),1), combos_max_damage=rng.randint(2000,7000), combos_avg_damage=round(rng.uniform(800,3200),0))
    du = DriveUsage(drive_rush_cancel=rng.randint(400,3500), overdrive=rng.randint(500,4000), drive_reversal=rng.randint(50,600), raw_drive_rush=rng.randint(200,2000), drive_parry=rng.randint(300,3000), burnout_drain=rng.randint(100,1500))
    tot_sec = rng.randint(36000,500000)
    gt = GameModeTime(total_play_time=tot_sec, ranked_time=round(tot_sec*rng.uniform(0.25,0.55)), casual_time=round(tot_sec*rng.uniform(0.05,0.20)), battle_hub_time=round(tot_sec*rng.uniform(0.05,0.20)), training_time=round(tot_sec*rng.uniform(0.05,0.20)), arcade_time=round(tot_sec*rng.uniform(0.02,0.10)), custom_room_time=round(tot_sec*rng.uniform(0.02,0.10)), world_tour_time=round(tot_sec*rng.uniform(0.02,0.15)), extreme_battle_time=round(tot_sec*rng.uniform(0.01,0.05)))
    gt.other_time = max(0, tot_sec - sum([gt.ranked_time, gt.casual_time, gt.battle_hub_time, gt.training_time, gt.arcade_time, gt.custom_room_time, gt.world_tour_time, gt.extreme_battle_time]))
    def _mu(mode, n):
        res = []
        for name in rng.sample(SF6_CHARS, min(n, len(SF6_CHARS))):
            t = rng.randint(5,80); w = round(t*rng.uniform(0.30,0.80))
            res.append(MatchupStat(opponent_char=name, wins=w, total=t, mode=mode))
        res.sort(key=lambda m: m.total, reverse=True); return res
    rmu = _mu("ranked", rng.randint(4,8)); cmu = _mu("casual", rng.randint(2,5)); bmu = _mu("battle_hub", rng.randint(2,5))
    recent = []
    for i in range(rng.randint(10,20)):
        oc = rng.choice(SF6_CHARS); pc = pool[0] if rng.random()<0.7 else rng.choice(pool)
        mode = rng.choice(MODES); won = rng.random()<0.52
        rw = rng.choice([1,2]) if won else rng.choice([0,1]); rl = 2-rw if won else 2-rng.choice([0,1])
        recent.append(RecentMatch(date=f"2026-{rng.randint(7,8):02d}-{rng.randint(1,28):02d} {rng.randint(10,23)}:{rng.randint(0,59):02d}", opponent_name=f"Player_{rng.randint(1000,9999)}", opponent_char=oc, player_char=pc, result="win" if won else "lose", mode=mode, rounds_won=rw, rounds_lost=rl, lp_change=rng.randint(0,65) if won else -rng.randint(0,65)))
    recent.sort(key=lambda m: m.date, reverse=True)
    return PlayerData(username=f"Fighter_{sf6_id[-8:]}", player_id=sf6_id, platform=rng.choice(["Steam","PS5","Xbox"]), game_time=gt, characters=chars, tech_stats=ts, drive_usage=du, ranked_matchups=rmu, casual_matchups=cmu, battle_hub_matchups=bmu, recent_matches=recent)

async def fetch_player_data(sf6_id):
    """Get player data: try real scraping, fall back to mock"""
    loop = __import__('asyncio').get_running_loop()
    result = await loop.run_in_executor(None, scrape_fighter_card, sf6_id)
    if result:
        print(f"[Buckler] Real data: {result.username} ({len(result.characters)} chars)")
        return result
    print(f"[Buckler] Using mock for {sf6_id}")
    return _gen_mock(sf6_id)
''')

print("Buckler client rewritten with requests + better headers!")
