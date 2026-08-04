from nonebot import on_command, on_message
from nonebot.adapters.onebot.v11 import MessageEvent

# Catch ALL group messages
echo = on_message(priority=1, block=False)

@echo.handle()
async def handle_echo(event: MessageEvent):
    text = event.get_plaintext()
    if text.startswith("!"):
        await echo.send(f"[DEBUG] Received: {text[:50]}")
