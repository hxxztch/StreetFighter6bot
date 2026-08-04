"""SQLite database - minimal sync version, wrapped in executor"""
import sqlite3, json, time, asyncio, functools
from src.config import DATABASE_PATH

class SimpleDB:
    def __init__(self):
        self._db = None

    def _get_db(self):
        if self._db is None:
            self._db = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            self._db.row_factory = sqlite3.Row
            self._db.execute("""CREATE TABLE IF NOT EXISTS bindings (
                qq_id TEXT PRIMARY KEY, sf6_id TEXT NOT NULL, created_at REAL)""")
            self._db.execute("""CREATE TABLE IF NOT EXISTS stats_cache (
                sf6_id TEXT PRIMARY KEY, data_json TEXT, updated_at REAL)""")
            self._db.commit()
        return self._db

    def _db_bind(self, qq_id, sf6_id):
        self._get_db().execute("INSERT OR REPLACE INTO bindings VALUES(?,?,?)",
            (str(qq_id), sf6_id, time.time()))
        self._get_db().commit()

    def _db_get_binding(self, qq_id):
        r = self._get_db().execute("SELECT sf6_id FROM bindings WHERE qq_id=?",
            (str(qq_id),)).fetchone()
        return r["sf6_id"] if r else None

    def _db_get_cache(self, sf6_id):
        r = self._get_db().execute("SELECT data_json, updated_at FROM stats_cache WHERE sf6_id=?",
            (sf6_id,)).fetchone()
        if r and time.time() - r["updated_at"] < 3600:
            return json.loads(r["data_json"])
        return None

    def _db_set_cache(self, sf6_id, data):
        self._get_db().execute("INSERT OR REPLACE INTO stats_cache VALUES(?,?,?)",
            (sf6_id, json.dumps(data, ensure_ascii=False), time.time()))
        self._get_db().commit()

db = SimpleDB()

async def get_binding(qq_id):
    return await asyncio.get_running_loop().run_in_executor(None, db._db_get_binding, qq_id)

async def bind_qq_to_sf6(qq_id, sf6_id):
    await asyncio.get_running_loop().run_in_executor(None, db._db_bind, qq_id, sf6_id)

async def get_cached_stats(sf6_id):
    return await asyncio.get_running_loop().run_in_executor(None, db._db_get_cache, sf6_id)

async def set_cached_stats(sf6_id, data):
    await asyncio.get_running_loop().run_in_executor(None, db._db_set_cache, sf6_id, data)
