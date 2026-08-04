path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the ENTIRE fetch_player_data function
old_func = "async def fetch_player_data(sf6_id):"
next_func = content.find("\n# ---", content.find(old_func))
if next_func < 0:
    next_func = len(content)

new_func = """async def fetch_player_data(sf6_id):
    cookie = _load_cookie()
    if not cookie:
        return _gen_mock(sf6_id)
    print(f"[Buckler] Cookie: {len(cookie)} chars")
    url = f"{BUCKLER_BASE_URL}/profile/{sf6_id}"
    result = _fetch(url, cookie)
    if not result:
        print("[Buckler] Fetch failed")
        return _gen_mock(sf6_id)
    status = result.get("StatusCode", 0)
    html = result.get("Content", "")
    print(f"[Buckler] Status: {status}, Size: {len(html)} bytes")
    if status != 200:
        print("[Buckler] Non-200")
        return _gen_mock(sf6_id)
    (DUMP_DIR / f"{sf6_id}_page.html").write_text(html, encoding="utf-8")
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', html, re.DOTALL)
    if not m:
        print("[Buckler] No __NEXT_DATA__")
        return _gen_mock(sf6_id)
    raw = json.loads(m.group(1))
    (DUMP_DIR / f"{sf6_id}_nextdata.json").write_text(json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8")
    data = _parse(raw, sf6_id)
    if not data:
        print("[Buckler] Parse failed")
        return _gen_mock(sf6_id)
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
    return data"""

if next_func > 0 and next_func > content.find(old_func):
    content = content[:content.find(old_func)] + new_func + content[next_func:]
else:
    content = content[:content.find(old_func)] + new_func

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("fetch_player_data rewritten with direct battle log fetching!")
