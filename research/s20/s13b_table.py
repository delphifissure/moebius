#!/usr/bin/env python3
"""S13b: interior holes per offset, base vs the changed option (_then shots), for each s13b_<pic>_<opt> UI-path dir."""
import os, glob, numpy as np
from PIL import Image
from scipy import ndimage
U = '/home/user/moebiusv2/harness/shots/ui_path'
def holes(files):
    if not files: return {}
    a0 = np.array(Image.open(files[0]).convert('RGBA')); al0 = a0[..., 3] > 0; H, W = al0.shape
    cols = np.nonzero(al0.mean(0) > 0.5)[0]; rows = np.nonzero(al0.mean(1) > 0.5)[0]
    X0, X1 = (cols.min(), cols.max() + 1) if len(cols) else (0, W); Y0, Y1 = (rows.min(), rows.max() + 1) if len(rows) else (0, H)
    out = {}
    for f in files:
        name = os.path.basename(f)[4:-4].replace('_then', ''); a = np.array(Image.open(f).convert('RGBA')); z = a[Y0:Y1, X0:X1, 3] == 0
        lab, n = ndimage.label(z); border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
        interior = z & ~np.isin(lab, list(border)) if border else z; out[name] = (int(interior.sum()), int(z.sum() - interior.sum()))
    return out
print('| picture | option | offset (m) | interior holes base → option | edge-connected alpha 0 base → option |'); print('|---|---|---|---|---|')
for d in sorted(glob.glob(U + '/s13b_*')):
    tag = os.path.basename(d)[5:]; pic, opt = tag.split('_', 1)
    base = sorted(f for f in glob.glob(d + '/off_*.png') if not f.endswith('_then.png')); then = sorted(glob.glob(d + '/off_*_then.png'))
    hb, ht = holes(base), holes(then)
    for k in sorted(hb, key=lambda s: [float(v) for v in s.split('_')]):
        b = hb[k]; t = ht.get(k, ('-', '-')); print(f'| {pic} | {opt} | {k.replace("_", ", ")} | {b[0]} → {t[0]} | {b[1]} → {t[1]} |')
