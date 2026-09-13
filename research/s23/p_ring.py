#!/usr/bin/env python3
"""Sprint 16: the over-claim by chessboard distance to the nearest occluder texel — the one-texel ring (distance 1) against the
between-leaf remainder (distance >= 2). Usage: p_ring.py <scene> <tag> [...pairs]"""
import sys, json, numpy as np
from scipy import ndimage
K = '/home/user/moebiusv2/harness/truthkit/out'; A = '/home/user/moebiusv2/harness/shots/a257probe'
args = sys.argv[1:]
for S, tag in zip(args[::2], args[1::2]):
    d = f'{A}/{S}_16plane{tag}'; m = json.load(open(d + '/meta.json')); pw, ph = m['pw'], m['ph']
    dis = np.fromfile(d + '/disocc.u8', np.uint8).reshape(ph, pw) > 0
    gt = np.load(f'{K}/{S}_env45/scope_gt.npz'); cls = gt['cls']; w = gt['w_disp'].astype(np.float32); H, W, _ = cls.shape; y0 = (H - ph) // 2; x0 = (W - pw) // 2
    hid = ((cls[y0:y0 + ph, x0:x0 + pw] >= 2) & (cls[y0:y0 + ph, x0:x0 + pw] <= 5) & (w[y0:y0 + ph, x0:x0 + pw] > 0)).any(-1)
    lab = gt['label'][y0:y0 + ph, x0:x0 + pw]; thing = (lab[..., 0] == 2) if lab.ndim == 3 else (lab == 2)
    ys, xs = np.nonzero(thing); top = ys.min()
    fp = dis & ~hid; dt = ndimage.distance_transform_cdt(~thing, metric='chessboard'); ring = dt == 1
    below_top = np.zeros_like(dis); below_top[top:, :] = True
    fpb = fp & below_top   # not above the occluder
    h = np.bincount(np.minimum(dt[fpb], 12).astype(int), minlength=13)
    print(f"{S}{tag}: band {int(dis.sum()):,} truth {int(hid.sum()):,} | occluder px {int(thing.sum()):,} ring px {int(ring.sum()):,} (ring/area {ring.sum() / thing.sum():.2f}) | "
          f"over-claim above top row {int((fp & ~below_top).sum()):,}; at/below: on ring {int((fpb & ring).sum()):,} ({100 * (fpb & ring).sum() / max(1, ring.sum()):.0f} % of ring), "
          f"dist 2 {int((fpb & (dt == 2)).sum()):,}, dist >= 3 {int((fpb & (dt >= 3)).sum()):,} | histogram 0..12+ {h.tolist()} | hidden on occluder texels {int((hid & thing).sum()):,} of {int(hid.sum()):,}")
