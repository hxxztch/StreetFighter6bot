path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Strategy 1: Replace "M.Bison":"维加", → add "M. Bison"
r1 = content.replace('"M.Bison":"维加",', '"M.Bison":"维加","M. Bison":"维加",')
r2 = r1.replace('"M.Bison":"维加"', '"M.Bison":"维加","M. Bison":"维加"')

# Strategy 2: Replace "Sagat":"沙加特", → add "Yasmine"
r3 = r2.replace('"Sagat":"沙加特",', '"Sagat":"沙加特","Yasmine":"亚斯敏",')
r4 = r3.replace('"Sagat":"沙加特"', '"Sagat":"沙加特","Yasmine":"亚斯敏"')

with open(path, "w", encoding="utf-8") as f:
    f.write(r4)

# Verify
with open(path, "r", encoding="utf-8") as f:
    vc = f.read()
for n in ["M. Bison", "M.Bison", "Yasmine"]:
    print(n + ": " + ("OK" if n in vc else "FAIL"))
