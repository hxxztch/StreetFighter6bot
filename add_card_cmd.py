path = r"bot2.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Add card import
old_imp = "from src.charts.dashboard_renderer import render as generate_charts"
new_imp = "from src.charts.dashboard_renderer import render as generate_charts\nfrom src.charts.card_renderer import render_card"
content = content.replace(old_imp, new_imp)

# Add /card command before help
old_help = "    elif cmd == \"help\":"
new_card = """    elif cmd == "card":
        if arg:
            if not arg.isdigit() or len(arg) != 10:
                await send_group_msg(ws, group_id, at_user + "请输入有效的玩家ID（10位纯数字）")
                return
            sid = arg
        else:
            sid = await get_binding(str(user_id))
            if not sid:
                await send_group_msg(ws, group_id, at_user + "请先绑定ID：/bind <玩家ID>\\n或直接查询：/card <玩家ID>")
                return

        await send_group_msg(ws, group_id, at_user + "正在生成深度分析卡片，请稍候...")
        try:
            data = await fetch_player_data(sid)
            from src.analyzer.stats import analyze
            a = analyze(data)
            card_data = render_card(data, a.get("characters", []))
            await send_group_image(ws, group_id, at_user, card_data)
        except Exception as e:
            await send_group_msg(ws, group_id, at_user + "卡片生成失败：" + str(e))
            return

    elif cmd == "help":"""

content = content.replace(old_help, new_card)
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("/card command added to bot2.py")
