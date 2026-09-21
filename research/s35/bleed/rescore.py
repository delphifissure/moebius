"""S43 / Sprint 23: restate the S39, S40 and S42 tables under the new score.

S38 found the metre score is not comparable across scenes because the depth law's gain varies twentyfold across the kit. S42
caught it doing real damage: L1's band reads 0.0112 m / 0.0198 d and L6's reads 0.0154 m / 0.0106 d, so the two units rank
those scenes in OPPOSITE orders. Every table this project has written is in metres.

This restates the field-scene comparison using `tk.depth_scores`, the single definition added in Sprint 23, and adds the three
things the harness never had: a do-nothing baseline, the accuracy/completeness split, and the exterior column.

  rescore.py [--class thing|bg|all]
"""
import sys, os, json, argparse
import numpy as np
sys.path.insert(0, '/home/user/moebiusv2/harness/truthkit')
from tk import app_norm_depth, depth_scores, commit_scores

ap = argparse.ArgumentParser(); ap.add_argument('--cls', default='thing', choices=['thing', 'bg', 'all'])
A = ap.parse_args()
K = '/home/user/moebiusv2/harness/truthkit/out'; P0 = '/home/user/moebiusv2/harness/shots/a257probe'
SPEC = [('L1', 'L1_16plane', 's35_RWCPh'), ('L5', 'L5_16plane', 's35_RWCPh_heads'), ('L6', 'L6_16plane', 's35_RWCPh_click'),
        ('L7', 'L7_16plane', 's35_click'), ('L8', 'L8_16plane', 's35_click'), ('L9', 'L9_16plane', 's35_click')]
CLS = {'thing': (3,), 'bg': (2,), 'all': (2, 3, 4, 5)}[A.cls]

rows = []
for S, pd, ad in SPEC:
    P = f'{P0}/{pd}'; D = f'{P}/{ad}'
    meta = json.load(open(f'{P}/meta.json')); pw, ph = meta['pw'], meta['ph']; outer, pn, inner = meta['outer'], meta['pn'], meta['inner']
    band = np.fromfile(f'{P}/disocc.u8', np.uint8).reshape(ph, pw) > 0; vis = ~band
    dQ = np.fromfile(f'{P}/dQ.f32', np.float32).reshape(ph, pw).astype(np.float64)
    ff = np.fromfile(f'{D}/farField_stop.f32', np.float32).reshape(ph, pw).astype(np.float64)
    step = float(np.median(np.diff(np.unique(dQ[vis])[:200])))
    mp = f'{P}/amodal_occ_grey.npy'
    md = np.load(mp).astype(np.float64) if os.path.exists(mp) else None
    z = np.load(f'{K}/{S}_env45/scope_gt.npz'); cls = z['cls']; w = z['w_disp']; dep = z['depth']
    H, W, _ = cls.shape; y0 = (H - ph) // 2; x0 = (W - pw) // 2
    cls = cls[y0:y0+ph, x0:x0+pw]; w = w[y0:y0+ph, x0:x0+pw]; dep = dep[y0:y0+ph, x0:x0+pw]
    v_ = (cls >= 2) & (cls <= 5) & (w > 0); has = v_.any(-1); kk = np.argmax(v_, -1)
    dT = np.take_along_axis(dep, kk[..., None], -1)[..., 0]; dT = np.where(has & np.isfinite(dT), dT, np.nan)
    cT = np.take_along_axis(cls, kk[..., None], -1)[..., 0]
    dTn = np.where(np.isfinite(dT), app_norm_depth(-dT, pn, outer, inner), np.nan)
    m = band & np.isfinite(dTn) & np.isin(cT, CLS)
    r = {'scene': S, 'n': int(m.sum()), 'step': step}
    # How much is there to get right? Counterfactual Depth filtered its test set to cases whose depth changed by at least
    # 0.25 m on removal, because "slight changes in depth can hardly be examined the performance". Where the hidden surface
    # sits at nearly the occluder's own depth, doing nothing is already correct and the comparison is uninformative.
    # NOTE the identity: doing nothing means predicting dQ, so the do-nothing error IS the median depth change there is to
    # recover. The baseline column and the "how much is there to get right" column are the same column.
    r['arm'] = depth_scores(ff, dTn, m, meta, step)
    r['none'] = depth_scores(dQ, dTn, m, meta, step)
    r['armC'] = commit_scores(ff, dQ, dTn, m, meta, step)
    if md is not None:
        r['model'] = depth_scores(md, dTn, m, meta, step)
        r['modelC'] = commit_scores(md, dQ, dTn, m, meta, step)
    rows.append(r)

W1 = '{:5s} {:>8s} | {:>9s} {:>9s} {:>9s} | {:>8s} {:>8s} {:>8s} | {:>7s} {:>7s} {:>7s}'
print(f'class = {A.cls}.  d = the app\'s normalised depth (PRIMARY).  m = metres behind the window (legacy).  '
      f'delta1 = fraction within a 1.25 ratio of camera distance.')
print(W1.format('scene', 'n', 'arm d', 'model d', 'none d', 'arm m', 'model m', 'none m', 'arm d1', 'mdl d1', 'none d1'))
print('  ("none" = keep the occluder\'s own plate depth. Its error is identically the median depth change there is to recover,'
      '\n   so where it is small there is little to get right and the other columns carry little information.)')
g = lambda r, k, f: (f'{r[k][f]:9.4f}' if k in r and f in r[k] else '        -')
g2 = lambda r, k, f: (f'{r[k][f]:8.4f}' if k in r and f in r[k] else '       -')
g3 = lambda r, k, f: (f'{r[k][f]:7.3f}' if k in r and f in r[k] else '      -')
for r in rows:
    print(W1.format(r['scene'], str(r['n']), g(r, 'arm', 'd_med').strip(), g(r, 'model', 'd_med').strip(), g(r, 'none', 'd_med').strip(),
                    g2(r, 'arm', 'm_med').strip(), g2(r, 'model', 'm_med').strip(), g2(r, 'none', 'm_med').strip(),
                    g3(r, 'arm', 'd1').strip(), g3(r, 'model', 'd1').strip(), g3(r, 'none', 'd1').strip()))
print()
print('{:5s} | {:>10s} {:>10s} | {:>10s} {:>10s} | {:>9s} {:>9s}'.format(
    'scene', 'arm compl', 'mdl compl', 'arm acc d', 'mdl acc d', 'arm steps', 'mdl steps'))
for r in rows:
    f = lambda k, fld, w=10, p=4: (f'{r[k][fld]:{w}.{p}f}' if k in r and fld in r[k] else ' ' * (w - 1) + '-')
    print(f"{r['scene']:5s} | {f('armC','commit_completeness')} {f('modelC','commit_completeness')} | "
          f"{f('armC','commit_d_med')} {f('modelC','commit_d_med')} | {f('arm','steps_med',9,1)} {f('model','steps_med',9,1)}")
print()
for nm, k in (('arm', 'arm'), ('model', 'model'), ('do nothing', 'none')):
    v = [r[k]['d_med'] for r in rows if k in r and 'd_med' in r[k]]
    vm = [r[k]['m_med'] for r in rows if k in r and 'm_med' in r[k]]
    if not v: continue
    # Report WORST CASE, not the spread ratio S39/S40 used: when the best case sits at the 16-bit quantisation floor the
    # ratio is an artefact of dividing by nothing (the arm's bg spread reads 8600x in d and 3.7e7x in m for that reason).
    print(f'{nm:>11s}: worst {max(v):.4f} d / {max(vm):.4f} m   best {min(v):.4f} d   median {sorted(v)[len(v)//2]:.4f} d')
