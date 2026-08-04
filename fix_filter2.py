path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = "data.characters.sort(key=lambda x: (x.league_points if hasattr(x,'league_points') else -1, x.usage_count), reverse=True)"
new = "data.characters = [c for c in data.characters if c.total > 0]\n    data.characters.sort(key=lambda x: (x.league_points if hasattr(x,'league_points') else -1, x.usage_count), reverse=True)"
content = content.replace(old, new)

# Also filter in dashboard renderer - explicit check
dpath = r"src\charts\dashboard_renderer.py"
with open(dpath, "r", encoding="utf-8") as f:
    dcontent = f.read()
old2 = "for i, c in enumerate(chars[:10]):"
new2 = "for i, c in enumerate([x for x in chars if x.get('usage_count',0) > 0][:10]):"
dcontent = dcontent.replace(old2, new2)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
with open(dpath, "w", encoding="utf-8") as f:
    f.write(dcontent)
print("Filter applied in both parser and dashboard renderer")
