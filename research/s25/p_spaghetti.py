#!/usr/bin/env python3
"""Sprint 17a: count the magenta check-view pixels (plate fragments stretched past the fold) in UI-path shots, inside the
picture rectangle (found as b_holes finds it). Usage: p_spaghetti.py <ui_path dir>"""
import sys, os, glob, numpy as np
from PIL import Image
d = sys.argv[1]; files = sorted(glob.glob(d + '/off_*.png'), key=lambda f: [float(v) for v in os.path.basename(f)[4:-4].replace('_then', '').split('_')])
if not files: print('no shots'); sys.exit(0)
a0 = np.array(Image.open(files[0]).convert('RGBA')); al0 = a0[..., 3] > 0; H, W = al0.shape
cols = np.nonzero(al0.mean(0) > 0.5)[0]; rows = np.nonzero(al0.mean(1) > 0.5)[0]
X0, X1 = (cols.min(), cols.max() + 1) if len(cols) else (0, W); Y0, Y1 = (rows.min(), rows.max() + 1) if len(rows) else (0, H)
for f in files:
    a = np.array(Image.open(f).convert('RGBA'))[Y0:Y1, X0:X1].astype(int); name = os.path.basename(f)[4:-4]
    mag = (a[..., 3] > 0) & (a[..., 0] > 200) & (a[..., 2] > 200) & (a[..., 1] < 60)
    print(f'{name} | magenta {int(mag.sum())} of {mag.size} ({100 * mag.sum() / mag.size:.2f} %)')
