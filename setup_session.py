"""Setup persistent browser session for Buckler - run once, login manually, session auto-saved"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

SESSION_DIR = Path("data/buckler_session")
BUCKLER_URL = "https://www.streetfighter.com/6/buckler"

async def main():
    SESSION_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            str(SESSION_DIR),
            headless=False,
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print(f"[Session] Opening {BUCKLER_URL} ...")
        print("[Session] Please login to your Capcom ID in the browser window.")
        print("[Session] After login, browse to your Buckler profile page, then press Enter here...")

        await page.goto(BUCKLER_URL, timeout=30000, wait_until="domcontentloaded")

        input("[Session] Press Enter once you're logged in and can see your profile...")

        # Verify session works by navigating to profile
        try:
            await page.goto(f"{BUCKLER_URL}/profile", timeout=15000, wait_until="domcontentloaded")
            title = await page.title()
            print(f"[Session] Page title: {title}")
        except Exception as e:
            print(f"[Session] Warning: {e}")

        # Extract and save cookies to the text file format
        cookies = await context.cookies()
        cookie_str = "; ".join(f"{c['name']}={c['value']}" for c in cookies if c.get('domain', '').endswith('streetfighter.com'))
        cookie_path = Path("data/buckler_cookie.txt")
        cookie_path.write_text(cookie_str, encoding="utf-8")
        print(f"[Session] Cookie saved to {cookie_path} ({len(cookie_str)} chars)")

        await context.close()
        print("[Session] Done! The session will persist across bot restarts.")

asyncio.run(main())
