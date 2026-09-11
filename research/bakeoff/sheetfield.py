#!/usr/bin/env python3
"""Sprint 12 step 1 — the far field solved per reveal component and per source sheet (thin-plate surface through the sheet's
rim samples), scored against truth (kit) and by seams, from an existing probe dump.
Usage: sheetfield.py <probe_dir> <q_levels> [<scope_gt.npz>]   (q_levels: 255 | 65535 | 568 ... = 1/effective quantum)"""
import sys, os, json, time, numpy as np
from scipy.ndimage import label
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.interpolate import RBFInterpolator
sys.path.insert(0, '/home/user/moebiusv2/harness/truthkit'); from tk import app_z_of_d
d = sys.argv[1]; q = 1.0 / float(sys.argv[2]); gtp = sys.argv[3] if len(sys.argv) > 3 else None
m = json.load(open(d + '/meta.json')); pw, ph = m['pw'], m['ph']; N = pw * ph; t = m['rimT']
ld = lambda n, ty, k=1: np.fromfile(f'{d}/{n}', ty).reshape(ph, pw) if k == 1 else np.fromfile(f'{d}/{n}', ty).reshape(ph, pw, k)
dq = ld('dQ.f32', np.float32).astype(float); axis = ld('farAxis.u8', np.uint8); kind = ld('farKind.u8', np.uint8)
rimJ = ld('farRimJ.i32', np.int32, 2); rimW = ld('farRimW.i32', np.int32, 2); mix = ld('farMix.f32', np.float32)
rimJ2 = ld('farRimJ2.i32', np.int32); side2 = np.fromfile(f'{d}/farSide2.bin', np.int8).reshape(ph, pw) if os.path.exists(f'{d}/farSide2.bin') else np.zeros((ph, pw), np.int8)
farDisp = ld('farDisp.f32', np.float32).astype(float); farCut = ld('farCut.u8', np.uint8) > 0; farField = ld('farField.f32', np.float32).astype(float)
sky = ld('skyClass.u8', np.uint8) > 0 if os.path.exists(f'{d}/skyClass.u8') else np.zeros((ph, pw), bool)
dis = ld('disocc.u8', np.uint8) > 0
lut = np.fromfile(d + '/zeLut.f32', np.float32).astype(float); grid = np.arange(1025) / 1024.0
ze = lambda a: np.interp(np.clip(a, 0, 1) * 1024, np.arange(1025), lut); disp = lambda a: 1.0 / ze(a)
dispLut = 1.0 / lut; order = np.argsort(dispLut); depth_of_disp = lambda v: np.interp(v, dispLut[order], grid[order])   # inverse of disp(d)
D = disp(dq); tol = np.abs(disp(np.minimum(1, dq + q)) - disp(np.maximum(0, dq - q))) + 1e-9
# --- sheets of the SOURCE under the join law (as seam_audit.py)
zd = ze(dq)
def joined_axis(a0, dd, tl):   # returns joined masks (rows: [ph, pw-1], cols: [ph-1, pw]) for depth array a0 with disparity dd and tol tl
    out = []
    for ax in (0, 1):
        if ax == 0: a, b = zd_[:, :-1], zd_[:, 1:]; da, db = dd[:, :-1], dd[:, 1:]; tt = np.maximum(tl[:, :-1], tl[:, 1:])
        else: a, b = zd_[:-1, :], zd_[1:, :]; da, db = dd[:-1, :], dd[1:, :]; tt = np.maximum(tl[:-1, :], tl[1:, :])
        j = np.maximum(a / b, b / a) <= t
        if ax == 0:
            prev = np.full_like(da, np.nan); prev[:, 1:] = dd[:, :-2]; nxt = np.full_like(db, np.nan); nxt[:, :-1] = dd[:, 2:]
        else:
            prev = np.full_like(da, np.nan); prev[1:, :] = dd[:-2, :]; nxt = np.full_like(db, np.nan); nxt[:-1, :] = dd[2:, :]
        r1 = np.abs(db - (2 * da - prev)) <= tt; r2 = np.abs(da - (2 * db - nxt)) <= tt
        j = j | np.nan_to_num(r1, nan=False) | np.nan_to_num(r2, nan=False)
        # sky joins nothing but sky
        if ax == 0: s1, s2 = sky_[:, :-1], sky_[:, 1:]
        else: s1, s2 = sky_[:-1, :], sky_[1:, :]
        j = np.where(s1 | s2, s1 & s2, j); out.append(j)
    return out
def sheets_of(a0):
    global zd_, sky_
    zd_ = ze(a0); sky_ = sky; dd = disp(a0); tl = np.abs(disp(np.minimum(1, a0 + q)) - disp(np.maximum(0, a0 - q))) + 1e-9
    jr, jc = joined_axis(a0, dd, tl); idx = np.arange(N).reshape(ph, pw)
    rows = np.concatenate([idx[:, :-1][jr], idx[:-1, :][jc]]); cols = np.concatenate([idx[:, 1:][jr], idx[1:, :][jc]])
    g = coo_matrix((np.ones(len(rows)), (rows, cols)), shape=(N, N)); nS, lab = connected_components(g, directed=False)
    return nS, lab.reshape(ph, pw), (jr, jc)
t0 = time.time(); nS, sheet, _ = sheets_of(dq); print(f'{os.path.basename(d)}: {pw}x{ph}, q 1/{sys.argv[2]}, source sheets {nS} ({time.time()-t0:.1f}s)')
# --- free set and its components
free = axis > 0; comp, nC = label(free); print(f'free texels {int(free.sum())}, components {nC}, largest {np.bincount(comp.ravel())[1:].max()}')
# --- rim samples per (component, sheet): the rim texel and its run outward along the rim's axis while joined, up to the window
def outward_samples(j, ax, dirn, w):
    # j rim texel index, ax 1=row (step 1) 2=col (step pw), dirn ±1 outward, w window (>=1): texels j, j+dirn*st, ... while joined
    st = 1 if ax == 1 else pw; out = [j]; prev = j
    for k in range(1, max(1, w)):
        n = prev + dirn * st; x = n % pw; y = n // pw
        if n < 0 or n >= N or (ax == 1 and (n // pw) != (prev // pw)): break
        if not joined_pair(prev, n): break
        out.append(n); prev = n
    return out
Dd = D; TOL = tol
def joined_pair(i, j):   # the app's joinedIdx along a line (ratio or affine rescue), on the source
    if sky.ravel()[i] or sky.ravel()[j]: return bool(sky.ravel()[i] and sky.ravel()[j])
    a, b = zd.ravel()[i], zd.ravel()[j]
    if max(a / b, b / a) <= t: return True
    da, db = Dd.ravel()[i], Dd.ravel()[j]; tl = max(TOL.ravel()[i], TOL.ravel()[j]); st = j - i
    p = i - st; n = j + st
    if 0 <= p < N and abs(db - (2 * da - Dd.ravel()[p])) <= tl: return True
    if 0 <= n < N and abs(da - (2 * db - Dd.ravel()[n])) <= tl: return True
    return False
samples = {}   # (comp, sheet) -> dict texel -> disparity
cands = {}     # texel -> list of (sheet, g)
ys, xs = np.nonzero(free); rimJf = rimJ.reshape(N, 2); rimWf = rimW.reshape(N, 2); axf = axis.ravel(); compf = comp.ravel(); sheetf = sheet.ravel(); rimJ2f = rimJ2.ravel(); side2f = side2.ravel()
t0 = time.time()
for y, x in zip(ys, xs):
    i = y * pw + x; ax = axf[i]; c = compf[i]; pos = x if ax == 1 else y; st = 1 if ax == 1 else pw
    cl = []
    for s4, dirn in ((0, -1), (1, +1)):
        j = rimJf[i, s4]
        if j < 0: continue
        sj = sheetf[j]; pj = (j % pw) if ax == 1 else (j // pw); g = abs(pos - pj); cl.append((sj, g, 1))
        key = (c, sj); dct = samples.setdefault(key, {})
        if j not in dct:
            for n in outward_samples(j, ax, dirn, rimWf[i, s4]): dct.setdefault(n, Dd.ravel()[n])
    j2 = rimJ2f[i]
    if j2 >= 0:
        sj = sheetf[j2]; pj = (j2 % pw) if ax == 1 else (j2 // pw); g = abs(pos - pj); cl.append((sj, g, 2))
        key = (c, sj); dct = samples.setdefault(key, {})
        if j2 not in dct:
            for n in outward_samples(j2, ax, int(side2f[i]) if side2f[i] != 0 else (1 if pj > pos else -1), 8): dct.setdefault(n, Dd.ravel()[n])
    cands[i] = cl
print(f'rim samples gathered for {len(samples)} (component, sheet) pairs in {time.time()-t0:.1f}s; sample counts median {int(np.median([len(v) for v in samples.values()]))} max {max(len(v) for v in samples.values())}')
# --- one surface per (component, sheet): thin-plate spline through the samples (subsampled to <= 1500), flat across for a single line
fields = {}; rng = np.random.default_rng(0); nTPS = nLine = 0; t0 = time.time()
CAP = 1500
for key, dct in samples.items():
    c, s = key; tex = np.fromiter(dct.keys(), np.int64); val = np.fromiter(dct.values(), float)
    if sky.ravel()[tex].all(): fields[key] = ('sky', None); continue
    if len(tex) > CAP: sel = rng.choice(len(tex), CAP, replace=False); tex, val = tex[sel], val[sel]
    P = np.stack([tex % pw, tex // pw], 1).astype(float)
    # rank of the point cloud: a single line (or a single texel) cannot fix the cross-line slope -> line fit along its axis, flat across
    if len(tex) < 3 or np.linalg.matrix_rank(P - P.mean(0), tol=1e-6) < 2:
        if len(tex) == 1: fields[key] = ('const', float(val[0])); nLine += 1; continue
        ax = 1 if np.ptp(P[:, 0]) > np.ptp(P[:, 1]) else 2; u = P[:, 0] if ax == 1 else P[:, 1]
        A = np.vstack([u, np.ones_like(u)]).T; co = np.linalg.lstsq(A, val, rcond=None)[0]; fields[key] = ('line', (ax, co[0], co[1])); nLine += 1; continue
    if os.environ.get('MODE') == 'plane':   # reference: the least-squares plane per sheet (the S7 pooling, falsified on curved sheets)
        A = np.hstack([P, np.ones((len(P), 1))]); co = np.linalg.lstsq(A, val, rcond=None)[0]; fields[key] = ('plane', co); nTPS += 1; continue
    try: fields[key] = ('tps', RBFInterpolator(P, val, kernel='thin_plate_spline', degree=1, smoothing=0.0)); nTPS += 1
    except Exception as e: fields[key] = ('const', float(np.median(val))); nLine += 1
print(f'surfaces: {nTPS} thin-plate, {nLine} line/const, in {time.time()-t0:.1f}s')
def eval_field(key, tex):
    kind_, obj = fields[key]
    if kind_ == 'sky': return np.zeros(len(tex))
    if kind_ == 'const': return np.full(len(tex), obj)
    if kind_ == 'line': ax, a, b = obj; u = (tex % pw) if ax == 1 else (tex // pw); return a * u + b
    if kind_ == 'plane': return obj[0] * (tex % pw) + obj[1] * (tex // pw) + obj[2]
    P = np.stack([tex % pw, tex // pw], 1).astype(float); out = np.empty(len(tex))
    for s0 in range(0, len(tex), 20000): out[s0:s0 + 20000] = obj(P[s0:s0 + 20000])
    return out
# --- evaluate each surface on the texels that see it, choose per texel by first arrival among its own sheets
t0 = time.time(); need = {}
for i, cl in cands.items():
    c = compf[i]
    for s, g, lay in cl: need.setdefault((c, s), {}).setdefault(i, g)
vals = {}
if os.environ.get('MODE') == 'local':
    from scipy.spatial import cKDTree
    trees = {}
    for key, dct in samples.items():
        tex = np.fromiter(dct.keys(), np.int64); val = np.fromiter(dct.values(), float)
        P = np.stack([tex % pw, tex // pw], 1).astype(float); trees[key] = (cKDTree(P), P, val, sky.ravel()[tex].all())
    cache = {}; nPl = nLn = 0
    for i, cl in cands.items():
        c = compf[i]; ax = axf[i]; pos = (i % pw) if ax == 1 else (i // pw)
        for s, g, lay in cl:
            # the rim texel this candidate came from: the side whose rim sheet is s (L, R) or the layer-2 rim
            j = -1
            for s4 in (0, 1):
                jj = rimJf[i, s4]
                if jj >= 0 and sheetf[jj] == s: j = jj; break
            if j < 0 and rimJ2f[i] >= 0 and sheetf[rimJ2f[i]] == s: j = rimJ2f[i]
            ck = (c, s, j, g, ax if os.environ.get('OWN') == '1' else 0)
            if ck not in cache:
                tree, P, val, isSky = trees[(c, s)]
                if os.environ.get('OWN') == '1' and not isSky:
                    # only the samples on the rim's own line (row or column of j), i.e. the run the app fitted
                    line_mask = (P[:, 1] == j // pw) if ax == 1 else (P[:, 0] == j % pw)
                    tree = cKDTree(P[line_mask]) if line_mask.any() else tree; P = P[line_mask] if line_mask.any() else P; val = val[line_mask] if line_mask.any() else val
                if isSky: cache[ck] = ('sky', None)
                else:
                    pj = np.array([j % pw, j // pw], float); idx = tree.query_ball_point(pj, g + 1.0)
                    if len(idx) == 0: idx = [tree.query(pj)[1]]
                    Q = P[idx]; V = val[idx]
                    # THE THIN RULE, in 2-D: a slope in a direction is evidence only if the samples span at least g+1 in that
                    # direction (the app: len < g+1 -> no extrapolated slope). Otherwise that slope is 0 (flat).
                    okx = np.ptp(Q[:, 0]) >= g + 1 - 1e-9; oky = np.ptp(Q[:, 1]) >= g + 1 - 1e-9
                    if os.environ.get('OWN') == '1':   # self-check: the texel's own rim run along its own axis only, as the app does
                        st_ = 1 if ax == 1 else pw; own = [k for k, tt in enumerate(np.fromiter(samples[(c, s)].keys(), np.int64)) if False]
                    cols = []
                    if okx: cols.append(Q[:, 0])
                    if oky: cols.append(Q[:, 1])
                    A = np.vstack(cols + [np.ones(len(Q))]).T if cols else np.ones((len(Q), 1))
                    co = np.linalg.lstsq(A, V, rcond=None)[0]; cx = co[0] if okx else 0.0; cy = (co[1] if okx else co[0]) if oky else 0.0; c0 = co[-1]
                    cache[ck] = ('plane', np.array([cx, cy, c0])); nPl += 1 if (okx or oky) else 0; nLn += 0 if (okx or oky) else 1
            kind_, obj = cache[ck]; x_, y_ = i % pw, i // pw
            if kind_ == 'sky': v = 0.0
            elif kind_ == 'const': v = obj
            elif kind_ == 'line': v = obj[1] * (x_ if obj[0] == 1 else y_) + obj[2]
            else: v = obj[0] * x_ + obj[1] * y_ + obj[2]
            vals[(s, i)] = v
    print(f'local fits: {nPl} planes, {nLn} lines/consts (cached by sheet, rim texel, gap)')
else:
  for key, dct in need.items():
    tex = np.fromiter(dct.keys(), np.int64); v = eval_field(key, tex)
    for tt, vv in zip(tex, v): vals[(key[1], tt)] = vv
  pass
newDisp = np.full(N, np.nan); newSheet = np.full(N, -1); newDisp2 = np.full(N, np.nan); nFall = 0
Df = Dd.ravel(); TOLf = TOL.ravel(); fdf = farDisp.ravel(); fcf = farCut.ravel()
for i, cl in cands.items():
    # layer 1: the NEAREST surface behind the texel among the two sides' sheets (combine's rule: the nearer line is in front);
    # layer 2: the layer-2 rim's surface, if behind. (The first-arrival order applies along one direction, inside the app's walk.)
    l1 = None; l2 = None
    for s, g, lay in cl:
        v = vals[(s, i)]
        if fcf[i] and v < fdf[i] - TOLf[i]: v = fdf[i]        # the ground cut, at the app's own ground value
        if Df[i] - v <= TOLf[i]: continue
        if lay == 1:
            if l1 is None or v > l1[0]: l1 = (v, s)
        else: l2 = (v, s)
    if l1 is None: newDisp[i] = fdf[i]; newSheet[i] = -2; nFall += 1; continue
    newDisp[i] = l1[0]; newSheet[i] = l1[1]
    if l2 is not None and l2[0] < l1[0]: newDisp2[i] = l2[0]
print(f'per-texel choice done in {time.time()-t0:.1f}s; texels with no surface behind them (kept the per-line value) {nFall}')
newDisp = newDisp.reshape(ph, pw); newSheet = newSheet.reshape(ph, pw)
newDepth = np.where(free, depth_of_disp(np.nan_to_num(newDisp, nan=0.0)), dq); plDepth = np.where(free, depth_of_disp(farDisp), dq)
# --- seams on each field: unjoined edges between adjacent FREE texels under the join law
def seams(a0, sh):
    global zd_, sky_
    zd_ = ze(a0); sky_ = np.zeros_like(sky); dd = disp(a0); tl = np.abs(disp(np.minimum(1, a0 + q)) - disp(np.maximum(0, a0 - q))) + 1e-9
    jr, jc = joined_axis(a0, dd, tl)
    ur = free[:, :-1] & free[:, 1:] & ~jr; uc = free[:-1, :] & free[1:, :] & ~jc
    same = int((ur & (sh[:, :-1] == sh[:, 1:])).sum() + (uc & (sh[:-1, :] == sh[1:, :])).sum())
    return int(ur.sum() + uc.sum()), same
plSheet = np.where(mix >= 0.5, np.where(rimJ[..., 0] >= 0, sheet.ravel()[np.maximum(rimJ[..., 0], 0)], -1), np.where(rimJ[..., 1] >= 0, sheet.ravel()[np.maximum(rimJ[..., 1], 0)], -1))
sPl, sPlSame = seams(plDepth, plSheet); sNew, sNewSame = seams(newDepth, newSheet)
print(f'SEAMS (free-free unjoined edges): per-line {sPl} (same sheet {sPlSame}) -> sheet field {sNew} (same sheet {sNewSame})')
# --- truth (kit)
if gtp:
    gt = np.load(gtp); cls = gt['cls']; w = gt['w_disp'].astype(np.float32); dep = gt['depth']; H, W, K = cls.shape; y0 = (H - ph) // 2; x0 = (W - pw) // 2
    cls_c = cls[y0:y0 + ph, x0:x0 + pw]; w_c = w[y0:y0 + ph, x0:x0 + pw]; dep_c = dep[y0:y0 + ph, x0:x0 + pw]
    vis = (cls_c >= 2) & (cls_c <= 5) & (w_c > 0); has = vis.any(-1); kk = np.argmax(vis, -1); d_true = np.take_along_axis(dep_c, kk[..., None], -1)[..., 0]
    outer, inner, pn = m['outer'], m['inner'], m['pn']; mk = dis & has & np.isfinite(d_true) & free
    for name, fld in (('per-line (farDisp)', plDepth), ('app farField', farField), ('sheet field', newDepth)):
        err = np.abs(-app_z_of_d(fld, pn, outer, inner) - d_true)[mk]; print(f'TRUTH band depth |err| m: {name:20s} median {np.median(err):.3f}  p90 {np.percentile(err, 90):.3f}  mean {err.mean():.3f}  (n {mk.sum()})')
    agree = (newSheet == plSheet); ePl = np.abs(-app_z_of_d(plDepth, pn, outer, inner) - d_true); eNw = np.abs(-app_z_of_d(newDepth, pn, outer, inner) - d_true)
    for lab_, msk in (('same sheet chosen', mk & agree), ('different sheet chosen', mk & ~agree)):
        if msk.any(): print(f'   {lab_:24s} n {msk.sum():6d}: per-line median {np.median(ePl[msk]):.3f} p90 {np.percentile(ePl[msk],90):.3f} | sheet field median {np.median(eNw[msk]):.3f} p90 {np.percentile(eNw[msk],90):.3f}')
np.save(f'{d}/sheetfield_depth.npy', newDepth.astype(np.float32)); np.save(f'{d}/sheetfield_sheet.npy', newSheet.astype(np.int32))
