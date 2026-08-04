import os
BASE = r"E:\Study\sf6-qq-bot"
def w(p, c):
    with open(os.path.join(BASE, p), "w", encoding="utf-8") as f:
        f.write(c)
    print("OK: " + p)

# 1. Fix parser tech stats keys
cpath = r"src\buckler\client.py"
with open(cpath, "r", encoding="utf-8") as f:
    cc = f.read()

# Fix tech stats keys
old_tech = """    data.tech_stats = TechStats(
        corner_pressure_time=bs.get("corner_time", 0) or 0,
        corner_pressured_time=bs.get("cornered_time", 0) or 0,
        throws_landed=bs.get("throw", 0) or 0,
        throw_escapes=bs.get("throw_escape", 0) or 0,
        perfect_parries=bs.get("perfect_parry", 0) or 0,
        drive_impacts=bs.get("drive_impact", 0) or 0,
        drive_impact_counters=bs.get("drive_impact_to_drive_impact", 0) or 0,
        drive_impacts_received=bs.get("receive_drive_impact", 0) or 0,
        punish_counters=bs.get("punish_counter", 0) or 0,
        punished_received=bs.get("receive_punish_counter", 0) or 0,
        super_arts=bs.get("super_arts_lv1", 0) or 0,
    )"""

new_tech = """    data.tech_stats = TechStats(
        corner_pressure_time=bs.get("corner_time", 0) or 0,
        corner_pressured_time=bs.get("cornered_time", 0) or 0,
        throws_landed=bs.get("throw_count", 0) or 0,
        throw_escapes=bs.get("throw_tech", 0) or 0,
        perfect_parries=bs.get("just_parry", 0) or 0,
        drive_impacts=bs.get("drive_impact", 0) or 0,
        drive_impact_counters=bs.get("drive_impact_to_drive_impact", 0) or 0,
        drive_impacts_received=bs.get("received_drive_impact", 0) or 0,
        punish_counters=bs.get("punish_counter", 0) or 0,
        punished_received=bs.get("received_punish_counter", 0) or 0,
        super_arts=bs.get("gauge_rate_sa_lv1", 0) or 0,
    )"""
cc = cc.replace(old_tech, new_tech)

# Fix drive usage keys (rate values 0-1, convert to pct)
old_drive = """    data.drive_usage = DriveUsage(
        drive_rush_cancel=bs.get("drive_rush_cancel", 0) or 0,
        overdrive=bs.get("overdrive_arts", 0) or 0,
        drive_reversal=bs.get("drive_reversal", 0) or 0,
        raw_drive_rush=bs.get("parry_drive_rush", 0) or 0,
        drive_parry=bs.get("drive_parry", 0) or 0,
        burnout_drain=bs.get("gauge_rate_ca", 0) or 0,
    )"""

new_drive = """    data.drive_usage = DriveUsage(
        drive_rush_cancel=round((bs.get("gauge_rate_drive_rush_from_cancel", 0) or 0) * 100),
        overdrive=round((bs.get("gauge_rate_drive_arts", 0) or 0) * 100),
        drive_reversal=round((bs.get("gauge_rate_drive_reversal", 0) or 0) * 100),
        raw_drive_rush=round((bs.get("gauge_rate_drive_rush_from_parry", 0) or 0) * 100),
        drive_parry=round((bs.get("gauge_rate_drive_guard", 0) or 0) * 100),
        burnout_drain=round((bs.get("gauge_rate_drive_impact", 0) or 0) * 100),
        other=round((bs.get("gauge_rate_drive_other", 0) or 0) * 100),
    )"""
cc = cc.replace(old_drive, new_drive)
with open(cpath, "w", encoding="utf-8") as f:
    f.write(cc)

# 2. Fix DriveUsage model labels
mpath = r"src\buckler\models.py"
with open(mpath, "r", encoding="utf-8") as f:
    mc = f.read()
old_pct = """return {"取消绿冲": self.drive_rush_cancel/t*100,"斗爆技(OD)": self.overdrive/t*100,"斗气反击": self.drive_reversal/t*100,"裸绿冲": self.raw_drive_rush/t*100,"蓝防": self.drive_parry/t*100,"被磨掉": self.burnout_drain/t*100}"""
new_pct = """return {"取消绿冲": self.drive_rush_cancel/t*100,"斗爆技(OD)": self.overdrive/t*100,"斗气反击": self.drive_reversal/t*100,"裸绿冲": self.raw_drive_rush/t*100,"蓝防": self.drive_parry/t*100,"迸发消耗": self.burnout_drain/t*100,"其他": self.other/t*100}"""
mc = mc.replace(old_pct, new_pct)
with open(mpath, "w", encoding="utf-8") as f:
    f.write(mc)

# 3. Fix dashboard tech info labels + remove SA
dpath = r"src\charts\dashboard_renderer.py"
with open(dpath, "r", encoding="utf-8") as f:
    dc = f.read()
old_tmap = """TECH_MAP = {
        "corner_pressure_time": "角落压制", "corner_pressured_time": "被压角落",
        "throws_landed": "投技成功", "throw_escapes": "拆投成功",
        "perfect_parries": "精准招架", "drive_impacts": "斗气迸发",
        "drive_impact_counters": "反迸", "drive_impacts_received": "被迸发",
        "punish_counters": "确反", "punished_received": "被确反",
        "super_arts": "SA使用",
    }"""
new_tmap = """TECH_MAP = {
        "corner_pressure_time": "角落压制(s)", "corner_pressured_time": "被压角落(s)",
        "throws_landed": "投技成功/场", "throw_escapes": "拆投成功/场",
        "perfect_parries": "精准招架/场", "drive_impacts": "斗气迸发/场",
        "drive_impact_counters": "反迸/场", "drive_impacts_received": "被迸发/场",
        "punish_counters": "确反/场", "punished_received": "被确反/场",
    }"""
dc = dc.replace(old_tmap, new_tmap)
with open(dpath, "w", encoding="utf-8") as f:
    f.write(dc)

print("All keys realigned, units added, SA removed, drive labels fixed")
