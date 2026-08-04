import sqlite3, os
from pathlib import Path

ROOT = Path(__file__).parent
DB = ROOT / "data" / "sf6bot2.db"

if not DB.exists():
    print("数据库文件不存在")
    exit()

db = sqlite3.connect(str(DB))
# Only clear stats cache, keep bindings
db.execute("DELETE FROM stats_cache")
db.commit()

# Verify
remaining = db.execute("SELECT COUNT(*) FROM stats_cache").fetchone()[0]
bindings = db.execute("SELECT COUNT(*) FROM bindings").fetchone()[0]
db.close()

print("stats_cache: 0 rows (cleared)")
print("bindings: " + str(bindings) + " rows (kept)")
print("Done")
