import os
BASE = r"E:\Study\sf6-qq-bot"
def w(p, c):
    with open(os.path.join(BASE, p), "w", encoding="utf-8") as f:
        f.write(c)
    print("OK: " + p)

w(r"src\buckler\client.py", r'''"""Buckler client - clean version"""
import json, random, re, subprocess, asyncio, base64
from pathlib import Path
from src.config import BUCKLER_BASE_URL, DATA_DIR
from src.buckler.models import (PlayerData, GameModeTime, CharacterStat, TechStats, DriveUsage, MatchupStat, RecentMatch)

SF6_CHARS = ["隆","肯","春丽","古烈","布兰卡","桑吉尔夫","达尔西姆","本田","迪杰","金佰莉","杰米","卢克","朱莉","玛丽莎","曼侬","莉莉","JP","嘉米","拉希德","阿鬼","爱德","豪鬼","维加","特瑞","舞","艾琳娜"]
RANKS = ["Rookie 1","Rookie 2","Iron 1","Iron 2","Iron 3","Bronze 1","Bronze 2","Bronze 3","Silver 1","Silver 2","Silver 3","Gold 1","Gold 2","Gold 3","Platinum 1","Platinum 2","Platinum 3","Diamond 1","Diamond 2","Diamond 3","Master"]
MODES = ["ranked","casual","battle_hub"]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0 Safari/537.36"
DUMP_DIR = DATA_DIR / "buckler_dumps"
CK_PATH = DATA_DIR / "buckler_cookie.txt"
DUMP_DIR.mkdir(parents=True, exist_ok=True)

CHAR_CN = {
    "Ryu":"隆","Luke":"卢克","Ken":"肯","Chun-Li":"春丽","Guile":"古烈","Blanka":"布兰卡","Zangief":"桑吉尔夫","Dhalsim":"达尔西姆","E.Honda":"本田","Dee Jay":"迪杰","Kimberly":"金佰莉","Jamie":"杰米","Manon":"曼侬","Marisa":"玛丽莎","JP":"JP","Juri":"朱莉","Cammy":"嘉米","Lily":"莉莉","Rashid":"拉希德","A.K.I.":"阿鬼","Ed":"爱德","Akuma":"豪鬼","M.Bison":"维加","Terry":"特瑞","Mai":"舞","Elena":"艾琳娜","Sagat":"沙加特","C.Viper":"深红毒蛇","Ingrid":"英格丽德","Alex":"阿历克斯","Oro":"欧罗","Rose":"罗斯","Edmond Honda":"本田","Any":"总计",
}

def _load_cookie():
    try:
        if CK_PATH.exists():
            c = CK_PATH.read_text(encoding="utf-8").strip()
            if c and not c.startswith("#"):
                return c
    except: pass
    return None

def _ps_fetch(url, cookie=None):
    try:
        parts = ['[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12']
        if cookie:
            parts.append(f'$c=[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String(\"' + base64.b64encode(cookie.encode()).decode() + '\"))')
        else:
            parts.append('$c=""')
        parts.append('$wc=New-Object System.Net.WebClient')
        parts.append('$wc.Headers.Add("User-Agent","Mozilla/5.0 Chrome/126")')
        parts.append('if($c){$wc.Headers.Add("Cookie",$c)}')
        parts.append('try{$d=$wc.DownloadString(\"' + url + '\");$b=[System.Text.Encoding]::UTF8.GetBytes($d);$b64=[Convert]::ToBase64String($b);[PSCustomObject]@{StatusCode=200;ContentBase64=$b64}|ConvertTo-Json -Compress}catch{exit 1}')
        r = subprocess.run(["powershell","-NoProfile","-Command",";".join(parts)], capture_output=True, text=True, timeout=25)
        if r.returncode == 0 and r.stdout.strip():
            data = json.loads(r.stdout.strip())
            if "ContentBase64" in data:
                data["Content"] = base64.b64decode(data["ContentBase64"]).decode("utf-8", errors="replace")
                del data["ContentBase64"]
            return data
    except: pass
    return None

def _req_fetch(url, cookie=None):
    try:
        import requests
        s = requests.Session()
        s.verify = False; s.trust_env = False; s.proxies = {"http": None, "https": None}
        s.headers["User-Agent"] = UA
        if cookie:
            s.headers["Cookie"] = cookie
        r = s.get(url, timeout=15)
        return {"StatusCode": r.status_code, "Content": r.text}
    except: return None

def _urllib_fetch(url, cookie=None):
    try:
        import urllib.request as ur, ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        req = ur.Request(url, headers={"User-Agent": UA})
        if cookie:
            req.add_header("Cookie", cookie)
        resp = ur.urlopen(req, timeout=15, context=ctx)
        return {"StatusCode": resp.status, "Content": resp.read().decode("utf-8", errors="replace")}
    except: return None

def _fetch(url, cookie=None):
    for name, fn in [("PS", lambda: _ps_fetch(url, cookie)), ("urllib", lambda: _urllib_fetch(url, cookie)), ("requests", lambda: _req_fetch(url, cookie))]:
        try:
            r = fn()
            if r:
                return r
        except: pass
    return None

def _lp_to_tier(lp):
    ranges = [
        (25000, "Master", "M"), (24000, "Diamond 5", "D5"), (23000, "Diamond 4", "D4"),
        (22000, "Diamond 3", "D3"), (21000, "Diamond 2", "D2"), (20000, "Diamond 1", "D1"),
        (19000, "Platinum 5", "P5"), (18000, "Platinum 4", "P4"), (17000, "Platinum 3", "P3"),
        (16000, "Platinum 2", "P2"), (15000, "Platinum 1", "P1"),
        (14000, "Gold 5", "G5"), (13000, "Gold 4", "G4"), (12000, "Gold 3", "G3"),
        (11000, "Gold 2", "G2"), (10000, "Gold 1", "G1"),
        (9000, "Silver 5", "S5"), (8000, "Silver 4", "S4"), (7000, "Silver 3", "S3"),
        (6000, "Silver 2", "S2"), (5000, "Silver 1", "S1"),
        (4500, "Bronze 5", "B5"), (4000, "Bronze 4", "B4"), (3500, "Bronze 3", "B3"),
        (3000, "Bronze 2", "B2"), (2500, "Bronze 1", "B1"),
        (2000, "Iron 5", "I5"), (1500, "Iron 4", "I4"), (1000, "Iron 3", "I3"),
        (500, "Iron 2", "I2"), (100, "Iron 1", "I1"), (1, "Rookie 1", "R1"), (0, "Unranked", "-"),
    ]
    for t, n, s in ranges:
        if lp >= t:
            return n, s
    return "Unranked", "-"

def _parse(raw, sf6_id):
    data = PlayerData(player_id=sf6_id)
    if not isinstance(raw, dict): return None
    pp = raw.get("props", {}).get("pageProps", {})
    if not isinstance(pp, dict) or not pp: return None
    fbi = pp.get("fighter_banner_info", {}) or {}
    pi = fbi.get("personal_info", {}) or {}
    data.username = pi.get("fighter_id", "") or f"Player_{sf6_id}"
    data.platform = pi.get("platform_name", "") or "?"

    play = pp.get("play", {}) or {}
    base = play.get("base_info", {}) or {}
    ctl = base.get("content_play_time_list", []) or []
    gt = GameModeTime(total_play_time=sum(c.get("play_time", 0) or 0 for c in ctl))
    for item in ctl:
        ct = item.get("content_type", -1); pt = item.get("play_time", 0) or 0
        if ct == 2: gt.ranked_time = pt
        elif ct == 5: gt.casual_time = pt
        elif ct == 4: gt.battle_hub_time = pt
        elif ct == 3: gt.arcade_time = pt
        elif ct == 8: gt.training_time = pt
    data.game_time = gt

    cli = play.get("character_league_infos", []) or []
    cwr = play.get("character_win_rates", []) or []
    wr_map = {}
    for item in cwr:
        name = CHAR_CN.get(item.get("character_name", ""), item.get("character_name", ""))
        bc = item.get("battle_count", 0) or 0; wc = item.get("win_count", 0) or 0
        if bc > 0: wr_map[name] = (wc, bc)
    for item in cli:
        if item.get("is_played"):
            name = CHAR_CN.get(item.get("character_name", ""), item.get("character_name", "?"))
            li = item.get("league_info", {}) or {}
            lp = li.get("league_point", 0) or 0; mr = li.get("master_rating", 0) or 0
            tn, ts = _lp_to_tier(lp)
            if mr > 0: rank_str = f"Master {mr}MR"
            elif lp > 0: rank_str = f"{ts} {lp}LP"
            else: rank_str = "Unranked"
            w, t = wr_map.get(name, (0, 0))
            data.characters.append(CharacterStat(name=name, usage_count=t, wins=w, total=t, rank=rank_str, league_points=mr if mr > 0 else lp))
    data.characters = [c for c in data.characters if c.total > 0]
    data.characters.sort(key=lambda x: (x.league_points if x.league_points > 0 else -1, x.usage_count), reverse=True)

    bs = play.get("battle_stats", {}) or {}
    data.tech_stats = TechStats(
        corner_pressure_time=bs.get("corner_time", 0) or 0,
        corner_pressured_time=bs.get("cornered_time", 0) or 0,
        throws_landed=bs.get("throw_count", 0) or 0,
        throw_escapes=bs.get("throw_tech", 0) or 0,
        perfect_parries=bs.get("just_parry", 0) or 0,
        drive_impacts=bs.get("drive_impact", 0) or 0,
        drive_impact_counters=bs.get("drive_impact_to_drive_impact", 0) or 0,
        drive_impacts_received=bs.get("received_drive_impact", 0) or 0,
        punish_counters=bs.get("punish_counter", 0) or 0,
        punished_received=bs.get("received_punish_counter", 0) or 0,
    )
    data.drive_usage = DriveUsage(
        drive_rush_cancel=round((bs.get("gauge_rate_drive_rush_from_cancel", 0) or 0) * 100),
        overdrive=round((bs.get("gauge_rate_drive_arts", 0) or 0) * 100),
        drive_reversal=round((bs.get("gauge_rate_drive_reversal", 0) or 0) * 100),
        raw_drive_rush=round((bs.get("gauge_rate_drive_rush_from_parry", 0) or 0) * 100),
        drive_parry=round((bs.get("gauge_rate_drive_guard", 0) or 0) * 100),
        burnout_drain=round((bs.get("gauge_rate_drive_impact", 0) or 0) * 100),
        other=round((bs.get("gauge_rate_drive_other", 0) or 0) * 100),
    )

    # Matchup data
    id_to_name = {}
    for c in cli:
        if c.get("character_id"):
            id_to_name[c["character_id"]] = CHAR_CN.get(c.get("character_name", ""), c.get("character_name", "?"))
    cwrbrc = play.get("character_win_rates_by_rival_character", []) or []
    mu_agg = {}
    for char_entry in cwrbrc:
        rival_list = char_entry.get("rival_character_win_rates", []) or []
        for item in rival_list:
            opp_id = item.get("rival_character_id")
            opp_name = id_to_name.get(opp_id, f"ID{opp_id}")
            if opp_name and not opp_name.startswith("ID"):
                key = opp_name
                if key not in mu_agg: mu_agg[key] = {"wins": 0, "total": 0}
                mu_agg[key]["wins"] += item.get("win_count", 0) or 0
                mu_agg[key]["total"] += item.get("battle_count", 0) or 0
    for opp_name, vals in sorted(mu_agg.items(), key=lambda x: x[1]["total"], reverse=True):
        if vals["total"] > 0:
            data.ranked_matchups.append(MatchupStat(opponent_char=opp_name, wins=vals["wins"], total=vals["total"], mode="ranked"))

    return data if data.username and len(data.characters) > 0 else None

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
    return PlayerData(username=f"Player_{sf6_id}", player_id=sf6_id, platform="Steam",
        game_time=GameModeTime(total_play_time=rng.randint(36000,500000)),
        characters=chars, tech_stats=TechStats(), drive_usage=DriveUsage(),
        ranked_matchups=[MatchupStat(opponent_char="Ken", wins=rng.randint(1,10), total=rng.randint(5,20), mode="ranked")],
        recent_matches=[RecentMatch(date="2026-08-01", opponent_name="Player_X", opponent_char="Ryu", player_char="Ken", result="win", mode="ranked", rounds_won=2, rounds_lost=1, lp_change=45) for _ in range(5)])

async def fetch_player_data(sf6_id):
    cookie = _load_cookie()
    if not cookie:
        print("[Buckler] No cookie, using mock")
        return _gen_mock(sf6_id)
    print(f"[Buckler] Cookie: {len(cookie)} chars")
    url = f"{BUCKLER_BASE_URL}/profile/{sf6_id}"
    result = _fetch(url, cookie)
    if not result:
        print("[Buckler] Fetch failed, using mock")
        return _gen_mock(sf6_id)
    status = result.get("StatusCode", 0)
    html = result.get("Content", "")
    print(f"[Buckler] Status: {status}, Size: {len(html)} bytes")
    if status != 200:
        print("[Buckler] Non-200, using mock")
        return _gen_mock(sf6_id)
    (DUMP_DIR / f"{sf6_id}_page.html").write_text(html, encoding="utf-8")
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', html, re.DOTALL)
    if not m:
        print("[Buckler] No __NEXT_DATA__, using mock")
        return _gen_mock(sf6_id)
    raw = json.loads(m.group(1))
    (DUMP_DIR / f"{sf6_id}_nextdata.json").write_text(json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8")
    data = _parse(raw, sf6_id)
    if data:
        print(f"[Buckler] REAL: {data.username} ({len(data.characters)} chars)")
        return data
    print("[Buckler] Parse failed, using mock")
    return _gen_mock(sf6_id)
''')
print("Client rebuilt from scratch!")
