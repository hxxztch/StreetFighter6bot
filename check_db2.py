import sys, asyncio
sys.path.insert(0, '.')
from src.database import get_binding, bind_qq_to_sf6, get_cached_stats, set_cached_stats
async def test():
    await bind_qq_to_sf6('test123', '4222666364')
    r = await get_binding('test123')
    print('Bind/Query:', r)
    print('PASSED' if r == '4222666364' else 'FAILED')
    await set_cached_stats('test_sf6', {'hello': 'world'})
    c = await get_cached_stats('test_sf6')
    print('Cache:', c)
    print('ALL PASSED' if c and c['hello'] == 'world' and r == '4222666364' else 'SOMETHING FAILED')
asyncio.run(test())
