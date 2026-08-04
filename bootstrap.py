import os
BASE = r"E:\Study\sf6-qq-bot"
files = {}
files["requirements.txt"] = "nb-cli>=1.4.0\nnonebot2[websockets]>=2.3.0\nhttpx>=0.24.0\naiosqlite>=0.19.0\nmatplotlib>=3.5.0\npillow>=9.0.0\npydantic>=2.0.0\npython-dotenv>=1.0.0\nnumpy>=1.21.0\nlxml>=4.9.0\n"
files[".env"] = "BOT_WS_URL=ws://127.0.0.1:3001\nSUPERUSERS=[]\nBUCKLER_BASE_URL=https://www.streetfighter.com/6/buckler\nCHART_DPI=150\nCHART_FIGSIZE=14,10\n"
files["src\\__init__.py"] = '"""SF6 QQ Bot"""\n'
files["src\\config.py"] = '"""global config"""\nimport os\nfrom pathlib import Path\nROOT_DIR = Path(__file__).resolve().parent.parent\nDATA_DIR = ROOT_DIR / "data"\nDATA_DIR.mkdir(parents=True, exist_ok=True)\nDATABASE_PATH = str(DATA_DIR / "sf6bot.db")\nBOT_WS_URL = os.getenv("BOT_WS_URL", "ws://127.0.0.1:3001")\nSUPERUSERS = []\nBUCKLER_BASE_URL = os.getenv("BUCKLER_BASE_URL", "https://www.streetfighter.com/6/buckler")\nBUCKLER_API_BASE = "https://www.streetfighter.com/6/buckler/api"\nCHART_DPI = int(os.getenv("CHART_DPI", "150"))\n_fsize_raw = os.getenv("CHART_FIGSIZE", "14,10").split(",")\nCHART_FIGSIZE = (int(_fsize_raw[0]), int(_fsize_raw[1]))\nCHART_OUTPUT_DIR = DATA_DIR / "charts"\nCHART_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)\nCACHE_TTL = 3600\n'
files["src\\plugins\\__init__.py"] = '"""plugins"""\n'
files["src\\buckler\\__init__.py"] = '"""buckler module"""\nfrom src.buckler.client import fetch_player_data\n'
files["src\\analyzer\\__init__.py"] = '"""analyzer module"""\nfrom src.analyzer.stats import analyze\n'
files["src\\charts\\__init__.py"] = '"""charts module"""\nfrom src.charts.renderer import generate_charts\n'
for relpath, content in files.items():
    fpath = os.path.join(BASE, relpath)
    os.makedirs(os.path.dirname(fpath), exist_ok=True)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK: {relpath}")
print("Phase 1 done!")
