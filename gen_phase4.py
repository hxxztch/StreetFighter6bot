import os
BASE = r"E:\Study\sf6-qq-bot"

def w(path, content):
    fpath = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(fpath), exist_ok=True)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK: {path}")

w(r"src\analyzer\stats.py", r'''def _fmt(sec): h=sec//3600; m=(sec%3600)//60; return f"{h}h{m}m" if h else f"{m}m"
def _pct(v): return f"{v*100:.1f}%"

def analyze(data):
    r = {}
    r["username"] = data.username
    r["player_id"] = data.player_id
    r["platform"] = data.platform
    gt = data.game_time
    r["total_time"] = _fmt(gt.total_play_time)
    r["mode_times"] = {"排位赛":_fmt(gt.ranked_time),"休闲赛":_fmt(gt.casual_time),"比赛间":_fmt(gt.battle_hub_time),"训练场":_fmt(gt.training_time),"街机模式":_fmt(gt.arcade_time),"自定义房间":_fmt(gt.custom_room_time),"环球游历":_fmt(gt.world_tour_time),"极限战斗":_fmt(gt.extreme_battle_time)}
    r["characters"] = [{"name":c.name,"usage_count":c.usage_count,"rank":c.rank,"win_rate":_pct(c.win_rate),"record":f"{c.wins}/{c.total}","win_rate_raw":c.win_rate,"wins":c.wins,"total":c.total} for c in data.characters]
    ts = data.tech_stats
    r["tech_stats"] = {"场均角落压制时间":f"{ts.corner_pressure_time:.1f}秒","场均被压制角落时间":f"{ts.corner_pressured_time:.1f}秒","场均投技成功":f"{ts.throws_landed:.1f}次","场均拆投成功":f"{ts.throw_escapes:.1f}次","场均精准招架":f"{ts.perfect_parries:.2f}次","场均斗气迸发":f"{ts.drive_impacts:.1f}次","场均反迸":f"{ts.drive_impact_counters:.1f}次","场均被迸发":f"{ts.drive_impacts_received:.1f}次","场均确反":f"{ts.punish_counters:.1f}次","场均被确反":f"{ts.punished_received:.1f}次","场均SA使用":f"{ts.super_arts:.1f}次","最大连段伤害":f"{ts.combos_max_damage:,}","平均连段伤害":f"{ts.combos_avg_damage:,.0f}"}
    r["tech_stats_raw"] = {"corner_pressure_time":ts.corner_pressure_time,"corner_pressured_time":ts.corner_pressured_time,"throws_landed":ts.throws_landed,"throw_escapes":ts.throw_escapes,"perfect_parries":ts.perfect_parries,"drive_impacts":ts.drive_impacts,"drive_impact_counters":ts.drive_impact_counters,"drive_impacts_received":ts.drive_impacts_received,"punish_counters":ts.punish_counters,"punished_received":ts.punished_received,"super_arts":ts.super_arts}
    du = data.drive_usage
    pcts = du.percentages()
    _dk = {"取消绿冲":"drive_rush_cancel","斗爆技(OD)":"overdrive","斗气反击":"drive_reversal","裸绿冲":"raw_drive_rush","蓝防":"drive_parry","被磨掉":"burnout_drain"}
    r["drive_usage"] = [{"label":k,"pct":round(v,1),"raw":getattr(du,_dk.get(k,"other"),0)} for k,v in sorted(pcts.items(),key=lambda x:x[1],reverse=True)]
    def _tmu(matchups):
        return [{"opponent":m.opponent_char,"win_rate":_pct(m.win_rate),"record":f"{m.wins}/{m.total}","total":m.total} for m in matchups[:10]]
    r["ranked_matchups"] = _tmu(data.ranked_matchups)
    r["casual_matchups"] = _tmu(data.casual_matchups)
    r["battle_hub_matchups"] = _tmu(data.battle_hub_matchups)
    mm = {"ranked":"排位","casual":"休闲","battle_hub":"比赛间"}
    r["recent_matches"] = [{"date":m.date,"result_icon":"O" if m.result=="win" else "X","opponent":m.opponent_char,"player_char":m.player_char,"mode":mm.get(m.mode,m.mode),"score":f"{m.rounds_won}-{m.rounds_lost} ({m.lp_change:+d})" if m.lp_change!=0 else f"{m.rounds_won}-{m.rounds_lost}"} for m in data.recent_matches[:15]]
    tw = sum(c.wins for c in data.characters)
    tg = sum(c.total for c in data.characters)
    r["overall_wr"] = _pct(tw/max(tg,1))
    r["total_games"] = tg
    r["total_wins"] = tw
    if data.recent_matches:
        rw = sum(1 for m in data.recent_matches if m.result=="win")
        r["recent_wr"] = _pct(rw/len(data.recent_matches))
        r["recent_record"] = f"{rw}W {len(data.recent_matches)-rw}L"
    return r
''')

w(r"src\plugins\bind.py", r'''from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import MessageEvent
from src.database import bind_qq_to_sf6, get_binding

bind_cmd = on_command("bind", aliases={"绑定"}, priority=5, block=True)
unbind_cmd = on_command("unbind", aliases={"解绑"}, priority=5, block=True)
myid_cmd = on_command("myid", aliases={"我的ID"}, priority=5, block=True)

@bind_cmd.handle()
async def hbind(event: MessageEvent, args: Message = CommandArg()):
    sid = args.extract_plain_text().strip()
    if not sid:
        await bind_cmd.finish("用法: !bind <你的SF6玩家ID>")
    await bind_qq_to_sf6(str(event.user_id), sid)
    await bind_cmd.finish(f"绑定成功! QQ {event.user_id} -> SF6 ID: {sid}")

@unbind_cmd.handle()
async def hunbind(event: MessageEvent):
    await bind_qq_to_sf6(str(event.user_id), "")
    await unbind_cmd.finish("已解绑")

@myid_cmd.handle()
async def hmyid(event: MessageEvent):
    sid = await get_binding(str(event.user_id))
    if sid:
        await myid_cmd.finish(f"你的 SF6 ID: {sid}")
    else:
        await myid_cmd.finish("未绑定, 请先用 !bind <SF6 ID>")
''')

print("Phase 4: analyzer + bind plugin done!")
