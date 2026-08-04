path = r"src\buckler\client.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace all mock fallbacks with exceptions
content = content.replace(
    'return _gen_mock(sf6_id)',
    'raise Exception("Cookie未配置，请先在浏览器登录Buckler后提取Cookie到 data/buckler_cookie.txt")'
)

# For the cookie check specifically
content = content.replace(
    'print("[Buckler] No cookie, using mock")\n        return _gen_mock(sf6_id)',
    'raise Exception("Cookie未配置")'
)

content = content.replace(
    'print("[Buckler] Fetch failed, using mock")\n        return _gen_mock(sf6_id)',
    'raise Exception("无法连接到Buckler服务器，请检查网络")'
)

content = content.replace(
    'print("[Buckler] Non-200: " + str(status))\n        return _gen_mock(sf6_id)',
    'raise Exception("Buckler返回HTTP " + str(status) + "，数据不可用")'
)

content = content.replace(
    'print("[Buckler] No __NEXT_DATA__, using mock")\n        return _gen_mock(sf6_id)',
    'raise Exception("页面结构异常，无法提取数据")'
)

content = content.replace(
    'print("[Buckler] Parse failed, using mock")\n        return _gen_mock(sf6_id)',
    'raise Exception("数据解析失败")'
)

# Remove _gen_mock function entirely
gen_start = content.find("\ndef _gen_mock")
gen_end = content.find("\nasync def fetch_player_data")
if gen_start > 0 and gen_end > gen_start:
    content = content[:gen_start] + content[gen_end:]
    print("_gen_mock function removed")

# Also remove the mock imports/data that are no longer needed
# But keep SF6_CHARS etc as they're used elsewhere
# Remove RANKS since only used by mock
content = content.replace('\nRANKS = ["Rookie 1","Rookie 2","Iron 1","Iron 2","Iron 3","Bronze 1","Bronze 2","Bronze 3","Silver 1","Silver 2","Silver 3","Gold 1","Gold 2","Gold 3","Platinum 1","Platinum 2","Platinum 3","Diamond 1","Diamond 2","Diamond 3","Master"]\n', '\n')

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("All mock data removed - errors now throw exceptions")
