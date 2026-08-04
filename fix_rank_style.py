path = r"src\charts\dashboard_renderer.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = """            rank_display = f'<div class=\\"rank-box\\"><div class=\\"rank-name\\">{rs[:12].strip()}</div><div class=\\"rank-lp\\">{rs}<span style=\\"font-size:10px\\"> LP</span></div></div>'"""

new = """            parts = rs.split()
            tier_name = parts[0] if parts else rs[:12]
            score_str = ' '.join(parts[1:]) if len(parts) > 1 else ''
            rank_display = f'<div class=\\"rank-box\\"><div class=\\"rank-name\\">{tier_name}</div><div class=\\"rank-lp\\">{score_str}<span style=\\"font-size:10px\\"> LP</span></div></div>'"""

content = content.replace(old, new)
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Non-Master rank now shows tier + score like Master style")
