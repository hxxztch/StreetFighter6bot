
# Scale both renderers to Plan B (1200px body, ~1.5x font/gap scaling)
import ast, os

# ----- DASHBOARD -----
c = open("src/charts/dashboard_renderer.py", "rb").read()
# Viewport
c = c.replace(b"2160, \"height\": 3400", b"1200, \"height\": 1800")
c = c.replace(b"width:2160px", b"width:1200px")

# Body padding
c = c.replace(b"padding:18px}", b"padding:24px}")

# Card
c = c.replace(b"padding:14px;border:1px", b"padding:20px;border:1px")
c = c.replace(b"margin-bottom:10px}", b"margin-bottom:18px}")

# Card title
c = c.replace(b"font-size:12px;font-weight:700", b"font-size:16px;font-weight:700")

# P-title/sub
c = c.replace(b"font-size:18px;font-weight:bold;color:#fff", b"font-size:24px;font-weight:bold;color:#fff")
c = c.replace(b"font-size:10px;color:#666;margin-top:2px", b"font-size:14px;color:#666;margin-top:3px")

# Rank
c = c.replace(b"font-size:11px;font-weight:bold", b"font-size:15px;font-weight:bold")
c = c.replace(b"font-size:20px;font-weight:bold", b"font-size:28px;font-weight:bold")

# Donut
c = c.replace(b"width:80px;height:80px", b"width:110px;height:110px")
c = c.replace(b"width:52px;height:52px", b"width:72px;height:72px")
c = c.replace(b"font-size:15px;font-weight", b"font-size:20px;font-weight")
c = c.replace(b"font-size:10px;color:#888", b"font-size:14px;color:#888")

# Mode items
c = c.replace(b"font-size:11px;margin-bottom:4px", b"font-size:15px;margin-bottom:6px")
c = c.replace(b"width:6px;height:6px", b"width:8px;height:8px")

# WR
c = c.replace(b"font-size:28px;font-weight:bold;color:#FFC000", b"font-size:38px;font-weight:bold;color:#FFC000")
c = c.replace(b"font-size:10px;color:#666}", b"font-size:14px;color:#666}")

# Char row
c = c.replace(b"gap:10px;padding:8px 0", b"gap:18px;padding:12px 0")
c = c.replace(b"width:38px;height:38px;border-radius", b"width:52px;height:52px;border-radius")
# char-avatar matching 38px
c = c.replace(b"width:38px;height:38px;border-radius:50%;display:none", b"width:52px;height:52px;border-radius:50%;display:none")
c = c.replace(b"font-size:12px;font-weight:bold", b"font-size:16px;font-weight:bold")
c = c.replace(b"font-size:10px;color:#666;margin-top:2px", b"font-size:14px;color:#666;margin-top:3px")
c = c.replace(b"font-size:10px;padding:2px 6px", b"font-size:14px;padding:3px 8px")

# Tech items
c = c.replace(b"font-size:11px;padding:2px 0", b"font-size:15px;padding:3px 0")

# Hbar
c = c.replace(b"margin-bottom:6px;font-size:11px", b"margin-bottom:8px;font-size:15px")
c = c.replace(b"height:5px;background:#1a1d26", b"height:10px;background:#1a1d26")

# VS cells
c = c.replace(b"gap:6px;font-size:11px;background:#131620;padding:8px", b"gap:8px;font-size:14px;background:#131620;padding:12px")
c = c.replace(b"width:22px;height:22px", b"width:32px;height:32px")
c = c.replace(b"width:30px;color:#fff;font-weight:bold;font-size:10px", b"width:40px;color:#fff;font-weight:bold;font-size:13px")
c = c.replace(b"height:4px;background:#1a1d26", b"height:8px;background:#1a1d26")
c = c.replace(b"width:36px;text-align:right;font-size:11px", b"width:40px;text-align:right;font-size:14px")
c = c.replace(b"font-size:9px}", b"font-size:13px}")

# Battle
c = c.replace(b"gap:8px;font-size:11px;padding:6px 0", b"gap:10px;font-size:14px;padding:8px 0")
c = c.replace(b"padding:1px 6px;border-radius:2px;font-weight:bold;font-size:9px", b"padding:2px 8px;border-radius:2px;font-weight:bold;font-size:12px")
c = c.replace(b"font-size:9px}", b"font-size:13px}")

# Footer
c = c.replace(b"font-size:10px;color:#444", b"font-size:14px;color:#444")

# Rank box padding
c = c.replace(b"padding:4px 12px;border-radius:4px", b"padding:6px 16px;border-radius:6px")

open("src/charts/dashboard_renderer.py", "wb").write(c)
ast.parse(c.decode())
print("Dashboard scaled OK")

# ----- CARD -----
c = open("src/charts/card_renderer.py", "rb").read()
# Viewport
c = c.replace(b"2160, \"height\": 2400", b"1200, \"height\": 1600")
c = c.replace(b"width=2160\"", b"width=1200\"")
c = c.replace(b"width:2160px", b"width:1200px")
c = c.replace(b"padding:18px}", b"padding:24px}")

# Card styling
c = c.replace(b"padding:16px 18px;border:1px solid #1a1d28;margin-bottom:10px", b"padding:20px 20px;border:1px solid #1a1d28;margin-bottom:18px")
c = c.replace(b"font-size:13px;font-weight:700", b"font-size:16px;font-weight:700")

# Col2
c = c.replace(b"grid-template-columns:1fr 1fr;gap:10px", b"grid-template-columns:1fr 1fr;gap:18px")

# Header
c = c.replace(b"font-size:22px;font-weight:bold;color:#fff", b"font-size:28px;font-weight:bold;color:#fff")
c = c.replace(b"font-size:12px;color:#777;margin-top:2px", b"font-size:16px;color:#777;margin-top:3px")

# Rank badges
c = c.replace(b"font-size:14px;font-weight:bold;color:#fff", b"font-size:18px;font-weight:bold;color:#fff")
c = c.replace(b"font-size:18px;font-weight:bold;color:#a78bfa", b"font-size:24px;font-weight:bold;color:#a78bfa")

# Tags
c = c.replace(b"font-size:12px;margin:3px", b"font-size:16px;margin:4px")

# Streak
c = c.replace(b"padding:12px 16px}", b"padding:16px 20px}")
c = c.replace(b"font-size:11px;color:#666", b"font-size:15px;color:#666")
c = c.replace(b"gap:16px;font-size:12px", b"gap:20px;font-size:16px")

# Gauge bars
c = c.replace(b"height:10px;border-radius:4px;overflow:hidden;margin-bottom:10px", b"height:12px;border-radius:4px;overflow:hidden;margin-bottom:12px")

# SA rows
c = c.replace(b"gap:4px 16px;font-size:12px", b"gap:6px 20px;font-size:16px")

# Stat rows
c = c.replace(b"gap:8px;font-size:12px;padding:3px 0", b"gap:10px;font-size:14px;padding:4px 0")
c = c.replace(b"width:80px;color:#aaa", b"width:100px;color:#aaa")
c = c.replace(b"width:56px;font-weight:600;color:#fff;text-align:right", b"width:60px;font-weight:600;color:#fff;text-align:right")
c = c.replace(b"width:92px;color:#666;font-size:11px;text-align:right", b"width:110px;color:#666;font-size:13px;text-align:right")
c = c.replace(b"width:60px;font-size:11px", b"width:70px;font-size:13px")

# VS rows
c = c.replace(b"gap:8px;font-size:12px;padding:4px 0", b"gap:10px;font-size:14px;padding:5px 0")
c = c.replace(b"width:65px;color:#fff;font-weight:bold", b"width:75px;color:#fff;font-weight:bold")
c = c.replace(b"height:5px;background:#1a1d28", b"height:8px;background:#1a1d28")
c = c.replace(b"width:44px;color:#fff;font-weight:600;text-align:right", b"width:50px;color:#fff;font-weight:600;text-align:right")
c = c.replace(b"width:38px;color:#666;font-size:11px", b"width:42px;color:#666;font-size:13px")

# Low sample
c = c.replace(b"font-size:11px;color:#555", b"font-size:14px;color:#555")

# Streak cell padding
c = c.replace(b"padding:12px 16px}", b"padding:16px 20px}")

open("src/charts/card_renderer.py", "wb").write(c)
ast.parse(c.decode())
print("Card scaled OK")

print("\nAll done - both renderers scaled to 1200px body")

