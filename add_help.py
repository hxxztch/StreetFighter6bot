path = r"bot2.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = """    elif cmd == "myid":"""

new = """    elif cmd == "help":
        msg = at_user
        msg += "指令列表：\n"
        msg += "/bind <玩家ID> — 绑定你的SF6玩家ID（10位纯数字）\n"
        msg += "/unbind — 解除绑定\n"
        msg += "/myid — 查看已绑定的玩家ID\n"
        msg += "/dashboard — 生成你的数据面板\n"
        msg += "/dashboard <玩家ID> — 查询其他玩家的数据面板\n"
        msg += "/help — 显示本帮助"
        await send_group_msg(ws, group_id, msg)

    elif cmd == "myid":"""

content = content.replace(old, new)
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("help command added")
