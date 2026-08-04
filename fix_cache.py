path = r"bot2.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update the import line
old_import = "from src.buckler.models import PlayerData"
new_import = "from src.buckler.models import PlayerData, GameModeTime, CharacterStat, TechStats, DriveUsage, MatchupStat, RecentMatch"
if old_import in content:
    content = content.replace(old_import, new_import)
    print("Import updated")
else:
    print("Import not found:", old_import[:50])

# 2. Replace cached loading code
old_cache = """                cached = await get_cached_stats(sid)
                if cached:
                    data = PlayerData(**cached)"""
new_cache = """                cached = await get_cached_stats(sid)
                if cached:
                    data = _reconstruct(cached)"""
if old_cache in content:
    content = content.replace(old_cache, new_cache)
    print("Cache loading fixed")
else:
    print("Cache loading pattern not found")

# 3. Add _reconstruct function before handle_message
reconstruct = '''
def _reconstruct(d):
    """Reconstruct PlayerData from cached dict"""
    from src.buckler.models import GameModeTime, CharacterStat, TechStats, DriveUsage, MatchupStat, RecentMatch
    gt = GameModeTime(**d.get("game_time", {}))
    chars = [CharacterStat(**c) for c in d.get("characters", [])]
    ts = TechStats(**d.get("tech_stats", {}))
    du = DriveUsage(**d.get("drive_usage", {}))
    ranked_mu = [MatchupStat(**m) for m in d.get("ranked_matchups", [])]
    casual_mu = [MatchupStat(**m) for m in d.get("casual_matchups", [])]
    bh_mu = [MatchupStat(**m) for m in d.get("battle_hub_matchups", [])]
    recent = [RecentMatch(**m) for m in d.get("recent_matches", [])]
    return PlayerData(username=d.get("username",""), player_id=d.get("player_id",""),
        platform=d.get("platform",""), game_time=gt, characters=chars,
        tech_stats=ts, drive_usage=du, ranked_matchups=ranked_mu,
        casual_matchups=casual_mu, battle_hub_matchups=bh_mu, recent_matches=recent)
'''

target = "\nasync def handle_message(ws, event):"
if target in content:
    content = content.replace(target, reconstruct + "\n\nasync def handle_message(ws, event):")
    print("_reconstruct function inserted")
else:
    print("handle_message not found")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("bot2.py fixed!")
