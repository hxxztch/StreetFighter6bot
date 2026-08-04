path = r"bot2.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = 'msg += "/help — 显示本帮助"'
new = 'msg += "/card — 深度攻防分析卡片\\n/help — 显示本帮助"'
content = content.replace(old, new)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Help updated with /card")
