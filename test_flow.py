import sys, asyncio
sys.path.insert(0, '.')
from src.buckler.client import fetch_player_data
from src.analyzer.stats import analyze
from src.charts.renderer import generate_charts

async def test():
    data = await fetch_player_data('test123456')
    print(f"Username: {data.username}")
    print(f"Platform: {data.platform}")
    total_sec = data.game_time.total_play_time
    print(f"Total time: {total_sec}s ({total_sec // 3600}h)")
    print(f"Characters: {len(data.characters)}")
    for c in data.characters[:5]:
        wr = c.win_rate * 100
        print(f"  {c.name}: {c.rank} | {c.wins}/{c.total} ({wr:.1f}%)")
    print(f"Tech: throws={data.tech_stats.throws_landed}, DI={data.tech_stats.drive_impacts}")
    print(f"Drive pcts: {data.drive_usage.percentages()}")
    print(f"Matchups: ranked={len(data.ranked_matchups)}, casual={len(data.casual_matchups)}")
    print(f"Recent: {len(data.recent_matches)} matches")
    a = analyze(data)
    print(f"Overall WR: {a['overall_wr']}")
    print(f"Recent WR: {a.get('recent_wr', 'N/A')}")
    print(f"Recent record: {a.get('recent_record', 'N/A')}")
    print("Generating chart...")
    img_path = generate_charts(data)
    print(f"Chart saved: {img_path}")
    print("ALL TESTS PASSED!")

asyncio.run(test())
