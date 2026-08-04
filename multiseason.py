path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Find scrape function and add multi-season support
old_scrape = """def scrape(sf6_id):
    url = f\"{BUCKLER_BASE_URL}/profile/{sf6_id}\"
    cookie = _load_cookie()
    print(f\"[Buckler] URL: {url}\")
    if cookie: print(f\"[Buckler] Cookie: {len(cookie)} chars\")

    result = _fetch(url, cookie)
    if not result:
        print(\"[Buckler] All methods failed\")
        return None

    status = result.get(\"StatusCode\", 0)
    html = result.get(\"Content\", \"\")
    print(f\"[Buckler] -> {status} ({len(html)} bytes)\")

    (DUMP_DIR / f\"{sf6_id}_profile.html\").write_text(html, encoding=\"utf-8\")

    if status != 200:
        m = re.search(r'\"statusCode\":(\\d+)', html)
        sc = int(m.group(1)) if m else status
        print(f\"[Buckler] Status code in JSON: {sc}\")
        if sc == 200 and html:
            pass
        elif status == 403:
            print(\"[Buckler] 403 - needs valid auth cookie or invalid player ID\")
            return None
        elif status == 404:
            print(\"[Buckler] 404 - player not found\")
            return None

    m = re.search(r'<script id=\"__NEXT_DATA__\" type=\"application/json\">(.+?)</script>', html, re.DOTALL)
    if m:
        raw = json.loads(m.group(1))
        (DUMP_DIR / f\"{sf6_id}_nextdata.json\").write_text(json.dumps(raw, indent=2, ensure_ascii=False), encoding=\"utf-8\")
        sc = raw.get(\"props\", {}).get(\"pageProps\", {}).get(\"common\", {}).get(\"statusCode\", 0)
        print(f\"[Buckler] __NEXT_DATA__ statusCode: {sc}\")
        parsed = _parse(raw, sf6_id)
        if parsed: return parsed
        if sc != 200:
            return None

    return None"""

new_scrape = """def _fetch_and_parse(url, cookie, sf6_id, label):
    result = _fetch(url, cookie)
    if not result: return None
    status = result.get(\"StatusCode\", 0)
    html = result.get(\"Content\", \"\")
    if status != 200: return None
    m = re.search(r'<script id=\"__NEXT_DATA__\" type=\"application/json\">(.+?)</script>', html, re.DOTALL)
    if not m: return None
    raw = json.loads(m.group(1))
    sc = raw.get(\"props\", {}).get(\"pageProps\", {}).get(\"common\", {}).get(\"statusCode\", 0)
    pp = raw.get(\"props\", {}).get(\"pageProps\", {})
    play = pp.get(\"play\", {})
    seasons = play.get(\"season_ids\", [])
    cli = play.get(\"character_league_infos\", [])
    return {\"raw\": raw, \"play\": play, \"seasons\": seasons, \"cli\": cli, \"pp\": pp}

def scrape(sf6_id):
    cookie = _load_cookie()
    if not cookie:
        print(\"[Buckler] No cookie\")
        return None
    print(f\"[Buckler] Cookie: {len(cookie)} chars\")

    base = f\"{BUCKLER_BASE_URL}/profile/{sf6_id}\"

    # Fetch current season
    print(f\"[Buckler] Fetching current season...\")
    data = _fetch_and_parse(base, cookie, sf6_id, \"current\")
    if not data:
        print(\"[Buckler] Current season fetch failed\")
        return None

    raw = data[\"raw\"]
    (DUMP_DIR / f\"{sf6_id}_nextdata.json\").write_text(json.dumps(raw, indent=2, ensure_ascii=False), encoding=\"utf-8\")

    # Merge character LP from multiple seasons
    merged_cli = {c.get(\"character_name\", \"\"): c for c in data.get(\"cli\", [])}
    seen_seasons = {data[\"play\"].get(\"current_season_id\", -1)}

    seasons = data.get(\"seasons\", [])
    if seasons:
        current = data[\"play\"].get(\"current_season_id\", seasons[0])
        prev_seasons = [s for s in seasons if s != current and s > current - 5]
        for sid in prev_seasons[:3]:  # Try 3 most recent previous seasons
            if sid in seen_seasons: continue
            print(f\"[Buckler] Trying season {sid}...\")
            sd = _fetch_and_parse(f\"{base}?season={sid}\", cookie, sf6_id, f\"S{sid}\")
            if sd:
                seen_seasons.add(sid)
                for c in sd.get(\"cli\", []):
                    name = c.get(\"character_name\", \"\")
                    if name and c.get(\"league_info\", {}).get(\"league_point\", -1) > 0:
                        if name not in merged_cli or merged_cli[name].get(\"league_info\", {}).get(\"league_point\", -1) <= 0:
                            merged_cli[name] = c

    # Update pp.data for parsing
    data[\"pp\"][\"play\"][\"character_league_infos\"] = list(merged_cli.values())
    data[\"raw\"][\"props\"][\"pageProps\"][\"play\"][\"character_league_infos\"] = list(merged_cli.values())

    parsed = _parse(data[\"raw\"], sf6_id)
    if parsed: return parsed

    return None"""

content = content.replace(old_scrape, new_scrape)
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Multi-season support added!")
