# Revert client.py - remove 400/404 special handling
cpath = r"src\buckler\client.py"
with open(cpath, "r", encoding="utf-8") as f:
    cc = f.read()
old_c = """    if status != 200:
        print("[Buckler] Non-200")
        if status in (400, 404):
            return None
        return _gen_mock(sf6_id)"""
new_c = """    if status != 200:
        print("[Buckler] Non-200: " + str(status))
        return _gen_mock(sf6_id)"""
cc = cc.replace(old_c, new_c)
with open(cpath, "w", encoding="utf-8") as f:
    f.write(cc)

# Revert bot2.py - remove None check
bpath = r"bot2.py"
with open(bpath, "r", encoding="utf-8") as f:
    bc = f.read()
old_b = """            await send_group_msg(ws, group_id, at_user + '正在抓取数据并生成图表，请稍候...')
        try:
            data = await fetch_player_data(sid)
            if data is None:
                await send_group_msg(ws, group_id, at_user + '玩家ID无效或不存在，请检查')
                return
            try:
                await set_cached_stats(sid, dataclasses.asdict(data))
            except:
                pass
        except Exception as e:
            await send_group_msg(ws, group_id, at_user + '数据抓取失败：' + str(e))
            return"""
new_b = """            await send_group_msg(ws, group_id, at_user + '正在抓取数据并生成图表，请稍候...')
        try:
            data = await fetch_player_data(sid)
            try:
                await set_cached_stats(sid, dataclasses.asdict(data))
            except:
                pass
        except Exception as e:
            await send_group_msg(ws, group_id, at_user + '数据抓取失败：' + str(e))
            return"""
bc = bc.replace(old_b, new_b)

# Fix the bind validation - only check non-digit and length > 20
old_b2 = """        if not arg or not arg.isdigit():
            await send_group_msg(ws, group_id, at_user + '请输入有效的玩家ID（纯数字），如 /bind 4222666364')
            return"""
new_b2 = """        if not arg or not arg.isdigit() or len(arg) > 20:
            await send_group_msg(ws, group_id, at_user + '请输入有效的玩家ID（纯数字且不超过20位）')
            return"""
bc = bc.replace(old_b2, new_b2)

# Fix dashboard validation too
old_b3 = """            if not arg.isdigit():
                await send_group_msg(ws, group_id, at_user + '玩家ID需为纯数字')
                return"""
new_b3 = """            if not arg.isdigit() or len(arg) > 20:
                await send_group_msg(ws, group_id, at_user + '玩家ID需为纯数字且不超过20位')
                return"""
bc = bc.replace(old_b3, new_b3)

with open(bpath, "w", encoding="utf-8") as f:
    f.write(bc)
print("Reverted: only validate non-digit and >20 chars")
