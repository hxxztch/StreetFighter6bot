"""SF6 frame data lookup backed by the extracted FAT data bundle."""
import json
import re
from functools import lru_cache
from pathlib import Path


CHARACTER_ALIASES = {
    "Ryu": ["ryu", "隆"],
    "Ken": ["ken", "肯"],
    "Chun-Li": ["chunli", "chun-li", "春丽"],
    "Guile": ["guile", "古烈", "盖尔"],
    "Cammy": ["cammy", "嘉米"],
    "Juri": ["juri", "朱莉"],
    "Jamie": ["jamie", "杰米"],
    "Manon": ["manon", "曼侬"],
    "Marisa": ["marisa", "玛丽莎"],
    "JP": ["jp"],
    "Zangief": ["zangief", "桑吉尔夫", "老桑"],
    "Luke": ["luke", "卢克"],
    "Blanka": ["blanka", "布兰卡"],
    "Dhalsim": ["dhalsim", "达尔西姆"],
    "E.Honda": ["ehonda", "e.honda", "本田"],
    "Dee Jay": ["deejay", "dee-jay", "迪杰"],
    "Kimberly": ["kimberly", "金佰莉", "金伯利"],
    "Lily": ["lily", "莉莉"],
    "Rashid": ["rashid", "拉希德"],
    "A.K.I.": ["aki", "a.k.i.", "阿鬼"],
    "Ed": ["ed", "爱德"],
    "Akuma": ["akuma", "豪鬼"],
    "M.Bison": ["mbison", "m.bison", "维嘉", "拜森"],
    "Terry": ["terry", "特瑞"],
    "Mai": ["mai", "舞"],
    "Elena": ["elena", "艾琳娜"],
    "Sagat": ["sagat", "沙加特"],
    "C.Viper": ["cviper", "c.viper", "viper", "深红毒蛇"],
    "Alex": ["alex", "阿历克斯", "亚历克斯"],
}


MOVE_HINTS_CN = {
    "升龙": ["shoryuken", "shoryu"],
    "波动": ["hadouken", "hadoken", "fireball"],
    "波掌": ["hashogeki"],
    "波掌击": ["hashogeki"],
    "旋风": ["tatsu", "tornado"],
    "龙尾": ["tatsu", "tornado"],
    "正蹬": ["kazekiri"],
    "迅雷": ["thunder kick", "thunder"],
    "急停": ["run stop", "stop"],
    "绿冲": ["drive rush", "rush"],
    "中段": ["overhead"],
    "投": ["throw", "grab"],
    "迸": ["drive impact", "di"],
    "斗反": ["drive reversal", "reversal"],
    "蓝防": ["drive parry", "parry"],
    "确反": ["punish"],
    "剪刀脚": ["knee press", "double knee press", "head press"],
}


STRENGTH_HINTS = {
    "轻": "lp",
    "中": "mp",
    "重": "hp",
    "od": "pp",
}


@lru_cache(maxsize=1)
def load_frame_data() -> dict:
    path = Path(__file__).resolve().parents[2] / "data" / "sf6_frame_data.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


@lru_cache(maxsize=1)
def load_move_names_zh() -> dict:
    path = Path(__file__).resolve().parents[2] / "data" / "sf6_move_names_zh.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def _find_character(question: str) -> str:
    q = question.lower()
    q_plain = _normalize(question)
    data = load_frame_data()

    for key, aliases in CHARACTER_ALIASES.items():
        if key not in data:
            continue
        key_norm = _normalize(key)
        if key.lower() in q or (key_norm and key_norm in q_plain):
            return key
        for alias in aliases:
            alias_lower = alias.lower()
            alias_norm = _normalize(alias)
            if alias_lower in q or (alias_norm and alias_norm in q_plain):
                return key

    for key in data:
        key_norm = _normalize(key)
        if key.lower() in q or (key_norm and key_norm in q_plain):
            return key
    return ""


def _format_number(value) -> str:
    if isinstance(value, (int, float)):
        if isinstance(value, float) and value == int(value):
            return str(int(value))
        return str(value)
    return str(value)


def _format_move(name: str, move: dict, zh_name: str = "") -> str:
    commands = [move.get(k) for k in ("plnCmd", "numCmd", "ezCmd") if move.get(k)]
    command_text = " / ".join(_format_number(c) for c in commands) if commands else "无指令"

    fields = []
    for key, label in (
        ("startup", "启动"),
        ("active", "持续"),
        ("recovery", "恢复"),
        ("total", "总帧"),
        ("onHit", "命中"),
        ("onBlock", "防御"),
        ("onPC", "打康"),
        ("onPP", "完美招架"),
        ("dmg", "伤害"),
        ("atkLvl", "攻击等级"),
        ("moveType", "类型"),
    ):
        if key in move:
            fields.append(f"{label} {_format_number(move[key])}")

    title = f"{zh_name} / {name}" if zh_name else name
    line = f"[{title}] 指令 {command_text}；" + "，".join(fields)
    extra = move.get("extraInfo")
    if isinstance(extra, list) and extra:
        line += "；备注 " + "；".join(str(x) for x in extra)
    return line


def _score_move(question: str, name: str, move: dict, zh_name: str = "") -> int:
    q = question.lower()
    score = 0

    if name.lower() in q:
        score += 6
    if zh_name and zh_name in question:
        score += 6

    searchable = " ".join(
        _format_number(move.get(k))
        for k in (
            "moveName",
            "plnCmd",
            "numCmd",
            "ezCmd",
            "moveType",
            "moveMotion",
            "moveButton",
        )
        if move.get(k)
    ).lower()
    if zh_name:
        searchable += " " + zh_name.lower()

    notation_tokens = [
        token
        for token in re.findall(r"[0-9]{0,3}[a-z]{1,4}", q.replace(" ", ""))
        if token not in {"od", "ex", "lp", "mp", "hp", "lk", "mk", "hk", "pp", "kk"}
    ]
    for token in notation_tokens:
        if token in searchable:
            score += 4

    for hint, keywords in MOVE_HINTS_CN.items():
        if hint in question and any(k in searchable for k in keywords):
            score += 5

    for hint, command in STRENGTH_HINTS.items():
        if hint in question and command in searchable and score > 0:
            score += 4

    if any(word in searchable for word in ("overhead", "throw", "drive impact", "drive reversal")):
        if "中段" in question and "overhead" in searchable:
            score += 5
        if "投" in question and "throw" in searchable:
            score += 5
        if "迸" in question and "drive impact" in searchable:
            score += 5
        if "斗反" in question and "drive reversal" in searchable:
            score += 5

    return score


def lookup_frame_data(question: str, max_chars: int = 12000) -> str:
    """Return frame-data snippets relevant to the question, or empty text."""
    data = load_frame_data()
    if not data:
        return ""

    character = _find_character(question)
    if not character:
        all_zh = load_move_names_zh()
        for candidate_char, candidate_obj in data.items():
            candidate_moves = candidate_obj.get("moves", {}).get("normal", {})
            candidate_zh = all_zh.get(candidate_char, {})
            for move_name, move in candidate_moves.items():
                zh_name = candidate_zh.get(move_name, {}).get("zh", "")
                if _score_move(question, move_name, move, zh_name) > 0:
                    character = candidate_char
                    break
            if character:
                break
        if not character:
            return ""

    moves = data[character].get("moves", {}).get("normal", {})
    if not moves:
        return ""

    scored = []
    zh_map = load_move_names_zh().get(character, {})
    for name, move in moves.items():
        zh_name = zh_map.get(name, {}).get("zh", "")
        score = _score_move(question, name, move, zh_name)
        if score > 0:
            scored.append((score, name, move, zh_name))

    scored.sort(key=lambda item: (-item[0], item[1]))
    selected = [(item[2], item[3]) for item in scored[:40]] if scored else [(move, zh_map.get(move.get("moveName", ""), {}).get("zh", "")) for move in list(moves.values())[:40]]

    stats = data[character].get("stats", {})
    lines = [
        f"【FAT帧数数据库】角色：{character}",
        "角色数据：" + "；".join(f"{k}={_format_number(v)}" for k, v in stats.items()),
        "招式帧数：",
    ]
    current_chars = sum(len(line) for line in lines)
    for move, zh_name in selected:
        line = _format_move(move.get("moveName", ""), move, zh_name)
        if current_chars + len(line) > max_chars:
            break
        lines.append(line)
        current_chars += len(line)
    return "\n".join(lines)
