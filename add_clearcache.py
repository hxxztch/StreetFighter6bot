path = r"bot2.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = """    elif cmd == "help":"""

new = """    elif cmd == "clearcache":
        import sqlite3
        from src.config import DATABASE_PATH
        db = sqlite3.connect(DATABASE_PATH)
        db.execute("DELETE FROM stats_cache")
        db.commit()
        db.close()
        await send_group_msg(ws, group_id, at_user + "缓存已清理，绑定记录保留")

    elif cmd == "help":"""

content = content.replace(old, new)
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("clearcache command added")
