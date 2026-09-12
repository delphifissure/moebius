#!/usr/bin/env python3
"""B sheets: per picture a row per arm — colour, the arm's depth map, and the UI-path shots at 0.1 m, 0.2 m, (0.301, 0.068) m."""
import os, sys
from PIL import Image, ImageDraw
R = '/home/user/moebiusv2'; U = f'{R}/harness/shots/ui_path'; B = f'{R}/harness/batchB'; OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad'
PICS = ['bristlecone', 'octopus', 'room', 'silverwarrior', 'starwatcher', 'vermeer']; ARMS = [('da3', 'DA3-Mono-Large 16-bit'), ('da3f', 'DA3 16-bit, floor forced'), ('repo8', "repo's 8-bit map"), ('repo8inv', "repo's 8-bit map, inverted (its convention was far = bright)"), ('da3sky', 'DA3 + sky at infinity')]
SH = ['0.1_0', '0.2_0', '0.301_0.068']; TW = 300
for P in PICS:
    rows = []
    for arm, lab in ARMS:
        d = f'{U}/ub_{P}_{arm}'
        if not os.path.isdir(d): continue
        tiles = []
        c = Image.open(f'{B}/{P}_color.png').convert('RGB'); th = int(c.size[1] * TW / c.size[0]); tiles.append(c.resize((TW, th)))
        dp = f'{B}/{P}_da3_16.png' if arm.startswith('da3') else f'{B}/{P}_{arm}.png'; dm = Image.open(dp); dm = dm.point(lambda v: v / 256) if dm.mode.startswith('I') else dm; tiles.append(dm.convert('L').resize((TW, th)).convert('RGB'))
        for s in SH:
            f = f'{d}/off_{s}.png'
            if os.path.exists(f): im = Image.open(f).convert('RGB'); tiles.append(im.resize((int(im.size[0] * th / im.size[1]), th)))
        rows.append((lab, tiles))
    if not rows: continue
    W = max(sum(t.size[0] for t in tiles) + 4 * len(tiles) for _, tiles in rows); H = sum(max(t.size[1] for t in tiles) + 22 for _, tiles in rows) + 4
    sheet = Image.new('RGB', (W, H), (18, 18, 18)); dr = ImageDraw.Draw(sheet); y = 4
    for lab, tiles in rows:
        dr.text((4, y), f'{P} — {lab}   [colour | depth | 0.1 m | 0.2 m | 0.301/0.068 m]', fill=(255, 255, 255)); y += 16; x = 0
        for t in tiles: sheet.paste(t, (x, y)); x += t.size[0] + 4
        y += max(t.size[1] for t in tiles) + 6
    sheet.save(f'{OUT}/b_{P}_sheet.png'); print(P, sheet.size)
