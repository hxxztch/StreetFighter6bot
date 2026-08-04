path = r"src\charts\dashboard_renderer.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

render_func = """

async def render(data: PlayerData, output_filename: str = None) -> Path:
    from playwright.async_api import async_playwright
    html = _gen_html(data)
    if output_filename is None:
        output_filename = "sf6_" + str(data.player_id) + ".png"
    output_path = CHART_OUTPUT_DIR / output_filename
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 820, "height": 1400})
        await page.set_content(html, wait_until="networkidle")
        await __import__("asyncio").sleep(1.5)
        await page.screenshot(path=str(output_path), full_page=True)
        await browser.close()
    return output_path
"""
content += render_func
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("render function appended!")
