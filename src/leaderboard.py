"""Weekly SF6 leaderboard ranking logic"""
import re
import datetime


def current_week_id():
    """Return ISO week string like '2026-W33'"""
    today = datetime.date.today()
    iso = today.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def _score_from_rank(rank_str):
    """Return sortable integer score from a rank string like 'Master 1469MR' or 'D3 22205LP'"""
    if not rank_str:
        return 0
    if rank_str.startswith("Master"):
        m = re.search(r"(\d+)\s*MR", rank_str)
        if m:
            # Master MR sorts above all LP; store MR*100 as synthetic key
            return int(m.group(1)) * 100
        return 0
    m = re.search(r"(\d+)\s*LP", rank_str)
    return int(m.group(1)) if m else 0


def _label_from_rank(rank_str):
    """Return human score label like '1469 MR' or '22205 LP'"""
    if not rank_str:
        return "0 LP"
    if rank_str.startswith("Master"):
        m = re.search(r"(\d+)\s*MR", rank_str)
        return f"{m.group(1)} MR" if m else "Master"
    m = re.search(r"(\d+)\s*LP", rank_str)
    return f"{m.group(1)} LP" if m else rank_str


def _unit_from_label(label):
    """Return 'MR' or 'LP' from a score label"""
    if "MR" in (label or ""):
        return "MR"
    return "LP"


TIER_COLORS = {
    "R": "#7ec850",  # Rookie - green
    "I": "#6b8aa8",  # Iron - steel blue
    "B": "#c48a5c",  # Bronze
    "S": "#b8c4cc",  # Silver
    "G": "#f4c430",  # Gold
    "P": "#23c8c8",  # Platinum - cyan
    "D": "#b388ff",  # Diamond - purple
    "M": "#ff5a3d",  # Master - red-orange
}


def tier_color(rank_str):
    """Return SF6 rank tier color for a rank string like 'D3 22205LP' or 'Master 1469MR'"""
    if not rank_str:
        return "#8a8f9d"
    if rank_str.startswith("Master"):
        return TIER_COLORS["M"]
    tier = rank_str.split()[0][:1].upper() if rank_str.strip() else ""
    return TIER_COLORS.get(tier, "#8a8f9d")


def top_character(data):
    """Extract the highest-score character entry from PlayerData"""
    if not data or not getattr(data, "characters", None):
        return None
    best = None
    best_score = -1
    for c in data.characters:
        score = c.league_points if c.league_points > 0 else 0
        # Prefer Master (score >= 250000 synthetic) and then highest score
        if score > best_score:
            best_score = score
            best = c
    if best is None:
        return None
    return {
        "name": best.name,
        "rank": best.rank,
        "label": _label_from_rank(best.rank),
        "score": _score_from_rank(best.rank),
    }


def build_leaderboard(current_snapshot, prev_snapshot):
    """Merge current + previous snapshots, compute score/rank deltas"""
    prev_map = {e["qq_id"]: e for e in prev_snapshot}
    entries = []
    for rank, e in enumerate(sorted(current_snapshot, key=lambda x: -x["score"]), start=1):
        prev = prev_map.get(e["qq_id"])
        score_delta = e["score"] - prev["score"] if prev else None
        rank_delta = prev["rank"] - rank if prev else None
        unit = _unit_from_label(e.get("rank_label", ""))
        score_delta_display = score_delta // 100 if unit == "MR" and score_delta is not None else score_delta
        entries.append({
            "qq_id": e["qq_id"],
            "nickname": e.get("nickname", ""),
            "character": e.get("character", ""),
            "rank_label": e.get("rank_label", ""),
            "score": e["score"],
            "rank": rank,
            "score_delta": score_delta,
            "score_delta_display": score_delta_display,
            "rank_delta": rank_delta,
            "unit": unit,
        })
    return entries
