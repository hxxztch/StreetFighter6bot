"""global config"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

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

# AI 对话接口（OpenAI 兼容协议，可接 OpenAI / DeepSeek / Qwen / Moonshot / 本地 Ollama 等）
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.openai.com/v1")
AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini")
AI_ENABLED = bool(AI_API_KEY)
