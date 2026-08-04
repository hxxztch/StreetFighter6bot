path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Find ALL _gen_mock references
import re
positions = list(re.finditer(r'_gen_mock', content))
print(str(len(positions)) + " _gen_mock references found")

# Replace all _gen_mock calls with exceptions
content = content.replace('return _gen_mock(sf6_id)', 'raise Exception("数据不可用")')
content = content.replace('return _gen_mock(sf6_id)  # fallback', 'raise Exception("数据不可用")')

# Double check
positions2 = list(re.finditer(r'_gen_mock', content))
print(str(len(positions2)) + " remaining after fix")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Cleaned all mock references")
