#!/usr/bin/env python3
"""Live-pass preview sheets: per picture one row per arm (cur = panel defaults, cand = + ceiling cut + line despeckle,
trade = cand + seams all + margin window) with the UI-path shots at the five poses. Usage: live_sheets.py [outdir]"""
import os, sys
from PIL import Image, ImageDraw
R = '/home/user/moebiusv2'; U = f'{R}/harness/shots/ui_path'
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad'
PICS = ['troll', 'bristlecone', 'octopus', 'room', 'silverwarrior', 'starwatcher', 'vermeer']
ARMS = [('cur', 'current defaults (plane, wash, picture margin, tier 35, stretched seams)'), ('cand', 'recommended: + ceiling cut + line-aware despeckle'),
        ('trade', 'trade arm: recommended + seams "all" + margin window')]
SH = [('0.05_0', '14°'), ('0.1_0', '27°'), ('0.2_0', '45°'), ('0.26_0.088', '52°/24°'), ('0.301_0.068', '56°/19°')]; TH = 300
for P in PICS:
    rows = []
    for arm, lab in ARMS:
        d = f'{U}/ul_{P}_{arm}'
        if not os.path.isdir(d): continue
        tiles = []
        for s, a in SH:
            f = f'{d}/off_{s}.png'
            if os.path.exists(f): im = Image.open(f).convert('RGB'); tiles.append((im.resize((int(im.size[0] * TH / im.size[1]), TH)), a))
        if tiles: rows.append((lab, tiles))
    if not rows: continue
    W = max(sum(t.size[0] for t, _ in tiles) + 4 * len(tiles) for _, tiles in rows); H = sum(TH + 34 for _ in rows) + 4
    sheet = Image.new('RGB', (W, H), (18, 18, 18)); dr = ImageDraw.Draw(sheet); y = 4
    for lab, tiles in rows:
        dr.text((4, y), f'{P} — {lab}', fill=(255, 255, 255)); y += 16; x = 0
        for t, a in tiles:
            sheet.paste(t, (x, y)); dr.text((x + 4, y + TH + 2), a, fill=(200, 200, 200)); x += t.size[0] + 4
        y += TH + 18
    sheet.save(f'{OUT}/live_{P}_sheet.png'); print(P, sheet.size, len(rows), 'rows')
