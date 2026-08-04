import re
path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Check for _gen_mock
found = list(re.finditer(r'_gen_mock', content))
print(str(len(found)) + " _gen_mock found")
for m in found:
    start = max(0, m.start() - 20)
    end = min(len(content), m.end() + 30)
    print("  ..." + repr(content[start:end]) + "...")

# Replace all _gen_mock containing lines
lines = content.split('\n')
removed = 0
for i, line in enumerate(lines):
    if '_gen_mock' in line:
        # Replace the line with raise Exception
        indent = len(line) - len(line.lstrip())
        lines[i] = ' ' * indent + 'raise Exception("数据解析失败")'
        removed += 1
if removed > 0:
    content = '\n'.join(lines)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Replaced " + str(removed) + " lines")
else:
    print("No _gen_mock references to remove")
