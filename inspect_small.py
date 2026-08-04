import sys
sys.path.insert(0, ".")
path = "data/buckler_dumps/4222666364_small_page.html"
import os
print("Size:", os.path.getsize(path))
with open(path, "r", encoding="utf-8", errors="replace") as f:
    content = f.read()
idx = content.find("__NEXT_DATA__")
print("__NEXT_DATA__ at:", idx)
if idx > 0:
    end = content.find("</script>", idx)
    snippet = content[idx:end]
    # Find statusCode
    sc = snippet.find("statusCode")
    print("statusCode at:", sc)
    if sc > 0:
        print(snippet[sc:sc+30])
    # Check for play vs fighter_list
    print("play in NEXT_DATA:", "play" in snippet)
    print("fighter_list in NEXT_DATA:", "fighter_list" in snippet)
    print("replay_list in NEXT_DATA:", "replay_list" in snippet)
