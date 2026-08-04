"""SF6 QQ Bot - Direct WebSocket (no NoneBot2 for message handling)"""
import asyncio, json, sys, traceback
sys.dont_write_bytecode = True
import websockets
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from src.database import get_binding, bind_qq_to_sf6, get_cached_stats, set_cached_stats
from src.buckler.client import fetch_player_data
from src.buckler.models import PlayerData, GameModeTime, CharacterStat, TechStats, DriveUsage, MatchupStat, RecentMatch
from src.analyzer.stats import analyze
from src.charts.dashboard_renderer import render as generate_charts
from src.charts.card_renderer import render_card
import dataclasses

WS_URL = "ws://127.0.0.1:3001"
TOKEN = "K9koSYAg1B9aOY-3m_axCfrCDdLkP7B7XdnRawxS7ZA"

async def send_group_msg(ws, group_id, text):
    """Send a text message to a QQ group"""
    msg = {
        "action": "send_group_msg",
        "params": {
            "group_id": int(group_id),
            "message": text
        },
        "echo": str(asyncio.get_running_loop().time())
    }
    await ws.send(json.dumps(msg))

async def send_group_image(ws, group_id, text, image_path):
    """Send text + image to a QQ group"""
    path = image_path.as_posix() if hasattr(image_path, 'as_posix') else image_path
    msg_text = f"{text}\n[CQ:image,file=file:///{path}]"
    await send_group_msg(ws, group_id, msg_text)

def _reconstruct(d):
    """Reconstruct PlayerData from cached dict"""
    from src.buckler.models import GameModeTime, CharacterStat, TechStats, DriveUsage, MatchupStat, RecentMatch
    gt = GameModeTime(**d.get("game_time", {}))
    chars = [CharacterStat(**c) for c in d.get("characters", [])]
    ts = TechStats(**d.get("tech_stats", {}))
    du = DriveUsage(**d.get("drive_usage", {}))
    ranked_mu = [MatchupStat(**m) for m in d.get("ranked_matchups", [])]
    casual_mu = [MatchupStat(**m) for m in d.get("casual_matchups", [])]
    bh_mu = [MatchupStat(**m) for m in d.get("battle_hub_matchups", [])]
    recent = [RecentMatch(**m) for m in d.get("recent_matches", [])]
    return PlayerData(username=d.get("username",""), player_id=d.get("player_id",""),
        platform=d.get("platform",""), game_time=gt, characters=chars,
        tech_stats=ts, drive_usage=du, ranked_matchups=ranked_mu,
        casual_matchups=casual_mu, battle_hub_matchups=bh_mu, recent_matches=recent)


def _parse_at(text):
    import re
    m = re.search(r'\[CQ:at,qq=(\d+)', text)
    return m.group(1) if m else None

async def handle_message(ws, event):
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
            await send_group_msg(ws, group_id, at_user + "请输入有效的玩家ID（10位纯数字）")
            return
        existing = await get_binding(str(user_id))
        if existing:
            if arg == existing:
                await send_group_msg(ws, group_id, at_user + "你已经绑定过该ID了")
            else:
                await send_group_msg(ws, group_id, at_user + "你已绑定ID " + existing + "，如需更改请先 /unbind")
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

    elif cmd == "card":
        if arg:
            at_qq = _parse_at(arg)
            if at_qq:
                print("[AT] Parsed QQ: " + str(at_qq))
                sid = await get_binding(at_qq)
                print("[AT] Bound SF6 ID: " + str(sid))
                if not sid:
                    await send_group_msg(ws, group_id, at_user + "该成员尚未绑定SF6 ID")
                    return
            elif not arg.isdigit() or len(arg) != 10:
                await send_group_msg(ws, group_id, at_user + "请输入有效的玩家ID（10位纯数字）")
                return
            else:
                sid = arg
        else:
            sid = await get_binding(str(user_id))
            if not sid:
                await send_group_msg(ws, group_id, at_user + "请先绑定ID：/bind <玩家ID>\n或直接查询：/card <玩家ID>")
                return

        await send_group_msg(ws, group_id, at_user + "正在生成深度分析卡片，请稍候...")
        try:
            data = await fetch_player_data(sid)
            from src.analyzer.stats import analyze
            a = analyze(data)
            card_data = await render_card(data, a.get("characters", []))
            await send_group_image(ws, group_id, at_user, card_data)
        except Exception as e:
            await send_group_msg(ws, group_id, at_user + "卡片生成失败：" + str(e))
            return

    elif cmd == "help":
        msg = at_user + "指令列表：\n/bind <玩家ID> — 绑定SF6玩家ID（10位纯数字）\n/unbind — 解除绑定\n/myid — 查看已绑定的ID\n/dashboard — 生成数据面板\n/dashboard <ID> — 查他人面板\n/help — 显示本帮助"
        await send_group_msg(ws, group_id, msg)
    elif cmd == "myid":
        sid = await get_binding(str(user_id))
        if sid:
            await send_group_msg(ws, group_id, at_user + "你的SF6玩家ID：" + sid)
        else:
            await send_group_msg(ws, group_id, at_user + "你还未绑定，请使用 /bind <玩家ID>")

    elif cmd == "dashboard":
        if arg:
            at_qq = _parse_at(arg)
            if at_qq:
                print("[AT] Parsed QQ: " + str(at_qq))
                sid = await get_binding(at_qq)
                print("[AT] Bound SF6 ID: " + str(sid))
                if not sid:
                    await send_group_msg(ws, group_id, at_user + "该成员尚未绑定SF6 ID")
                    return
            elif not arg.isdigit() or len(arg) != 10:
                await send_group_msg(ws, group_id, at_user + "请输入有效的玩家ID（10位纯数字）")
                return
            else:
                sid = arg
        else:
            sid = await get_binding(str(user_id))
            if not sid:
                await send_group_msg(ws, group_id, at_user + "请先绑定ID：/bind <玩家ID>\n或直接查询：/dashboard <玩家ID>")
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

async def main():
    headers = {"Authorization": "Bearer " + TOKEN}
    while True:
        try:
            async with websockets.connect(WS_URL, extra_headers=headers, ping_interval=30) as ws:
                print("[BOT] Connected to NapCatQQ at " + WS_URL)
                while True:
                    try:
                        raw = await ws.recv()
                        data = json.loads(raw)
                        if data.get("post_type") == "message":
                            asyncio.create_task(handle_message(ws, data))
                        elif data.get("post_type") == "meta_event":
                            mt = data.get("meta_event_type", "")
                            if mt not in ("lifecycle", "heartbeat"):
                                print("[META] " + str(data))
                    except websockets.exceptions.ConnectionClosed:
                        print("[BOT] Connection lost, reconnecting in 3s...")
                        break
                    except Exception as e:
                        print("[WS] " + str(e))
                        break
        except Exception as e:
            print("[BOT] Connect failed: " + str(e) + ", retrying in 5s...")
        import asyncio as _asyncio
        await _asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())

