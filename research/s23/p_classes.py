#!/usr/bin/env python3
"""Sprint 16: the porous scenes' band errors by REGION. From the probe dump (disocc, dQ) and the env45 truth (as check_app_band
reads it): app-only (over-claim) and truth-only (miss) texels split into: ABOVE the occluder's top row, INSIDE the occluder's
bounding box (between the leaves / slats), BELOW it, and elsewhere. The occluder = the near texels of the rest depth (the
things: label 2 in the truth's rest layer). Usage: p_classes.py <scene> [tag]"""
import sys, os, json, numpy as np
sys.path.insert(0, '/home/user/moebiusv2/harness/truthkit')
S = sys.argv[1]; tag = sys.argv[2] if len(sys.argv) > 2 else '_c'; K = '/home/user/moebiusv2/harness/truthkit/out'; A = '/home/user/moebiusv2/harness/shots/a257probe'
suf = 'planesky' if S in ('S15', 'S32') else 'plane'; d = f'{A}/{S}_16{suf}{tag}'
m = json.load(open(d + '/meta.json')); pw, ph = m['pw'], m['ph']
dis = np.fromfile(d + '/disocc.u8', np.uint8).reshape(ph, pw) > 0
gt = np.load(f'{K}/{S}_env45/scope_gt.npz'); cls = gt['cls']; w = gt['w_disp'].astype(np.float32); H, W, Kk = cls.shape; y0 = (H - ph) // 2; x0 = (W - pw) // 2
cls_c = cls[y0:y0 + ph, x0:x0 + pw]; w_c = w[y0:y0 + ph, x0:x0 + pw]
hidden = ((cls_c >= 2) & (cls_c <= 5) & (w_c > 0)).any(-1)
lab = gt['label']; lab_c = lab[y0:y0 + ph, x0:x0 + pw]; thing = (lab_c[..., 0] == 2) if lab_c.ndim == 3 else (lab_c == 2)
ys, xs = np.nonzero(thing); top, bot, left, right = ys.min(), ys.max(), xs.min(), xs.max()
region = np.full((ph, pw), 3, np.uint8)   # 3 elsewhere
region[:top, :] = 0                       # above the occluder
region[top:bot + 1, left:right + 1] = 1   # inside its bounding box
region[bot + 1:, left:right + 1] = 2      # below it
fp = dis & ~hidden; fn = hidden & ~dis; tp = dis & hidden
names = ['above', 'inside bbox', 'below', 'elsewhere']
print(f'{S}{tag}: band {int(dis.sum())}, truth {int(hidden.sum())}, P {tp.sum() / max(1, dis.sum()):.3f}, R {tp.sum() / max(1, hidden.sum()):.3f}; occluder bbox rows {top}-{bot}, cols {left}-{right}')
print(f"{'region':12s} {'app-only':>9s} {'% of FP':>8s} {'truth-only':>11s} {'% of FN':>8s} {'both':>7s}")
for r, n in enumerate(names):
    a = int((fp & (region == r)).sum()); b = int((fn & (region == r)).sum()); c = int((tp & (region == r)).sum())
    print(f'{n:12s} {a:9d} {100 * a / max(1, fp.sum()):8.1f} {b:11d} {100 * b / max(1, fn.sum()):8.1f} {c:7d}')
