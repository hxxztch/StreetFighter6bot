path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix ALL character name assignments in _parse
# 1. Fix the `name = item.get("character_name", "Unknown")` line  
old_name_assign = 'name = item.get("character_name", "Unknown")'
new_name_assign = 'name = CHAR_CN.get(item.get("character_name", ""), item.get("character_name", "Unknown"))'
content = content.replace(old_name_assign, new_name_assign)

# 2. Fix opponent names in matchup parsing
old_opp_key = 'key = opp_name'
new_opp_key = 'key = CHAR_CN.get(opp_name, opp_name)'
content = content.replace(old_opp_key, new_opp_key)

# 3. Fix opponent name display
old_mu_name = 'opponent_char=opp_name,'
new_mu_name = 'opponent_char=CHAR_CN.get(opp_name, opp_name),'
content = content.replace(old_mu_name, new_mu_name)

# 4. Also fix the dashboard - character name in header (main char)
dpath = r"src\charts\dashboard_renderer.py"
with open(dpath, "r", encoding="utf-8") as f:
    dc = f.read()

# Fix main char name in header
old_main = "Main: {chars[0]['name'] if chars else 'N/A'}"
new_main = "Main: {chars[0]['name'] if chars else 'N/A'}"
dc = dc.replace(old_main, new_main)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
with open(dpath, "w", encoding="utf-8") as f:
    f.write(dc)
print("All character names now run through CHAR_CN")
