import os

BASE = r"E:\Study\sf6-qq-bot"

def write(path, content):
    fpath = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(fpath), exist_ok=True)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK: {path}")

write(r"src\database.py", r'''"""SQLite database - QQ bindings and data cache"""
import aiosqlite
import json
import time
from src.config import DATABASE_PATH, CACHE_TTL

_db = None

async def get_db():
    global _db
    if _db is None:
        _db = await aiosqlite.connect(DATABASE_PATH)
        _db.row_factory = aiosqlite.Row
        await _db.execute("PRAGMA journal_mode=WAL")
        await _init_tables()
    return _db

async def _init_tables():
    db = await get_db()
    await db.execute("""CREATE TABLE IF NOT EXISTS bindings (
        qq_id TEXT PRIMARY KEY, sf6_id TEXT NOT NULL,
        created_at INTEGER NOT NULL DEFAULT (unixepoch()))""")
    await db.execute("""CREATE TABLE IF NOT EXISTS stats_cache (
        sf6_id TEXT PRIMARY KEY, data_json TEXT NOT NULL,
        updated_at REAL NOT NULL)""")
    await db.commit()

async def bind_qq_to_sf6(qq_id, sf6_id):
    db = await get_db()
    await db.execute("INSERT OR REPLACE INTO bindings (qq_id, sf6_id, created_at) VALUES (?, ?, unixepoch())", (str(qq_id), sf6_id))
    await db.commit()

async def get_binding(qq_id):
    db = await get_db()
    cursor = await db.execute("SELECT sf6_id FROM bindings WHERE qq_id = ?", (str(qq_id),))
    row = await cursor.fetchone()
    return row["sf6_id"] if row else None

async def get_cached_stats(sf6_id):
    db = await get_db()
    cursor = await db.execute("SELECT data_json, updated_at FROM stats_cache WHERE sf6_id = ?", (sf6_id,))
    row = await cursor.fetchone()
    if row is None or time.time() - row["updated_at"] > CACHE_TTL:
        return None
    return json.loads(row["data_json"])

async def set_cached_stats(sf6_id, data):
    db = await get_db()
    await db.execute("INSERT OR REPLACE INTO stats_cache (sf6_id, data_json, updated_at) VALUES (?, ?, ?)", (sf6_id, json.dumps(data, ensure_ascii=False), time.time()))
    await db.commit()

async def close_db():
    global _db
    if _db:
        await _db.close()
        _db = None
''')

print("Phase 2: database done!")
