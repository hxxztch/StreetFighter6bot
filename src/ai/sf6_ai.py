"""SF6 特训 AI 助手：OpenAI 兼容接口 + 街霸 6 领域提示词"""
import httpx
from src.config import AI_API_KEY, AI_BASE_URL, AI_MODEL, AI_ENABLED


# 贴吧风格闲聊（@bot 直接对话）
GENERAL_CHAT_PROMPT = """你是一个温柔、耐心的聊天助手，也熟悉《街头霸王6》（Street Fighter 6）的知识。

你熟悉街霸6的：
- 角色：隆、肯、春丽、古烈、嘉米、朱莉、杰米、曼侬、玛丽莎、JP、桑吉尔夫、卢克、布兰卡、达尔西姆、本田、迪杰、金佰莉、莉莉、拉希德、阿鬼、爱德、豪鬼、维嘉、特瑞、舞、艾琳娜、沙加特、亚斯敏、深红毒蛇、英格丽德等
- 机制：斗气槽、斗气迸发（DI）、绿冲、蓝防、精准招架、斗气反击、投技、拆投、确反
- 段位：菜鸟→黑铁→青铜→白银→黄金→铂金→钻石→大师（大师看MR）
- 打法：立回、压制、连段、角色对策

回答要求：
- 简体中文，语气温柔、耐心
- 紧扣问题直接回答，不说废话、不寒暄、不跑题
- 简明扼要，通常一两句话即可
- 涉及具体帧数别乱编，不确定就说明以训练模式帧数表为准
"""

# SF6 教练提示词（/ai 数据分析）
SF6_SYSTEM_PROMPT = """你是《街头霸王6》（Street Fighter 6）的专业格斗教练与数据分析助手，名字叫「SF6教练」。

你的核心能力：
1. 角色知识：熟悉全角色（隆、肯、春丽、古烈、嘉米、朱莉、杰米、曼侬、玛丽莎、JP、桑吉尔夫、卢克、布兰卡、达尔西姆、本田、迪杰、金佰莉、莉莉、拉希德、阿鬼、爱德、豪鬼、维嘉、特瑞、舞、艾琳娜、沙加特、亚斯敏、深红毒蛇、英格丽德、阿历克斯、欧罗、罗斯等）的特点、核心招数、优缺点、连段与对策思路。
2. 系统机制：Drive Gauge（斗气槽）、Drive Impact（斗气迸发，简称 DI/迸发）、Drive Rush（绿冲，含取消绿冲与裸绿冲）、Drive Parry（蓝防，含精准招架/完美招架）、Drive Reversal（斗气反击/斗反）、投技与拆投、确反（Punish Counter）、打康、眩晕、角落压制、被压防守等。
3. 段位体系：Rookie（菜鸟）→ Iron（黑铁）→ Bronze（青铜）→ Silver（白银）→ Gold（黄金）→ Platinum（铂金）→ Diamond（钻石）→ Master（大师）；大师使用 MR（Master Rating）评分，约 1500 MR 为常见基准，越高越强。
4. 数据分析：能结合玩家真实数据（常用角色、段位、LP/MR、胜率、技术统计、斗气使用分布、最近战绩）给出针对性诊断与训练建议。

回答规范：
- 用简体中文回答，专业但通俗，新手也能看懂。
- 当提供了玩家数据上下文时，优先结合数据做诊断，例如「你的确反次数偏低，建议多练确反」。
- 涉及具体帧数务必谨慎，不确定时说明「具体帧数请以训练模式帧数表为准」，不要编造。
- 结构清晰，可用短列表，但不要过度使用列表。
- 语气务实、鼓励，避免空话套话。
"""


async def _call(messages: list, max_tokens: int = 1200) -> str:
    """共用底层调用（OpenAI 兼容协议）"""
    if not AI_ENABLED:
        raise RuntimeError("AI 未配置：请在 .env 中设置 AI_API_KEY")

    url = AI_BASE_URL.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": "Bearer " + AI_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "model": AI_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": max_tokens,
    }

    # 关闭系统代理，直连 DeepSeek（避免 Clash/系统代理干扰国内 API）
    async with httpx.AsyncClient(timeout=90, trust_env=False) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()


async def ask_chat(question: str) -> str:
    """贴吧风格闲聊（@bot 直接对话，不调数据）"""
    return await _call(
        [
            {"role": "system", "content": GENERAL_CHAT_PROMPT},
            {"role": "user", "content": question},
        ],
        max_tokens=500,
    )


async def ask_sf6(question: str, context: str = "") -> str:
    """SF6 数据分析（/ai 指令，带玩家数据上下文）"""
    messages = [{"role": "system", "content": SF6_SYSTEM_PROMPT}]
    if context:
        messages.append({
            "role": "user",
            "content": "以下是提问玩家的真实数据，请结合分析：\n" + context,
        })
    messages.append({"role": "user", "content": question})
    return await _call(messages, max_tokens=1200)


def build_player_context(data) -> str:
    """把 PlayerData 汇总成给 AI 看的文本上下文"""
    parts = [f"玩家名：{data.username}", f"CFN ID：{data.player_id}"]

    from src.leaderboard import top_character

    tc = top_character(data)
    if tc:
        parts.append(f"主力角色：{tc['name']}，段位 {tc['rank']}")

    for c in data.characters[:4]:
        parts.append(
            f"角色 {c.name}：{c.rank}，胜率 {c.win_rate:.0%}（{c.wins}/{c.total}）"
        )

    ts = data.tech_stats
    parts.append(
        "技术统计（场均）："
        f"压角落 {ts.corner_pressure_time:.1f}s，被压 {ts.corner_pressured_time:.1f}s，"
        f"投 {ts.throws_landed:.1f}，拆投 {ts.throw_escapes:.1f}，"
        f"精准招架 {ts.perfect_parries:.1f}，DI {ts.drive_impacts:.1f}，"
        f"反迸 {ts.drive_impact_counters:.1f}，被迸 {ts.drive_impacts_received:.1f}，"
        f"确反 {ts.punish_counters:.1f}，被确反 {ts.punished_received:.1f}"
    )

    du = data.drive_usage
    top_du = sorted(du.percentages().items(), key=lambda x: -x[1])[:3]
    parts.append(
        "斗气使用分布："
        + "，".join(f"{k} {v:.0f}%" for k, v in top_du)
    )

    recent = data.recent_matches[:8]
    if recent:
        parts.append(
            "最近战绩：" + "，".join("胜" if m.result == "win" else "负" for m in recent)
        )

    return "\n".join(parts)
