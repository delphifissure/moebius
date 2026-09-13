#!/usr/bin/env python3
"""Sprint 16 sheet: per porous scene, the truth-check overlay under the current law (left) and with the ceiling cut (right).
The check PNGs are two 800-px tiles (rest RGB | overlay); the overlay tile is taken. Usage: p_sheet.py out.png scenes..."""
import sys, os
from PIL import Image, ImageDraw
K = '/home/user/moebiusv2/harness/truthkit/out'
out = sys.argv[1]; scenes = sys.argv[2:]
NAMES = {'S7': 'S7 canopy (reference)', 'P1': 'P1 sparse canopy (300 discs)', 'P2': 'P2 dense canopy (1 800 discs)', 'P3': 'P3 fine leaves (3 600 discs, half radius)',
         'P4': 'P4 two crowns layered', 'P5': 'P5 picket fence', 'P6': 'P6 grille'}


def overlay(S, tag):
    p = f'{K}/{S}/check_app16plane{tag}.png'
    if not os.path.isfile(p): return None
    im = Image.open(p).convert('RGB'); W, H = im.size
    pad = (W - 1600) // 3   # pad + tile + pad + tile + pad
    return im.crop((2 * pad + 800, 0, 2 * pad + 1600, H))


tiles = []
for S in scenes:
    a, b = overlay(S, '_c'), overlay(S, '_ceil')
    if a is None and b is None: continue
    tiles.append((S, a, b))
if not tiles: sys.exit('nothing to draw')
tw, th = 800, tiles[0][1].size[1] if tiles[0][1] else tiles[0][2].size[1]
pad = 12; sh = Image.new('RGB', (2 * tw + 3 * pad, len(tiles) * (th + 26 + pad) + pad), (20, 20, 20)); d = ImageDraw.Draw(sh)
y = pad
for S, a, b in tiles:
    d.text((pad, y), f'{NAMES.get(S, S)} — current law (left) | with the ceiling cut (right); green both, orange app only, blue truth only', fill=(235, 235, 235))
    y += 22
    if a: sh.paste(a, (pad, y))
    if b: sh.paste(b, (2 * pad + tw, y))
    y += th + pad + 4
sh.save(out); print('wrote', out, sh.size)
