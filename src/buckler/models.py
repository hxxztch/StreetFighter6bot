from dataclasses import dataclass, field

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
    drive_parry: float = 0.0; drive_reversal: float = 0.0
    stuns: float = 0.0; stuns_received: float = 0.0
    throw_drive_parry: float = 0.0; received_throw_drive_parry: float = 0.0
    sa_lv1_rate: float = 0.0; sa_lv2_rate: float = 0.0; sa_lv3_rate: float = 0.0; ca_rate: float = 0.0

@dataclass
class DriveUsage:
    drive_rush_cancel: int = 0; overdrive: int = 0; drive_reversal: int = 0
    raw_drive_rush: int = 0; drive_parry: int = 0; burnout_drain: int = 0; other: int = 0
    @property
    def total(self): return self.drive_rush_cancel + self.overdrive + self.drive_reversal + self.raw_drive_rush + self.drive_parry + self.burnout_drain + self.other
    def percentages(self):
        t = self.total or 1
        return {"取消绿冲": self.drive_rush_cancel/t*100,"裸绿冲": self.raw_drive_rush/t*100,"斗爆技(OD)": self.overdrive/t*100,"蓝防": self.drive_parry/t*100,"迸发消耗": self.burnout_drain/t*100,"斗气反击": self.drive_reversal/t*100,"其他": self.other/t*100}

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
