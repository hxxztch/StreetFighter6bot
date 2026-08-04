path = r"src\charts\dashboard_renderer.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Find where rank_tier is set
import re
matches = list(re.finditer(r'rank_(?:tier|lp|score|unit|str)', content))
print("rank_ variables found:")
for m in matches:
    line_start = content.rfind('\n', 0, m.start()) + 1
    line_end = content.find('\n', m.end())
    print(f"  pos={m.start()}: {content[line_start:line_end].strip()}")
