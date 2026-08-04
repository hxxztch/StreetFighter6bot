path = r"bot2.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Find the broken help section by looking for the first line
idx = content.find("msg += \"指令列表")
if idx < 0:
    print("Not found")
else:
    # Find the line before (elif cmd == "help":)
    prev_line = content.rfind("\n", 0, idx)
    prev2 = content.rfind("\n", 0, prev_line) + 1
    # Find the end (next elif or after send_group_msg)
    end_idx = content.find("\n    elif", idx)
    if end_idx < 0:
        end_idx = content.find("\n    #", idx)
    if end_idx < 0:
        end_idx = content.find("\n    return", idx)
    broken = content[prev2:end_idx]
    print("Broken section:", repr(broken)[:200])
    
    new_help = """    elif cmd == "help":
        msg = at_user + "指令列表：\\n/bind <玩家ID> — 绑定SF6玩家ID（10位纯数字）\\n/unbind — 解除绑定\\n/myid — 查看已绑定的ID\\n/dashboard — 生成数据面板\\n/dashboard <ID> — 查他人面板\\n/help — 显示本帮助"
        await send_group_msg(ws, group_id, msg)"""
    
    content = content[:prev2] + new_help + content[end_idx:]
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Help fixed!")
