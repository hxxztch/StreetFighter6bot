import os
BASE = r"E:\Study\sf6-qq-bot"

def w(path, content):
    fpath = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(fpath), exist_ok=True)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK: {path}")

w(r"src\charts\renderer.py", r'''import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from pathlib import Path
from src.config import CHART_DPI, CHART_OUTPUT_DIR

_CN_FONT = None

def _init_font():
    global _CN_FONT
    if _CN_FONT is not None: return _CN_FONT
    for name in ["Microsoft YaHei","SimHei","Noto Sans CJK SC"]:
        for f in fm.fontManager.ttflist:
            if f.name == name:
                _CN_FONT = fm.FontProperties(fname=f.fname)
                return _CN_FONT
    _CN_FONT = fm.FontProperties(); return _CN_FONT

def _fp(): return _init_font()

COLS = ["#E74C3C","#3498DB","#2ECC71","#F39C12","#9B59B6","#1ABC9C","#E67E22","#2980B9","#C0392B","#27AE60"]
BG = "#1a1a2e"; TC = "#e0e0e0"; GC = "#2d2d44"; WC = "#2ecc71"; LC = "#e74c3c"

def generate_charts(data, output_filename=None):
    _init_font(); fp = _fp()
    sc = {"axes.facecolor":BG,"figure.facecolor":BG,"axes.edgecolor":"#444","axes.labelcolor":TC,"text.color":TC,"xtick.color":TC,"ytick.color":TC,"grid.color":GC,"grid.alpha":0.5}
    with plt.style.context(sc):
        fig = plt.figure(figsize=(18, 24), dpi=CHART_DPI, facecolor=BG)
        fig.suptitle(f"{data.username}  SF6 Data Report", fontproperties=fp, fontsize=22, color="#fff", y=0.98, weight="bold")
        tg = sum(c.total for c in data.characters)
        tw = sum(c.wins for c in data.characters)
        info = f"Player ID: {data.player_id}  |  Platform: {data.platform}  |  Games: {tg}  |  WR: {tw/max(tg,1)*100:.1f}%"
        fig.text(0.5, 0.96, info, fontproperties=fp, fontsize=12, color="#aaa", ha="center")

        # 1. Characters bar
        ax1 = fig.add_subplot(3,3,1)
        chars = data.characters[:10]
        names = [c.name for c in chars]
        counts = [c.usage_count for c in chars]
        bars = ax1.barh(range(len(names)), counts, color=COLS[:len(names)], height=0.6)
        ax1.set_yticks(range(len(names))); ax1.set_yticklabels(names, fontproperties=fp, fontsize=9); ax1.invert_yaxis()
        ax1.set_title("Character Usage", fontproperties=fp, fontsize=13, color="#fff", pad=10)
        ax1.set_xlabel("Games", fontproperties=fp, fontsize=9); ax1.grid(axis="x", alpha=0.3)
        for bar, c in zip(bars, chars):
            ax1.text(bar.get_width()+max(counts)*0.02, bar.get_y()+bar.get_height()/2, f"{c.usage_count} ({c.win_rate*100:.1f}%)", va="center", fontproperties=fp, fontsize=8, color="#ccc")

        # 2. Game mode time
        ax2 = fig.add_subplot(3,3,2)
        gt = data.game_time
        md = [("Ranked",gt.ranked_time),("Casual",gt.casual_time),("Battle Hub",gt.battle_hub_time),("Training",gt.training_time),("Arcade",gt.arcade_time),("Custom Room",gt.custom_room_time),("World Tour",gt.world_tour_time),("Extreme",gt.extreme_battle_time)]
        md = [(l,v) for l,v in md if v>0]; lbs = [m[0] for m in md]; vs = [m[1] for m in md]
        tot = sum(vs); pcts = [f"{v/tot*100:.1f}%" for v in vs]
        wedges, _ = ax2.pie(vs, labels=None, colors=COLS[:len(lbs)], startangle=90, wedgeprops={"edgecolor":BG,"linewidth":1})
        ax2.legend(wedges, [f"{l} ({p})" for l,p in zip(lbs,pcts)], loc="center", prop=fp, fontsize=8, framealpha=0.5, facecolor=BG, labelcolor=TC)
        ax2.set_title("Game Mode Distribution", fontproperties=fp, fontsize=13, color="#fff", pad=10)
        ax2.text(0,-1.3, f"Total: {gt.total_play_time//3600}h{(gt.total_play_time%3600)//60}m", ha="center", fontproperties=fp, fontsize=10, color="#aaa", transform=ax2.transAxes)

        # 3. Character win rates
        ax3 = fig.add_subplot(3,3,3)
        wrs = [c.win_rate*100 for c in chars]; x = np.arange(len(names))
        bars3 = ax3.bar(x, wrs, color=COLS[:len(names)], width=0.6, edgecolor="#444")
        ax3.axhline(y=50, color="#888", linestyle="--", linewidth=0.8)
        ax3.set_xticks(x); ax3.set_xticklabels(names, fontproperties=fp, fontsize=8, rotation=30)
        ax3.set_ylim(0,100); ax3.set_title("Win Rate by Character", fontproperties=fp, fontsize=13, color="#fff", pad=10)
        ax3.set_ylabel("Win Rate (%)", fontproperties=fp, fontsize=9); ax3.grid(axis="y", alpha=0.3)
        for b, wr, c in zip(bars3, wrs, chars):
            ax3.text(b.get_x()+b.get_width()/2, b.get_height()+1, f"{wr:.1f}%\n{c.wins}/{c.total}", ha="center", fontproperties=fp, fontsize=7, color="#ccc")

        # 4. Tech radar
        ax4 = fig.add_subplot(3,3,4, projection="polar")
        ts = data.tech_stats
        labs = ["Corner+","Corner-","Throw+","Escape","Parry","DI","DI-Cnt","DI-Rcv","Punish+","Punish-"]
        vals = [ts.corner_pressure_time, ts.corner_pressured_time, ts.throws_landed, ts.throw_escapes, ts.perfect_parries*10, ts.drive_impacts, ts.drive_impact_counters, ts.drive_impacts_received, ts.punish_counters, ts.punished_received]
        mx = [max(v,1) for v in vals]; nv = [v/m for v,m in zip(vals,mx)]; N=len(labs)
        angs = [n/N*2*np.pi for n in range(N)]; nv.append(nv[0]); angs.append(angs[0])
        ax4.fill(angs, nv, alpha=0.25, color="#3498db")
        ax4.plot(angs, nv, "o-", color="#3498db", linewidth=1.5, markersize=4)
        ax4.set_xticks(angs[:-1]); ax4.set_xticklabels(labs, fontproperties=fp, fontsize=8)
        ax4.set_ylim(0,1); ax4.set_yticks([0.25,0.5,0.75]); ax4.set_yticklabels(["25%","50%","75%"], fontsize=7, color="#888")
        ax4.set_title("Technical Stats Radar (Avg)", fontproperties=fp, fontsize=13, color="#fff", pad=18); ax4.grid(True, alpha=0.3)

        # 5. Drive usage
        ax5 = fig.add_subplot(3,3,5)
        du = data.drive_usage; pcts5 = du.percentages()
        items = sorted(pcts5.items(), key=lambda x: x[1], reverse=True)
        lbs5 = [k for k,v in items]; vs5 = [v for k,v in items]
        cd = ["#E74C3C","#F39C12","#3498DB","#2ECC71","#9B59B6","#E67E22"]
        w5, _ = ax5.pie(vs5, labels=None, colors=cd[:len(lbs5)], startangle=90, wedgeprops={"edgecolor":BG,"linewidth":1})
        ax5.legend(w5, [f"{l} ({v:.1f}%)" for l,v in zip(lbs5,vs5)], loc="center", prop=fp, fontsize=8, framealpha=0.5, facecolor=BG, labelcolor=TC)
        ax5.set_title("Drive Gauge Usage", fontproperties=fp, fontsize=13, color="#fff", pad=10)

        # 6. Ranked matchups
        ax6 = fig.add_subplot(3,3,6)
        rmu = sorted(data.ranked_matchups, key=lambda m: m.total, reverse=True)[:8]
        if rmu:
            n6 = [m.opponent_char for m in rmu]; w6 = [m.win_rate*100 for m in rmu]; t6 = [m.total for m in rmu]
            x6 = np.arange(len(n6))
            bc6 = [WC if w>=50 else LC for w in w6]
            b6 = ax6.bar(x6, w6, color=bc6, width=0.6, edgecolor="#444")
            ax6.axhline(y=50, color="#888", linestyle="--", linewidth=0.8)
            ax6.set_xticks(x6); ax6.set_xticklabels(n6, fontproperties=fp, fontsize=8, rotation=30)
            ax6.set_ylim(0,100); ax6.set_title("Ranked Matchup WR Top8", fontproperties=fp, fontsize=13, color="#fff", pad=10)
            ax6.set_ylabel("Win Rate (%)", fontproperties=fp, fontsize=9); ax6.grid(axis="y", alpha=0.3)
            for b, w, t in zip(b6, w6, t6):
                ax6.text(b.get_x()+b.get_width()/2, b.get_height()+1, f"{w:.0f}%\n({t})", ha="center", fontproperties=fp, fontsize=7, color="#ccc")
        else:
            ax6.text(0.5,0.5,"No Data",ha="center",va="center",fontproperties=fp,fontsize=14,color="#666",transform=ax6.transAxes)
            ax6.set_title("Ranked Matchup WR", fontproperties=fp, fontsize=13, color="#fff", pad=10)

        # 7. Recent results
        ax7 = fig.add_subplot(3,3,7)
        rec = data.recent_matches[:20]
        if rec:
            n7 = [f"{m.player_char} vs {m.opponent_char}" for m in rec]
            rc = [WC if m.result=="win" else LC for m in rec]
            y7 = np.arange(len(rec))
            ax7.barh(y7, [1]*len(rec), color=rc, height=0.7, edgecolor="#333")
            ax7.set_yticks(y7); ax7.set_yticklabels(n7, fontproperties=fp, fontsize=7); ax7.invert_yaxis()
            ax7.set_xlim(0,1); ax7.set_xticks([])
            wins_c = sum(1 for m in rec if m.result=="win")
            ax7.set_title("Recent Results", fontproperties=fp, fontsize=13, color="#fff", pad=10)
            ax7.text(0.5,-0.5, f"Last {len(rec)}: {wins_c}W {len(rec)-wins_c}L", ha="center", fontproperties=fp, fontsize=10, color="#aaa", transform=ax7.transAxes)
            from matplotlib.patches import Patch
            ax7.legend(handles=[Patch(facecolor=WC,label="Win"),Patch(facecolor=LC,label="Lose")], loc="lower right", prop=fp, fontsize=7, framealpha=0.5, facecolor=BG, labelcolor=TC)

        # 8. Casual/BH matchups
        ax8 = fig.add_subplot(3,3,8)
        cmu = data.casual_matchups + data.battle_hub_matchups
        if cmu:
            t8 = sorted(cmu, key=lambda m: m.total, reverse=True)[:8]
            n8 = [m.opponent_char for m in t8]; w8 = [m.win_rate*100 for m in t8]; t8t = [m.total for m in t8]
            x8 = np.arange(len(n8))
            bc8 = [WC if w>=50 else LC for w in w8]
            b8 = ax8.bar(x8, w8, color=bc8, width=0.6, edgecolor="#444")
            ax8.axhline(y=50, color="#888", linestyle="--", linewidth=0.8)
            ax8.set_xticks(x8); ax8.set_xticklabels(n8, fontproperties=fp, fontsize=8, rotation=30)
            ax8.set_ylim(0,100); ax8.set_title("Casual/BH Matchup WR", fontproperties=fp, fontsize=13, color="#fff", pad=10)
            ax8.set_ylabel("Win Rate (%)", fontproperties=fp, fontsize=9); ax8.grid(axis="y", alpha=0.3)
            for b, w, t in zip(b8, w8, t8t):
                ax8.text(b.get_x()+b.get_width()/2, b.get_height()+1, f"{w:.0f}%\n({t})", ha="center", fontproperties=fp, fontsize=7, color="#ccc")
        else:
            ax8.text(0.5,0.5,"No Data",ha="center",va="center",fontproperties=fp,fontsize=14,color="#666",transform=ax8.transAxes)
            ax8.set_title("Casual/BH Matchup WR", fontproperties=fp, fontsize=13, color="#fff", pad=10)

        # 9. Ranks
        ax9 = fig.add_subplot(3,3,9)
        ax9.axis("off")
        ax9.set_title("Ranks", fontproperties=fp, fontsize=13, color="#fff", pad=10)
        yp = 0.9
        for i, c in enumerate(chars[:8]):
            cl = COLS[i%len(COLS)]
            ax9.text(0.1, yp, c.name, fontproperties=fp, fontsize=12, color=cl, va="center", weight="bold")
            ax9.text(0.35, yp, c.rank, fontproperties=fp, fontsize=10, color="#ddd", va="center")
            yp -= 0.1
        ax9.set_xlim(0,1); ax9.set_ylim(0,1)

        plt.tight_layout(rect=[0,0,1,0.95])
        if output_filename is None: output_filename = f"sf6_{data.player_id}.png"
        op = CHART_OUTPUT_DIR / output_filename
        fig.savefig(op, dpi=CHART_DPI, bbox_inches="tight", facecolor=BG, edgecolor="none")
        plt.close(fig)
        return op
''')

print("Phase 5: chart renderer done!")
