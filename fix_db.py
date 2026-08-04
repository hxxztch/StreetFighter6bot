import os
BASE = r"E:\Study\sf6-qq-bot"
def w(path, content):
    fpath = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(fpath), exist_ok=True)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK: {path}")

# Rewrite database with sqlite3 + executor (no aiosqlite)
w(r"src\database.py", r'''"""SQLite database using built-in sqlite3 + executor (Windows-safe)"""
import sqlite3, json, time, asyncio
from src.config import DATABASE_PATH

def _init_db():
    """Synchronous database initialization"""
    db = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("""CREATE TABLE IF NOT EXISTS bindings (
        qq_id TEXT PRIMARY KEY, sf6_id TEXT NOT NULL,
        created_at INTEGER NOT NULL DEFAULT (strftime('%s','now')))""")
    db.execute("""CREATE TABLE IF NOT EXISTS stats_cache (
        sf6_id TEXT PRIMARY KEY, data_json TEXT NOT NULL,
        updated_at REAL NOT NULL)""")
    db.commit()
    return db

class Database:
    def __init__(self):
        self._db = None
        self._lock = asyncio.Lock()

    async def _connect(self):
        if self._db is None:
            loop = asyncio.get_running_loop()
            self._db = await loop.run_in_executor(None, _init_db)
        return self._db

    async def bind_qq_to_sf6(self, qq_id, sf6_id):
        async with self._lock:
            db = await self._connect()
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, lambda: db.execute(
                "INSERT OR REPLACE INTO bindings (qq_id, sf6_id, created_at) VALUES (?, ?, strftime('%s','now'))",
                (str(qq_id), sf6_id)
            ))
            await loop.run_in_executor(None, db.commit)

    async def get_binding(self, qq_id):
        db = await self._connect()
        loop = asyncio.get_running_loop()
        cursor = await loop.run_in_executor(None, lambda: db.execute(
            "SELECT sf6_id FROM bindings WHERE qq_id = ?", (str(qq_id),)
        ))
        row = await loop.run_in_executor(None, cursor.fetchone)
        return row["sf6_id"] if row else None

    async def get_cached_stats(self, sf6_id):
        db = await self._connect()
        loop = asyncio.get_running_loop()
        cursor = await loop.run_in_executor(None, lambda: db.execute(
            "SELECT data_json, updated_at FROM stats_cache WHERE sf6_id = ?", (sf6_id,)
        ))
        row = await loop.run_in_executor(None, cursor.fetchone)
        if row is None or time.time() - row["updated_at"] > 3600:
            return None
        return json.loads(row["data_json"])

    async def set_cached_stats(self, sf6_id, data):
        async with self._lock:
            db = await self._connect()
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, lambda: db.execute(
                "INSERT OR REPLACE INTO stats_cache (sf6_id, data_json, updated_at) VALUES (?, ?, ?)",
                (sf6_id, json.dumps(data, ensure_ascii=False), time.time())
            ))
            await loop.run_in_executor(None, db.commit)

_db_instance = Database()

async def get_binding(qq_id):
    return await _db_instance.get_binding(qq_id)

async def bind_qq_to_sf6(qq_id, sf6_id):
    await _db_instance.bind_qq_to_sf6(qq_id, sf6_id)

async def get_cached_stats(sf6_id):
    return await _db_instance.get_cached_stats(sf6_id)

async def set_cached_stats(sf6_id, data):
    await _db_instance.set_cached_stats(sf6_id, data)

async def close_db():
    if _db_instance._db:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, _db_instance._db.close)
        _db_instance._db = None
''')

# Update stats plugin with try/except and better error logging
w(r"src\plugins\stats.py", r'''"""SF6 stats command"""
import asyncio, dataclasses, traceback
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment
from src.database import get_binding, get_cached_stats, set_cached_stats
from src.buckler.client import fetch_player_data
from src.buckler.models import PlayerData
from src.analyzer.stats import analyze
from src.charts.renderer import generate_charts
from src.config import CHART_OUTPUT_DIR

sf6_cmd = on_command("sf6", aliases={"街霸6","SF6"}, priority=5, block=True)

@sf6_cmd.handle()
async def hsf6(event: MessageEvent, args: Message = CommandArg()):
    try:
        arg = args.extract_plain_text().strip()
        qq = str(event.user_id)
        if arg:
            sid = arg
        else:
            sid = await get_binding(qq)
            if not sid:
                await sf6_cmd.finish("Please bind first: !bind <SF6 ID>\nOr query directly: !sf6 <Player ID>")
        await sf6_cmd.send("Fetching SF6 data and generating charts, please wait...")
        try:
            cached = await get_cached_stats(sid)
            if cached:
                data = PlayerData(**cached)
                await sf6_cmd.send("(From cache)")
            else:
                data = await fetch_player_data(sid)
                await set_cached_stats(sid, dataclasses.asdict(data))
        except Exception as fe:
            await sf6_cmd.send(f"Data fetch failed: {fe}")
            return
        loop = asyncio.get_running_loop()
        img_path = await loop.run_in_executor(None, generate_charts, data)
        a = analyze(data)
        summary = f"=== {a['username']} SF6 Report ===\nPlatform: {a['platform']} | Games: {a['total_games']} | WR: {a['overall_wr']}\nTime: {a['total_time']}\n"
        rw = a.get("recent_wr","")
        if rw: summary += f"Recent WR: {rw}\n"
        summary += "\n--- Characters ---\n"
        for c in a["characters"][:5]:
            summary += f"  {c['name']}: {c['rank']} | {c['record']} ({c['win_rate']})\n"
        msg = summary + MessageSegment.image(f"file:///{img_path.as_posix()}")
        await sf6_cmd.finish(msg)
    except Exception as e:
        await sf6_cmd.send(f"Error: {e}")
        traceback.print_exc()
''')

print("Database + stats plugin fixed!")
