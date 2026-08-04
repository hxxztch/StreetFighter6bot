import os
BASE = r"E:\Study\sf6-qq-bot"

# Fix database threading
with open(os.path.join(BASE, r"src\database.py"), "r", encoding="utf-8") as f:
    dcontent = f.read()
old_conn = 'sqlite3.connect(DATABASE_PATH)'
new_conn = 'sqlite3.connect(DATABASE_PATH, check_same_thread=False)'
dcontent = dcontent.replace(old_conn, new_conn)
with open(os.path.join(BASE, r"src\database.py"), "w", encoding="utf-8") as f:
    f.write(dcontent)
print("SQLite: check_same_thread=False added")

# Fix bind conflict in bot2.py
with open(os.path.join(BASE, "bot2.py"), "r", encoding="utf-8") as f:
    bcontent = f.read()

old_bind = """        existing = await get_binding(str(user_id))
        if arg == existing:
            await send_group_msg(ws, group_id, at_user + "你已经绑定过该ID了")
            return
        await bind_qq_to_sf6(str(user_id), arg)
        await send_group_msg(ws, group_id, at_user + "绑定成功！你的SF6玩家ID：" + arg)"""

new_bind = """        existing = await get_binding(str(user_id))
        if existing:
            if arg == existing:
                await send_group_msg(ws, group_id, at_user + "你已经绑定过该ID了")
            else:
                await send_group_msg(ws, group_id, at_user + "你已绑定ID " + existing + "，如需更改请先 /unbind")
            return
        await bind_qq_to_sf6(str(user_id), arg)
        await send_group_msg(ws, group_id, at_user + "绑定成功！你的SF6玩家ID：" + arg)"""

bcontent = bcontent.replace(old_bind, new_bind)
with open(os.path.join(BASE, "bot2.py"), "w", encoding="utf-8") as f:
    f.write(bcontent)
print("Bind conflict: requires /unbind before changing ID")

print("Done! Restart bot2.py")
