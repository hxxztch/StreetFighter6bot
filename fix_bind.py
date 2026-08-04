import os
BASE = r"E:\Study\sf6-qq-bot"
def w(path, content):
    fpath = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(fpath), exist_ok=True)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK: {path}")

w(r"src\plugins\bind.py", r'''"""Bind QQ to SF6 player ID"""
import traceback
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import MessageEvent
from src.database import bind_qq_to_sf6, get_binding

bind_cmd = on_command("bind", aliases={"绑定"}, priority=5, block=True)
unbind_cmd = on_command("unbind", aliases={"解绑"}, priority=5, block=True)
myid_cmd = on_command("myid", aliases={"我的ID"}, priority=5, block=True)

@bind_cmd.handle()
async def hbind(event: MessageEvent, args: Message = CommandArg()):
    try:
        sid = args.extract_plain_text().strip()
        if not sid:
            await bind_cmd.finish("Usage: !bind <SF6 Player ID>")
        qq_id = str(event.user_id)
        await bind_qq_to_sf6(qq_id, sid)
        await bind_cmd.finish(f"Bind OK! QQ {qq_id} -> SF6 ID: {sid}")
    except Exception as e:
        await bind_cmd.finish(f"Bind failed: {e}")
        traceback.print_exc()

@unbind_cmd.handle()
async def hunbind(event: MessageEvent):
    try:
        await bind_qq_to_sf6(str(event.user_id), "")
        await unbind_cmd.finish("Unbind OK")
    except Exception as e:
        await unbind_cmd.finish(f"Unbind failed: {e}")

@myid_cmd.handle()
async def hmyid(event: MessageEvent):
    try:
        sid = await get_binding(str(event.user_id))
        if sid:
            await myid_cmd.finish(f"Your SF6 ID: {sid}")
        else:
            await myid_cmd.finish("Not bound, use !bind <SF6 ID>")
    except Exception as e:
        await myid_cmd.finish(f"Error: {e}")
''')

print("Bind plugin fixed!")
