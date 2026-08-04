"""SF6 Dark Dashboard - HTML template + Playwright PNG renderer"""
import asyncio, json, re, time
from pathlib import Path
from src.config import CHART_OUTPUT_DIR, DATA_DIR
from src.buckler.models import PlayerData
from src.analyzer.stats import analyze

# Character tool name mapping for Buckler CDN images
CHAR_TOOL = {
    "Ryu": "ryu", "Luke": "luke", "Ken": "ken", "Chun-Li": "chunli",
    "Guile": "guile", "Blanka": "blanka", "Zangief": "zangief",
    "Dhalsim": "dhalsim", "E.Honda": "ehonda", "Dee Jay": "deejay",
    "Kimberly": "kimberly", "Jamie": "jamie", "Manon": "manon",
    "Marisa": "marisa", "JP": "jp", "Juri": "juri", "Cammy": "cammy",
    "Lily": "lily", "Rashid": "rashid", "A.K.I.": "aki",
    "Ed": "ed", "Akuma": "akuma", "M.Bison": "mbison",
    "Terry": "terry", "Mai": "mai", "Elena": "elena",
    "Sagat": "sagat", "C.Viper": "cviper", "Ingrid": "ingrid",
    "Alex": "alex", "Oro": "oro", "Rose": "rose",
}
CHAR_COLORS = ["#E74C3C","#3498DB","#2ECC71","#F39C12","#9B59B6","#1ABC9C","#E67E22","#2980B9","#C0392B","#27AE60","#8E44AD","#D35400","#16A085","#2C3E50","#F1C40F"]

def _gen_html(data: PlayerData) -> str:
    a = analyze(data)
    chars = a.get("characters", [])
    tsr = a.get("tech_stats_raw", {})
    du_list = a.get("drive_usage", [])
    gt = data.game_time

    username = a.get("username", "Player")
    player_id = data.player_id
    platform = data.platform

    # Dynamic donut from mode times
    mt = a.get("mode_times", {})
    mode_colors = ["#F15A24","#3B82F6","#FFFFFF","#2ECC71","#9B59B6","#1ABC9C","#E67E22","#95A5A6"]
    mode_rows = ""
    gradient_parts = []
    parsed_modes = []
    total_mins = 0
    for k, v in mt.items():
        if "0m" not in v and v != "0m":
            parts = v.replace("h",":").replace("m","").split(":")
            try:
                mins = int(parts[0]) * 60 + int(parts[1]) if len(parts) >= 2 else 0
            except:
                mins = 0
            total_mins += mins
            parsed_modes.append((k, v, mins))
    current_deg = 0
    for idx, (m_name, m_val, m_mins) in enumerate(parsed_modes[:4]):
        color = mode_colors[idx % len(mode_colors)]
        mode_rows += f"""<div class="mode-item">
          <span><span class="mode-dot" style="background:{color}"></span>{m_name}</span>
          <span style="color:#fff;font-weight:600">{m_val}</span>
        </div>"""
        deg = (m_mins / max(total_mins, 1) * 360)
        next_deg = current_deg + deg
        gradient_parts.append(f"{color} {current_deg:.0f}deg {next_deg:.0f}deg")
        current_deg = next_deg
    donut_gradient = ",".join(gradient_parts) if gradient_parts else "#F15A24 0deg 180deg, #3B82F6 180deg 360deg"

    # Most used characters
    char_rows = ""
    for i, c in enumerate([x for x in chars if x.get('usage_count',0) > 0][:10]):
        tool = CHAR_TOOL.get(c["name"], c["name"].lower().replace(" ",""))
        img_url = f"https://www.streetfighter.com/6/buckler/assets/images/character/face/{tool}.png"
        badge_rank = c["rank"][:3] if c["rank"] != "Unranked" else None
        badge_html = f'<div class="rank-tag">{badge_rank}</div>' if badge_rank else '<div class="rank-tag" style="background:rgba(255,255,255,0.06);color:#555">-</div>'
        char_rows += f"""<div class="char-row">
          <img class="char-img" src="{img_url}" onerror="this.style.display='none'"/>
          <div class="char-avatar" style="background:{CHAR_COLORS[i%len(CHAR_COLORS)]}">{c['name'][0]}</div>
          <div class="char-info">
            <div class="char-title-line"><span class="char-name">{c['name']}</span><span class="char-use">{c['win_rate']}</span></div>
            <div class="char-sub">SEASON WR {c['win_rate']} ({c['record']})</div>
          </div>
          {badge_html}
        </div>"""

    # Tech Info matrix
    TECH_MAP = {
        "corner_pressure_time": "角落压制(s)", "corner_pressured_time": "被压角落(s)",
        "throws_landed": "投技成功/场", "throw_escapes": "拆投成功/场",
        "perfect_parries": "精准招架/场", "drive_impacts": "斗气迸发/场",
        "drive_impact_counters": "反迸/场", "drive_impacts_received": "被迸发/场",
        "punish_counters": "确反/场", "punished_received": "被确反/场",
    }
    tech_items = ""
    for k, v in tsr.items():
        label = TECH_MAP.get(k, k.replace("_"," ").title())
        tech_items += f"""<div class="tech-item"><span>{label}</span><span class="tech-val">{v}</span></div>"""

    # Drive usage bars
    du_rows = ""
    for item in du_list[:6]:
        pct = item.get("pct", 0)
        du_rows += f"""<div class="hbar-wrap">
          <div class="hbar-label"><span>{item['label']}</span><span>{pct:.1f}%</span></div>
          <div class="hbar-track"><div class="hbar-fill" style="width:{pct}%"></div></div>
        </div>"""

    # Sagat VS grid - from matchup data
    all_mu = data.ranked_matchups + data.casual_matchups + data.battle_hub_matchups
    mu_agg = {}
    for m in all_mu:
        key = m.opponent_char
        if key not in mu_agg:
            mu_agg[key] = {"wins": 0, "total": 0}
        mu_agg[key]["wins"] += m.wins
        mu_agg[key]["total"] += m.total
    top_vs = sorted(mu_agg.items(), key=lambda x: x[1]["total"], reverse=True)[:4]
    vs_cells = ""
    for name, vals in top_vs:
        if vals["total"] > 0:
            pct = vals["wins"] / vals["total"] * 100
            tool = CHAR_TOOL.get(name, name.lower().replace(" ",""))
            vs_cells += f"""<div class="vs-cell">
              <img class="vs-avatar" src="https://www.streetfighter.com/6/buckler/assets/images/character/face/{tool}.png" onerror="this.style.display='none'"/>
              <span class="vs-name">{name}</span>
              <div class="vs-bar-track"><div class="vs-bar-fill" style="width:{pct:.0f}%"></div></div>
              <span class="vs-rate">{pct:.1f}%</span>
              <span class="vs-detail">{vals['wins']}/{vals['total']}</span>
            </div>"""
    if not vs_cells:
        vs_cells = '<div style="color:#666;font-size:11px;text-align:center;padding:10px">No matchup data available</div>'

    # Recent matches
    recent_rows = ""
    for m in a.get("recent_matches", [])[:5]:
        cls = "win" if m["result_icon"] == "O" else "loss"
        recent_rows += f"""<div class="battle-row">
          <span class="battle-tag {cls}">{cls.upper()}</span>
          <span class="battle-mode">{m.get('mode','')}</span>
          <span class="vs-text">VS</span>
          <span class="opp-name">{m.get('opponent','')}</span>
          <span class="opp-lp">{m.get('score','')}</span>
        </div>"""

    # Career totals
    ranked_cnt = a.get("total_games", 0)
    casual_cnt = len(data.casual_matchups)
    bh_cnt = len(data.battle_hub_matchups)
    total_wins = a.get("total_wins", 0)
    total_h = gt.total_play_time // 3600
    total_m = (gt.total_play_time % 3600) // 60

    
    # Rank display logic
    rank_display = ""
    if chars:
        r = chars[0]
        rs = r.get("rank", "")
        if "Master" in rs:
            import re as _re
            m = _re.search(r'(\d+)MR', rs)
            rank_display = f'<div class=\"rank-box\"><div class=\"rank-name\">MASTER</div><div class=\"rank-lp\">{m.group(1)}<span style=\"font-size:10px\"> MR</span></div></div>'
        else:
            tier_short = rs.split()[0] if rs.strip() else ""
            tier_map = {"D1":"Diamond 1","D2":"Diamond 2","D3":"Diamond 3","D4":"Diamond 4","D5":"Diamond 5",
                        "P1":"Platinum 1","P2":"Platinum 2","P3":"Platinum 3","P4":"Platinum 4","P5":"Platinum 5",
                        "G1":"Gold 1","G2":"Gold 2","G3":"Gold 3","G4":"Gold 4","G5":"Gold 5",
                        "S1":"Silver 1","S2":"Silver 2","S3":"Silver 3","S4":"Silver 4","S5":"Silver 5",
                        "B1":"Bronze 1","B2":"Bronze 2","B3":"Bronze 3","B4":"Bronze 4","B5":"Bronze 5",
                        "I1":"Iron 1","I2":"Iron 2","I3":"Iron 3","I4":"Iron 4","I5":"Iron 5",
                        "R1":"Rookie 1","R2":"Rookie 2"}
            tier_name = tier_map.get(tier_short, tier_short)
            rs_clean = rs.split()[-1].replace("LP","")
            rank_display = f'<div class=\"rank-box\"><div class=\"rank-name\">{tier_name}</div><div class=\"rank-lp\">{rs_clean}<span style=\"font-size:10px\"> LP</span></div></div>'
    
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#060709;color:#e8e8e8;font-family:"Microsoft YaHei","Segoe UI",sans-serif;width:1200px;margin:0 auto;padding:24px}}
.card{{background:#0e1018;border-radius:6px;padding:22px;border:1px solid #1e2230;margin-bottom:18px}}
.card-title{{font-size:18px;font-weight:700;color:#a0a5b4;letter-spacing:0.5px;margin-bottom:10px;display:flex;align-items:center;gap:6px}}
.card-title::before{{content:"";width:3px;height:12px;background:#F15A24}}
.col2{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}
.top-header{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px}}
.p-title{{font-size:32px;font-weight:bold;color:#fff}}
.p-sub{{font-size:17px;color:#999;margin-top:4px}}
.rank-box{{background:#0078d4;color:#fff;padding:6px 16px;border-radius:6px;text-align:right}}
.rank-name{{font-size:22px;font-weight:bold}}
.rank-lp{{font-size:36px;font-weight:bold}}
.donut-wrap{{display:flex;align-items:center;gap:20px}}
.donut{{width:120px;height:120px;border-radius:50%;background:conic-gradient({donut_gradient});display:flex;align-items:center;justify-content:center;position:relative;flex-shrink:0}}
.donut::after{{content:"";width:72px;height:72px;border-radius:50%;background:#0d0f15;position:absolute}}
.donut-text{{position:relative;z-index:1;text-align:center;font-size:24px;font-weight:bold;color:#fff}}
.donut-sub{{font-size:17px;color:#aaa}}
.mode-list{{flex:1}}
.mode-item{{display:flex;justify-content:space-between;font-size:17px;margin-bottom:7px}}
.mode-dot{{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:6px}}
.wr-big{{font-size:46px;font-weight:bold;color:#FFC000}}
.wr-sub{{font-size:17px;color:#999}}
.char-row{{display:flex;align-items:center;gap:18px;padding:12px 0;border-bottom:1px solid #161922}}
.char-img{{width:52px;height:52px;border-radius:50%;background:#1a1d26;object-fit:cover;display:block}}
.char-avatar{{width:60px;height:60px;border-radius:50%;display:none;align-items:center;justify-content:center;font-size:19px;font-weight:bold;flex-shrink:0}}
.char-img[onerror]+.char-avatar,.char-img:not([src]),.char-img[src=""],img.char-img[src=""]+div.char-avatar{{display:none!important}}
.char-avatar.fallback{{display:flex!important}}
.char-info{{flex:1}}
.char-title-line{{display:flex;gap:8px;font-size:19px;font-weight:bold}}
.char-use{{color:#FFC000}}
.char-sub{{font-size:17px;color:#999;margin-top:4px}}
.rank-tag{{background:#2563eb;color:#fff;font-size:16px;padding:4px 10px;border-radius:2px;font-weight:bold;white-space:nowrap}}
.tech-grid{{display:grid;grid-template-columns:1fr 1fr;gap:3px 16px}}
.tech-item{{display:flex;justify-content:space-between;font-size:17px;padding:4px 0}}
.tech-val{{font-weight:600;color:#FFC000}}
.hbar-wrap{{margin-bottom:8px;font-size:17px}}
.hbar-label{{display:flex;justify-content:space-between;color:#8a8f9d;margin-bottom:2px}}
.hbar-track{{height:11px;background:#1a1d26;border-radius:2px;overflow:hidden}}
.hbar-fill{{height:100%;background:#F15A24;border-radius:2px}}
.vs-grid{{display:grid;grid-template-columns:1fr 1fr;gap:8px}}
.vs-cell{{display:flex;align-items:center;gap:8px;font-size:17px;background:#131620;padding:12px;border-radius:4px}}
.vs-avatar{{width:36px;height:36px;border-radius:50%;background:#1e2230;object-fit:cover}}
.vs-name{{width:50px;color:#fff;font-weight:bold;font-size:16px}}
.vs-bar-track{{flex:1;height:9px;background:#1a1d26;border-radius:2px;overflow:hidden}}
.vs-bar-fill{{height:100%;background:#F15A24}}
.vs-rate{{color:#fff;font-weight:bold;width:50px;text-align:right;font-size:17px}}
.vs-detail{{color:#666;font-size:16px}}
.battle-row{{display:flex;align-items:center;gap:10px;font-size:17px;padding:9px 0;border-bottom:1px solid #161922}}
.battle-tag{{padding:1px 6px;border-radius:2px;font-weight:bold;font-size:16px}}
.battle-tag.win{{background:#2ecc7120;color:#2ecc71}}
.battle-tag.loss{{background:#e74c3c20;color:#e74c3c}}
.battle-mode{{color:#666;width:65px}}
.vs-text{{color:#444;font-size:16px}}
.opp-name{{color:#fff;flex:1}}
.opp-lp{{color:#666;font-size:10px}}
.footer{{display:flex;justify-content:space-between;font-size:16px;color:#555;padding-top:4px}}
</style></head><body>

<div class="top-header">
  <div>
    <div class="p-title">{username}</div>
    <div class="p-sub">PLAYER | {player_id}</div>
    <div class="p-sub">{platform} | Main: {chars[0]['name'] if chars else 'N/A'}</div>
  </div>
  {rank_display}
</div>

<div class="col2">
  <div class="card">
    <div class="card-title">PLAYING TIME</div>
    <div class="donut-wrap">
      <div class="donut"><div class="donut-text">{total_h}:{total_m}<br><span class="donut-sub">Total</span></div></div>
      <div class="mode-list">{mode_rows}</div>
    </div>
  </div>
  <div class="card">
    <div class="card-title">WIN RATE</div>
    <div style="display:flex;justify-content:space-between">
      <div><div class="wr-big">{a.get('overall_wr','N/A')}</div><div class="wr-sub">Total {a.get('total_wins',0)}/{a.get('total_games',0)}</div></div>
      <div><div class="wr-big" style="color:#22d3ee">{a.get('recent_wr','N/A')}</div><div class="wr-sub">Recent {a.get('recent_record','N/A')}</div></div>
    </div>
  </div>
</div>

<div class="card">
  <div class="card-title">MOST USED</div>
  {char_rows}
</div>

<div class="col2">
  <div class="card">
    <div class="card-title">TECH INFO</div>
    <div class="tech-grid">{tech_items}</div>
  </div>
  <div class="card">
    <div class="card-title">DRIVE USAGE</div>
    {du_rows}
  </div>
</div>

<div class="card">
  <div class="card-title">MATCHUP VS</div>
  <div class="vs-grid">{vs_cells}</div>
</div>

<div class="card">
  <div class="card-title">LAST 5 BATTLES</div>
  {recent_rows}
</div>

<div class="footer">
  <div>CAREER {ranked_cnt+casual_cnt+bh_cnt} matches (R: {ranked_cnt} / C: {casual_cnt} / BH: {bh_cnt})</div>
  <div>Updated {time.strftime('%Y-%m-%d %H:%M')} UTC+8</div>
</div>

</body></html>"""



async def render(data: PlayerData, output_filename: str = None) -> Path:
    from playwright.async_api import async_playwright
    html = _gen_html(data)
    if output_filename is None:
        output_filename = "sf6_" + str(data.player_id) + ".png"
    output_path = CHART_OUTPUT_DIR / output_filename
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1200, "height": 1800})
        await page.set_content(html, wait_until="networkidle")
        await __import__("asyncio").sleep(1.5)
        await page.screenshot(path=str(output_path), full_page=True)
        await browser.close()
    return output_path
