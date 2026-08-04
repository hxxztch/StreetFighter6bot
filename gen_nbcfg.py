import os
BASE = r"E:\Study\sf6-qq-bot"
def w(path, content):
    fpath = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(fpath), exist_ok=True)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK: {path}")

# Update .env with proper NoneBot2 keys
w(".env", r"""# NoneBot2 configuration
DRIVER=~httpx+~websockets
ONEBOT_WS_URLS=["ws://127.0.0.1:3001"]
SUPERUSERS=[""]

# Buckler's Boot Camp
BUCKLER_BASE_URL=https://www.streetfighter.com/6/buckler
BUCKLER_COOKIE_FILE=data/buckler_cookie.txt

# Chart settings
CHART_DPI=150
CHART_FIGSIZE=14,10
""")

# Update bot.py with correct config
w("bot.py", r'''"""SF6 QQ Bot - NoneBot2 main entry"""
import nonebot
from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(OneBotV11Adapter)

nonebot.load_plugins("src/plugins")

if __name__ == "__main__":
    nonebot.run()
''')

# Update config.py to remove dotenv dependency
w(r"src\config.py", r'''"""global config"""
import os
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_PATH = str(DATA_DIR / "sf6bot.db")
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

print("All configs updated for NoneBot2!")
