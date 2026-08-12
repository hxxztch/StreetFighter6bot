"""Card renderer - offense/defense deep analysis"""
import asyncio, time
from pathlib import Path
from src.config import CHART_OUTPUT_DIR
from src.analyzer.card_analyzer import analyze_card
from src.leaderboard import tier_color

async def render_card(data, chars_list):
    from playwright.async_api import async_playwright
    analysis = analyze_card(data, chars_list)
    html = _gen_html(analysis)
    output_path = CHART_OUTPUT_DIR / ("card_" + str(data.player_id) + ".png")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1200, "height": 1600})
        await page.set_content(html, wait_until="networkidle")
        await asyncio.sleep(1)
        await page.screenshot(path=str(output_path), full_page=True)
        await browser.close()
    return output_path

def _gen_html(a):
    s = a.get("streaks", {})
    def _streak_badge(stype, cur, cur_type, max_w, max_l):
        cls = "streak-bad" if stype == "bad" else "streak-good"
        label = "\u5168\u6a21\u5f0f" if stype == "all" else "\u7eaf\u6392\u4f4d"
        if cur_type == "win": cur_str = "\u5f53\u524d " + str(cur) + " \u8fde\u8d5c"
        elif cur_type == "lose": cur_str = "\u5f53\u524d " + str(cur) + " \u8fde\u8d25"
        else: cur_str = "\u5f53\u524d -"
        return "<div class='streak-cell'><div class='streak-label'>" + label + "</div><div class='streak-stats'><span class='s-w'>\u2714 " + str(max_w) + "</span><span class='s-l'>\u2716 " + str(max_l) + "</span><span class='" + cls + "'>" + cur_str + "</span></div></div>"
    streak_html = _streak_badge("all", s.get("all_cur", 0), s.get("all_cur_type", ""), s.get("all_max_win", 0), s.get("all_max_lose", 0)) + _streak_badge("ranked", s.get("ranked_cur", 0), s.get("ranked_cur_type", ""), s.get("ranked_max_win", 0), s.get("ranked_max_lose", 0))

    sa_items = a.get("sa_items", [])
    sa_bar = "".join("<div class='sa-seg' style='width:" + str(item["pct"]) + "%;background:" + item["color"] + "'></div>" for item in sa_items)
    sa_rows = "".join("<div class='sa-row'><span class='sa-circ' style='background:" + item["color"] + "'></span><span>" + item["label"] + "</span><span>" + str(item["pct"]) + "%</span></div>" for item in sa_items)

    dr_items = a.get("drive_items", [])
    dr_colors = ["#E74C3C", "#F39C12", "#3498DB", "#2ECC71", "#9B59B6", "#E67E22", "#95A5A6"]
    dr_bar = "".join("<div class='sa-seg' style='width:" + str(item["pct"]) + "%;background:" + dr_colors[i % 7] + "'></div>" for i, item in enumerate(dr_items))
    dr_rows = "".join("<div class='dr-row'><span class='dr-circ' style='background:" + dr_colors[i % 7] + "'></span><span>" + item["label"] + "</span><span>" + str(item["pct"]) + "%</span></div>" for i, item in enumerate(dr_items))

    def _stat_rows(items):
        rows = ""
        for item in items:
            color = item["color"]
            rows += "<div class='stat-row'><span class='stat-label'>" + item["label"] + "</span><span class='stat-val'>" + str(item["value"]) + item["unit"] + "</span><span class='stat-ref'>" + item["ref"] + "</span><span class='stat-tag' style='color:" + color + "'>\u25cf " + item["status"] + "</span></div>"
        return rows

    off_rows = _stat_rows(a.get("offense_items", []))
    def_rows = _stat_rows(a.get("defense_items", []))

    tags_html = " ".join("<span class='tag'>#" + t + "</span>" for t in a.get("tags", []))

    vs_list = a.get("vs_list", [])
    vs_rows = ""
    for v in vs_list:
        vs_rows += "<div class='vs-row'><span class='vs-name'>" + v["name"] + "</span><div class='vs-bar-track'><div class='vs-bar-fill' style='width:" + str(v["pct"]) + "%'></div></div><span class='vs-rate'>" + str(v["rate"]) + "%</span><span class='vs-detail'>" + v["detail"] + "</span></div>"

    low_sample = a.get("low_sample", [])
    low_html = ""
    if low_sample:
        low_html = "<div class='low-sample'>\u6837\u672c\u4e0d\u8db3: " + " ".join(low_sample) + "</div>"

    mr = a.get("main_rank", "?")
    color = tier_color(mr)
    title_html = ""
    if mr.startswith("Master"):
        title_html = "<div class='rank-badge master'><div class='r-tier'>Master</div><div class='r-score'>" + mr + "</div></div>"
    else:
        title_html = "<div class='rank-badge'><div class='r-tier'>" + mr[:20] + "</div></div>"

    return "<!DOCTYPE html>\n<html lang=\"zh-CN\"><head><meta charset=\"UTF-8\"><meta name=\"viewport\" content=\"width=2160\"><style>\n*{margin:0;padding:0;box-sizing:border-box}\nbody{background:#060709;color:#e8e8e8;font-family:\"Microsoft YaHei\",sans-serif;width:1200px;margin:0 auto;padding:24px}\n.card{background:#0e1018;border-radius:6px;padding:22px 22px;border:1px solid #1e2230;margin-bottom:18px}\n.card-title{font-size:18px;font-weight:700;color:#a0a5b4;letter-spacing:0.5px;margin-bottom:10px;display:flex;align-items:center;gap:6px}\n.card-title::before{content:\"\";width:3px;height:13px;background:#F15A24}\n.col2{display:grid;grid-template-columns:1fr 1fr;gap:18px}\n.header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px}\n.p-name{font-size:34px;font-weight:bold;color:#fff}\n.p-sub{font-size:18px;color:#999;margin-top:4px}\n.rank-badge{background:#10131c;border:2px solid #8a8f9d;color:#fff;padding:6px 16px;border-radius:5px;text-align:right}\n.rank-badge.master{background:#10131c;border:2px solid #ff5a3d}\n.r-tier{font-size:18px;font-weight:bold;color:#fff}\n.r-score{font-size:30px;font-weight:bold;color:#a78bfa;margin-top:2px}\n.tag{display:inline-block;background:rgba(61,26,69,0.5);color:#c084fc;padding:4px 12px;border-radius:12px;font-size:17px;margin:5px;border:1px solid rgba(155,89,182,0.3)}\n.streak-panel{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:10px}\n.streak-cell{background:#0b0d13;border:1px solid #1a1d28;border-radius:5px;padding:16px 20px}\n.streak-label{font-size:17px;color:#888;margin-bottom:5px}\n.streak-stats{display:flex;gap:22px;font-size:18px;align-items:center}\n.s-w{color:#2ecc71}\n.s-l{color:#e74c3c}\n.streak-good{color:#2ecc71;font-weight:bold}\n.streak-bad{color:#e74c3c;font-weight:bold;background:rgba(231,76,60,0.1);padding:2px 8px;border-radius:3px}\n.gauge-bar{display:flex;height:14px;border-radius:4px;overflow:hidden;margin-bottom:14px}\n.sa-seg{height:100%}\n.sa-rows{display:grid;grid-template-columns:1fr 1fr;gap:6px 20px;font-size:18px}\n.sa-row,.dr-row{display:flex;align-items:center;gap:6px;color:#aaa}\n.sa-circ,.dr-circ{width:8px;height:8px;border-radius:50%;flex-shrink:0}\n.stat-row{display:flex;align-items:center;gap:12px;font-size:17px;padding:5px 0;border-bottom:1px solid #11141d}\n.stat-label{width:120px;color:#999;flex-shrink:0}\n.stat-val{width:65px;font-weight:600;color:#fff;text-align:right}\n.stat-ref{width:120px;color:#888;font-size:15px;text-align:right}\n.stat-tag{width:75px;font-size:15px;text-align:right;font-weight:600}\n.vs-row{display:flex;align-items:center;gap:12px;font-size:17px;padding:6px 0;border-bottom:1px solid #11141d}\n.vs-name{width:85px;color:#fff;font-weight:bold}\n.vs-bar-track{flex:1;height:10px;background:#1a1d28;border-radius:2px;overflow:hidden}\n.vs-bar-fill{height:100%;background:#F15A24;border-radius:2px}\n.vs-rate{width:55px;color:#fff;font-weight:600;text-align:right}\n.vs-detail{width:48px;color:#888;font-size:15px;text-align:right}\n.low-sample{font-size:16px;color:#666;margin-top:8px}\n</style></head><body>\n<div class=\"header\">\n  <div>\n    <div class=\"p-name\">" + a["username"] + "</div>\n    <div class=\"p-sub\">CFN " + str(a["player_id"]) + " | Main: " + a["main_char"] + "</div>\n    <div class=\"p-sub\">" + a["platform"] + " | \u6392\u4f4d\u573a\u6b21: " + str(a.get("games", 0)) + "</div>\n  </div>\n  " + title_html + "\n</div>\n<div class=\"streak-panel\">" + streak_html + "</div>\n<div style=\"margin-bottom:10px\">" + tags_html + "</div>\n<div class=\"col2\">\n  <div class=\"card\">\n    <div class=\"card-title\">SA \u69fd\u5206\u5e03</div>\n    <div class=\"gauge-bar\">" + sa_bar + "</div>\n    <div class=\"sa-rows\">" + sa_rows + "</div>\n  </div>\n  <div class=\"card\">\n    <div class=\"card-title\">DRIVE GAUGE USAGE</div>\n    <div class=\"gauge-bar\">" + dr_bar + "</div>\n    <div class=\"sa-rows\">" + dr_rows + "</div>\n  </div>\n  <div class=\"card\">\n    <div class=\"card-title\">OFFENSE</div>\n    " + off_rows + "\n  </div>\n  <div class=\"card\">\n    <div class=\"card-title\">DEFENSE</div>\n    " + def_rows + "\n  </div>\n</div>\n<div class=\"card\">\n  <div class=\"card-title\">VS MATCHUPS</div>\n  " + vs_rows + "\n  " + low_html + "\n</div>\n</body></html>"
