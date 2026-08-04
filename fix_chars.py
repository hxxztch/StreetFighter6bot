path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Fix character sorting - LP first, then usage count
old_sort = "data.characters.sort(key=lambda x: x.usage_count, reverse=True)"
new_sort = "data.characters.sort(key=lambda x: (x.league_points if hasattr(x,'league_points') else -1, x.usage_count), reverse=True)"
content = content.replace(old_sort, new_sort)

# 2. Increase season fetch to 5 previous seasons
old_seasons = "prev_seasons[:3]"
new_seasons = "prev_seasons[:6]"
content = content.replace(old_seasons, new_seasons)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Sort: LP priority | Seasons: up to 6 previous")

# 3. Fix dashboard HTML to show more characters (all ranked + up to 8 total)
dpath = r"src\charts\dashboard_renderer.py"
with open(dpath, "r", encoding="utf-8") as f:
    dcontent = f.read()

# Change chars[:6] to show all characters with non-zero games
old_chars = "for i, c in enumerate(chars[:6]):"
new_chars = "for i, c in enumerate(chars[:10]):"
dcontent = dcontent.replace(old_chars, new_chars)

with open(dpath, "w", encoding="utf-8") as f:
    f.write(dcontent)
print("HTML: show up to 10 characters")
