path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the multi-season fetch logic to try multiple URL formats
old = """                print(f\"[Buckler] Trying season {sid}...\")
            sd = _fetch_and_parse(f\"{base}?season={sid}\", cookie, sf6_id, f\"S{sid}\")"""

new = """                for fmt in [\"?season=\", \"?season_id=\", \"?s=\"]:
                    url = base + fmt + str(sid)
                    print(f\"[Buckler] Season {sid}: {url.split(\"profile/\")[1]}\")
                    sd = _fetch_and_parse(url, cookie, sf6_id, f\"S{sid}\")
                    if sd and sd.get(\"raw\"):
                        break"""

content = content.replace(old, new)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Multi-season URL: try 3 query formats (?season=, ?season_id=, ?s=)")
