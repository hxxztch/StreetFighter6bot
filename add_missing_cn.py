path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# "M.Bison" is at position 1233, add "M. Bison" next to it
old = '"M.Bison": "维加",'
new = '"M.Bison": "维加",\n    "M. Bison": "维加",'
content = content.replace(old, new)

# Add Yasmine next to the Y section or end of CHAR_CN
old2 = '"Sagat": "沙加特",'
new2 = '"Sagat": "沙加特",\n    "Yasmine": "亚斯敏",'
content = content.replace(old2, new2)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

# Verify
with open(path, "r", encoding="utf-8") as f:
    vcontent = f.read()
for name in ["M. Bison", "M.Bison", "Yasmine"]:
    print(name + ": " + ("OK" if name in vcontent else "FAIL"))
