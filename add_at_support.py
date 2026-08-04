path = r"bot2.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Add _parse_at helper function before handle_message
old = "async def handle_message(ws, event):"
new_at = "def _parse_at(text):\n    import re\n    m = re.search(r'\[CQ:at,qq=(\d+)\]', text)\n    return m.group(1) if m else None\n\nasync def handle_message(ws, event):"
content = content.replace(old, new_at)

# Update /dashboard command to handle @mentions
old_dash = """if arg:
            if not arg.isdigit() or len(arg) != 10:"""

new_dash = """if arg:
            at_qq = _parse_at(arg)
            if at_qq:
                sid = await get_binding(at_qq)
                if not sid:
                    await send_group_msg(ws, group_id, at_user + "该成员尚未绑定SF6 ID")
                    return
            elif not arg.isdigit() or len(arg) != 10:"""

content = content.replace(old_dash, new_dash)

# Update /card command to handle @mentions  
old_card = """if arg:
            if not arg.isdigit() or len(arg) != 10:"""

new_card = """if arg:
            at_qq = _parse_at(arg)
            if at_qq:
                sid = await get_binding(at_qq)
                if not sid:
                    await send_group_msg(ws, group_id, at_user + "该成员尚未绑定SF6 ID")
                    return
            elif not arg.isdigit() or len(arg) != 10:"""

content = content.replace(old_card, new_card)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("@mention support added to /dashboard and /card")
