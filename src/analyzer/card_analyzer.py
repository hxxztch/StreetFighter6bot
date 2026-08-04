"""Card analyzer for offense/defense deep dive"""
from src.buckler.models import PlayerData

def _judge(val, mn, mx, is_pct=False):
    current = val * 100 if is_pct and val <= 1.0 else val
    if current < mn: return "偏低", "#3b82f6"
    elif current > mx: return "偏高", "#f39c12"
    return "正常", "#2ecc71"

def _calc_streaks(results):
    if not results: return 0, 0, 0, ""
    max_w = max_l = 0; cnt = 1
    for i in range(1, len(results)):
        if results[i] == results[i-1]: cnt += 1
        else:
            if results[i-1] == "win" and cnt > max_w: max_w = cnt
            if results[i-1] == "lose" and cnt > max_l: max_l = cnt
            cnt = 1
    if results[-1] == "win" and cnt > max_w: max_w = cnt
    if results[-1] == "lose" and cnt > max_l: max_l = cnt
    cur = 1
    for i in range(1, len(results)):
        if results[i] == results[0]: cur += 1
        else: break
    return max_w, max_l, cur, results[0]

def analyze_card(data: "PlayerData", chars_list: list):
    ts = data.tech_stats; du = data.drive_usage
    # Buckler battle_stats are already per-game averages
    s = {
        "di": round(ts.drive_impacts, 1),
        "throw": round(ts.throws_landed, 1),
        "punish": round(ts.punish_counters, 1),
        "drive_throw": round(ts.throw_drive_parry, 1),
        "stun": round(ts.stuns, 2),
        "corner_time": round(ts.corner_pressure_time, 1),
        "pressed_time": round(ts.corner_pressured_time, 1),
        "corner_ratio": round(ts.corner_pressure_time / max(ts.corner_pressured_time, 0.1), 1),
        "parry": round(ts.drive_parry, 1),
        "perfect_parry": round(ts.perfect_parries, 1),
        "tech": round(ts.throw_escapes, 1),
        "drive_reversal": round(ts.drive_reversal, 2),
        "di_received": round(ts.drive_impacts_received, 1),
        "punish_received": round(ts.punished_received, 1),
        "thrown": round(ts.throws_landed + ts.throw_escapes, 1),
        "drive_thrown": round(ts.received_throw_drive_parry, 1),
        "stun_received": round(ts.stuns_received, 2),
        "parry_rate": round(ts.perfect_parries / max(ts.drive_parry, 1), 2),
    }

    OFF = {
        "di": {"min": 0.2, "max": 0.4, "label": "迸发(DI)"},
        "throw": {"min": 2.0, "max": 3.0, "label": "投"},
        "punish": {"min": 0.1, "max": 0.2, "label": "确反"},
        "drive_throw": {"min": 0.1, "max": 0.3, "label": "蓝防投"},
        "stun": {"min": 0.0, "max": 0.1, "label": "打晕"},
        "corner_time": {"min": 7.4, "max": 10.9, "unit": "s", "label": "压角落"},
        "pressed_time": {"min": 7.2, "max": 9.8, "unit": "s", "label": "被压"},
        "corner_ratio": {"min": 0.8, "max": 1.4, "unit": "x", "label": "角落压制比"},
    }
    DEF = {
        "parry": {"min": 0.8, "max": 1.5, "label": "蓝防"},
        "perfect_parry": {"min": 0.1, "max": 0.4, "label": "精准招架"},
        "tech": {"min": 0.2, "max": 0.5, "label": "拆投"},
        "drive_reversal": {"min": 0.0, "max": 0.1, "label": "斗反"},
        "di_received": {"min": 0.2, "max": 0.4, "label": "被迸发"},
        "punish_received": {"min": 0.1, "max": 0.3, "label": "被确反"},
        "thrown": {"min": 1.9, "max": 2.5, "label": "被投"},
        "drive_thrown": {"min": 0.1, "max": 0.3, "label": "被蓝防投"},
        "stun_received": {"min": 0.0, "max": 0.1, "label": "被晕"},
        "parry_rate": {"min": 0.11, "max": 0.20, "unit": "%", "label": "精准招架率"},
    }

    def _build(cfg):
        items = []
        for key, c in cfg.items():
            val = s.get(key, 0); unit = c.get("unit", ""); mn, mx = c["min"], c["max"]
            status, color = _judge(val, mn, mx, is_pct=(unit == "%"))
            ref = "MR15 " + str(mn) + "-" + str(mx) + unit
            items.append({"label": c["label"], "value": val, "unit": unit, "ref": ref, "status": status, "color": color})
        return items
    off_items = _build(OFF)
    def_items = _build(DEF)

    drive_items = []
    if du:
        pcts = du.percentages()
        drive_items = [{"label": k, "pct": round(v, 1)} for k, v in sorted(pcts.items(), key=lambda x: x[1], reverse=True)]

    sa_items = []
    total_sa = max(ts.sa_lv1_rate + ts.sa_lv2_rate + ts.sa_lv3_rate + (ts.ca_rate or 0), 0.01)
    for label, rate, color in [("SA1", ts.sa_lv1_rate, "#E8B923"), ("SA2", ts.sa_lv2_rate, "#F09C2A"), ("SA3", ts.sa_lv3_rate, "#E64E38")]:
        sa_items.append({"label": label, "pct": round(rate / total_sa * 100, 1), "color": color})
    if ts.ca_rate and ts.ca_rate > 0:
        sa_items.append({"label": "CA", "pct": round(ts.ca_rate / total_sa * 100, 1), "color": "#D42020"})

    tags = []
    for item in off_items + def_items:
        if item["status"] != "正常":
            clean = item["label"].replace("(DI)", "").replace("(OD)", "")
            tags.append(clean + ("高" if item["status"] == "偏高" else "低"))

    ranked_res = [m.result for m in data.recent_matches if "rank" in m.mode.lower() and m.result in ("win", "lose")]
    all_res = [m.result for m in data.recent_matches if m.result in ("win", "lose")][:25]
    rmax_w, rmax_l, rcur, rcur_t = _calc_streaks(ranked_res)
    amax_w, amax_l, acur, acur_t = _calc_streaks(all_res)
    streaks = {"ranked_max_win": rmax_w, "ranked_max_lose": rmax_l, "ranked_cur": rcur, "ranked_cur_type": rcur_t,
               "all_max_win": amax_w, "all_max_lose": amax_l, "all_cur": acur, "all_cur_type": acur_t}

    vs_list = []; low_sample = []
    for mu in data.ranked_matchups[:10]:
        if mu.total < 2: low_sample.append(mu.opponent_char)
        elif mu.total > 0: vs_list.append({"name": mu.opponent_char, "rate": round(mu.win_rate * 100, 1), "detail": str(mu.wins) + "/" + str(mu.total), "pct": round(mu.win_rate * 100, 1)})

    mc = chars_list[0] if chars_list else {}
    main_rank = mc.get("rank", "?") if isinstance(mc, dict) else "?"
    return {"username": data.username, "player_id": data.player_id, "platform": data.platform,
        "main_char": mc.get("name", "?") if isinstance(mc, dict) else "?", "main_rank": main_rank,
        "offense_items": off_items, "defense_items": def_items, "drive_items": drive_items,
        "sa_items": sa_items, "tags": tags[:5], "vs_list": vs_list[:6], "low_sample": low_sample,
        "streaks": streaks, "games": ts.games_played}
