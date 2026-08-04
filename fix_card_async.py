# Fix card_renderer.py - make all async
cpath = r"src\charts\card_renderer.py"
with open(cpath, "r", encoding="utf-8") as f:
    cc = f.read()

# Replace render_card to be async
old = """def render_card(data, chars_list):
    analysis = analyze_card(data, chars_list)
    html = _gen_html(analysis)
    return _sync_render(html, data.player_id)

def _sync_render(html, player_id):
    import asyncio
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(_render(html, player_id))
    finally:
        loop.close()"""

new = """async def render_card(data, chars_list):
    analysis = analyze_card(data, chars_list)
    html = _gen_html(analysis)
    return await _render(html, data.player_id)"""

cc = cc.replace(old, new)
with open(cpath, "w", encoding="utf-8") as f:
    f.write(cc)

# Fix bot2.py - await render_card
bpath = "bot2.py"
with open(bpath, "r", encoding="utf-8") as f:
    bc = f.read()

old2 = "card_data = render_card(data, a.get(\"characters\", []))"
new2 = "card_data = await render_card(data, a.get(\"characters\", []))"
bc = bc.replace(old2, new2)

with open(bpath, "w", encoding="utf-8") as f:
    f.write(bc)
print("Card renderer and bot2.py updated to async")
