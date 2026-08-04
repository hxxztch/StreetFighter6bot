path = r"src\charts\dashboard_renderer.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix rank display in header - extract tier/score properly
old_rank = """    rank_tier = ""
    rank_lp = ""
    if chars:
        first_char = chars[0]
        rank_str = first_char.get("rank", "")
        rank_tier = rank_str[:12]
        rank_lp = rank_str"""

new_rank = """    rank_tier = ""
    rank_score = ""
    rank_unit = "LP"
    if chars:
        first_char = chars[0]
        rank_str = first_char.get("rank", "")
        if "Master" in rank_str:
            rank_tier = "MASTER"
            import re as _re
            mr_match = _re.search(r'(\d+)MR', rank_str)
            rank_score = mr_match.group(1) if mr_match else ""
            rank_unit = "MR"
        elif "Diamond" in rank_str or rank_str.startswith("D"):
            rank_tier = "DIAMOND"
            parts = rank_str.split()
            rank_score = parts[1] if len(parts) > 1 else ""
        elif rank_str and rank_str != "Unranked":
            parts = rank_str.split(maxsplit=1)
            rank_tier = parts[0] if parts else rank_str[:12]
            rank_score = parts[1] if len(parts) > 1 else ""
        else:
            rank_tier = rank_str[:12]"""

content = content.replace(old_rank, new_rank)

# Fix the HTML to use rank_score and rank_unit
old_html = """<div class="rank-badge">
    <div class="rank-tier">{rank_tier}</div>
    <div class="rank-lp">{rank_lp}<span style="font-size:10px">LP</span></div>
  </div>"""

new_html = """<div class="rank-badge">
    <div class="rank-tier">{rank_tier}</div>
    <div class="rank-lp">{rank_score}<span style="font-size:10px"> {rank_unit}</span></div>
  </div>"""

content = content.replace(old_html, new_html)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Master display fixed: shows MR not LP, tier/score separated")
