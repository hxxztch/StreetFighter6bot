path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add cookie loading function
cookie_load = '''
def _load_cookie():
    try:
        p = __import__("pathlib").Path(BUCKLER_COOKIE_FILE)
        if p.exists():
            c = p.read_text(encoding="utf-8").strip()
            if c and not c.startswith("#"):
                return c
    except: pass
    return None
'''
content = content.replace("DUMP_DIR = DATA_DIR / \"buckler_dumps\"", "BUCKLER_COOKIE_FILE = DATA_DIR / \"buckler_cookie.txt\"\nDUMP_DIR = DATA_DIR / \"buckler_dumps\"")
content = content.replace("DUMP_DIR.mkdir(parents=True, exist_ok=True)", "DUMP_DIR.mkdir(parents=True, exist_ok=True)\n" + cookie_load)

# 2. Update _ps_fetch to accept and use cookie
old_ps = """def _ps_fetch(url, timeout=15):
    ps_sc = (
        '[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; '
        'try{$r=Invoke-WebRequest -Uri \"' + url + '\" -Method Get -TimeoutSec ' + str(timeout) + ' -UseBasicParsing; '
        '$b=[System.Text.Encoding]::UTF8.GetBytes($r.Content);$b64=[Convert]::ToBase64String($b); '
        '[PSCustomObject]@{StatusCode=$r.StatusCode;ContentBase64=$b64}|ConvertTo-Json -Compress}catch{exit 1}'"""

new_ps = """def _ps_fetch(url, timeout=15, cookie=None):
    cookie_part = ''
    if cookie:
        cookie_part = ' -Headers @{\"Cookie\"=\"' + cookie.replace('\"', '\\\\\"') + '\"}'
    ps_sc = (
        '[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; '
        'try{$r=Invoke-WebRequest -Uri \"' + url + '\" -Method Get -TimeoutSec ' + str(timeout) + ' -UseBasicParsing' + cookie_part + '; '
        '$b=[System.Text.Encoding]::UTF8.GetBytes($r.Content);$b64=[Convert]::ToBase64String($b); '
        '[PSCustomObject]@{StatusCode=$r.StatusCode;ContentBase64=$b64}|ConvertTo-Json -Compress}catch{exit 1}'"""

content = content.replace(old_ps, new_ps)

# 3. Update _req_fetch to use cookie
old_req = """def _req_fetch(url):
    try:
        import requests
        s = requests.Session()
        s.verify = False; s.trust_env = False; s.proxies = {\"http\": None, \"https\": None}
        s.headers.update({\"User-Agent\": \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0 Safari/537.36\"})
        r = s.get(url, timeout=15)
        return {\"StatusCode\": r.status_code, \"Content\": r.text}
    except Exception as e:
        print(f\"[Requests] {e}\")
        return None"""

new_req = """def _req_fetch(url, cookie=None):
    try:
        import requests
        s = requests.Session()
        s.verify = False; s.trust_env = False; s.proxies = {\"http\": None, \"https\": None}
        s.headers.update({\"User-Agent\": \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0 Safari/537.36\"})
        if cookie:
            s.headers.update({\"Cookie\": cookie})
        r = s.get(url, timeout=15)
        return {\"StatusCode\": r.status_code, \"Content\": r.text}
    except Exception as e:
        print(f\"[Requests] {e}\")
        return None"""

content = content.replace(old_req, new_req)

# 4. Update scrape_fighter_card to load and pass cookie
old_scrape = """def scrape_fighter_card(sf6_id):
    urls = ["""

new_scrape = """def scrape_fighter_card(sf6_id):
    cookie = _load_cookie()
    if cookie:
        print(f\"[Buckler] Using cookie ({len(cookie)} chars)\")
    else:
        print(f\"[Buckler] No cookie found\")\n    urls = ["""

content = content.replace(old_scrape, new_scrape)

# 5. Update the calls to pass cookie
content = content.replace("result = _ps_fetch(url, 20)", "result = _ps_fetch(url, 20, cookie)")
content = content.replace("result = _req_fetch(url)", "result = _req_fetch(url, cookie)")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Cookie integration complete!")
