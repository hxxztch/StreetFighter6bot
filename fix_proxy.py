path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()
content = content.replace(
    "s.verify = False",
    "s.verify = False\n    s.trust_env = False\n    s.proxies = {\"http\": None, \"https\": None}"
)
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Proxy bypass added!")
