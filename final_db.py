import os
BASE = r"E:\Study\sf6-qq-bot"
def w(path, content):
    fpath = os.path.join(BASE, path)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK: {path}")

# Update config to use new db name
w(r"src\config.py", r'''"""global config"""
import os
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_PATH = str(DATA_DIR / "sf6bot2.db")
BUCKLER_BASE_URL = os.getenv("BUCKLER_BASE_URL", "https://www.streetfighter.com/6/buckler")
BUCKLER_API_BASE = "https://www.streetfighter.com/6/buckler/api"
BUCKLER_COOKIE_FILE = str(DATA_DIR / os.getenv("BUCKLER_COOKIE_FILE", "buckler_cookie.txt"))
CHART_DPI = int(os.getenv("CHART_DPI", "150"))
_fsize_raw = os.getenv("CHART_FIGSIZE", "14,10").split(",")
CHART_FIGSIZE = (int(_fsize_raw[0]), int(_fsize_raw[1]))
CHART_OUTPUT_DIR = DATA_DIR / "charts"
CHART_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CACHE_TTL = 3600
''')

# Simplest possible database module
w(r"src\database.py", r'''"""SQLite database - minimal sync version, wrapped in executor"""
import sqlite3, json, time, asyncio, functools
from src.config import DATABASE_PATH

class SimpleDB:
    def __init__(self):
        self._db = None

    def _get_db(self):
        if self._db is None:
            self._db = sqlite3.connect(DATABASE_PATH)
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
''')

print("Database + config completely rewritten!")
