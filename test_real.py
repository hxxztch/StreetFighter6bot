import sys, asyncio
sys.path.insert(0, '.')
from src.buckler.client import fetch_player_data
async def test():
    data = await fetch_player_data('test12345')
    print('Username:', data.username)
    print('Platform:', data.platform)
    print('Characters:', len(data.characters))
    for c in data.characters[:3]:
        print(f'  {c.name}: {c.rank}')
asyncio.run(test())
