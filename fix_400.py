path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = """    if status != 200:
        print("[Buckler] Non-200")
        return _gen_mock(sf6_id)"""

new = """    if status != 200:
        print("[Buckler] Non-200")
        if status in (400, 404):
            return None
        return _gen_mock(sf6_id)"""

content = content.replace(old, new)
with open(path, "w", encoding="utf-8") as f:
    f.write(content)

# Update bot2.py to handle None from fetch_player_data
bpath = r"bot2.py"
with open(bpath, "r", encoding="utf-8") as f:
    bcontent = f.read()

old2 = """            await send_group_msg(ws, group_id, at_user + "正在抓取数据并生成图表，请稍候...")
        try:
            data = await fetch_player_data(sid)
            try:
                await set_cached_stats(sid, dataclasses.asdict(data))
            except:
                pass
        except Exception as e:
            await send_group_msg(ws, group_id, at_user + "数据抓取失败：" + str(e))
            return"""

new2 = """            await send_group_msg(ws, group_id, at_user + "正在抓取数据并生成图表，请稍候...")
        try:
            data = await fetch_player_data(sid)
            if data is None:
                await send_group_msg(ws, group_id, at_user + "玩家ID无效或不存在，请检查")
                return
            try:
                await set_cached_stats(sid, dataclasses.asdict(data))
            except:
                pass
        except Exception as e:
            await send_group_msg(ws, group_id, at_user + "数据抓取失败：" + str(e))
            return"""

bcontent = bcontent.replace(old2, new2)
with open(bpath, "w", encoding="utf-8") as f:
    f.write(bcontent)
print("400/404 now returns helpful error instead of mock")
