path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix: save dump regardless of status, try multiple URLs
old_scrape = """def scrape_fighter_card(sf6_id):
    url = f\"{BUCKLER_BASE_URL}/fighter_card/{sf6_id}\"

    print(f\"[Buckler] Fetching {url} via PowerShell...\")
    result = _ps_fetch(url, timeout=20)"""

new_scrape = """def scrape_fighter_card(sf6_id):
    urls = [
        f\"{BUCKLER_BASE_URL}/profile/{sf6_id}\",
        f\"{BUCKLER_BASE_URL}/fighter_card/{sf6_id}\",
        f\"{BUCKLER_BASE_URL}/en/profile/{sf6_id}\",
        f\"{BUCKLER_BASE_URL}/en/fighter_card/{sf6_id}\",
        f\"{BUCKLER_BASE_URL}/api/en/profile/{sf6_id}\",
        f\"{BUCKLER_BASE_URL}/api/profile/{sf6_id}\",
    ]
    for url in urls:
        result = None
        print(f\"[Buckler] Trying {url}...\")
        result = _ps_fetch(url, timeout=20)"""

content = content.replace(old_scrape, new_scrape)

# Fix the rest of scrape_fighter_card to loop over URLs
old_loop = """    if not result:"""

new_loop = """        if not result:
            print(f\"[Buckler] PS failed, trying requests...\")
            try:
                import requests; s = requests.Session()
                s.verify = False; s.trust_env = False; s.proxies = {\"http\": None, \"https\": None}
                s.headers.update({\"User-Agent\": \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0\"})
                r = s.get(url, timeout=15)
                result = {\"StatusCode\": r.status_code, \"Content\": r.text}
            except Exception as e:
                print(f\"[Requests] {e}\")
                continue

        status = result.get(\"StatusCode\", 0)
        html = result.get(\"Content\", \"\")
        print(f\"[Buckler] {url} -> {status} ({len(html)} bytes)\")

        # Save ALL responses for debugging
        safe_url = url.replace(\"https://www.streetfighter.com/6/buckler/\", \"\").replace(\"/\", \"_\")
        (DUMP_DIR / f\"{sf6_id}_{safe_url}.html\").write_text(html, encoding=\"utf-8\")

        if status != 200 or not html:
            continue"""

content = content.replace(old_loop, new_loop)

# Fix the remaining code that was after the URL
old_fallback = """    if not result:
        # Try requests as fallback
        try:
            import requests
            s = requests.Session()
            s.verify = False; s.trust_env = False; s.proxies = {\"http\": None, \"https\": None}
            s.headers.update({\"User-Agent\": \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0\"})
            r = s.get(url, timeout=15)
            result = {\"StatusCode\": r.status_code, \"Content\": r.text}
        except Exception as e:
            print(f\"[Requests fallback] Failed: {e}\")
            return None

    status = result.get(\"StatusCode\", 0)
    html = result.get(\"Content\", \"\")
    print(f\"[Buckler] Status: {status}, Size: {len(html)} bytes\")

    if status != 200 or not html:
        return None

    # Save for debugging
    (DUMP_DIR / f\"{sf6_id}_page.html\").write_text(html, encoding=\"utf-8\")"""

new_fallback = """    # Try __NEXT_DATA__"""

content = content.replace(old_fallback, new_fallback)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Multi-URL probe + dump-all-responses applied!")
