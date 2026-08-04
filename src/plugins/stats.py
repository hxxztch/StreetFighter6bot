"""SF6 stats command"""
import asyncio, dataclasses, traceback
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment
from src.database import get_binding, get_cached_stats, set_cached_stats
from src.buckler.client import fetch_player_data
from src.buckler.models import PlayerData
from src.analyzer.stats import analyze
from src.charts.renderer import generate_charts
from src.config import CHART_OUTPUT_DIR

sf6_cmd = on_command("sf6", aliases={"街霸6","SF6"}, priority=5, block=True)

@sf6_cmd.handle()
async def hsf6(event: MessageEvent, args: Message = CommandArg()):
    try:
        arg = args.extract_plain_text().strip()
        qq = str(event.user_id)
        if arg:
            sid = arg
        else:
            sid = await get_binding(qq)
            if not sid:
                await sf6_cmd.finish("Please bind first: !bind <SF6 ID>\nOr query directly: !sf6 <Player ID>")
        await sf6_cmd.send("Fetching SF6 data and generating charts, please wait...")
        try:
            cached = await get_cached_stats(sid)
            if cached:
                data = PlayerData(**cached)
                await sf6_cmd.send("(From cache)")
            else:
                data = await fetch_player_data(sid)
                await set_cached_stats(sid, dataclasses.asdict(data))
        except Exception as fe:
            await sf6_cmd.send(f"Data fetch failed: {fe}")
            return
        loop = asyncio.get_running_loop()
        img_path = await loop.run_in_executor(None, generate_charts, data)
        a = analyze(data)
        summary = f"=== {a['username']} SF6 Report ===\nPlatform: {a['platform']} | Games: {a['total_games']} | WR: {a['overall_wr']}\nTime: {a['total_time']}\n"
        rw = a.get("recent_wr","")
        if rw: summary += f"Recent WR: {rw}\n"
        summary += "\n--- Characters ---\n"
        for c in a["characters"][:5]:
            summary += f"  {c['name']}: {c['rank']} | {c['record']} ({c['win_rate']})\n"
        msg = summary + MessageSegment.image(f"file:///{img_path.as_posix()}")
        await sf6_cmd.finish(msg)
    except Exception as e:
        await sf6_cmd.send(f"Error: {e}")
        traceback.print_exc()
