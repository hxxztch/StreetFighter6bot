path = "bot2.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = "async def main():"
idx = content.find(old)

# Replace everything from main to end
new_main = """async def main():
    headers = {"Authorization": "Bearer " + TOKEN}
    while True:
        try:
            async with websockets.connect(WS_URL, extra_headers=headers, ping_interval=30) as ws:
                print("[BOT] Connected to NapCatQQ at " + WS_URL)
                while True:
                    try:
                        raw = await ws.recv()
                        data = json.loads(raw)
                        if data.get("post_type") == "message":
                            asyncio.create_task(handle_message(ws, data))
                        elif data.get("post_type") == "meta_event":
                            mt = data.get("meta_event_type", "")
                            if mt not in ("lifecycle", "heartbeat"):
                                print("[META] " + str(data))
                    except websockets.exceptions.ConnectionClosed:
                        print("[BOT] Connection lost, reconnecting in 3s...")
                        break
                    except Exception as e:
                        print("[WS] " + str(e))
                        break
        except Exception as e:
            print("[BOT] Connect failed: " + str(e) + ", retrying in 5s...")
        import asyncio as _asyncio
        await _asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())
"""

# Find the existing main and if __name__ blocks
main_start = content.find("async def main():")
name_start = content.find('if __name__ == "__main__":')
if main_start >= 0 and name_start > main_start:
    content = content[:main_start] + new_main

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("bot2.py: reconnection logic added")
