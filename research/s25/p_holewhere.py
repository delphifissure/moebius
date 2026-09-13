#!/usr/bin/env python3
"""Where are the interior holes? Per UI-path shot: the interior alpha-0 components (not touching the picture rectangle's
border), largest first: area, bounding box (relative to the picture rectangle), distance from the rectangle's right/left/
top/bottom edges in px, and whether the component touches the rectangle's border strip within 2 % of the width.
Usage: p_holewhere.py <ui_path dir> [offset names ...]"""
import sys, os, glob, numpy as np
from PIL import Image
from scipy import ndimage
d = sys.argv[1]; want = sys.argv[2:]
files = sorted(glob.glob(d + '/off_*.png'), key=lambda f: [float(v) for v in os.path.basename(f)[4:-4].replace('_then', '').split('_')])
a0 = np.array(Image.open(files[0]).convert('RGBA')); al0 = a0[..., 3] > 0; H, W = al0.shape
cols = np.nonzero(al0.mean(0) > 0.5)[0]; rows = np.nonzero(al0.mean(1) > 0.5)[0]
X0, X1 = (cols.min(), cols.max() + 1) if len(cols) else (0, W); Y0, Y1 = (rows.min(), rows.max() + 1) if len(rows) else (0, H)
print(f'{os.path.basename(d)}: rect x {X0}-{X1} y {Y0}-{Y1} ({X1 - X0}x{Y1 - Y0})')
for f in files:
    name = os.path.basename(f)[4:-4]
    if want and name not in want: continue
    a = np.array(Image.open(f).convert('RGBA')); al = a[Y0:Y1, X0:X1, 3]; z = al == 0
    lab, n = ndimage.label(z); border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    sizes = ndimage.sum(z, lab, range(1, n + 1)); order = np.argsort(-sizes)
    print(f'  {name}: {n} alpha-0 components, {len(border)} touch the border; interior total {int(sum(s for k, s in enumerate(sizes) if (k + 1) not in border))}')
    shown = 0
    for k in order:
        if (k + 1) in border or shown >= 6: continue
        ys, xs = np.nonzero(lab == k + 1); rw = X1 - X0; rh = Y1 - Y0
        print(f'    area {int(sizes[k]):5d}  bbox x {xs.min()}-{xs.max()} y {ys.min()}-{ys.max()}  | to right edge {rw - 1 - xs.max()} px, left {xs.min()}, bottom {rh - 1 - ys.max()}, top {ys.min()}  ({100 * xs.mean() / rw:.0f} % across, {100 * ys.mean() / rh:.0f} % down)')
        shown += 1
