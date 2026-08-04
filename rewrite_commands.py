path = r"bot2.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old_func_start = "async def handle_message(ws, event):"
next_func = content.find("async def main():")

new_func = """async def handle_message(ws, event):
    msg_type = event.get("message_type", "")
    if msg_type != "group":
        return
    group_id = event.get("group_id", 0)
    user_id = event.get("user_id", 0)
    raw_msg = event.get("raw_message", "").strip()
    print("[MSG] Group:" + str(group_id) + " User:" + str(user_id) + " -> " + raw_msg[:80])
    if not raw_msg.startswith("/"):
        return
    parts = raw_msg[1:].split(maxsplit=1)
    cmd = parts[0].lower() if parts else ""
    arg = parts[1] if len(parts) > 1 else ""
    at_user = "[CQ:at,qq=" + str(user_id) + "] "

    if cmd == "bind":
        if not arg or not arg.isdigit():
            await send_group_msg(ws, group_id, at_user + "请输入有效的玩家ID（纯数字），如 /bind 4222666364")
            return
        existing = await get_binding(str(user_id))
        if arg == existing:
            await send_group_msg(ws, group_id, at_user + "你已经绑定过该ID了")
            return
        await bind_qq_to_sf6(str(user_id), arg)
        await send_group_msg(ws, group_id, at_user + "绑定成功！你的SF6玩家ID：" + arg)

    elif cmd == "unbind":
        sid = await get_binding(str(user_id))
        if not sid:
            await send_group_msg(ws, group_id, at_user + "你没有绑定任何ID")
            return
        await bind_qq_to_sf6(str(user_id), "")
        await send_group_msg(ws, group_id, at_user + "已解除绑定")

    elif cmd == "myid":
        sid = await get_binding(str(user_id))
        if sid:
            await send_group_msg(ws, group_id, at_user + "你的SF6玩家ID：" + sid)
        else:
            await send_group_msg(ws, group_id, at_user + "你还未绑定，请使用 /bind <玩家ID>")

    elif cmd == "dashboard":
        if arg:
            if not arg.isdigit():
                await send_group_msg(ws, group_id, at_user + "玩家ID需为纯数字")
                return
            sid = arg
        else:
            sid = await get_binding(str(user_id))
            if not sid:
                await send_group_msg(ws, group_id, at_user + "请先绑定ID：/bind <玩家ID>\\n或直接查询：/dashboard <玩家ID>")
                return

        await send_group_msg(ws, group_id, at_user + "正在抓取数据并生成图表，请稍候...")
        try:
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
            img_path = await generate_charts(data)
        except Exception as e:
            await send_group_msg(ws, group_id, at_user + "图表生成失败：" + str(e))
            return

        await send_group_image(ws, group_id, at_user, img_path)
"""

if next_func > 0:
    idx_start = content.find(old_func_start)
    content = content[:idx_start] + new_func + "\n" + content[next_func:]
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("handle_message rewritten with all requested changes!")
else:
    print("ERROR: Could not find main() function")
