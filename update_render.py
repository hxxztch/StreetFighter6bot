import os
BASE = r"E:\Study\sf6-qq-bot"
def w(p, c):
    fp = os.path.join(BASE, p)
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    with open(fp, "w", encoding="utf-8") as f:
        f.write(c)
    print("OK: " + p)

# Update __init__.py
w(r"src\charts\__init__.py", '"""charts module"""\nfrom src.charts.dashboard_renderer import render as generate_charts\n')

# Update renderer.py to keep matplotlib as fallback
w(r"src\charts\renderer.py", '"""SF6 data charts - matplotlib fallback (kept for reference)"""\nimport matplotlib; matplotlib.use("Agg")\n# This module is replaced by dashboard_renderer.py for production use.\n# Import dashboard_renderer.generate_charts instead.\n')

# Update bot2.py to use new renderer
bpath = r"bot2.py"
with open(bpath, "r", encoding="utf-8") as f:
    bcontent = f.read()

# Replace import
old_imp = "from src.charts.renderer import generate_charts"
new_imp = "from src.charts.dashboard_renderer import render as generate_charts"
if old_imp in bcontent:
    bcontent = bcontent.replace(old_imp, new_imp)
    with open(bpath, "w", encoding="utf-8") as f:
        f.write(bcontent)
    print("OK: bot2.py updated")
else:
    # Check if already using dashboard_renderer
    if "dashboard_renderer" in bcontent:
        print("bot2.py already uses dashboard_renderer")
    else:
        print("Import not found in bot2.py, checking...")

print("\nDone! Restart: python bot2.py")
