"""Weekly SF6 leaderboard PNG renderer"""
import asyncio
from pathlib import Path
from src.config import CHART_OUTPUT_DIR


async def render_weekly(week_id, group_id, entries):
    from playwright.async_api import async_playwright
    html = _gen_html(week_id, entries)
    output_path = CHART_OUTPUT_DIR / f"weekly_{group_id}_{week_id}.png"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1200, "height": 1800})
        await page.set_content(html, wait_until="networkidle")
        await asyncio.sleep(1)
        await page.screenshot(path=str(output_path), full_page=True)
        await browser.close()
    return output_path


def _delta_badge(score_delta, score_delta_display, rank_delta, unit):
    """Build colored delta markers for score and rank"""
    parts = []
    # Score change
    if score_delta is None:
        parts.append('<span class="delta new">NEW</span>')
    elif score_delta > 0:
        parts.append(f'<span class="delta up">▲ +{score_delta_display} {unit}</span>')
    elif score_delta < 0:
        parts.append(f'<span class="delta down">▼ {score_delta_display} {unit}</span>')
    else:
        parts.append('<span class="delta flat">= 0</span>')
    # Rank change
    if rank_delta is None:
        pass  # already showed NEW
    elif rank_delta > 0:
        parts.append(f'<span class="delta up">↑{rank_delta}</span>')
    elif rank_delta < 0:
        parts.append(f'<span class="delta down">↓{abs(rank_delta)}</span>')
    else:
        parts.append('<span class="delta flat">—</span>')
    return " ".join(parts)


def _score_cell(e):
    """Return score + tier HTML for a rank row"""
    label = e["rank_label"]
    tier = e["tier"]
    color = e.get("tier_color", "#8a8f9d")
    if tier == "Master":
        return f'<span class="score-cell"><span class="rank-score">{label}</span><span class="tier-tag" style="color:{color}">Master</span></span>'
    return f'<span class="score-cell"><span class="rank-score">{label} <span class="tier-tag" style="color:{color}">{tier}</span></span></span>'


def _gen_html(week_id, entries):
    top3 = [e for e in entries if e["rank"] <= 3]
    rest_top = [e for e in entries if 4 <= e["rank"] <= 10]
    rest = [e for e in entries if e["rank"] >= 11]

    # Podium order: 2nd, 1st, 3rd
    podium_order = [2, 1, 3]
    podium_cards = ""
    medal = {1: ("GOLD", "#FFD700", "#8a6d00"), 2: ("SILVER", "#C0C0C0", "#7d7d7d"), 3: ("BRONZE", "#CD7F32", "#7a4a1d")}
    for r in podium_order:
        e = next((x for x in top3 if x["rank"] == r), None)
        if e is None:
            continue
        name, color, border = medal[r]
        delta = _delta_badge(e["score_delta"], e["score_delta_display"], e["rank_delta"], e["unit"])
        podium_cards += f'''<div class="podium-card" style="border-color:{border}">
            <div class="medal" style="color:{color}">{name}</div>
            <div class="podium-nick">{e["nickname"]}</div>
            <div class="podium-char">{e["character"]}</div>
            <div class="podium-score">{e["rank_label"]}</div>
            <div class="podium-tier" style="color:{e["tier_color"]}">{e["tier_full"]}</div>
            <div class="podium-delta">{delta}</div>
        </div>'''

    def _card(e):
        delta = _delta_badge(e["score_delta"], e["score_delta_display"], e["rank_delta"], e["unit"])
        return f'''<div class="rank-row">
            <span class="rank-no">#{e["rank"]}</span>
            <span class="rank-nick">{e["nickname"]}</span>
            <span class="rank-char">{e["character"]}</span>
            {_score_cell(e)}
            <span class="rank-delta">{delta}</span>
        </div>'''

    top_rows = "".join(_card(e) for e in rest_top)
    rest_rows = "".join(_card(e) for e in rest)

    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=1200">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#060709;color:#e8e8e8;font-family:"Microsoft YaHei",sans-serif;width:1200px;margin:0 auto;padding:24px}}
.title{{text-align:center;font-size:40px;font-weight:bold;color:#fff;margin-bottom:4px}}
.subtitle{{text-align:center;font-size:16px;color:#999;margin-bottom:24px}}
.podium{{display:flex;justify-content:center;gap:20px;align-items:flex-end;margin-bottom:28px}}
.podium-card{{width:280px;background:#0e1018;border:2px solid;border-radius:10px;padding:22px 16px;text-align:center}}
.medal{{font-size:18px;font-weight:bold;letter-spacing:2px}}
.podium-nick{{font-size:22px;font-weight:bold;color:#fff;margin:8px 0 4px}}
.podium-char{{font-size:16px;color:#ccc;margin-bottom:8px}}
.podium-score{{font-size:30px;font-weight:bold;color:#FFC000}}
.podium-delta{{font-size:14px;margin-top:8px}}
.rank-row{{display:flex;align-items:center;gap:14px;padding:10px 16px;border-bottom:1px solid #1a1d28;font-size:18px}}
.rank-no{{width:52px;color:#F15A24;font-weight:bold}}
.rank-nick{{flex:1;color:#fff;font-weight:600}}
.rank-char{{width:120px;color:#ccc}}
.rank-score{{width:140px;text-align:right;color:#FFC000;font-weight:bold}}
.rank-delta{{width:240px;text-align:right}}
.delta{{font-weight:bold;margin-left:6px}}
.delta.up{{color:#2ecc71}}
.delta.down{{color:#e74c3c}}
.delta.flat{{color:#666}}
.delta.new{{color:#3b82f6}}
.section-label{{font-size:16px;color:#8a8f9d;font-weight:bold;margin:16px 0 8px;padding-left:4px}}
.small .rank-row{{font-size:15px;padding:7px 14px}}
.small .rank-score{{font-size:15px}}
</style></head><body>
<div class="title">SF6 周榜</div>
<div class="subtitle">{week_id}</div>
<div class="podium">{podium_cards}</div>
<div class="section-label">TOP 4-10</div>
{top_rows}
<div class="section-label small">11名以后</div>
<div class="small">{rest_rows}</div>
</body></html>"""
