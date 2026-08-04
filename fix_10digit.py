path = r"bot2.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix bind validation
old1 = '"if not arg or not arg.isdigit():"'
new1 = '"if not arg or not arg.isdigit() or len(arg) != 10:"'
content = content.replace(old1, new1)

# Fix dashboard validation  
old2 = 'if not arg.isdigit():'
new2 = 'if not arg.isdigit() or len(arg) != 10:'
content = content.replace(old2, new2)

# Fix bind error message
old3 = '请输入有效的玩家ID（纯数字），如 /bind 4222666364'
new3 = '请输入10位纯数字玩家ID，如 /bind 4222666364'
content = content.replace(old3, new3)

# Fix dashboard error message
old4 = '玩家ID需为纯数字'
new4 = '玩家ID需为10位纯数字'
content = content.replace(old4, new4)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

# Verify
with open(path, "r", encoding="utf-8") as f:
    vc = f.read()
for term in ['len(arg) != 10', '10位纯数字']:
    if term in vc:
        print(term + ': OK')
    else:
        print(term + ': NOT FOUND')
