import sys, asyncio
sys.path.insert(0, '.')
from src.buckler.client import fetch_player_data
from src.analyzer.stats import analyze
from src.charts.renderer import generate_charts

async def test():
    data = await fetch_player_data('test12345')
    print(f'Data: {data.username} ({data.platform})')
    print(f'Chars: {len(data.characters)}')
    print(f'Recent matches: {len(data.recent_matches)}')
    a = analyze(data)
    print(f'Overall WR: {a["overall_wr"]}')
    print(f'Recent: {a.get("recent_record","N/A")}')
    img = generate_charts(data)
    print(f'Chart: {img}')
    print('ALL OK!')

asyncio.run(test())
