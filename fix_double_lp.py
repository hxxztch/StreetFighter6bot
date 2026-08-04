path = r"src\charts\dashboard_renderer.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = """            tier_map = {"D1":"DIAMOND","D2":"DIAMOND","D3":"DIAMOND","D4":"DIAMOND","D5":"DIAMOND",
                        "P1":"PLATINUM","P2":"PLATINUM","P3":"PLATINUM","P4":"PLATINUM","P5":"PLATINUM",
                        "G1":"GOLD","G2":"GOLD","G3":"GOLD","G4":"GOLD","G5":"GOLD",
                        "S1":"SILVER","S2":"SILVER","S3":"SILVER","S4":"SILVER","S5":"SILVER",
                        "B1":"BRONZE","B2":"BRONZE","B3":"BRONZE","B4":"BRONZE","B5":"BRONZE",
                        "I1":"IRON","I2":"IRON","I3":"IRON","I4":"IRON","I5":"IRON",
                        "R1":"ROOKIE","R2":"ROOKIE"}
            tier_name = tier_map.get(tier_short, tier_short)
            rank_display = f'<div class=\\"rank-box\\"><div class=\\"rank-name\\">{tier_name}</div><div class=\\"rank-lp\\">{rs}<span style=\\"font-size:10px\\"> LP</span></div></div>'"""

new = """            tier_map = {"D1":"DIAMOND","D2":"DIAMOND","D3":"DIAMOND","D4":"DIAMOND","D5":"DIAMOND",
                        "P1":"PLATINUM","P2":"PLATINUM","P3":"PLATINUM","P4":"PLATINUM","P5":"PLATINUM",
                        "G1":"GOLD","G2":"GOLD","G3":"GOLD","G4":"GOLD","G5":"GOLD",
                        "S1":"SILVER","S2":"SILVER","S3":"SILVER","S4":"SILVER","S5":"SILVER",
                        "B1":"BRONZE","B2":"BRONZE","B3":"BRONZE","B4":"BRONZE","B5":"BRONZE",
                        "I1":"IRON","I2":"IRON","I3":"IRON","I4":"IRON","I5":"IRON",
                        "R1":"ROOKIE","R2":"ROOKIE"}
            tier_name = tier_map.get(tier_short, tier_short)
            rs_clean = rs.replace("LP","").strip()
            rank_display = f'<div class=\\"rank-box\\"><div class=\\"rank-name\\">{tier_name}</div><div class=\\"rank-lp\\">{rs_clean}<span style=\\"font-size:10px\\"> LP</span></div></div>'"""

content = content.replace(old, new)
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed: removed double LP suffix")
