import sqlite3, time, os
os.remove('data/sf6bot.db')
db = sqlite3.connect('data/sf6bot.db')
db.row_factory = sqlite3.Row
db.execute("CREATE TABLE IF NOT EXISTS bindings (qq_id TEXT PRIMARY KEY, sf6_id TEXT NOT NULL, created_at REAL)")
db.execute("INSERT OR REPLACE INTO bindings VALUES (?, ?, ?)", ('test123', '4222666364', time.time()))
db.commit()
r = db.execute("SELECT sf6_id FROM bindings WHERE qq_id = ?", ('test123',)).fetchone()
print('Result:', r['sf6_id'] if r else 'NONE')
db.close()
