path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Add Chinese name mapping at module level (after imports)
cn_map = """
CHAR_CN = {
    "Ryu": "隆", "Luke": "卢克", "Ken": "肯", "Chun-Li": "春丽",
    "Guile": "古烈", "Blanka": "布兰卡", "Zangief": "桑吉尔夫",
    "Dhalsim": "达尔西姆", "E.Honda": "本田", "Dee Jay": "迪杰",
    "Kimberly": "金佰莉", "Jamie": "杰米", "Manon": "曼侬",
    "Marisa": "玛丽莎", "JP": "JP", "Juri": "朱莉", "Cammy": "嘉米",
    "Lily": "莉莉", "Rashid": "拉希德", "A.K.I.": "阿鬼",
    "Ed": "爱德", "Akuma": "豪鬼", "M.Bison": "维加",
    "Terry": "特瑞", "Mai": "舞", "Elena": "艾琳娜",
    "Sagat": "沙加特", "C.Viper": "深红毒蛇", "Ingrid": "英格丽德",
    "Alex": "阿历克斯", "Oro": "欧罗", "Rose": "罗斯",
    "Edmond Honda": "本田", "Any": "总计",
    "DeeJay": "迪杰", "MBison": "维加", "CViper": "深红毒蛇",
}
"""

# Insert after CHAR_COLORS line
idx = content.find("CHAR_COLORS = [")
end_idx = content.find("\n", content.find("]", idx)) + 1
content = content[:end_idx] + cn_map + content[end_idx:]

# Replace character names in _parse function - when building CharacterStat
old_name = """name=c.get("characterName","") or c.get("character_name","") or "Unknown","""
new_name = """name=CHAR_CN.get(c.get("character_name","") or c.get("characterName",""), c.get("character_name","") or c.get("characterName","") or "Unknown","""
content = content.replace(old_name, new_name)

# In matchup parsing - translate opponent names
old_opp = """opp_name = id_to_name.get(opp_id, f"ID{opp_id}")"""
new_opp = """opp_name = CHAR_CN.get(id_to_name.get(opp_id, ""), id_to_name.get(opp_id, f"ID{opp_id}"))"""
content = content.replace(old_opp, new_opp)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Chinese character name mappings added!")
