path = r"bot2.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Unify all ID validation messages
content = content.replace("请输入10位纯数字玩家ID，如 /bind 4222666364", "请输入有效的玩家ID（10位纯数字）")
content = content.replace("玩家ID需为10位纯数字", "请输入有效的玩家ID（10位纯数字）")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("All ID validation messages unified")
