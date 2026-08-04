import os
BASE = r"E:\Study\sf6-qq-bot"

def w(path, content):
    fpath = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(fpath), exist_ok=True)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK: {path}")

# ========== models.py ==========
w(r"src\buckler\models.py", r"""from dataclasses import dataclass, field

@dataclass
class CharacterStat:
    name: str; usage_count: int; wins: int; total: int; rank: str; league_points: int = 0
    @property
    def win_rate(self): return self.wins / max(self.total, 1)

@dataclass
class TechStats:
    games_played: int = 0
    corner_pressure_time: float = 0.0; corner_pressured_time: float = 0.0
    throws_landed: float = 0.0; throw_escapes: float = 0.0
    perfect_parries: float = 0.0; drive_impacts: float = 0.0
    drive_impact_counters: float = 0.0; drive_impacts_received: float = 0.0
    punish_counters: float = 0.0; punished_received: float = 0.0
    super_arts: float = 0.0; combos_max_damage: int = 0; combos_avg_damage: float = 0.0

@dataclass
class DriveUsage:
    drive_rush_cancel: int = 0; overdrive: int = 0; drive_reversal: int = 0
    raw_drive_rush: int = 0; drive_parry: int = 0; burnout_drain: int = 0; other: int = 0
    @property
    def total(self): return self.drive_rush_cancel + self.overdrive + self.drive_reversal + self.raw_drive_rush + self.drive_parry + self.burnout_drain + self.other
    def percentages(self):
        t = self.total or 1
        return {"取消绿冲": self.drive_rush_cancel/t*100,"斗爆技(OD)": self.overdrive/t*100,"斗气反击": self.drive_reversal/t*100,"裸绿冲": self.raw_drive_rush/t*100,"蓝防": self.drive_parry/t*100,"被磨掉": self.burnout_drain/t*100}

@dataclass
class GameModeTime:
    total_play_time: int = 0; ranked_time: int = 0; casual_time: int = 0
    battle_hub_time: int = 0; training_time: int = 0; arcade_time: int = 0
    custom_room_time: int = 0; world_tour_time: int = 0; extreme_battle_time: int = 0; other_time: int = 0

@dataclass
class MatchupStat:
    opponent_char: str; wins: int; total: int; mode: str = ""
    @property
    def win_rate(self): return self.wins / max(self.total, 1)

@dataclass
class RecentMatch:
    date: str; opponent_name: str; opponent_char: str; player_char: str
    result: str; mode: str; rounds_won: int = 0; rounds_lost: int = 0; lp_change: int = 0

@dataclass
class PlayerData:
    username: str = ""; player_id: str = ""; platform: str = ""
    game_time: GameModeTime = field(default_factory=GameModeTime)
    characters: list = field(default_factory=list)
    tech_stats: TechStats = field(default_factory=TechStats)
    drive_usage: DriveUsage = field(default_factory=DriveUsage)
    ranked_matchups: list = field(default_factory=list)
    casual_matchups: list = field(default_factory=list)
    battle_hub_matchups: list = field(default_factory=list)
    recent_matches: list = field(default_factory=list)
""")

# ========== client.py ==========
w(r"src\buckler\client.py", r"""import random, httpx
from src.config import BUCKLER_BASE_URL
from src.buckler.models import (PlayerData, GameModeTime, CharacterStat, TechStats, DriveUsage, MatchupStat, RecentMatch)

SF6_CHARS = ["隆","肯","春丽","古烈","布兰卡","桑吉尔夫","达尔西姆","本田","迪杰","金佰莉","杰米","卢克","朱莉","玛丽莎","曼侬","莉莉","JP","嘉米","拉希德","阿鬼","爱德","豪鬼","维加","特瑞","舞","艾琳娜"]
RANKS = ["Rookie 1","Rookie 2","Iron 1","Iron 2","Iron 3","Bronze 1","Bronze 2","Bronze 3","Silver 1","Silver 2","Silver 3","Gold 1","Gold 2","Gold 3","Platinum 1","Platinum 2","Platinum 3","Diamond 1","Diamond 2","Diamond 3","Master"]
MODES = ["ranked","casual","battle_hub"]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def _gen_mock(sf6_id):
    rng = random.Random(sf6_id)
    nc = rng.choice([1,1,2,2,3,4])
    pool = rng.sample(SF6_CHARS, nc)
    tm = rng.randint(200, 3500)
    wts = [rng.uniform(0.3,1.0) for _ in range(nc)]
    ws = sum(wts)
    fracs = [w/ws for w in wts]
    fracs[0] = max(fracs[0], 0.4)
    diff = sum(fracs) - 1.0
    fracs[1:] = [f - diff/(len(fracs)-1) for f in fracs[1:]]
    chars = []
    for i, name in enumerate(pool):
        count = max(5, round(tm*fracs[i]))
        wr = min(0.75, max(0.35, rng.uniform(0.35,0.75)))
        wins = round(count*wr)
        ri = rng.randint(8, 19)
        rank = RANKS[ri]
        lp = rng.randint(1300,2100) if rank=="Master" else rng.randint(8000,25000)
        chars.append(CharacterStat(name=name,usage_count=count,wins=wins,total=count,rank=f"{rank} {lp}{'MR' if rank=='Master' else 'LP'}",league_points=lp))
    chars.sort(key=lambda c: c.usage_count, reverse=True)
    games = max(1, sum(c.total for c in chars))
    ts = TechStats(games_played=games, corner_pressure_time=round(rng.uniform(2.5,8.0),1), corner_pressured_time=round(rng.uniform(2.0,7.5),1), throws_landed=round(rng.uniform(1.0,4.5),1), throw_escapes=round(rng.uniform(0.5,3.5),1), perfect_parries=round(rng.uniform(0.1,1.2),2), drive_impacts=round(rng.uniform(1.5,5.0),1), drive_impact_counters=round(rng.uniform(0.3,2.0),1), drive_impacts_received=round(rng.uniform(1.0,4.5),1), punish_counters=round(rng.uniform(0.5,3.0),1), punished_received=round(rng.uniform(0.4,2.8),1), super_arts=round(rng.uniform(0.8,2.5),1), combos_max_damage=rng.randint(2000,7000), combos_avg_damage=round(rng.uniform(800,3200),0))
    du = DriveUsage(drive_rush_cancel=rng.randint(400,3500), overdrive=rng.randint(500,4000), drive_reversal=rng.randint(50,600), raw_drive_rush=rng.randint(200,2000), drive_parry=rng.randint(300,3000), burnout_drain=rng.randint(100,1500))
    tot_sec = rng.randint(36000, 500000)
    gt = GameModeTime(total_play_time=tot_sec, ranked_time=round(tot_sec*rng.uniform(0.25,0.55)), casual_time=round(tot_sec*rng.uniform(0.05,0.20)), battle_hub_time=round(tot_sec*rng.uniform(0.05,0.20)), training_time=round(tot_sec*rng.uniform(0.05,0.20)), arcade_time=round(tot_sec*rng.uniform(0.02,0.10)), custom_room_time=round(tot_sec*rng.uniform(0.02,0.10)), world_tour_time=round(tot_sec*rng.uniform(0.02,0.15)), extreme_battle_time=round(tot_sec*rng.uniform(0.01,0.05)))
    gt.other_time = max(0, tot_sec - sum([gt.ranked_time, gt.casual_time, gt.battle_hub_time, gt.training_time, gt.arcade_time, gt.custom_room_time, gt.world_tour_time, gt.extreme_battle_time]))
    def _mu(mode, n):
        res = []
        for name in rng.sample(SF6_CHARS, min(n, len(SF6_CHARS))):
            t = rng.randint(5,80)
            w = round(t * rng.uniform(0.30,0.80))
            res.append(MatchupStat(opponent_char=name, wins=w, total=t, mode=mode))
        res.sort(key=lambda m: m.total, reverse=True)
        return res
    rmu = _mu("ranked", rng.randint(4,8))
    cmu = _mu("casual", rng.randint(2,5))
    bmu = _mu("battle_hub", rng.randint(2,5))
    recent = []
    for i in range(rng.randint(10,20)):
        oc = rng.choice(SF6_CHARS)
        pc = pool[0] if rng.random()<0.7 else rng.choice(pool)
        mode = rng.choice(MODES)
        won = rng.random()<0.52
        rw = rng.choice([1,2]) if won else rng.choice([0,1])
        rl = 2-rw if won else 2-rng.choice([0,1])
        recent.append(RecentMatch(date=f"2026-{rng.randint(7,8):02d}-{rng.randint(1,28):02d} {rng.randint(10,23)}:{rng.randint(0,59):02d}", opponent_name=f"Player_{rng.randint(1000,9999)}", opponent_char=oc, player_char=pc, result="win" if won else "lose", mode=mode, rounds_won=rw, rounds_lost=rl, lp_change=rng.randint(0,65) if won else -rng.randint(0,65)))
    recent.sort(key=lambda m: m.date, reverse=True)
    return PlayerData(username=f"Fighter_{sf6_id[-8:]}", player_id=sf6_id, platform=rng.choice(["Steam","PS5","Xbox"]), game_time=gt, characters=chars, tech_stats=ts, drive_usage=du, ranked_matchups=rmu, casual_matchups=cmu, battle_hub_matchups=bmu, recent_matches=recent)

async def fetch_player_data(sf6_id, use_mock=True):
    if use_mock:
        return _gen_mock(sf6_id)
    headers = {"User-Agent": UA, "Accept": "application/json", "Referer": f"{BUCKLER_BASE_URL}/"}
    async with httpx.AsyncClient(headers=headers, timeout=30.0) as cl:
        resp = await cl.get(f"{BUCKLER_BASE_URL}/api/profile/{sf6_id}")
        resp.raise_for_status()
        raise NotImplementedError("Real Buckler API parser - implement parse_profile")
""")

print("Phase 3: models + client done!")
