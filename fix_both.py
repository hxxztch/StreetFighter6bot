# 1. Add Yasmine + M.Bison variants to CHAR_CN in client.py
cpath = r"src\buckler\client.py"
with open(cpath, "r", encoding="utf-8") as f:
    cc = f.read()

old_cn = """    "Sagat": "沙加特", "C.Viper": "深红毒蛇", "Ingrid": "英格丽德","""
new_cn = """    "Sagat": "沙加特", "C.Viper": "深红毒蛇", "Ingrid": "英格丽德",
    "Yasmine": "亚斯敏",
    "M. Bison": "维嘉", "M Bison": "维嘉", "MBison": "维嘉","""
cc = cc.replace(old_cn, new_cn)
with open(cpath, "w", encoding="utf-8") as f:
    f.write(cc)
print("CHAR_CN updated: Yasmine + M.Bison variants")

# 2. Fix rank display in dashboard_renderer.py
dpath = r"src\charts\dashboard_renderer.py"
with open(dpath, "r", encoding="utf-8") as f:
    dc = f.read()

# Find where the HTML template uses rank_str
# The template has: {rank_str} in the rank-box div
# We need to add proper rank display logic BEFORE the return line

# Find the variable assignments before the return
idx_rank = dc.find("rank_str = chars")
if idx_rank < 0:
    # Search for how rank_str is set
    idx_rank = dc.find("rank_str = first_char") if "first_char" in dc else -1
if idx_rank < 0:
    idx_rank = dc.find('{"rank"')
    if idx_rank >= 0:
        # rank_str is read from chars but not stored separately
        # Just find where chars is defined
        pass

# Find the return statement
idx_return = dc.find("return f")
if idx_return < 0:
    idx_return = dc.find("return f")  # f-string start

# Add rank display logic before the return
rank_logic = """
    # Rank display logic
    rank_display = ""
    if chars:
        r = chars[0]
        rs = r.get("rank", "")
        if "Master" in rs:
            import re as _re
            m = _re.search(r'(\\d+)MR', rs)
            rank_display = f'<div class=\\"rank-box\\"><div class=\\"rank-name\\">MASTER</div><div class=\\"rank-lp\\">{m.group(1)}<span style=\\"font-size:10px\\"> MR</span></div></div>'
        else:
            rank_display = f'<div class=\\"rank-box\\"><div class=\\"rank-name\\">{rs[:12].strip()}</div><div class=\\"rank-lp\\">{rs}<span style=\\"font-size:10px\\"> LP</span></div></div>'
    """

# Insert rank_logic before the return, and replace the old rank-box in the HTML
# First, find and replace the old rank-box HTML in the template
old_rank_html = '<div class="rank-box"><div class="rank-tier">{rank_str}</div><div class="rank-lp">{rank_str}<span style="font-size:10px">LP</span></div></div>'
new_rank_html = '{rank_display}'
dc = dc.replace(old_rank_html, new_rank_html)

# Also try the variant without rank-tier
old_rank_html2 = '<div class="rank-box"><div class="rank-tier">{rank_str[:12]}</div><div class="rank-lp">{rank_str}<span style="font-size:10px">LP</span></div></div>'
dc = dc.replace(old_rank_html2, new_rank_html)

# Insert the rank_logic before the return f-string
if idx_return > 0:
    dc = dc[:idx_return] + rank_logic + "\n    " + dc[idx_return:]

with open(dpath, "w", encoding="utf-8") as f:
    f.write(dc)
print("Rank display fixed: Master shows MR, Diamond shows LP")
