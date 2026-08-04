"""Buckler client - clean version"""
import json, random, re, subprocess, asyncio, base64
from pathlib import Path
from src.config import BUCKLER_BASE_URL, DATA_DIR
from src.buckler.models import (PlayerData, GameModeTime, CharacterStat, TechStats, DriveUsage, MatchupStat, RecentMatch)

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0 Safari/537.36"
DUMP_DIR = DATA_DIR / "buckler_dumps"
CK_PATH = DATA_DIR / "buckler_cookie.txt"
DUMP_DIR.mkdir(parents=True, exist_ok=True)

SESSION_DIR = DATA_DIR / "buckler_session"

CHAR_CN = {"Ryu":"隆","Luke":"卢克","Ken":"肯","Chun-Li":"春丽","Guile":"古烈","Blanka":"布兰卡","Zangief":"桑吉尔夫","Dhalsim":"达尔西姆","E.Honda":"本田","Dee Jay":"迪杰","Kimberly":"金佰莉","Jamie":"杰米","Manon":"曼侬","Marisa":"玛丽莎","JP":"JP","Juri":"朱莉","Cammy":"嘉米","Lily":"莉莉","Rashid":"拉希德","A.K.I.":"阿鬼","Ed":"爱德","Akuma":"豪鬼","M.Bison":"维嘉","M. Bison":"维嘉","Terry":"特瑞","Mai":"舞","Elena":"艾琳娜","Sagat":"沙加特","Yasmine":"亚斯敏","C.Viper":"深红毒蛇","Ingrid":"英格丽德","Alex":"阿历克斯","Oro":"欧罗","Rose":"罗斯","Edmond Honda":"本田","Any":"总计",}

def _load_cookie():
    try:
        if CK_PATH.exists():
            c = CK_PATH.read_text(encoding="utf-8").strip()
            if c and not c.startswith("#"):
                return c
    except: pass
    if SESSION_DIR.exists():
        import asyncio as _asyncio
        try:
            from src.buckler.session import refresh_cookie
            return _asyncio.run(refresh_cookie())
        except (RuntimeError, Exception):
            pass
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
    for name, fn in [("urllib", lambda: _urllib_fetch(url, cookie)), ("PS", lambda: _ps_fetch(url, cookie)), ("requests", lambda: _req_fetch(url, cookie))]:
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
    games_played = (bs.get("rank_match_play_count", 0) or 0) + (bs.get("casual_match_play_count", 0) or 0) + (bs.get("battle_hub_match_play_count", 0) or 0)
    data.tech_stats = TechStats(
        games_played=games_played,
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
        drive_parry=bs.get("drive_parry", 0) or 0,
        drive_reversal=bs.get("drive_reversal", 0) or 0,
        stuns=bs.get("stun", 0) or 0,
        stuns_received=bs.get("received_stun", 0) or 0,
        throw_drive_parry=bs.get("throw_drive_parry", 0) or 0,
        received_throw_drive_parry=bs.get("received_throw_drive_parry", 0) or 0,
        sa_lv1_rate=bs.get("gauge_rate_sa_lv1", 0) or 0,
        sa_lv2_rate=bs.get("gauge_rate_sa_lv2", 0) or 0,
        sa_lv3_rate=bs.get("gauge_rate_sa_lv3", 0) or 0,
        ca_rate=bs.get("gauge_rate_ca", 0) or 0,
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

async def fetch_player_data(sf6_id):
    cookie = _load_cookie()
    if not cookie:
        raise Exception("Cookie闁哄牜浜崢銈囩磾椤曞棛绀夐悹鍥у槻閸樻盯宕烽妸锔俱偦閻熸瑥鐗嗗▍鎺楁儌鐠囪尙绉緽uckler闁告艾瀛╄ぐ渚€宕ｉ張鍣妎kie闁?data/buckler_cookie.txt")
    print(f"[Buckler] Cookie: {len(cookie)} chars")
    url = f"{BUCKLER_BASE_URL}/profile/{sf6_id}"
    result = _fetch(url, cookie)
    if not result:
        print("[Buckler] Fetch failed")
        raise Exception("Cookie闁哄牜浜崢銈囩磾椤曞棛绀夐悹鍥у槻閸樻盯宕烽妸锔俱偦閻熸瑥鐗嗗▍鎺楁儌鐠囪尙绉緽uckler闁告艾瀛╄ぐ渚€宕ｉ張鍣妎kie闁?data/buckler_cookie.txt")
    status = result.get("StatusCode", 0)
    html = result.get("Content", "")
    print(f"[Buckler] Status: {status}, Size: {len(html)} bytes")
    if status != 200:
        print("[Buckler] Non-200: " + str(status))
        raise Exception("Cookie闁哄牜浜崢銈囩磾椤曞棛绀夐悹鍥у槻閸樻盯宕烽妸锔俱偦閻熸瑥鐗嗗▍鎺楁儌鐠囪尙绉緽uckler闁告艾瀛╄ぐ渚€宕ｉ張鍣妎kie闁?data/buckler_cookie.txt")
    # Retry if page too small (search page instead of profile)
    import time as _t, random as _rnd
    _retry = 0
    while len(html) < 50000 and _retry < 2:
        _retry += 1
        print(f"[Buckler] Small page ({len(html)}b), retry {_retry}/2...")
        _t.sleep(1.5)
        # Try with cache-busting param
        _bu = url + ("&" if "?" in url else "?") + "_t=" + str(int(_t.time()))
        _r2 = _fetch(_bu, cookie)
        if not _r2 or _r2.get("StatusCode",0) != 200:
            _r2 = _fetch(url, cookie)  # fallback to original
        if _r2 and _r2.get("StatusCode",0) == 200 and len(_r2.get("Content","")) > len(html):
            html = _r2["Content"]
            print(f"[Buckler] Retry: {len(html)} bytes")
    
    if len(html) < 50000:
        (DUMP_DIR / f"{sf6_id}_small_page.html").write_text(html, encoding="utf-8")
        print("[Buckler] Small page saved as _small_page.html")
    (DUMP_DIR / f"{sf6_id}_page.html").write_text(html, encoding="utf-8")
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', html, re.DOTALL)
    if not m:
        print("[Buckler] No __NEXT_DATA__")
        raise Exception("Cookie闁哄牜浜崢銈囩磾椤曞棛绀夐悹鍥у槻閸樻盯宕烽妸锔俱偦閻熸瑥鐗嗗▍鎺楁儌鐠囪尙绉緽uckler闁告艾瀛╄ぐ渚€宕ｉ張鍣妎kie闁?data/buckler_cookie.txt")
    raw = json.loads(m.group(1))
    (DUMP_DIR / f"{sf6_id}_nextdata.json").write_text(json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8")
    data = _parse(raw, sf6_id)
    if not data:
        print("[Buckler] Parse failed - page may be incomplete or player has no data")
        raise Exception("Cookie闁哄牜浜崢銈囩磾椤曞棛绀夐悹鍥у槻閸樻盯宕烽妸锔俱偦閻熸瑥鐗嗗▍鎺楁儌鐠囪尙绉緽uckler闁告艾瀛╄ぐ渚€宕ｉ張鍣妎kie闁?data/buckler_cookie.txt")
    
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
    
    print(f"[Buckler] REAL: {data.username} ({len(data.characters)} chars)")
    # Battle log
    bl_url = f"{BUCKLER_BASE_URL}/profile/{sf6_id}/battlelog"
    print(f"[Buckler] Fetching battle log: {bl_url}")
    bl_result = _fetch(bl_url, cookie)
    if bl_result and bl_result.get("StatusCode", 0) == 200:
        bl_html = bl_result.get("Content", "")
        bl_m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', bl_html, re.DOTALL)
        if bl_m:
            bl_raw = json.loads(bl_m.group(1))
            bl_pp = bl_raw.get("props", {}).get("pageProps", {}) or {}
            replay_list = bl_pp.get("replay_list", []) or []
            print(f"[Buckler] Replay list: {len(replay_list)} entries")
            for entry in replay_list[:5]:
                if not isinstance(entry, dict): continue
                p1 = entry.get("player1_info", {}) or {}
                p2 = entry.get("player2_info", {}) or {}
                p1_sid = str((p1.get("player", {}) or {}).get("short_id", ""))
                p2_sid = str((p2.get("player", {}) or {}).get("short_id", ""))
                tid = str(sf6_id)
                if p2_sid == tid: u, o = p2, p1
                elif p1_sid == tid: u, o = p1, p2
                else: u, o = p2, p1
                ur = u.get("round_results", []) or []; orr = o.get("round_results", []) or []
                uw = sum(1 for r in ur if r == 1); ow = sum(1 for r in orr if r == 1)
                res = "win" if uw > ow else "lose"
                uc = CHAR_CN.get(u.get("character_name",""), u.get("character_name","?"))
                oc = CHAR_CN.get(o.get("character_name",""), o.get("character_name","?"))
                on = (o.get("player",{}) or {}).get("fighter_id","?")
                md = entry.get("replay_battle_type_name","?")
                ts = entry.get("uploaded_at",0) or 0
                if ts:
                    import datetime
                    ds = datetime.datetime.fromtimestamp(ts).strftime("%m/%d %H:%M")
                else:
                    ds = "?"
                data.recent_matches.append(RecentMatch(date=ds, opponent_name=str(on), opponent_char=str(oc), player_char=str(uc), result=res, mode=str(md), rounds_won=uw, rounds_lost=ow, lp_change=0))
        else:
            print(f"[Buckler] No __NEXT_DATA__ in battle log response")
    else:
        print(f"[Buckler] BL status: {bl_result.get('StatusCode',0) if bl_result else 'None'}")
    return data
