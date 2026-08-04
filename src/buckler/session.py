
"""Persistent Playwright session for Buckler cookie management"""
from pathlib import Path
from src.config import DATA_DIR

SESSION_DIR = DATA_DIR / "buckler_session"
CK_PATH = DATA_DIR / "buckler_cookie.txt"

async def refresh_cookie():
    """Launch persistent Playwright browser to refresh Buckler cookie"""
    try:
        from playwright.async_api import async_playwright
        if not SESSION_DIR.exists():
            print("[Session] No persistent session found. Run: python setup_session.py")
            return None
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                str(SESSION_DIR), headless=True,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            await page.goto("https://www.streetfighter.com/6/buckler", timeout=15000, wait_until="domcontentloaded")
            cookies = await context.cookies()
            cookie_str = "; ".join(
                "{}={}".format(c["name"], c["value"]) for c in cookies
                if "streetfighter.com" in c.get("domain", "")
            )
            CK_PATH.write_text(cookie_str, encoding="utf-8")
            await context.close()
            print("[Buckler] Cookie auto-refreshed via Playwright ({} chars)".format(len(cookie_str)))
            return cookie_str
    except Exception as e:
        print("[Buckler] Playwright refresh failed: {}".format(e))
        return None

