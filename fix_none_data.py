path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Change "Parse failed" to print page size info
content = content.replace(
    'print("[Buckler] Parse failed")',
    'print("[Buckler] Parse failed - page may be incomplete or player has no data")'
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

# Fix bot2.py to handle None from fetch_player_data
bpath = r"bot2.py"
with open(bpath, "r", encoding="utf-8") as f:
    bc = f.read()

# For /dashboard handler - add None check after fetch
old = """            try:
                data = await fetch_player_data(sid)
                try:
                    await set_cached_stats(sid, dataclasses.asdict(data))
                except:
                    pass
            except Exception as e:
                await send_group_msg(ws, group_id, at_user + "数据抓取失败：" + str(e))
                return

        loop = asyncio.get_running_loop()
        try:
            img_path = await generate_charts(data)"""

new = """            try:
                data = await fetch_player_data(sid)
                if data is None:
                    await send_group_msg(ws, group_id, at_user + "该玩家暂无有效数据，可能未注册Buckler")
                    return
                try:
                    await set_cached_stats(sid, dataclasses.asdict(data))
                except:
                    pass
            except Exception as e:
                await send_group_msg(ws, group_id, at_user + "数据抓取失败：" + str(e))
                return

        loop = asyncio.get_running_loop()
        try:
            img_path = await generate_charts(data)"""

bc = bc.replace(old, new)

# Same for /card handler
old2 = """            try:
                data = await fetch_player_data(sid)
                from src.analyzer.stats import analyze"""

new2 = """            try:
                data = await fetch_player_data(sid)
                if data is None:
                    await send_group_msg(ws, group_id, at_user + "该玩家暂无有效数据，可能未注册Buckler")
                    return
                from src.analyzer.stats import analyze"""

bc = bc.replace(old2, new2)

with open(bpath, "w", encoding="utf-8") as f:
    f.write(bc)
print("Added None-data handling for /dashboard and /card")
