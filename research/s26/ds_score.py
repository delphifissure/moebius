#!/usr/bin/env python3
"""Sprint 18 step 3: align each model's output to the scene on the VISIBLE texels only and score the HIDDEN texels
against the truth, next to the plane law scored on the same texels.

Protocol (per scene, per picture peel1 / bg, per model):
  fit   : on m_fit (texels whose colour is the source picture's and whose depth is known and finite), a robust
          affine fit between the model output and the true visible depth, in three spaces — disparity affine
          (1/d = a/m + b), depth affine (d = a m + b), depth scale (d = a m); two rounds of 3xMAD trimming; the
          space with the smallest median |residual| on the visible texels is kept (chosen on visible data only)
  score : on the hidden set (m_peel1 with d_peel1, or m_bg with d_bg; finite truth), |d_pred - d_true| in metres:
          median, p90, mean signed; and the same after the ordering clamp d_pred >= d_vis (a hidden layer lies
          behind the visible surface at its own texel — a135)
  control: the model on the source picture 'rest', same fit, median |residual| on m_fit (can it read the scene at all)
  plane law: plateF.f32 from the newest current-law probe of the scene (priority _c, _ceil, base), in metres via
          app_z_of_d, on exactly the same hidden sets; and its coverage (fraction of the hidden set inside the band)
Writes out/scores.json and prints a table.
"""
import sys, os, json, glob
import numpy as np
sys.path.insert(0, '/home/user/moebiusv2/harness/truthkit'); from tk import app_z_of_d
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out'); PROBE = '/home/user/moebiusv2/harness/shots/a257probe'
MODELS = sorted({os.path.basename(f)[:-len('_peel1.npy')] for f in glob.glob(f'{OUT}/*/*_peel1.npy') if not f.endswith('_aligned.npy')}, key=lambda m: (m != 'da3', m != 'moge3', m))

def robust_fit(x, y):
    """y ~ a x + b with two rounds of 3xMAD trimming; returns a, b, median |res| on the kept set."""
    keep = np.isfinite(x) & np.isfinite(y)
    for _ in range(3):
        A = np.stack([x[keep], np.ones(keep.sum())], 1); a, b = np.linalg.lstsq(A, y[keep], rcond=None)[0]
        r = np.abs(a * x + b - y); mad = np.median(r[keep]) + 1e-12
        nk = keep & (r <= 3 * 1.4826 * mad)
        if nk.sum() < 100 or nk.sum() == keep.sum(): break
        keep = nk
    return a, b, float(np.median(np.abs(a * x + b - y)[keep]))

def scale_fit(x, y):
    keep = np.isfinite(x) & np.isfinite(y)
    for _ in range(3):
        a = float(np.sum(x[keep] * y[keep]) / max(1e-12, np.sum(x[keep] ** 2)))
        r = np.abs(a * x - y); mad = np.median(r[keep]) + 1e-12; nk = keep & (r <= 3 * 1.4826 * mad)
        if nk.sum() < 100 or nk.sum() == keep.sum(): break
        keep = nk
    return a, float(np.median(np.abs(a * x - y)[keep]))

def align(m, valid, d_true, fit_mask):
    """Return (d_pred over the plate, space name, visible median residual)."""
    f = fit_mask & valid & np.isfinite(d_true) & np.isfinite(m) & (m > 0)
    cands = []
    a, b, r = robust_fit(1.0 / m[f], 1.0 / d_true[f]); disp = a / np.where(m > 0, m, np.nan) + b
    cands.append(('disp_affine', r, np.where(disp > 1e-6, 1.0 / disp, np.inf), (a, b)))
    a, b, r = robust_fit(m[f], d_true[f]); cands.append(('depth_affine', r, a * m + b, (a, b)))
    a, r = scale_fit(m[f], d_true[f]); cands.append(('depth_scale', r, a * m, (a, 0.0)))
    # the visible residual of the disparity fit is in 1/m units; compare all three in metres on the fit set
    best = None
    for name, _, dp, ab in cands:
        rm = float(np.median(np.abs(dp - d_true)[f]))
        if best is None or rm < best[2]: best = (name, dp, rm, ab)
    return best

from scipy import ndimage
def local_align(m, valid, d_true, fit_mask, hid):
    """The user's normalisation in its strong form: per connected hidden component, the affine fit is made only on the
    visible texels within r of the component, r = its equivalent radius sqrt(A/pi) (scale-free, no constant); falls
    back to the global fit where fewer than 100 fit texels are in reach. Returns d_pred on the hidden set (nan elsewhere)."""
    gname, gdp, _, _ = align(m, valid, d_true, fit_mask)
    out = np.full(m.shape, np.nan); lab, n = ndimage.label(hid)
    for i in range(1, n + 1):
        comp = lab == i; A = comp.sum(); r = max(3.0, np.sqrt(A / np.pi))
        ring = (ndimage.distance_transform_edt(~comp) <= r) & fit_mask & valid & np.isfinite(d_true) & np.isfinite(m) & (m > 0)
        if ring.sum() < 100: out[comp] = gdp[comp]; continue
        _, dp, _, _ = align(m, valid, d_true, ring); out[comp] = dp[comp]
    return out, n

def errs(dp, dt, mask, cap=None):
    """|dp - dt| on mask where the truth is finite. A non-finite prediction (a disparity fit at or below zero = 'at
    infinity') is NOT dropped: it is scored at `cap` = the farthest finite surface of the scene, and counted in inf_frac."""
    m = mask & np.isfinite(dt)
    if m.sum() == 0: return None
    dpe = np.where(np.isfinite(dp), dp, cap if cap is not None else np.nan)
    e = (dpe - dt)[m]; fin = np.isfinite(e)
    if fin.sum() == 0: return None
    return {'n': int(m.sum()), 'median_abs': float(np.median(np.abs(e[fin]))), 'p90_abs': float(np.percentile(np.abs(e[fin]), 90)), 'mean': float(e[fin].mean()),
            'inf_frac': float((~np.isfinite(dp[m])).mean())}

def probe_dir(S):
    for suf in ('_16plane_c', '_16planesky_c', '_16plane_ceil', '_16planesky_ceil', '_16plane', '_16planesky'):
        if os.path.isdir(f'{PROBE}/{S}{suf}') and os.path.exists(f'{PROBE}/{S}{suf}/plateF.f32'): return f'{PROBE}/{S}{suf}'
    return None

res = {}
for td in sorted(glob.glob(f'{OUT}/*/truth.npz')):
    S = os.path.basename(os.path.dirname(td)); t = np.load(td); pw, ph = int(t['pw']), int(t['ph'])
    d_vis = t['d_vis']; m_fit = t['m_fit']
    own = t['m_peel1'] & np.isin(t['cls_first'], (4, 5))          # first hidden layer is the object's own back face
    sets = {'peel1': (t['m_peel1'], t['d_peel1']), 'bg': (t['m_bg'], t['d_bg']), 'own': (own, t['d_peel1'])}
    R = {'outer': float(t['outer']), 'hidden_px': {k: int(v[0].sum()) for k, v in sets.items()}}
    fv = d_vis[m_fit & np.isfinite(d_vis)]
    R['vis_depth_p5_p95'] = [float(np.percentile(fv, 5)), float(np.percentile(fv, 95))]
    R['hidden_depth_p5_p95'] = {k: [float(np.nanpercentile(v[1][v[0]], 5)), float(np.nanpercentile(v[1][v[0]], 95))] for k, v in sets.items() if v[0].any()}
    cap = float(np.nanmax([np.nanmax(np.where(np.isfinite(d_vis), d_vis, np.nan))] + [np.nanmax(np.where(np.isfinite(v[1]), v[1], np.nan)) for v in sets.values() if v[0].any()]))
    R['cap_m'] = cap
    pd = probe_dir(S)
    if pd:
        meta = json.load(open(f'{pd}/meta.json')); pf = np.fromfile(f'{pd}/plateF.f32', np.float32).reshape(ph, pw)[::-1]
        dis = np.fromfile(f'{pd}/disocc.u8', np.uint8).reshape(ph, pw) > 0
        d_pl = -app_z_of_d(pf, meta['pn'], meta['outer'], meta['inner'])
        R['plane'] = {'probe': os.path.basename(pd)}
        for k, (mk, dk) in sets.items():
            R['plane'][k] = errs(d_pl, dk, mk, cap); R['plane'][k + '_in_band'] = errs(d_pl, dk, mk & dis, cap)
            R['plane'][k + '_band_cover'] = float((mk & dis).sum() / max(1, mk.sum()))
    for mdl in MODELS:
        R[mdl] = {}
        for pic in ('rest', 'peel1', 'bg'):
            p = f'{OUT}/{S}/{mdl}_{pic}.npy'
            if not os.path.exists(p): continue
            m = np.load(p).astype(np.float64); vm = np.load(p.replace('.npy', '_mask.npy')) if os.path.exists(p.replace('.npy', '_mask.npy')) else np.ones_like(m, bool)
            name, dp, rvis, ab = align(m, vm, d_vis.astype(np.float64), m_fit)
            e = {'space': name, 'vis_median_abs': rvis, 'ab': [float(ab[0]), float(ab[1])], 'model_valid': float(vm.mean())}
            if pic != 'rest':
                mk, dk = sets[pic]; e['hidden'] = errs(dp, dk, mk & vm, cap)
                dpc = np.maximum(dp, np.where(np.isfinite(d_vis), d_vis, -np.inf)); e['hidden_clamped'] = errs(dpc, dk, mk & vm, cap)
                if pd: e['hidden_in_band'] = errs(dp, dk, mk & vm & dis, cap)
                if pic == 'peel1' and own.any():
                    e['own'] = errs(dp, dk, own & vm, cap); e['own_clamped'] = errs(dpc, dk, own & vm, cap)
                dl, ncomp = local_align(m, vm, d_vis.astype(np.float64), m_fit, mk)
                e['local'] = {'components': int(ncomp), **(errs(dl, dk, mk & vm, cap) or {})}
                dlc = np.maximum(dl, np.where(np.isfinite(d_vis), d_vis, -np.inf)); e['local_clamped'] = errs(dlc, dk, mk & vm, cap)
                np.save(f'{OUT}/{S}/{mdl}_{pic}_local.npy', dl.astype(np.float32))
                # oracle: the same fit made on the hidden truth itself — the best any normalisation could do with this
                # output's SHAPE; separates "shape wrong" from "scale/offset wrong"
                oname, odp, orv, oab = align(m, vm, np.where(mk, dk, np.nan).astype(np.float64), mk)
                e['oracle'] = {'space': oname, **(errs(odp, dk, mk & vm, cap) or {})}
                if mdl.startswith('depthlab'):   # metric by construction: also the unaligned output
                    e['raw_unaligned'] = errs(m, dk, mk & vm, cap)
                np.save(f'{OUT}/{S}/{mdl}_{pic}_aligned.npy', dp.astype(np.float32))
            R[mdl][pic] = e
    res[S] = R
json.dump(res, open(f'{OUT}/scores.json', 'w'), indent=1)
# table: hidden median |err| in metres, per scene, per arm, on the peel1 and bg sets
hdr = f"{'scene':6} {'outer':>6} {'set':5} {'n':>6} | {'plane':>7} {'cover':>5} |" + ''.join(f" {m+'glob':>9} {m+'clamp':>9} {m+'local':>9} {m+'oracle':>9} {'inf':>4} {m+'vis':>8} {'space':>12} |" for m in MODELS)
print(hdr)
for S, R in res.items():
    for k in ('peel1', 'bg', 'own'):
        n = R['hidden_px'][k]
        if n == 0: continue
        pl = R.get('plane', {}).get(k); row = f"{S:6} {R['outer']:6.3f} {k:5} {n:6d} | {pl['median_abs'] if pl else float('nan'):7.4f} {R.get('plane', {}).get(k + '_band_cover', float('nan')):5.2f} |"
        for m in MODELS:
            e = R.get(m, {}).get('peel1' if k == 'own' else k)
            if not e or not e.get('hidden'): row += f" {'-':>9} {'-':>9} {'-':>9} {'-':>9} {'-':>4} {'-':>8} {'-':>12} |"; continue
            if k == 'own':
                row += f" {e['own']['median_abs']:9.4f} {e['own_clamped']['median_abs']:9.4f} {'-':>9} {'-':>9} {e['own']['inf_frac']:4.2f} {e['vis_median_abs']:8.4f} {e['space']:>12} |"
            else:
                row += f" {e['hidden']['median_abs']:9.4f} {e['hidden_clamped']['median_abs']:9.4f} {e['local']['median_abs']:9.4f} {e['oracle']['median_abs']:9.4f} {e['hidden']['inf_frac']:4.2f} {e['vis_median_abs']:8.4f} {e['space']:>12} |"
        print(row)
