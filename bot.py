"""SF6 QQ Bot - Direct WebSocket (no NoneBot2 for message handling)"""
import asyncio, json, sys, traceback
sys.dont_write_bytecode = True
import websockets
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from src.database import get_binding, bind_qq_to_sf6, get_cached_stats, set_cached_stats
from src.database import all_bindings, save_weekly, get_weekly, get_prev_weekly
from src.leaderboard import current_week_id, top_character, build_leaderboard
from src.charts.weekly_renderer import render_weekly
from src.buckler.client import fetch_player_data
from src.buckler.models import PlayerData, GameModeTime, CharacterStat, TechStats, DriveUsage, MatchupStat, RecentMatch
from src.analyzer.stats import analyze
from src.charts.dashboard_renderer import render as generate_charts
from src.charts.card_renderer import render_card
from src.ai.sf6_ai import ask_sf6, ask_chat, build_player_context
import dataclasses

WS_URL = "ws://127.0.0.1:3001"
TOKEN = "K9koSYAg1B9aOY-3m_axCfrCDdLkP7B7XdnRawxS7ZA"

PENDING = {}

async def api_call(ws, action, params, timeout=15):
    import uuid
    echo = str(uuid.uuid4())
    fut = asyncio.get_running_loop().create_future()
    PENDING[echo] = fut
    await ws.send(json.dumps({"action": action, "params": params, "echo": echo}))
    try:
        return await asyncio.wait_for(fut, timeout=timeout)
    finally:
        PENDING.pop(echo, None)

def _fetch_sync(sf6_id):
    """Run async fetch_player_data in a fresh event loop (thread-safe)"""
    return asyncio.run(fetch_player_data(sf6_id))

async def _fetch_and_save_weekly(ws, group_id):
    week_id = current_week_id()
    members = await api_call(ws, "get_group_member_list", {"group_id": int(group_id)})
    member_map = {}
    for m in members.get("data", []):
        qq = str(m.get("user_id"))
        nickname = m.get("card") or m.get("nickname") or qq
        member_map[qq] = nickname
    bindings = await all_bindings()
    target = [(qq, sf6_id) for qq, sf6_id in bindings if qq in member_map]
    loop = asyncio.get_running_loop()
    sem = asyncio.Semaphore(3)

    async def fetch_one(qq, sf6_id):
        async with sem:
            try:
                data = await loop.run_in_executor(None, _fetch_sync, sf6_id)
                return qq, sf6_id, data
            except Exception as e:
                print("[Weekly] skip " + qq + ": " + str(e))
                return qq, sf6_id, None

    results = await asyncio.gather(*[fetch_one(qq, sf6_id) for qq, sf6_id in target])
    snapshot = []
    for qq, sf6_id, data in results:
        if data is None:
            continue
        tc = top_character(data)
        if tc is None:
            continue
        snapshot.append({
            "qq_id": qq, "sf6_id": sf6_id,
            "nickname": member_map.get(qq, qq),
            "character": tc["name"],
            "rank_label": tc["label"],
            "score": tc["score"],
        })
    snapshot.sort(key=lambda x: -x["score"])
    for i, e in enumerate(snapshot):
        e["rank"] = i + 1
    await save_weekly(week_id, str(group_id), snapshot)
    return snapshot

async def _render_and_send_weekly(ws, group_id, at_user, current):
    week_id = current_week_id()
    prev = await get_prev_weekly(week_id, str(group_id))
    entries = build_leaderboard(current, prev)
    img_path = await render_weekly(week_id, group_id, entries)
    await send_group_image(ws, group_id, at_user, img_path)


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
    at_user = "[CQ:at,qq=" + str(user_id) + "] "
    print("[MSG] Group:" + str(group_id) + " User:" + str(user_id) + " -> " + raw_msg[:80])

    # 直接 @bot 即可对话（无需 /ai 指令）
    self_id = str(event.get("self_id", ""))
    at_bot = "[CQ:at,qq=" + self_id + "]"
    if not raw_msg.startswith("/") and at_bot in raw_msg:
        import re as _re
        question = _re.sub(r"\[CQ:at,qq=\d+\]", "", raw_msg).strip()
        if not question:
            await send_group_msg(ws, group_id, at_user + "请问你想问什么？")
            return
        try:
            answer = await ask_chat(question)
            await send_group_msg(ws, group_id, at_user + answer)
        except Exception as e:
            await send_group_msg(ws, group_id, at_user + "AI 调用失败：" + str(e))
        return

    if not raw_msg.startswith("/"):
        return
    parts = raw_msg[1:].split(maxsplit=1)
    cmd = parts[0].lower() if parts else ""
    arg = parts[1] if len(parts) > 1 else ""

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

    elif cmd == "weekly":
        await send_group_msg(ws, group_id, at_user + "正在获取周榜...")
        try:
            week_id = current_week_id()
            current = await get_weekly(week_id, str(group_id))
            if not current:
                current = await _fetch_and_save_weekly(ws, group_id)
            await _render_and_send_weekly(ws, group_id, at_user, current)
        except Exception as e:
            await send_group_msg(ws, group_id, at_user + "周榜获取失败：" + str(e))

    elif cmd == "weekrefresh":
        await send_group_msg(ws, group_id, at_user + "正在刷新周榜数据，请稍候...")
        try:
            current = await _fetch_and_save_weekly(ws, group_id)
            await _render_and_send_weekly(ws, group_id, at_user, current)
        except Exception as e:
            await send_group_msg(ws, group_id, at_user + "周榜刷新失败：" + str(e))

    elif cmd == "ai":
        if not arg:
            await send_group_msg(ws, group_id, at_user + "请输入问题：/ai <你的问题>")
            return
        context = ""
        sid = await get_binding(str(user_id))
        if sid:
            try:
                data = await fetch_player_data(sid)
                context = build_player_context(data)
            except Exception:
                pass
        try:
            answer = await ask_sf6(arg, context)
            await send_group_msg(ws, group_id, at_user + answer)
        except Exception as e:
            await send_group_msg(ws, group_id, at_user + "AI 调用失败：" + str(e))

    elif cmd == "help":
        msg = at_user + "指令列表：\n/bind <玩家ID> — 绑定SF6玩家ID（10位纯数字）\n/unbind — 解除绑定\n/myid — 查看已绑定的ID\n/dashboard [ID|@QQ] — 生成数据面板\n/card [ID|@QQ] — 生成攻防深度分析卡片\n/weekly — 查看当前周榜\n/ai <问题> — 向SF6教练提问\n/help — 显示本帮助"
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
                        elif data.get("echo") in PENDING:
                            fut = PENDING[data["echo"]]
                            if not fut.done():
                                fut.set_result(data)
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

