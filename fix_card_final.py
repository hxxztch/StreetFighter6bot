# Rewrite card_renderer.py to match dashboard pattern exactly
cpath = r"src\charts\card_renderer.py"
with open(cpath, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find and replace render_card to use same pattern as dashboard_renderer
content = open(cpath, "r", encoding="utf-8").read()
old = """async def render_card(data, chars_list):
    analysis = analyze_card(data, chars_list)
    html = _gen_html(analysis)
    return await _render(html, data.player_id)"""

new = """async def render_card(data, chars_list):
    from playwright.async_api import async_playwright
    analysis = analyze_card(data, chars_list)
    html = _gen_html(analysis)
    output_path = CHART_OUTPUT_DIR / f\"card_{data.player_id}.png\"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={\"width\": 820, \"height\": 1600})
        await page.set_content(html, wait_until=\"networkidle\")
        await __import__(\"asyncio\").sleep(1)
        await page.screenshot(path=str(output_path), full_page=True)
        await browser.close()
    return output_path"""

content = content.replace(old, new)

# Remove _render function
old2 = """
async def _render(html, player_id):
    from playwright.async_api import async_playwright"""
end2 = content.find("def _gen_html", content.find(old2))
if end2 > 0:
    content = content[:content.find(old2)] + "\n" + content[end2:]

with open(cpath, "w", encoding="utf-8") as f:
    f.write(content)
print("Card renderer rewritten to match dashboard pattern")
