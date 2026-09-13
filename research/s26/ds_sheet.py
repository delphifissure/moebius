#!/usr/bin/env python3
"""Sprint 18 sheets: per scene one row per picture (peel1, bg): the picture, the truth hidden depth, the plane law, and
each model's aligned depth on the hidden set, plus |error| maps on a common metre scale (0..outer/4 clipped).
  python3 ds_sheet.py S15 S2 ... -> out/sheet_<S>.png
"""
import sys, os, json, glob
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, '/home/user/moebiusv2/harness/truthkit'); from tk import app_z_of_d
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out'); PROBE = '/home/user/moebiusv2/harness/shots/a257probe'
scores = json.load(open(f'{OUT}/scores.json'))
MODELS = sorted({os.path.basename(f)[:-len('_peel1_aligned.npy')] for f in glob.glob(f'{OUT}/*/*_peel1_aligned.npy')}, key=lambda m: (m != 'da3', m != 'moge3', m))

def cmap(v, lo, hi):
    """3-stop map: blue = near, green = middle, red = far; nan = dark grey."""
    t = np.clip((v - lo) / max(1e-9, hi - lo), 0, 1); bad = ~np.isfinite(v)
    r = np.clip(1.5 - np.abs(4 * t - 3), 0, 1); g = np.clip(1.5 - np.abs(4 * t - 2), 0, 1); b = np.clip(1.5 - np.abs(4 * t - 1), 0, 1)
    im = (np.stack([r, g, b], -1) * 255).astype(np.uint8); im[bad] = 40; return im

def errmap(e, scale):
    t = np.clip(np.abs(e) / scale, 0, 1); bad = ~np.isfinite(e)
    im = (np.stack([t, 1 - t, np.zeros_like(t)], -1) * 255).astype(np.uint8); im[bad] = 40; return im

for S in sys.argv[1:]:
    t = np.load(f'{OUT}/{S}/truth.npz'); pw, ph = int(t['pw']), int(t['ph']); R = scores[S]; outer = R['outer']
    pd = R.get('plane', {}).get('probe'); d_pl = None
    if pd:
        meta = json.load(open(f'{PROBE}/{pd}/meta.json')); pf = np.fromfile(f'{PROBE}/{pd}/plateF.f32', np.float32).reshape(ph, pw)[::-1]
        d_pl = -app_z_of_d(pf, meta['pn'], meta['outer'], meta['inner'])
    rows = []
    for pic in ('peel1', 'bg'):
        mk = t['m_' + pic]; dk = t['d_' + pic]
        if mk.sum() == 0: continue
        fin = np.isfinite(dk) & mk; lo = float(np.percentile(dk[fin], 1)); hi = float(np.percentile(dk[fin], 99)) if fin.any() else outer
        esc = max(1e-6, 0.25 * (hi - lo))
        tiles = [(np.array(Image.open(f'{OUT}/{S}/{pic}.png').convert('RGB')), f'{pic}: the completed-layer picture'),
                 (cmap(np.where(mk, dk, np.nan), lo, hi), f'truth hidden depth (blue {lo:.3f} .. red {hi:.3f} m)')]
        if d_pl is not None:
            e = R['plane'][pic]; tiles.append((cmap(np.where(mk, d_pl, np.nan), lo, hi), f'plane law  med {e["median_abs"]:.4f} p90 {e["p90_abs"]:.3f} m'))
            tiles.append((errmap(np.where(mk, d_pl - dk, np.nan), esc), f'|err| plane (0..{esc:.3f} m)'))
        for m in MODELS:
            p = f'{OUT}/{S}/{m}_{pic}_aligned.npy'
            if not os.path.exists(p): continue
            dp = np.load(p); e = R[m][pic]['hidden']; ec = R[m][pic]['hidden_clamped']
            tiles.append((cmap(np.where(mk, dp, np.nan), lo, hi), f'{m} ({R[m][pic]["space"]})  med {e["median_abs"]:.4f} / clamped {ec["median_abs"]:.4f} / inf {e["inf_frac"]:.2f}'))
            tiles.append((errmap(np.where(mk, dp - dk, np.nan), esc), f'|err| {m} (global fit)'))
            pl_ = f'{OUT}/{S}/{m}_{pic}_local.npy'
            if os.path.exists(pl_):
                dl = np.load(pl_); el = R[m][pic]['local']
                tiles.append((cmap(np.where(mk, dl, np.nan), lo, hi), f'{m} local fit ({el["components"]} comps)  med {el["median_abs"]:.4f}'))
        rows.append(tiles)
    Wt, Ht = pw // 2, ph // 2; pad = 6; ncol = max(len(r) for r in rows)
    sh = Image.new('RGB', (ncol * (Wt + pad) + pad, 30 + len(rows) * (Ht + 22 + pad)), (20, 20, 20)); d = ImageDraw.Draw(sh)
    d.text((pad, 6), f'{S}  depth stage on truth: hidden-layer depth from the completed picture (aligned on visible texels only) vs the plane law; scene depth {outer} m', fill=(255, 255, 255))
    for r, tiles in enumerate(rows):
        for c, (im, txt) in enumerate(tiles):
            x = pad + c * (Wt + pad); y = 30 + r * (Ht + 22 + pad)
            d.text((x, y), txt[:70], fill=(255, 230, 120)); sh.paste(Image.fromarray(im).resize((Wt, Ht), Image.NEAREST), (x, y + 14))
    sh.save(f'{OUT}/sheet_{S}.png'); print('wrote', f'{OUT}/sheet_{S}.png')
