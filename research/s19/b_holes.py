#!/usr/bin/env python3
"""Holes in UI-path shots for any picture: the picture's rest rectangle is taken from the smallest-offset shot (columns/rows with
alpha > 0 in more than half the frame's extent); holes = alpha-0 pixels and near-black opaque pixels inside that rectangle.
Usage: b_holes.py <ui_path dir>  -> one line per offset: 'dx dy | angle | alpha0 inside | dark inside | inside px'"""
import sys, os, glob, numpy as np
from PIL import Image
d = sys.argv[1]; files = sorted(glob.glob(d + '/off_*.png'), key=lambda f: [float(v) for v in os.path.basename(f)[4:-4].replace('_then', '').split('_')])
if not files: print('no shots'); sys.exit(0)
def load(f): return np.array(Image.open(f).convert('RGBA'))
a0 = load(files[0]); al0 = a0[..., 3] > 0; H, W = al0.shape
cols = np.nonzero(al0.mean(0) > 0.5)[0]; rows = np.nonzero(al0.mean(1) > 0.5)[0]
X0, X1 = (cols.min(), cols.max() + 1) if len(cols) else (0, W); Y0, Y1 = (rows.min(), rows.max() + 1) if len(rows) else (0, H)
print(f'rect x {X0}-{X1} y {Y0}-{Y1} of {W}x{H}')
for f in files:
    a = load(f); name = os.path.basename(f)[4:-4].replace('_then', ''); dx, dy = map(float, name.split('_'))
    ang = f'{np.degrees(np.arctan(dx / 0.2)):.0f}/{np.degrees(np.arctan(dy / 0.2)):.0f}'
    al = a[Y0:Y1, X0:X1, 3]; z = (al == 0)
    # interior holes: alpha-0 components that do not touch the picture rectangle's border (those are the frame's own edge
    # uncovering beyond-frame space, which margin=picture leaves open on purpose)
    from scipy import ndimage
    lab, n = ndimage.label(z); border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    interior = z & ~np.isin(lab, list(border)) if border else z
    print(f'{dx} {dy} | {ang} | {int(interior.sum())} | {int(z.sum() - interior.sum())} | {al.size}')
