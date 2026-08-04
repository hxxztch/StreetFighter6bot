path = r"bot2.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old1 = "if not arg or not arg.isdigit() or len(arg) > 20:"
new1 = "if not arg or not arg.isdigit() or len(arg) != 10:"
content = content.replace(old1, new1)

old2 = "if not arg.isdigit() or len(arg) > 20:"
new2 = "if not arg.isdigit() or len(arg) != 10:"
content = content.replace(old2, new2)

old3 = "请输入有效的玩家ID（纯数字且不超过20位）"
new3 = "请输入10位纯数字玩家ID"
content = content.replace(old3, new3)

old4 = "玩家ID需为纯数字且不超过20位"
new4 = "玩家ID需为10位纯数字"
content = content.replace(old4, new4)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("ID validation: exactly 10 digits required")
