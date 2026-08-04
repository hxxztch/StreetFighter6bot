path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix the mock username (two places: the f-string template and the return statement)
content = content.replace("Fighter_", "Player_")
content = content.replace("{sf6_id[-8:]}", "{sf6_id}")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Username now shows full player ID (e.g. Player_4222666364)")
