#!/usr/bin/env python3
"""Criterion 1 per model: from the raw float output, converted to inverse depth (the app's disparity), (a) the sub-8-bit part's
sigma and lag-1 autocorrelation along rows (0 = white noise, ~1 = smooth ramps), (b) the 5-texel along-row affine residual in
units of the map's own 8-bit step (relative to the map's inverse-depth range), (c) share of texel triples whose second
difference exceeds one 8-bit step. Also the sign check against the DA2 map (correlation of inverse depth with depth16.png).
Usage: noise_stats.py <out_dir> <model> [<model> ...]"""
import sys, json, numpy as np
from PIL import Image
out = sys.argv[1]; ref = np.array(Image.open('/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad/depth16_pushed.png')).astype(float)
log = json.load(open(f'{out}/log.json'))
print('| model | kind | s (CPU) | corr with DA2 map | sub-8-bit sigma (steps) | lag-1 autocorr | affine residual median / p90 (8-bit steps) | triples > 1 step |'); print('|---|---|---|---|---|---|---|---|')
for m in sys.argv[2:]:
    if m == 'da2large': a = ref.copy(); kind = 'inverse'
    else:
        try: a = np.load(f'{out}/{m}.npy').astype(np.float64)
        except FileNotFoundError: print(f'| {m} | not run | | | | | | |'); continue
        kind = log.get(m, {}).get('kind', 'depth')
    valid = np.isfinite(a) & ((a > 0) if kind == 'depth' else True)
    inv = np.where(valid, 1.0 / np.maximum(a, 1e-9), np.nan) if kind == 'depth' else np.where(valid, a, np.nan)
    lo, hi = np.nanmin(inv), np.nanmax(inv); u = (inv - lo) / (hi - lo)            # 0..1, bright = near
    corr = np.corrcoef(np.nan_to_num(u).ravel(), ref.ravel())[0, 1]
    step = 1 / 255.0; frac = u / step - np.round(u / step)                          # sub-8-bit part in steps
    f0, f1 = frac[:, :-1], frac[:, 1:]; ok = np.isfinite(f0) & np.isfinite(f1); ac = np.corrcoef(f0[ok], f1[ok])[0, 1]
    x = np.arange(5) - 2; A = np.vstack([x, np.ones(5)]).T; P = A @ np.linalg.pinv(A)
    win = np.lib.stride_tricks.sliding_window_view(u, 5, axis=1); res = win - win @ P.T; rms = np.sqrt((res ** 2).mean(-1)) / step; rms = rms[np.isfinite(rms)]
    sd = np.abs(u[:, 2:] - 2 * u[:, 1:-1] + u[:, :-2]) / step; sd = sd[np.isfinite(sd)]
    print(f"| {m} | {kind} | {log.get(m,{}).get('seconds','?')} | {corr:.3f} | {np.nanstd(frac):.3f} | {ac:.3f} | {np.median(rms):.3f} / {np.percentile(rms,90):.3f} | {np.mean(sd>1):.4f} |")
