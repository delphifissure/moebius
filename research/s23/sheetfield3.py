#!/usr/bin/env python3
"""Sprint 15 (from Sprint 12 v2): MODE=slope — the per-line law with its along-axis SLOPE regularised across the neighbouring lines of the same sheet (median over the w lines each side, w = the candidate's own window; the intercept stays the line's own rim value); MODE=cmed — the per-line VALUE replaced by the median over the same lines (same sheet). Sprint 12 v2 text follows.
"""
"""Sprint 12 step 1 (v2) — the far field with the app's per-line law reproduced offline (OWN) and two consistent-surface
variants (LOCAL: plane through the sheet's rim samples within the gap radius, with the 2-D thin rule; TPS: thin-plate per
sheet per component), scored against truth and by seams. Usage: MODE=own|local|tps sheetfield2.py <probe_dir> <q_levels> [scope_gt.npz]"""
import sys, os, json, time, numpy as np
from scipy.ndimage import label
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree
from scipy.interpolate import RBFInterpolator
sys.path.insert(0, '/home/user/moebiusv2/harness/truthkit'); from tk import app_z_of_d
MODE = os.environ.get('MODE', 'own')
d = sys.argv[1]; q = 1.0 / float(sys.argv[2]); gtp = sys.argv[3] if len(sys.argv) > 3 else None
m = json.load(open(d + '/meta.json')); pw, ph = m['pw'], m['ph']; N = pw * ph; t = m['rimT']; G = m.get('ground')
ld = lambda n, ty, k=1: np.fromfile(f'{d}/{n}', ty).reshape(ph, pw) if k == 1 else np.fromfile(f'{d}/{n}', ty).reshape(ph, pw, k)
dq = ld('dQ.f32', np.float32).astype(float); axis = ld('farAxis.u8', np.uint8).ravel()
rimJ = ld('farRimJ.i32', np.int32, 2).reshape(N, 2); rimW = ld('farRimW.i32', np.int32, 2).reshape(N, 2); mix = ld('farMix.f32', np.float32).ravel()
rimJ2 = ld('farRimJ2.i32', np.int32).ravel(); side2 = np.fromfile(f'{d}/farSide2.bin', np.int8) if os.path.exists(f'{d}/farSide2.bin') else np.zeros(N, np.int8)
farDisp = ld('farDisp.f32', np.float32).astype(float).ravel(); farCut = ld('farCut.u8', np.uint8).ravel() > 0; farField = ld('farField.f32', np.float32).astype(float)
farKind = ld('farKind.u8', np.uint8).ravel()
SKY = os.environ.get('SKY') == '1'   # the scene bakes with the sky at infinity (_skyInf): sky = source depth below half a quantum (bgSkyQ)
sky = (dq.ravel() < 0.5 * q) if SKY else np.zeros(N, bool)
gTex = (ld('groundTex.u8', np.uint8) > 0).ravel() if os.path.exists(f'{d}/groundTex.u8') else np.zeros(N, bool)
gCol = (np.fromfile(f'{d}/groundCol.u8', np.uint8) > 0) if os.path.exists(f'{d}/groundCol.u8') else np.zeros(pw, bool)
dis = ld('disocc.u8', np.uint8) > 0
lut = np.fromfile(d + '/zeLut.f32', np.float32).astype(float); grid = np.arange(1025) / 1024.0
ze = lambda a: np.interp(np.clip(a, 0, 1) * 1024, np.arange(1025), lut); disp = lambda a: 1.0 / ze(a)
dispLut = 1.0 / lut; order = np.argsort(dispLut); depth_of_disp = lambda v: np.interp(v, dispLut[order], grid[order])
skyDisp = float(disp(np.array([0.5 * q]))[0]) if SKY else -np.inf
D = disp(dq).ravel(); D[sky] = 0.0; tol = (np.abs(disp(np.minimum(1, dq + q)) - disp(np.maximum(0, dq - q))) + 1e-9).ravel(); zd = ze(dq).ravel()
ground_at = (lambda x, y: G['a'] + G['b'] * x + G['c'] * y) if G else None
# --- sheets of the source (join law), components of the free set
def joined_masks(a0, skym):
    zz = ze(a0); dd = disp(a0); tl = np.abs(disp(np.minimum(1, a0 + q)) - disp(np.maximum(0, a0 - q))) + 1e-9; out = []
    for ax in (0, 1):
        if ax == 0: a, b = zz[:, :-1], zz[:, 1:]; da, db = dd[:, :-1], dd[:, 1:]; tt = np.maximum(tl[:, :-1], tl[:, 1:]); s1, s2 = skym[:, :-1], skym[:, 1:]
        else: a, b = zz[:-1, :], zz[1:, :]; da, db = dd[:-1, :], dd[1:, :]; tt = np.maximum(tl[:-1, :], tl[1:, :]); s1, s2 = skym[:-1, :], skym[1:, :]
        j = np.maximum(a / b, b / a) <= t
        prev = np.full_like(da, np.nan); nxt = np.full_like(db, np.nan)
        if ax == 0: prev[:, 1:] = dd[:, :-2]; nxt[:, :-1] = dd[:, 2:]
        else: prev[1:, :] = dd[:-2, :]; nxt[:-1, :] = dd[2:, :]
        j = j | np.nan_to_num(np.abs(db - (2 * da - prev)) <= tt, nan=False) | np.nan_to_num(np.abs(da - (2 * db - nxt)) <= tt, nan=False)
        out.append(np.where(s1 | s2, s1 & s2, j))
    return out
jr, jc = joined_masks(dq, sky.reshape(ph, pw)); idx = np.arange(N).reshape(ph, pw)
rows = np.concatenate([idx[:, :-1][jr], idx[:-1, :][jc]]); cols = np.concatenate([idx[:, 1:][jr], idx[1:, :][jc]])
nS, sheet = connected_components(coo_matrix((np.ones(len(rows)), (rows, cols)), shape=(N, N)), directed=False)
free = axis > 0; comp, nC = label(free.reshape(ph, pw)); comp = comp.ravel()
print(f'{os.path.basename(d)} [{MODE}]: {pw}x{ph}, q 1/{sys.argv[2]}, sheets {nS}, free {int(free.sum())}, components {nC}, ground {"yes" if G else "no"} ({int(gTex.sum())} ground texels)')
def joined_pair(i, j):
    if sky[i] or sky[j]: return bool(sky[i] and sky[j])
    a, b = zd[i], zd[j]
    if max(a / b, b / a) <= t: return True
    da, db = D[i], D[j]; tl = max(tol[i], tol[j]); st = j - i; p = i - st; n = j + st
    if 0 <= p < N and abs(db - (2 * da - D[p])) <= tl: return True
    if 0 <= n < N and abs(da - (2 * db - D[n])) <= tl: return True
    return False
# --- the app's run segmentation along each line (bgFarSidePlane L~531-540): a run breaks where the second difference of
# disparity exceeds tol (steady state), or at the first pair where the ratio test fails and the third sample does not vouch;
# a sky/non-sky change always breaks.
RS = [np.zeros(N, np.int32), np.zeros(N, np.int32)]; RE = [np.zeros(N, np.int32), np.zeros(N, np.int32)]
PERSIST = os.environ.get('SEG') == 'persist'; skipd = np.zeros(N, bool); nSkip = [0]
def segment_all():
    for ax in (1, 2):
        st = 1 if ax == 1 else pw; L = pw if ax == 1 else ph; nl = ph if ax == 1 else pw; rs = RS[ax - 1]; re = RE[ax - 1]
        for line in range(nl):
            base = line * pw if ax == 1 else line; s0 = 0
            for tt in range(1, L + 1):
                brk = (tt == L)
                if not brk:
                    a = base + (tt - 1) * st; b = base + tt * st
                    if sky[a] != sky[b]: brk = True
                    elif tt - 1 == s0:
                        ok = (max(zd[a] / zd[b], zd[b] / zd[a]) <= t) if not (sky[a] or sky[b]) else True
                        if not ok and tt + 1 < L: c = base + (tt + 1) * st; ok = abs(D[c] - 2 * D[b] + D[a]) <= tol[b]
                        brk = not ok
                    else:
                        c = base + (tt - 2) * st; brk = abs(D[b] - 2 * D[a] + D[c]) > tol[a]
                        # SEG=persist (Sprint 16): a departure of ONE sample that the next sample does not continue is an outlier, not a
                        # break — one sample cannot establish a new line (two define one). The run's last two samples (c, a) predict
                        # the sample after b as 3D[a] - 2D[c]; three samples each within q/2 of the truth put that two-step
                        # prediction within 1.5 tol (tol bounds one step: 2q of disparity slope; two steps: 3q). If it holds, b is
                        # skipped (masked out of the fits) and the run continues through it.
                        if brk and PERSIST and tt + 1 < L and not skipd[a]:
                            n = base + (tt + 1) * st
                            if sky[n] == sky[a] and abs(D[n] - (3 * D[a] - 2 * D[c])) <= 1.5 * tol[a]: brk = False; skipd[b] = True; nSkip[0] += 1
                if brk:
                    for pp in range(s0, tt): k = base + pp * st; rs[k] = s0; re[k] = tt - 1
                    s0 = tt
t0 = time.time(); segment_all(); print(f'runs segmented as the app does ({time.time()-t0:.1f}s)' + (f'; SEG=persist skipped {nSkip[0]} single-sample departures' if PERSIST else ''))
_nr = int((RE[0] == np.arange(N) % pw).sum()); _nc = int((RE[1] == np.arange(N) // pw).sum()); print(f'runs: {_nr / ph:.1f} per row, {_nc / pw:.1f} per column')
def run_of(j, ax): return int(RS[ax - 1][j]), int(RE[ax - 1][j])
def line_fit(ax, line, wa, wb, p):   # least squares of disparity vs position over [wa, wb] on the line; returns (slope, value at p)
    st = 1 if ax == 1 else pw; base = line * pw if ax == 1 else line
    pos = np.arange(wa, wb + 1); vals = D[base + pos * st]
    if PERSIST: keep = ~skipd[base + pos * st]; pos = pos[keep] if keep.sum() >= 2 else pos; vals = D[base + pos * st]
    if len(pos) < 2: return 0.0, float(vals[0])
    A = np.vstack([pos - p, np.ones_like(pos)]).T; co = np.linalg.lstsq(A, vals, rcond=None)[0]; return float(co[0]), float(co[1])
# --- per texel: the candidate from each side, as the app's cand/rebuild builds it (window, fit, thin, ground continuation, cut)
def candidate(i, j, ax, dirn, w):
    x_ = i % pw; y_ = i // pw; xpos = x_ if ax == 1 else y_; line = y_ if ax == 1 else x_
    p = (j % pw) if ax == 1 else (j // pw); g = abs(p - xpos)
    if sky[j]:   # a sky run: the plane at infinity, then the ground cut below (the ground meets the sky ray)
        gB = ground_at(x_, y_) if (G and gCol[x_]) else -np.inf; v = 0.0
        if gB > 0 and v < gB - tol[i]: v = gB
        return dict(v=v, m=0.0, v0=0.0, p=p, g=g, w=1, len=1, j=j, a=p, b=p, thin=False)
    a, b = run_of(j, ax); ln = b - a + 1; w = min(ln, g + 1)
    wa, wb = (p, min(b, p + w - 1)) if dirn > 0 else (max(a, p - w + 1), p)
    mslope, v0 = line_fit(ax, line, wa, wb, p); v = v0 + mslope * (xpos - p); thin = ln < g + 1
    if thin:
        if ax == 2 and G and gTex[j]: mslope = G['c']; v0 = ground_at(x_, p); v = ground_at(x_, xpos)
        else: mslope = 0.0; v = v0
    gB = ground_at(x_, y_) if (G and gCol[x_]) else -np.inf
    if gB > 0 and v < gB - tol[i]: v = gB; mslope = 0.0; v0 = gB
    return dict(v=v, m=mslope, v0=v0, p=p, g=g, w=w, len=ln, j=j, a=a, b=b, thin=thin)
# --- the consistent-surface variants replace the VALUE of a non-thin, non-ground candidate by a surface through the sheet's rim samples
samples = {}   # (comp, sheet) -> {texel: disparity}
if MODE in ('local', 'tps'):
    for i in np.nonzero(free)[0]:
        ax = axis[i]; st = 1 if ax == 1 else pw
        for s4, dirn in ((0, -1), (1, 1)):
            j = rimJ[i, s4]
            if j < 0 or sky[j]: continue
            key = (comp[i], sheet[j]); dct = samples.setdefault(key, {})
            if j in dct: continue
            a, b = run_of(j, ax); p = (j % pw) if ax == 1 else (j // pw)
            for k in range(0, (b - p + 1) if dirn > 0 else (p - a + 1)):
                n = j + dirn * k * st; dct.setdefault(n, D[n])
    trees = {k: (cKDTree(np.stack([np.fromiter(v.keys(), np.int64) % pw, np.fromiter(v.keys(), np.int64) // pw], 1).astype(float)), np.fromiter(v.values(), float)) for k, v in samples.items()}
    tps = {}
    if MODE == 'tps':
        rng = np.random.default_rng(0)
        for k, (tree, val) in trees.items():
            P = tree.data
            if len(P) >= 3 and np.linalg.matrix_rank(P - P.mean(0), tol=1e-6) >= 2:
                sel = rng.choice(len(P), min(1500, len(P)), replace=False); tps[k] = RBFInterpolator(P[sel], val[sel], kernel='thin_plate_spline', degree=1, smoothing=0.0)
cache = {}
def surface_value(i, c, key):   # the surface's value for candidate c (rim j, gap g, window w) at texel i
    x_ = i % pw; y_ = i // pw; ax = axis[i]
    if MODE == 'tps':
        f = tps.get(key)
        if f is None: return None
        ck = (key, i); return float(f(np.array([[x_, y_]], float))[0])
    ck = (key, c['j'], c['g'])
    if ck not in cache:
        tree, val = trees[key]; pj = np.array([c['j'] % pw, c['j'] // pw], float); ids = tree.query_ball_point(pj, c['g'] + 1.0)
        if len(ids) < 2: cache[ck] = None
        else:
            Q = tree.data[ids]; V = val[ids]; okx = np.ptp(Q[:, 0]) >= c['g'] + 1 - 1e-9; oky = np.ptp(Q[:, 1]) >= c['g'] + 1 - 1e-9   # the thin rule per direction
            colsA = ([Q[:, 0]] if okx else []) + ([Q[:, 1]] if oky else []); A = np.vstack(colsA + [np.ones(len(Q))]).T
            co = np.linalg.lstsq(A, V, rcond=None)[0]; cx = co[0] if okx else 0.0; cy = (co[1] if okx else co[0]) if oky else 0.0
            cache[ck] = (cx, cy, co[-1])
    pl = cache[ck]
    if pl is None: return None
    return pl[0] * x_ + pl[1] * y_ + pl[2]
CS = None
if MODE in ('slope', 'cmed', 'both'):
    # per side: the candidate's slope, sheet, thin flag, window and value, for every free texel (the per-line law's own products)
    CS = {s4: dict(m=np.full(N, np.nan), sh=np.full(N, -1), thin=np.ones(N, bool), w=np.zeros(N, np.int32), v=np.full(N, np.nan), v0=np.full(N, np.nan), p=np.full(N, -1), gnd=np.zeros(N, bool)) for s4 in (0, 1)}
    tC = time.time()
    for i in np.nonzero(free)[0]:
        ax = axis[i]
        for s4, dirn in ((0, -1), (1, 1)):
            j = rimJ[i, s4]
            if j < 0 or sky[j]: continue
            c = candidate(i, j, ax, dirn, rimW[i, s4]); cs = CS[s4]
            gB = ground_at(i % pw, i // pw) if (G and gCol[i % pw]) else -np.inf
            cs['m'][i] = c['m']; cs['sh'][i] = sheet[j]; cs['thin'][i] = c['thin']; cs['w'][i] = c['w']; cs['v'][i] = c['v']; cs['v0'][i] = c['v0']; cs['p'][i] = c['p']; cs['gnd'][i] = (gB > 0 and c['v'] == gB)
    print(f'candidates collected ({time.time()-tC:.1f}s)')
def regularised(i, s4, c):
    """slope: median slope over the neighbouring lines (w each side) whose candidate on this side comes from the same sheet, is not thin
    and not the ground cut; the value re-extrapolated from THIS line's own rim value. cmed: median of the values themselves."""
    cs = CS[s4]; ax = axis[i]; stL = pw if ax == 1 else 1; w = max(1, int(c['w'])); sh = cs['sh'][i]
    xs = []; v0s = []; L0 = (i // pw) if ax == 1 else (i % pw); nl = ph if ax == 1 else pw
    for k in range(-w, w + 1):
        L = L0 + k
        if L < 0 or L >= nl: continue
        n = i + k * stL
        if not free[n] or axis[n] != ax or cs['sh'][n] != sh or cs['thin'][n] or cs['gnd'][n] or np.isnan(cs['m'][n]): continue
        xs.append(cs['m'][n] if MODE in ('slope', 'both') else cs['v'][n])
        if MODE == 'both': v0s.append(cs['v0'][n] + cs['m'][n] * (c['p'] - cs['p'][n]))   # the neighbour's line evaluated at THIS rim's position
    if len(xs) < 2: return None
    med = float(np.median(xs))
    if MODE == 'cmed': return med
    xpos = (i % pw) if ax == 1 else (i // pw); v0 = float(np.median(v0s)) if MODE == 'both' else c['v0']
    return v0 + med * (xpos - c['p'])
newDisp = farDisp.copy(); newSheet = np.full(N, -1); nRepl = 0; nOwnMatch = 0; nFree = 0; t0 = time.time()
plSheet = np.where(mix >= 0.5, np.where(rimJ[:, 0] >= 0, sheet[np.maximum(rimJ[:, 0], 0)], -1), np.where(rimJ[:, 1] >= 0, sheet[np.maximum(rimJ[:, 1], 0)], -1))
for i in np.nonzero(free)[0]:
    ax = axis[i]; sides = []
    for s4, dirn in ((0, -1), (1, 1)):
        j = rimJ[i, s4]
        if j < 0: continue
        c = candidate(i, j, ax, dirn, rimW[i, s4]); v = c['v']; sj = sheet[j]
        if sky[j]: sides.append((v, sj)); continue
        if MODE != 'own' and not c['thin'] and not (v == ground_at(i % pw, i // pw) if (G and gCol[i % pw]) else False):
            sv = regularised(i, s4, c) if MODE in ('slope', 'cmed', 'both') else surface_value(i, c, (comp[i], sj))
            if sv is not None:
                gB = ground_at(i % pw, i // pw) if (G and gCol[i % pw]) else -np.inf
                if gB > 0 and sv < gB - tol[i]: sv = gB
                v = sv; nRepl += 1
        sides.append((v, sj))
    nFree += 1
    if not sides: continue
    # combine across sides: the nearer line is in front (kind 4); behind the texel by more than tol
    if SKY: sides = [((0.0 if v < skyDisp else v), s) for v, s in sides]   # S3: a far side below the sky threshold is the plane at infinity
    beh = [(v, s) for v, s in sides if D[i] - v > tol[i]]
    if not beh: newDisp[i] = D[i]; newSheet[i] = -2; continue
    v, s = max(beh); newDisp[i] = v; newSheet[i] = s
    if abs(v - farDisp[i]) <= tol[i]: nOwnMatch += 1
print(f'choice done in {time.time()-t0:.1f}s; free {nFree}; values within tol of the app\'s farDisp: {100*nOwnMatch/max(1,nFree):.1f} %' + (f'; candidates replaced by a surface: {nRepl}' if MODE != 'own' else ''))
newDepth = np.where(free, depth_of_disp(newDisp), dq.ravel()).reshape(ph, pw); plDepth = np.where(free, depth_of_disp(farDisp), dq.ravel()).reshape(ph, pw)
def seams(a0, sh):
    jr_, jc_ = joined_masks(a0, np.zeros((ph, pw), bool)); fr = free.reshape(ph, pw); sh = sh.reshape(ph, pw)
    ur = fr[:, :-1] & fr[:, 1:] & ~jr_; uc = fr[:-1, :] & fr[1:, :] & ~jc_
    return int(ur.sum() + uc.sum()), int((ur & (sh[:, :-1] == sh[:, 1:])).sum() + (uc & (sh[:-1, :] == sh[1:, :])).sum())
sPl = seams(plDepth, plSheet); sNew = seams(newDepth, newSheet if MODE != 'own' else plSheet)
print(f'SEAMS free-free unjoined: app per-line {sPl[0]} (same sheet {sPl[1]}) -> {MODE} {sNew[0]} (same sheet {sNew[1]})')
if gtp:
    gt = np.load(gtp); cls = gt['cls']; w = gt['w_disp'].astype(np.float32); dep = gt['depth']; H, W, K = cls.shape; y0 = (H - ph) // 2; x0 = (W - pw) // 2
    cls_c = cls[y0:y0 + ph, x0:x0 + pw]; w_c = w[y0:y0 + ph, x0:x0 + pw]; dep_c = dep[y0:y0 + ph, x0:x0 + pw]
    vis = (cls_c >= 2) & (cls_c <= 5) & (w_c > 0); has = vis.any(-1); kk = np.argmax(vis, -1); d_true = np.take_along_axis(dep_c, kk[..., None], -1)[..., 0]
    outer, inner, pn = m['outer'], m['inner'], m['pn']; mk = dis & has & np.isfinite(d_true) & free.reshape(ph, pw)
    for name, fld in (('app per-line', plDepth), (MODE, newDepth)):
        err = np.abs(-app_z_of_d(fld, pn, outer, inner) - d_true)[mk]; print(f'TRUTH band |err| m: {name:14s} median {np.median(err):.3f}  p90 {np.percentile(err, 90):.3f}  mean {err.mean():.3f}  (n {mk.sum()})')
np.save(f'{d}/sf3_{MODE}_depth.npy', newDepth.astype(np.float32))
