#!/usr/bin/env python3
"""Sprint 16: one markdown table for the porous set (and S7 for reference): band / truth / P / R / depth (median, p90) /
layer 2 / region split of the over-claim (above the occluder, inside its bbox, below, elsewhere) — per scene and arm.
Usage: p_table.py [scenes...] ; arms _c (current law) and _ceil (ceiling cut); missing files are skipped."""
import sys, os, json, numpy as np
K = '/home/user/moebiusv2/harness/truthkit/out'; A = '/home/user/moebiusv2/harness/shots/a257probe'
scenes = sys.argv[1:] or ['S7', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6']
NAMES = {'S7': 'S7 canopy (reference)', 'P1': 'P1 sparse canopy (300 discs)', 'P2': 'P2 dense canopy (1 800)', 'P3': 'P3 fine leaves (3 600, r/2)',
         'P4': 'P4 two crowns layered', 'P5': 'P5 picket fence', 'P6': 'P6 grille'}


def regions(S, tag):
    d = f'{A}/{S}_16plane{tag}'
    if not os.path.isfile(d + '/disocc.u8'): return None
    m = json.load(open(d + '/meta.json')); pw, ph = m['pw'], m['ph']
    dis = np.fromfile(d + '/disocc.u8', np.uint8).reshape(ph, pw) > 0
    gt = np.load(f'{K}/{S}_env45/scope_gt.npz')
    if 'label' not in gt.files: return None
    cls = gt['cls']; w = gt['w_disp'].astype(np.float32); H, W, _ = cls.shape; y0 = (H - ph) // 2; x0 = (W - pw) // 2
    cls_c = cls[y0:y0 + ph, x0:x0 + pw]; w_c = w[y0:y0 + ph, x0:x0 + pw]
    hidden = ((cls_c >= 2) & (cls_c <= 5) & (w_c > 0)).any(-1)
    lab = gt['label'][y0:y0 + ph, x0:x0 + pw]; thing = (lab[..., 0] == 2) if lab.ndim == 3 else (lab == 2)
    ys, xs = np.nonzero(thing); top, bot, left, right = ys.min(), ys.max(), xs.min(), xs.max()
    region = np.full((ph, pw), 3, np.uint8); region[:top, :] = 0; region[top:bot + 1, left:right + 1] = 1; region[bot + 1:, left:right + 1] = 2
    fp = dis & ~hidden; fn = hidden & ~dis; tp = dis & hidden
    # synthesised colour among the over-claim above the occluder (the wash the viewer would see)
    paint = None
    if os.path.isfile(d + '/platePaint.u8'):
        paint = np.fromfile(d + '/platePaint.u8', np.uint8).reshape(ph, pw) > 0
    r = {'band': int(dis.sum()), 'truth': int(hidden.sum()), 'P': tp.sum() / max(1, dis.sum()), 'R': tp.sum() / max(1, hidden.sum()),
         'fp': [int((fp & (region == k)).sum()) for k in range(4)], 'fn': [int((fn & (region == k)).sum()) for k in range(4)],
         'tp': [int((tp & (region == k)).sum()) for k in range(4)], 'bbox': (int(top), int(bot), int(left), int(right)),
         'paint_above': int((fp & (region == 0) & paint).sum()) if paint is not None else None,
         'thing_px': int(thing.sum())}
    return r


rows = []
for S in scenes:
    for tag in ['_c', '_ceil']:
        jp = f'{K}/{S}/check_app16plane{tag}.json'
        if not os.path.isfile(jp): continue
        j = json.load(open(jp)); r = regions(S, tag)
        if r is None: continue
        bd = j['band_depth_err_m']; l2 = j['layer2']
        rows.append((S, tag, j, r, bd, l2))

print('| scene | arm | band | truth | P | R | depth median / p90 m | layer 2 app (kit) | over-claim above | inside bbox | below | elsewhere | miss inside bbox |')
print('|---|---|---:|---:|---:|---:|---|---|---:|---:|---:|---:|---:|')
for S, tag, j, r, bd, l2 in rows:
    fp = r['fp']; tot = max(1, sum(fp))
    print(f"| {NAMES.get(S, S)} | {'current' if tag == '_c' else 'ceiling cut'} | {r['band']:,} | {r['truth']:,} | {r['P']:.3f} | {r['R']:.3f} | "
          f"{bd['median_abs']:.3f} / {bd['p90_abs']:.3f} | {l2['app_px']:,} ({l2['kit_px']:,}) | {fp[0]:,} ({100 * fp[0] / tot:.0f} %) | "
          f"{fp[1]:,} ({100 * fp[1] / tot:.0f} %) | {fp[2]:,} | {fp[3]:,} | {r['fn'][1]:,} of {r['fn'][1] + r['tp'][1]:,} |")
print()
for S, tag, j, r, bd, l2 in rows:
    print(f"{S}{tag}: occluder bbox rows {r['bbox'][0]}-{r['bbox'][1]} cols {r['bbox'][2]}-{r['bbox'][3]}, occluder px {r['thing_px']:,}; "
          f"tp by region {r['tp']}; fn by region {r['fn']}; synthesised colour among over-claim above: {r['paint_above']}; "
          f"clones {j.get('clone_count_final')}; carriers {j.get('carrier_px'):,}; recall_thing {j.get('recall_thing'):.3f} recall_side {j.get('recall_side'):.3f}")
