path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = """        if ct == 1: gt.ranked_time = pt
        elif ct == 2: gt.casual_time = pt
        elif ct == 5: gt.battle_hub_time = pt
        elif ct == 3: gt.arcade_time = pt
        elif ct == 4: gt.training_time = pt"""

new = """        if ct == 2: gt.ranked_time = pt
        elif ct == 5: gt.casual_time = pt
        elif ct == 4: gt.battle_hub_time = pt
        elif ct == 3: gt.arcade_time = pt
        elif ct == 8: gt.training_time = pt"""

content = content.replace(old, new)
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Content type mapping fixed: 2=Ranked 4=BH 5=Casual 8=Training")
