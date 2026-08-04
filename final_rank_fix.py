import re
path = r"src\charts\dashboard_renderer.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Find the exact rank-box HTML to replace
old_box = '<div class="rank-box">\n    <div class="rank-name">{chars[0][\'rank\'][:12] if chars else \'Unranked\'}</div>\n    <div class="rank-lp">{chars[0][\'rank\'] if chars else \'\'}<span style="font-size:10px">LP</span></div>\n  </div>'

# Check if this exact string exists
if old_box in content:
    content = content.replace(old_box, '{rank_display}')
    print("Replaced rank-box HTML")
else:
    # Try different whitespace
    old_box2 = '<div class="rank-box">\n    <div class="rank-name">{chars[0][\'rank\'][:12] if chars else \'Unranked\'}</div>\n    <div class="rank-lp">{chars[0][\'rank\'] if chars else \'\'}<span style="font-size:10px">LP</span></div></div>'
    if old_box2 in content:
        content = content.replace(old_box2, '{rank_display}')
        print("Replaced rank-box HTML (variant 2)")
    else:
        # Try regex
        pattern = r'<div class="rank-box">.*?</div>\s*</div>'
        m = re.search(pattern, content, re.DOTALL)
        if m:
            content = content[:m.start()] + '{rank_display}' + content[m.end():]
            print("Replaced via regex")
        else:
            print("Could not find rank-box pattern")
            # Show context around 'Unranked'
            idx = content.find("'Unranked'")
            if idx >= 0:
                print("Context around 'Unranked':")
                print(content[idx-100:idx+150])

# Check if rank_display is defined
if 'def _gen_html' in content and 'rank_display' in content and '{rank_display}' in content:
    print("CHECK: rank_display is defined AND used in template")
elif 'rank_display' in content and '{rank_display}' not in content:
    print("WARNING: rank_display defined but NOT used in template")
elif 'rank_display' not in content:
    print("WARNING: rank_display NOT defined")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
