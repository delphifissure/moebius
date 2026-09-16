#!/usr/bin/env python3
"""S35 — offline prototype: one continuation SHEET per visible surface behind each hole, the nearest sheet shows.

  python3 sheets.py <probe dump dir> [--truth scope_gt.npz] [--step VISIBLE_STEP] [--q QUANTUM] [--out DIR] [--tag NAME]

Input: an a257_probe dump (dQ.f32 source depth, disocc.u8 the app's band, farField.f32 the per-line law's answer, meta.json
with outer/inner/pn/D/rimT/ground, groundCol.u8). Everything below uses the app's own definitions (moebius.js bgRimLawFor,
bgFarSidePlane), ported: the depth law z(d), the eye distance ze = D - z, disparity 1/ze, the join tolerance tolAt(d) with
the effective quantum q, the join test (ratio <= t, or the linear prediction from either side within tol), the fit window
w = min(run length, gap + 1), the ground plane as a bound where a column has a ground run.

Construction (the user's sheet model, S33/S34):
  1 far-rim texels: visible (non-band) 4-neighbours of band texels that lie BEHIND the band texel's own depth by > tol
    (the occluder's own visible interior is joined to the band texel and is not a rim);
  2 surfaces: far-rim texels clustered along the hole's contour — 8-adjacent rim texels joined by the join law are one surface;
  3 strip per surface: visible texels reached from its rim texels through joined steps, up to the surface's own reach (the
    longest gap its lines must cross, +1: the app's window rule, generalised to 2-D);
  4 sheet per surface: least-squares plane in DISPARITY over the strip (affine in disparity: the plane's homography), residuals
    trimmed at 3 MAD (the app's fit), plus the harmonic extension of the rim residuals into the domain (Dirichlet at the rim,
    zero flux elsewhere; the least-squares residuals have zero mean, so the extension relaxes to the plane away from the rim);
  5 domain: 'stop' = the band texels reached from the surface's rim texels along their lines (rows for side rims, columns for
    top/bottom rims) until the band ends; 'extend' = the whole hole component;
  6 the ground plane (meta.ground, disparity = a + b x + c y) is a sheet everywhere a column has a ground run (the app's rule);
    sky rims (d < skyQ) are a sheet at disparity 0;
  7 order: per band texel, of the sheets whose domain holds it and whose value lies behind the texel's own depth by > tol, the
    NEAREST shows (max disparity); the second-nearest is layer 2; none -> the texel's own depth (counted as unreached).
Scoring: band depth error against the kit's first hidden layer (metres; as check_app_band.py) and the wall instrument (adjacent
band texels whose depths differ by more than the visible step: count and summed length in steps), for the per-line law
(farField.f32) and for the sheets, 'stop' and 'extend'. Figures: surfaces, far fields, the wall maps.
"""
import sys, os, json, time, argparse
import numpy as np
from scipy import ndimage, sparse
from scipy.sparse.linalg import spsolve, cg
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument('probe'); ap.add_argument('--truth'); ap.add_argument('--step', type=float); ap.add_argument('--q', type=float, default=1 / 65535)
ap.add_argument('--out'); ap.add_argument('--tag', default='sheets'); ap.add_argument('--no-ground', action='store_true'); ap.add_argument('--no-residual', action='store_true'); ap.add_argument('--no-extend', action='store_true'); ap.add_argument('--drop-thin2', action='store_true', help='a surface thin along both axes is not extrapolated at all'); ap.add_argument('--local', action='store_true', help='sheet = Shepard blend of local tangent planes fitted around each rim texel (2-D windows), instead of one plane + pinned residual'); ap.add_argument('--mask', help='object-id PNG (0 = background): texels of different ids are never joined, so an object is its own surface and never part of its background'); ap.add_argument('--merge', action='store_true', help='merge a visible fragment into an adjacent surface when its texels lie within the join tolerance of that surface\'s fitted plane (regional join instead of pairwise)'); ap.add_argument('--evidence', action='store_true', help='a sheet extrapolated at constant depth along a thin axis is a hedge, not a measurement: where a fully fitted sheet also lies behind the texel, the fitted sheet shows'); ap.add_argument('--twosided', action='store_true', help='an OBJECT surface (mask id > 0) passes behind an occluder only where its own rims close the span on both sides of the line (S3 kind-2: a same-surface pair is a positive detection); a one-sided march of an object sheet is a hedge'); ap.add_argument('--twosided-all', action='store_true', help='the two-sided rule for every surface, not only masked objects (backgrounds end at corners too); the ground plane is the exception'); ap.add_argument('--fused', action='store_true', help='a visible component whose boundary to other mask ids is depth-JOINED on the majority of its length is fused with its neighbours (DA3 gives a narrow background gap between two near objects the objects\' depth); its sheet is a hedge, never a measurement'); ap.add_argument('--reach', action='store_true', help="where a sheet ends: it continues into the hole no farther than the surface itself extends outside it (geodesic radius of its own visible patch from its rims), instead of as far as the hole is deep"); ap.add_argument('--geo', action='store_true', help='2-D domain: a sheet claims the band texels within geodesic reach of its rims through the band (reach = its own longest march) instead of the along-line marches only'); ap.add_argument('--patches', action='store_true', help='split every visible component into planar patches (region growing; a texel joins while one plane fits the patch within the visible step tolAt); patches are the surfaces'); ap.add_argument('--tps', action='store_true', help='sheet = smoothing thin plate over strip + domain, data weighted by the strip noise, lambda by the discrepancy principle')
A = ap.parse_args()
P = A.probe; meta = json.load(open(f'{P}/meta.json')); pw, ph = meta['pw'], meta['ph']; N = pw * ph
dQ = np.fromfile(f'{P}/dQ.f32', np.float32).reshape(ph, pw).astype(np.float64)
band = np.fromfile(f'{P}/disocc.u8', np.uint8).reshape(ph, pw) > 0
ffL = np.fromfile(f'{P}/farField.f32', np.float32).reshape(ph, pw).astype(np.float64)
gcol = np.fromfile(f'{P}/groundCol.u8', np.uint8) if os.path.exists(f'{P}/groundCol.u8') else None
OUT = A.out or f'{P}/s35'; os.makedirs(OUT, exist_ok=True)
outer, inner, pn, D, t = meta['outer'], meta['inner'], meta['pn'], meta.get('D', 0.2), meta['rimT']
q = A.q; skyQ = 0.5 * (1 / 65535)

# ---- the app's depth law and join law (bgRimLawFor) ----
def z_of_d(d):
    d = np.clip(d, 0, 1); s1 = d / pn; s2 = (d - pn) / (1 - pn)
    return np.where(d < pn, -outer + outer * (s1 * s1 * (3 - 2 * s1)), inner * (s2 * s2 * (3 - 2 * s2)))
def ze(d): return np.maximum(1e-4, D - z_of_d(d))
def disp(d): return 1.0 / ze(d)
def tolAt(d): return np.abs(disp(np.minimum(1, d + q)) - disp(np.maximum(0, d - q))) + 1e-9
DISP = disp(dQ); TOL = tolAt(dQ); ZE = ze(dQ)
def joined_pair(i, j):   # flat indices; the app's joinedIdx (ratio test, then the linear prediction from either side)
    dA, dB = dQ.flat[i], dQ.flat[j]
    if dA < skyQ or dB < skyQ: return (dA < skyQ) and (dB < skyQ)
    a, b = ZE.flat[i], ZE.flat[j]
    if (a / b if a > b else b / a) <= t: return True
    xi, yi = i % pw, i // pw; xj, yj = j % pw, j // pw; dx, dy = xj - xi, yj - yi
    da, db, tl = DISP.flat[i], DISP.flat[j], max(TOL.flat[i], TOL.flat[j])
    xp, yp = xi - dx, yi - dy
    if 0 <= xp < pw and 0 <= yp < ph and abs(db - (2 * da - DISP[yp, xp])) <= tl: return True
    xn, yn = xj + dx, yj + dy
    if 0 <= xn < pw and 0 <= yn < ph and abs(da - (2 * db - DISP[yn, xn])) <= tl: return True
    return False

T0 = time.time()
# ---- vectorised join test between two arrays of flat indices (the same rule as joined_pair) ----
def joined_arr(I, J):
    dA = dQ.ravel()[I]; dB = dQ.ravel()[J]; skyA = dA < skyQ; skyB = dB < skyQ
    a = ZE.ravel()[I]; b = ZE.ravel()[J]; ratio = np.where(a > b, a / b, b / a) <= t
    xi = I % pw; yi = I // pw; xj = J % pw; yj = J // pw; dx = xj - xi; dy = yj - yi
    da = DISP.ravel()[I]; db = DISP.ravel()[J]; tl = np.maximum(TOL.ravel()[I], TOL.ravel()[J])
    xp = xi - dx; yp = yi - dy; okp = (xp >= 0) & (xp < pw) & (yp >= 0) & (yp < ph)
    pr = np.zeros_like(da); pr[okp] = 2 * da[okp] - DISP[yp[okp], xp[okp]]; lin1 = okp & (np.abs(db - pr) <= tl)
    xn = xj + dx; yn = yj + dy; okn = (xn >= 0) & (xn < pw) & (yn >= 0) & (yn < ph)
    pn_ = np.zeros_like(da); pn_[okn] = 2 * db[okn] - DISP[yn[okn], xn[okn]]; lin2 = okn & (np.abs(da - pn_) <= tl)
    j = ratio | lin1 | lin2
    return np.where(skyA | skyB, skyA & skyB, j)
# ---- runs along rows and columns (the app's rs/re): consecutive texels joined by the join law ----
idx = np.arange(N).reshape(ph, pw)
jh = joined_arr(idx[:, :-1].ravel(), idx[:, 1:].ravel()).reshape(ph, pw - 1)   # texel x joined to x+1
jv = joined_arr(idx[:-1, :].ravel(), idx[1:, :].ravel()).reshape(ph - 1, pw)   # texel y joined to y+1
if A.mask:
    # S35 object-aware surfaces: an object mask (SAM, S28/S29) separates the occluder from its background where the depth map
    # joins them (contact points, ramps); pairs of different ids are unjoined, so runs, components and strips stop at the mask
    oid = np.asarray(Image.open(A.mask)); oid = oid[..., 0] if oid.ndim == 3 else oid
    if oid.shape != (ph, pw): oid = np.asarray(Image.fromarray(oid).resize((pw, ph), Image.NEAREST))
    jh0 = jh.copy(); jv0 = jv.copy()   # the depth law's own verdict on every pair, kept for the fusion test (--fused)
    jh &= (oid[:, :-1] == oid[:, 1:]); jv &= (oid[:-1, :] == oid[1:, :])
    print(f'object mask: {len(np.unique(oid)) - 1} objects, {int((oid > 0).sum())} texels')
def runs_1d(joinedNext, axis):
    # returns start and end index along the axis for every texel
    if axis == 0:
        brk = np.ones((ph, pw), bool); brk[:, 1:] = ~joinedNext; rid = np.cumsum(brk, axis=1)
        st = np.zeros((ph, pw), int); en = np.zeros((ph, pw), int)
        for y in range(ph):
            r = rid[y]; starts = np.flatnonzero(brk[y]); ends = np.append(starts[1:] - 1, pw - 1)
            st[y] = starts[r - 1]; en[y] = ends[r - 1]
    else:
        brk = np.ones((ph, pw), bool); brk[1:, :] = ~joinedNext; rid = np.cumsum(brk, axis=0)
        st = np.zeros((ph, pw), int); en = np.zeros((ph, pw), int)
        for x in range(pw):
            r = rid[:, x]; starts = np.flatnonzero(brk[:, x]); ends = np.append(starts[1:] - 1, ph - 1)
            st[:, x] = starts[r - 1]; en[:, x] = ends[r - 1]
    return st, en
rsX, reX = runs_1d(jh, 0); rsY, reY = runs_1d(jv, 1)
print(f'runs: rows {int((np.diff(rsX, axis=1) != 0).sum() + ph)}, columns {int((np.diff(rsY, axis=0) != 0).sum() + pw)}  ({time.time() - T0:.1f}s)')
# ---- ground detector: REMOVED (S35 §14). The app's S3/S12 rule (rising column runs -> shared horizon -> Theil-Sen plane -> inlier
# majority) was ported here with the precision tolerance at the noise sigma instead of the grid, on the premise that the grid
# tolerance was why it found no ground on 16-bit DA3 maps. Measured on vermeer: with the tolerance at the grid, at sigma (which the
# third-difference estimator reads as 1.0 grid on this map) or at the join quantum, the result is the same — horizon at row
# -335 404, 0 inliers of 326-355 columns. The cause is structural, not the tolerance: under the join law the wall and the floor
# are ONE column run (rows 0-1007 at columns 700/800; DA3's wall-floor crease is a smooth bend), so every 'rising run' is
# wall+floor and its line fit is meaningless; and in the app's flattened world (6 cm of relief) a real floor's horizon lies
# ~10 000 rows above the frame, so the horizon vote has no power. The premise is falsified and the code is gone; the L-bend
# is a deformed sheet (thin plate) like any other.
gtex = None
# ---- 1 far rims (the app's cand(): march along the line beyond the texel's own run; runs that are not behind the texel by more
# than tol are the occluder's own parts and are skipped; the first run that IS behind (or sky) is the far side, its first texel
# the rim). A rim may be a band texel (the reveal set holds one texel of the background at the silhouette).
DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]
rimOf = {}   # rim -> set of (band texel b, dir)
def scan_lines(axis):
    # axis 0: rows (dirs +x, -x); axis 1: columns (dirs +y, -y)
    L = pw if axis == 0 else ph; nL = ph if axis == 0 else pw
    for l in range(nL):
        if axis == 0: line = idx[l, :]; bnd = band[l, :]; rs_, re_ = rsX[l, :], reX[l, :]
        else: line = idx[:, l]; bnd = band[:, l]; rs_, re_ = rsY[:, l], reY[:, l]
        if not bnd.any(): continue
        starts = np.flatnonzero(np.r_[True, rs_[1:] != rs_[:-1]]); ends = np.r_[starts[1:] - 1, L - 1]
        dStart = DISP.ravel()[line[starts]]; dEnd = DISP.ravel()[line[ends]]; skyS = dQ.ravel()[line[starts]] < skyQ; skyE = dQ.ravel()[line[ends]] < skyQ
        bpos = np.flatnonzero(bnd); own = DISP.ravel()[line[bpos]]; tol_ = TOL.ravel()[line[bpos]]
        # forward (+): EVERY run with start > re[b] that lies behind the texel (or is sky) is a far side of it — the app's cand()
        # lists them all and lets the arrival order choose; here the layered order chooses among their sheets
        M = (starts[None, :] > re_[bpos][:, None]) & ((dStart[None, :] < (own - tol_)[:, None]) | skyS[None, :])
        for bi, ri in zip(*np.nonzero(M)):
            r = int(line[starts[ri]]); bb = int(line[bpos[bi]]); k = 0 if axis == 0 else 2
            rimOf.setdefault(r, set()).add((bb, k))
        # backward (-): runs with end < rs[b]
        M = (ends[None, :] < rs_[bpos][:, None]) & ((dEnd[None, :] < (own - tol_)[:, None]) | skyE[None, :])
        for bi, ri in zip(*np.nonzero(M)):
            r = int(line[ends[ri]]); bb = int(line[bpos[bi]]); k = 1 if axis == 0 else 3
            rimOf.setdefault(r, set()).add((bb, k))
scan_lines(0); scan_lines(1)
rims = np.array(sorted(rimOf.keys()), dtype=np.int64); nR = len(rims)
print(f'band {int(band.sum())} texels; far-rim texels {nR}  ({time.time() - T0:.1f}s)')

# ---- 2 surfaces: a visible surface is a connected component of the depth map under the join law (4-neighbour pairs joined),
# through the interior, not only along the hole's contour: two rim texels of one wall stay one surface when noise breaks
# their contour neighbours, because the wall's interior connects them. (The first version clustered rims along the contour
# only: the troll's rims fell into 643 pieces, 338 of them single texels, and the boundaries between pieces were the seams.)
from scipy.sparse.csgraph import connected_components
I_h = idx[:, :-1].ravel()[jh.ravel()]; J_h = idx[:, 1:].ravel()[jh.ravel()]; I_v = idx[:-1, :].ravel()[jv.ravel()]; J_v = idx[1:, :].ravel()[jv.ravel()]
adj = sparse.coo_matrix((np.ones(len(I_h) + len(I_v)), (np.r_[I_h, I_v], np.r_[J_h, J_v])), shape=(N, N))
nComp, comp = connected_components(adj, directed=False)
if A.merge:
    # S35 §11: the pairwise join law splits a wall into fragments wherever DA3's noise exceeds the tolerance between two neighbours.
    # A REGIONAL join: a fragment belongs to an adjacent component if its texels lie within the same tolerance (tolAt, the app's) of
    # that component's fitted plane in disparity — the surface's model instead of one neighbour's sample. Smallest fragments first,
    # planes refitted after a merge; repeated until nothing merges. Fragments that fit no neighbour stay apart (a speck at another depth).
    tm0 = time.time(); compM = comp.copy(); nBefore = nComp
    # adjacency across 4-neighbour pairs that are NOT joined (different components), never across the mask
    Ih = idx[:, :-1].ravel(); Jh = idx[:, 1:].ravel(); Iv = idx[:-1, :].ravel(); Jv = idx[1:, :].ravel()
    if A.mask: okh = (oid[:, :-1] == oid[:, 1:]).ravel(); okv = (oid[:-1, :] == oid[1:, :]).ravel()
    else: okh = np.ones(len(Ih), bool); okv = np.ones(len(Iv), bool)
    PI = np.r_[Ih[okh], Iv[okv]]; PJ = np.r_[Jh[okh], Jv[okv]]
    planeC = {}
    def plane_of(c):
        if c in planeC: return planeC[c]
        t_ = np.flatnonzero(compM == c)
        if len(t_) > 5000: t_ = t_[np.linspace(0, len(t_) - 1, 5000).astype(int)]
        X_ = t_ % pw; Y_ = t_ // pw; V_ = DISP.ravel()[t_]
        if len(t_) < 3: pl = (float(np.median(V_)), 0.0, 0.0)
        else:
            Am = np.stack([np.ones(len(t_)), X_, Y_], 1); c_, *_ = np.linalg.lstsq(Am, V_, rcond=None); pl = tuple(c_)
        planeC[c] = pl; return pl
    for it in range(4):
        sizes_ = np.bincount(compM, minlength=compM.max() + 1)
        ci = compM[PI]; cj = compM[PJ]; diff = ci != cj
        pairs = np.unique(np.stack([np.minimum(ci[diff], cj[diff]), np.maximum(ci[diff], cj[diff])], 1), axis=0)
        adj = {}
        for a_, b_ in pairs: adj.setdefault(int(a_), set()).add(int(b_)); adj.setdefault(int(b_), set()).add(int(a_))
        order = sorted(adj.keys(), key=lambda c: sizes_[c]); nM = 0
        for c in order:
            if sizes_[c] == 0: continue
            t_ = np.flatnonzero(compM == c)
            if len(t_) == 0: continue
            X_ = t_ % pw; Y_ = t_ // pw; V_ = DISP.ravel()[t_]; tol_ = np.median(TOL.ravel()[t_])
            best = None
            for n_ in adj.get(c, ()):
                if sizes_[n_] <= sizes_[c] or sizes_[n_] == 0: continue   # merge into a larger neighbour only
                pl = plane_of(n_); res = np.abs(V_ - (pl[0] + pl[1] * X_ + pl[2] * Y_))
                if np.median(res) <= tol_ and (best is None or sizes_[n_] > sizes_[best]): best = n_
            if best is not None:
                compM[t_] = best; sizes_[best] += sizes_[c]; sizes_[c] = 0; planeC.pop(best, None); nM += 1
                for n_ in adj.get(c, ()):
                    if n_ != best: adj.setdefault(best, set()).add(n_); adj.setdefault(n_, set()).add(best)
        print(f'merge pass {it + 1}: {nM} fragments merged  ({time.time() - tm0:.1f}s)')
        if nM == 0: break
    # relabel to dense ids
    _, comp = np.unique(compM, return_inverse=True); nComp = int(comp.max()) + 1
    print(f'regional join: {nBefore} components -> {nComp}')
compSize = np.bincount(comp, minlength=int(comp.max()) + 1)
# ---- fusion test (--fused, S35 §14). A monocular depth map gives a narrow strip of background seen between two near objects the
# objects' depth (vermeer: the wall between the table and the woman reads 0.40-0.45, the skirt 0.40, the cloth 0.43, the wall 0.003).
# Under the mask such a strip is its own component, fits a plane, and being nearer than the wall it wins the fill behind the
# occluder (the blocks). The evidence that a component is fused: along its boundary to OTHER mask ids its depth is the
# neighbouring object's own depth. A background that really lies behind the objects meets them with a depth step along its
# silhouette and matches them only at contact points (feet on the floor); a fused strip matches along its whole boundary.
# The comparison is texel-to-BODY, not texel-to-texel across the mask line: SAM's edge sits a few texels off DA3's depth edge, so
# the pair straddling the mask line is wall-wall or skirt-skirt and the pairwise share read 0.8-1.0 for every component (first
# version, vermeer). The body of an id is its largest depth component; for a boundary texel t of c next to id B, the test is the
# join law's ratio test (the app's rimT) between t and the nearest texel of B's body. Rule: fused when the matching pairs are the
# majority of the boundary pairs (the app's majority rule; no threshold to tune). A fused surface's sheet is a hedge (it fills
# only what no fitted sheet reaches), as the thin and the one-sided sheets are.
fusedComp = np.zeros(int(comp.max()) + 1, bool); fusedFrac = np.full(int(comp.max()) + 1, np.nan)
if A.mask and A.fused:
    tf0 = time.time(); nc_ = len(fusedComp); ids = np.unique(oid); bodyNear = {}
    for B in ids:
        cB = comp[(oid == B).ravel()]; body = np.bincount(cB, minlength=nc_).argmax()
        _, ind = ndimage.distance_transform_edt(comp.reshape(ph, pw) != body, return_indices=True)
        bodyNear[int(B)] = (ind[0] * pw + ind[1]).ravel()   # for every texel: the flat index of the nearest body texel of id B
    cutH = (oid[:, :-1] != oid[:, 1:]); cutV = (oid[:-1, :] != oid[1:, :])
    T = np.r_[idx[:, :-1][cutH], idx[:-1, :][cutV], idx[:, 1:][cutH], idx[1:, :][cutV]]; U = np.r_[idx[:, 1:][cutH], idx[1:, :][cutV], idx[:, :-1][cutH], idx[:-1, :][cutV]]
    idU = oid.ravel()[U]; nb = np.zeros(len(T), np.int64)
    for B in ids: m_ = idU == B; nb[m_] = bodyNear[int(B)][U[m_]]
    a_ = ZE.ravel()[T]; b_ = ZE.ravel()[nb]; match = (np.where(a_ > b_, a_ / b_, b_ / a_) <= t) & (dQ.ravel()[T] >= skyQ) & (dQ.ravel()[nb] >= skyQ)
    tot = np.bincount(comp[T], minlength=nc_); jn = np.bincount(comp[T], weights=match.astype(float), minlength=nc_)
    # the BODY of an id (its largest depth component) is the object or the background itself and is never 'fused': two bodies
    # matched along their boundary are one surface under the app's law (the wall and the basket hanging on it: ze within rimT).
    # Fusion is a property of a FRAGMENT: a non-body component whose boundary is matched to other ids' bodies (vermeer comp 0,
    # the wall+floor body, read 0.66 matched from the basket and the foot warmer; the gap sliver 0.99).
    isBody = np.zeros(nc_, bool)
    for B in ids: isBody[np.bincount(comp[(oid == B).ravel()], minlength=nc_).argmax()] = True
    has = tot > 0; fusedFrac[has] = jn[has] / tot[has]; fusedComp = has & (2 * jn >= tot) & ~isBody
    big = has & (compSize >= 100); fr = fusedFrac[big]
    print(f'fusion test: {int(has.sum())} components touch another id; of the {int(big.sum())} with >= 100 texels the body-matched share is <10 % for {int((fr < 0.1).sum())}, 10-50 % for {int(((fr >= 0.1) & (fr < 0.5)).sum())}, 50-90 % for {int(((fr >= 0.5) & (fr < 0.9)).sum())}, >= 90 % for {int((fr >= 0.9).sum())}; fused (majority) {int(fusedComp.sum())} components, {int(compSize[fusedComp].sum())} texels  ({time.time() - tf0:.1f}s)')
    for c_ in np.argsort(-compSize * big)[:10]:
        if big[c_]: t_ = np.flatnonzero(comp == c_); print(f'   comp {c_}: {compSize[c_]} texels, id {int(np.median(oid.ravel()[t_]))}, depth median {np.median(dQ.ravel()[t_]):.3f}, rows {t_.min() // pw}-{t_.max() // pw}, cols {(t_ % pw).min()}-{(t_ % pw).max()}: body-matched {fusedFrac[c_]:.2f} of {int(tot[c_])} boundary pairs -> {"FUSED" if fusedComp[c_] else ("body" if isBody[c_] else "distinct")}')
# ---- planar patches (--patches, S35 §14). A visible component under the join law can be an L (vermeer's side wall + back wall +
# floor: DA3's creases are smooth bends, so the pairwise law never breaks them), and neither a plane nor a thin plate is a sheet
# for an L: the plane is the slab of §12; the thin plate, interpolating three folds, overshoots across the hole (depth 1.0
# behind the woman's legs, 0.000 above her). The sheets are the FACES: each component is split into patches that one plane fits
# within the visible step (tolAt, the app's join tolerance — a texel within one visible step of a plane IS that plane at every
# pose, S10). Region growing in waves: the seed is the unassigned texel deepest inside the unassigned set (distance transform);
# the patch's plane is refitted from all its members after every wave; a frontier texel joins when |plane − disp| ≤ tolAt;
# members the final plane no longer fits are released and seeded again. Patches are the components from here on (surfaces,
# strips, fits, order); the fusion flag is inherited from the join-law component; sky keeps its join-law components.
if A.patches:
    tp0 = time.time(); compJ = comp.copy(); nJ = int(compJ.max()) + 1; lab = np.full(N, -1, np.int64); nP = 0
    dv = DISP.ravel(); tl = TOL.ravel(); Xf = (np.arange(N) % pw).astype(float); Yf = (np.arange(N) // pw).astype(float)
    unassigned = (dQ.ravel() >= skyQ)
    def neighbours(F):
        x = F % pw; y = F // pw; out = []
        for dx, dy in DIRS:
            ok = (x + dx >= 0) & (x + dx < pw) & (y + dy >= 0) & (y + dy < ph); out.append(F[ok] + dy * pw + dx)
        return np.unique(np.concatenate(out))
    def fitS(S):
        n_, sx, sy, sxx, sxy, syy, sv, sxv, syv = S
        if n_ < 3: return (sv / n_, 0.0, 0.0)
        useX = (sxx - sx * sx / n_) > 1e-9; useY = (syy - sy * sy / n_) > 1e-9
        Am = np.array([[n_, sx, sy], [sx, sxx, sxy], [sy, sxy, syy]]); rhs = np.array([sv, sxv, syv]); keep = [0] + ([1] if useX else []) + ([2] if useY else [])
        try: sol = np.linalg.solve(Am[np.ix_(keep, keep)], rhs[keep])
        except np.linalg.LinAlgError: return (sv / n_, 0.0, 0.0)
        full = [0.0, 0.0, 0.0]
        for k_, j in enumerate(keep): full[j] = float(sol[k_])
        return tuple(full)
    released = 0; rounds = 0; waves = 0
    while unassigned.any() and rounds < 50:
        rounds += 1
        dist = ndimage.distance_transform_edt(unassigned.reshape(ph, pw)).ravel()
        seeds = np.flatnonzero(unassigned); seeds = seeds[np.argsort(-dist[seeds], kind='stable')]
        for s0 in seeds:
            if not unassigned[s0]: continue
            c_ = compJ[s0]; mem = [np.array([s0])]; unassigned[s0] = False
            S = np.array([1.0, Xf[s0], Yf[s0], Xf[s0] ** 2, Xf[s0] * Yf[s0], Yf[s0] ** 2, dv[s0], Xf[s0] * dv[s0], Yf[s0] * dv[s0]])
            pl = (dv[s0], 0.0, 0.0); front = neighbours(np.array([s0]))
            while True:
                front = front[unassigned[front] & (compJ[front] == c_)]
                if len(front) == 0: break
                res = np.abs(pl[0] + pl[1] * Xf[front] + pl[2] * Yf[front] - dv[front]); add = front[res <= tl[front]]
                if len(add) == 0: break
                unassigned[add] = False; mem.append(add); waves += 1
                x_ = Xf[add]; y_ = Yf[add]; v_ = dv[add]
                S += np.array([len(add), x_.sum(), y_.sum(), (x_ * x_).sum(), (x_ * y_).sum(), (y_ * y_).sum(), v_.sum(), (x_ * v_).sum(), (y_ * v_).sum()])
                pl = fitS(S); front = neighbours(add)
            M = np.concatenate(mem)
            res = np.abs(pl[0] + pl[1] * Xf[M] + pl[2] * Yf[M] - dv[M]); bad = res > tl[M]
            if bad.any() and (~bad).sum() >= 1: unassigned[M[bad]] = True; released += int(bad.sum()); M = M[~bad]
            lab[M] = nP; nP += 1
    left = np.flatnonzero(unassigned)
    if len(left): lab[left] = nP + np.arange(len(left)); nP += len(left)
    sky_ = dQ.ravel() < skyQ; lab[sky_] = nP + compJ[sky_]
    _, comp = np.unique(lab, return_inverse=True); comp = comp.astype(np.int64); nComp = int(comp.max()) + 1
    fusedJ = fusedComp; fusedFracJ = fusedFrac
    fusedComp = np.zeros(nComp, bool); fusedComp[comp[fusedJ[compJ]]] = True
    fusedFrac = np.full(nComp, np.nan); fusedFrac[comp] = fusedFracJ[compJ]
    compSize = np.bincount(comp, minlength=nComp)
    print(f'planar patches: {nComp} from {nJ} join-law components ({int((compSize >= 1000).sum())} of >= 1000 texels, {int(((compSize >= 100) & (compSize < 1000)).sum())} of 100-999, {int((compSize < 100).sum())} under 100); released {released} texels in {rounds} rounds, {waves} waves  ({time.time() - tp0:.1f}s)')
    for c_ in np.argsort(-compSize)[:8]:
        t_ = np.flatnonzero(comp == c_); X_ = t_ % pw; Y_ = t_ // pw; V_ = dv[t_]
        Am = np.stack([np.ones(len(t_)), X_, Y_], 1); cc, *_ = np.linalg.lstsq(Am, V_, rcond=None)
        print(f'   patch {c_}: {compSize[c_]} texels, id {int(np.median(oid.ravel()[t_])) if A.mask else -1}, depth median {np.median(dQ.ravel()[t_]):.3f}, rows {Y_.min()}-{Y_.max()}, cols {X_.min()}-{X_.max()}, plane slope/row {cc[2]:+.2e} slope/col {cc[1]:+.2e} (disparity)')
compOfRim = comp[rims]; roots = {}; surfOf = {}
for r, c in zip(rims, compOfRim): surfOf[r] = roots.setdefault(int(c), len(roots))
nS = len(roots); members = [[] for _ in range(nS)]; compOfSurf = np.zeros(nS, int)
for r in rims: members[surfOf[r]].append(r); compOfSurf[surfOf[r]] = comp[r]
sizes = np.array([len(m) for m in members]); print(f'surfaces {nS} of {nComp} visible components (rim texels per surface: median {int(np.median(sizes))}, max {sizes.max()}, singletons {(sizes == 1).sum()})  ({time.time() - T0:.1f}s)')
fusedS = fusedComp[compOfSurf]
# ---- 5 domains: along-line reach from each rim texel into the band ----
holeLab, nHoles = ndimage.label(band, structure=[[0, 1, 0], [1, 1, 1], [0, 1, 0]])
def dom_march(b, k):
    dx, dy = DIRS[k]; x, y = b % pw, b // pw; out = []
    while 0 <= x < pw and 0 <= y < ph and band[y, x]:
        out.append(y * pw + x); x -= dx; y -= dy
    return out
closeStat = {}; geoInfo = {}; reachOwn = np.zeros(nS, dtype=np.int64)
domStop = [None] * nS; domExt = [None] * nS; domWeak = [None] * nS; reachMax = np.zeros(nS, dtype=np.int64); reachX = np.zeros(nS, dtype=np.int64); reachY = np.zeros(nS, dtype=np.int64)
oidArr = oid if A.mask else None
if gtex is None: gtex = np.fromfile(f'{P}/groundTex.u8', np.uint8) if os.path.exists(f'{P}/groundTex.u8') else None
for s in range(nS):
    dom = set(); holes = set(); weak = set()
    isObj = A.twosided_all or ((oidArr is not None) and (oidArr.flat[members[s][0]] > 0))
    for r in members[s]:
        for (b, k) in rimOf[r]:
            dx, dy = DIRS[k]; x, y = b % pw, b // pw; n = 0; march = []
            while 0 <= x < pw and 0 <= y < ph and band[y, x]:
                i2 = y * pw + x
                if i2 != r: dom.add(i2); march.append(i2)
                x -= dx; y -= dy; n += 1   # march away from the rim through the band
            # WHERE A SHEET ENDS, attempt 1 — REMOVED (S35 §15). Rule tried: a march that exits into a surface FARTHER than the
            # sheet contradicts it (the far surface is visible where the sheet would have to be), while closed, frame-edge and
            # nearer-surface exits do not. Falsified on S15: the fill that is right there is the NEAR canopy (fill 0.47 against
            # truth 0.08 m), and its marches exit into the far hill and the sky, so the rule demoted it — 17 878 of 26 087 scored
            # texels changed owner and their error went 0.054 -> 2.264 m (band median 0.069 -> 1.315 m). A near surface genuinely
            # continues behind an occluder and its march legitimately comes out into the far background; the exit says nothing
            # about how far the sheet reaches, only that the sheet must end SOMEWHERE along it. The two-sided rule for masked
            # objects (below) is kept: there the surface is known to be a bounded thing.
            if isObj and (A.twosided or A.twosided_all):
                # the first texel beyond the band on the far side of this march that belongs to a surface with support (a
                # component of 3+ texels; silhouette specks are skipped): the span is closed if it is this same surface
                xx, yy = x, y; closed = False; bid = oidArr.flat[b] if oidArr is not None else -1
                while 0 <= xx < pw and 0 <= yy < ph:
                    i3 = yy * pw + xx; c_ = comp[i3]
                    if compSize[c_] >= 3 and not band[yy, xx] and not (oidArr is not None and oidArr.flat[i3] == bid and bid > 0): closed = (c_ == compOfSurf[s]); break
                    xx -= dx; yy -= dy
                if not closed: weak.update(march)
                closeStat.setdefault(s, {'closed': 0, 'open': 0})['closed' if closed else 'open'] += 1
            reachMax[s] = max(reachMax[s], n); holes.add(int(holeLab[b // pw, b % pw]))
            if dx != 0: reachX[s] = max(reachX[s], n)
            else: reachY[s] = max(reachY[s], n)
    domStop[s] = np.fromiter(dom, dtype=np.int64); domWeak[s] = np.sort(np.fromiter(weak, dtype=np.int64)); weak = None   # arrays, not sets: 4 311 sets of weak texels were 12.8 GB on vermeer
    ext = np.nonzero(np.isin(holeLab.ravel(), list(holes)) & band.ravel())[0]
    domExt[s] = ext
    if A.geo:
        # 2-D DOMAIN (S35 §14). The along-line marches are the per-line law's domain: a floor strip whose rims lie along the
        # skirt's edge reaches only its own rows, and between two strips' rows the wall's column marches or a hedge show — the
        # row striping of the patch arm (jumps 21 716 / 45 861 on vermeer). A sheet continues into the hole as far as its
        # evidence lets it along a line; sideways the same distance applies — the reach is a property of the hole, not of a
        # direction. Domain: band texels within geodesic distance R of the sheet's entry texels through the band, R = the
        # sheet's own longest march. For an object under the two-sided rule, texels not on a closed march stay weak. Computed
        # on demand in build() for the sheets that get a plane (4 311 stored discs of up to 370 k texels were 14 GB: OOM).
        # WHERE A SHEET ENDS, attempt 2 (--reach, S35 §15): a sheet continues into the hole no farther than the surface itself
        # extends OUTSIDE it. The reach used so far is the depth of the HOLE (the longest march), which lets a 20-texel leaf fill
        # 200 texels of a flower's band; the surface's own extent is the evidence of how big the surface is. Measured the same way
        # as the domain, so the two are comparable with no constant and no units to convert: the geodesic radius of the surface's
        # own visible patch, walking from its rim texels inside the patch, capped at the march length.
        Rg = int(reachMax[s])
        if A.reach and Rg > 0:
            cmpId = compOfSurf[s]; rr_ = np.array(members[s], dtype=np.int64); seenV = np.zeros(N, bool); seenV[rr_] = True; fr_ = rr_; E = 0
            for stp in range(1, Rg + 1):
                x_ = fr_ % pw; y_ = fr_ // pw; nb = []
                for dx_, dy_ in DIRS:
                    okn_ = (x_ + dx_ >= 0) & (x_ + dx_ < pw) & (y_ + dy_ >= 0) & (y_ + dy_ < ph); nb.append(fr_[okn_] + dy_ * pw + dx_)
                nb = np.unique(np.concatenate(nb)); nb = nb[(comp[nb] == cmpId) & ~seenV[nb]]
                if len(nb) == 0: break
                seenV[nb] = True; fr_ = nb; E = stp
            reachOwn[s] = E; Rg = min(Rg, E)
        geoInfo[s] = (np.array(sorted({int(b) for r in members[s] for (b, k) in rimOf[r]}), dtype=np.int64), Rg, (np.setdiff1d(domStop[s], domWeak[s]) if (isObj and (A.twosided or A.twosided_all)) else None))
if closeStat:
    print(f'closure (masked objects): closed {sum(cs["closed"] for cs in closeStat.values())}, open {sum(cs["open"] for cs in closeStat.values())} marches')
comp.astype(np.int32).tofile(f'{OUT}/comp.i32')
if A.patches: compJ.astype(np.int32).tofile(f'{OUT}/compJ.i32')
if A.reach: print(f'own extent vs hole depth: surfaces whose extent bounds the reach {int((reachOwn < reachMax).sum())} of {nS}; extent median {int(np.median(reachOwn))}, hole depth median {int(np.median(reachMax))}')
print(f'domains: stop median {int(np.median([len(d) for d in domStop]))} texels, extend median {int(np.median([len(d) for d in domExt]))}  ({time.time() - T0:.1f}s)')

# ---- 3 strips + 4 planes ----
def strip_of(s):
    W = int(reachMax[s]) + 1; cm = comp.reshape(ph, pw) == compOfSurf[s]
    seed = np.ones((ph, pw), bool); rr = np.array(members[s]); seed[rr // pw, rr % pw] = False
    ys_, xs_ = rr // pw, rr % pw; y0_, y1_ = max(0, ys_.min() - W), min(ph, ys_.max() + W + 1); x0_, x1_ = max(0, xs_.min() - W), min(pw, xs_.max() + W + 1)
    dist = ndimage.distance_transform_edt(seed[y0_:y1_, x0_:x1_])
    m = (dist <= W) & cm[y0_:y1_, x0_:x1_]
    yy, xx = np.nonzero(m); return (yy + y0_) * pw + (xx + x0_)
hedge = np.zeros(nS, bool); planes = np.zeros((nS, 3)); isSky = np.zeros(nS, bool); stripN = np.zeros(nS, int); isThin = np.zeros(nS, bool); isGround = np.zeros(nS, bool); isGroundSurf = np.zeros(nS, bool)
for s in range(nS):
    if all(dQ.flat[r] < skyQ for r in members[s]): isSky[s] = True; continue
    st = strip_of(s); stripN[s] = len(st)
    X = st % pw; Y = st // pw; V = DISP.ravel()[st]
    # THIN EVIDENCE (the app's rule, evalRun): a surface whose strip is shorter than the gap it must cross has a slope uncertain
    # by more than a quantum at the far end and is not extrapolated — it continues at constant disparity (the strip's mean).
    # In 2-D the strip's extent along each axis is measured against the reach along that axis.
    # a surface whose rim texels are the ground's own texels IS the ground: the ground sheet (meta.ground) carries it (the app's
    # thin rule sends a thin ground run along the fitted ground plane for the same reason)
    # a surface whose rim texels are the ground's own texels follows the fitted ground plane (the app sends thin ground runs along
    # it for the same reason: the plane is exact on the kit and the local strip may be too short along the reach axis)
    if (not A.no_ground) and meta.get('ground') and gtex is not None and np.mean([gtex[r] for r in members[s]]) > 0.5:
        g = meta['ground']; planes[s] = (g['a'], g['b'], g['c']); isGroundSurf[s] = True; stripN[s] = len(st); continue
    # per axis: the strip's extent along the axis against the reach along that axis (the app's w = min(len, g + 1) rule);
    # a slope the strip cannot support is not extrapolated (constant along that axis)
    extX = X.max() - X.min() + 1; extY = Y.max() - Y.min() + 1
    # NO AREA, NO SURFACE (S35 §14): a strip whose texels are collinear along a grid line (extent 1 along an axis) is a line, not
    # a surface — three non-collinear points determine a plane, collinear ones only a line. On vermeer these are DA3's one-texel
    # silhouette ramps (0.24–0.32 between the skirt at 0.33 and the floor at 0.056): behind the texel by more than a step, so
    # legitimate far rims under the app's candidate rule, and nearer than the floor, so under the layered order they won the
    # whole band behind her legs (fill 0.32–0.45 where the floor is 0.06–0.10). No sheet; the surface behind shows.
    if extX < 2 or extY < 2: isGround[s] = True; continue
    # The app's thin rule per LINE (S7b): g + 1 samples put the slope's error at half a quantum over g texels — an error budget.
    # A 2-D strip fits one slope from many lines at once: the least-squares slope error falls as 1/((extent − 1)·√lines), so the
    # same budget over the reach g is met when (extent − 1)·√(lines) ≥ g. (Vermeer's floor: 170 rows × 300 columns must carry
    # its slope 600 rows up behind the woman; per line it is thin, as a strip it is not.)
    nLinesX = len(np.unique(Y)); nLinesY = len(np.unique(X))   # lines available for the x-slope (rows) and the y-slope (columns)
    useX = extX >= 3 and (reachX[s] == 0 or (extX - 1) * np.sqrt(nLinesX) >= reachX[s]); useY = extY >= 3 and (reachY[s] == 0 or (extY - 1) * np.sqrt(nLinesY) >= reachY[s])
    hedge[s] = not (useX and useY)   # constant along at least one axis: a hedge along that axis
    cols = [np.ones_like(X, float)] + ([X] if useX else []) + ([Y] if useY else [])
    if not (useX or useY):
        isThin[s] = True
        if A.drop_thin2: isGround[s] = True; continue   # no extent along either axis: no sheet; the surface behind shows
    # a rim whose strip holds fewer than three texels cannot support the model (three samples define a plane; two a line): it is a
    # ramp sample at a silhouette, not a surface — no sheet (the next surface behind shows). Before this rule S26 had 1- and 2-rim
    # sheets at constant depth winning 1-texel lines against the ground (109 k of 141 k jump length at sheet boundaries).
    if len(st) < 3: isGround[s] = True; continue
    Amat = np.stack(cols, 1)
    keep = np.ones(len(st), bool)
    for _ in range(2):
        c, *_ = np.linalg.lstsq(Amat[keep], V[keep], rcond=None); res = V - Amat @ c
        mad = np.median(np.abs(res[keep] - np.median(res[keep]))) * 1.4826
        if mad <= 0: break
        keep = np.abs(res) <= 3 * mad
    full = [c[0], 0.0, 0.0]; k = 1
    if useX: full[1] = c[k]; k += 1
    if useY: full[2] = c[k]
    planes[s] = full
# diagnostic: does the largest surface's strip contain the occluder? (its rims are far; texels much nearer than the rims are not that surface)
try:
    sBig = int(np.argmax(np.where(isSky, -1, stripN))); stB = strip_of(sBig); rr = np.array(members[sBig]); dR = DISP.ravel()[rr]; dS = DISP.ravel()[stB]; tR = np.median(TOL.ravel()[rr])
    near = dS > np.percentile(dR, 90) + 20 * tR
    print(f'strip check, largest surface {sBig}: {len(stB)} strip texels, {len(rr)} rims; rim disparity median {np.median(dR):.3f} (p10 {np.percentile(dR,10):.3f}, p90 {np.percentile(dR,90):.3f}); strip texels nearer than the rims by > 20 tol: {int(near.sum())} ({100*near.mean():.1f} %), their disparity median {np.median(dS[near]) if near.any() else 0:.3f}; band texels own disparity median {np.median(DISP[band]):.3f}')
except Exception as e: print('strip check failed', e)
print(f'planes fitted: {int((~isSky & ~isThin & ~isGround & ~isGroundSurf).sum())} full, {int(isThin.sum())} thin (constant), {int(isSky.sum())} sky, {int(isGroundSurf.sum())} on the ground plane, {int(isGround.sum())} dropped (strip under three texels); strip texels median {int(np.median(stripN[~isSky & ~isGround])) if (~isSky & ~isGround).any() else 0}  ({time.time() - T0:.1f}s)')

# ---- 4b residual extension per surface over its domain (harmonic, Dirichlet at the surface's rim texels) ----
def harmonic_ext(dom, rim_vals):
    """dom: flat indices (band texels); rim_vals: dict rim flat index -> residual. Laplace on dom with the rim texels as
    Dirichlet neighbours, zero flux elsewhere. Returns values on dom."""
    if len(dom) == 0: return np.zeros(0)
    idx = {int(i): k for k, i in enumerate(dom)}; n = len(dom)
    rows, cols, vals = [], [], []; rhs = np.zeros(n)
    for k, i in enumerate(dom):
        x, y = int(i % pw), int(i // pw); deg = 0
        for dx, dy in DIRS:
            xn, yn = x + dx, y + dy
            if not (0 <= xn < pw and 0 <= yn < ph): continue
            j = yn * pw + xn
            if j in idx: rows.append(k); cols.append(idx[j]); vals.append(-1.0); deg += 1
            elif j in rim_vals: rhs[k] += rim_vals[j]; deg += 1
        rows.append(k); cols.append(k); vals.append(max(deg, 1))
    Lm = sparse.csr_matrix((vals, (rows, cols)), shape=(n, n))
    try: h = spsolve(Lm.tocsc(), rhs)
    except Exception: h, _ = cg(Lm, rhs)
    return h

# ---- local tangent planes (--local): for every rim texel a plane in disparity over the component texels within its window
# (w = the longest march its band texels make + 1, the app's min(len, g + 1) in 2-D), trimmed at 3 MAD; a domain texel's sheet
# value is the Shepard (1/g, p = 1 — the app's band-fill weights) blend of the local planes of the rims whose marches reach it.
localPlane = {}
def fit_local(r, W):
    cm = comp.reshape(ph, pw) == comp[r]; x0_, y0_ = r % pw, r // pw
    ys0, ys1 = max(0, y0_ - W), min(ph, y0_ + W + 1); xs0, xs1 = max(0, x0_ - W), min(pw, x0_ + W + 1)
    sub = cm[ys0:ys1, xs0:xs1]; yy, xx = np.nonzero(sub); yy = yy + ys0; xx = xx + xs0
    d2 = (yy - y0_) ** 2 + (xx - x0_) ** 2; keep = d2 <= W * W; yy = yy[keep]; xx = xx[keep]
    if len(yy) > 2000: sel = np.linspace(0, len(yy) - 1, 2000).astype(int); yy = yy[sel]; xx = xx[sel]
    V = DISP[yy, xx]
    if len(V) < 3: return (float(np.median(V)) if len(V) else float(DISP.flat[r]), 0.0, 0.0)
    extX = xx.max() - xx.min() + 1; extY = yy.max() - yy.min() + 1
    cols = [np.ones(len(V))] + ([xx.astype(float)] if extX >= 3 else []) + ([yy.astype(float)] if extY >= 3 else [])
    Am = np.stack(cols, 1); kp = np.ones(len(V), bool)
    for _ in range(2):
        c, *_ = np.linalg.lstsq(Am[kp], V[kp], rcond=None); res = V - Am @ c
        mad = np.median(np.abs(res[kp] - np.median(res[kp]))) * 1.4826
        if mad <= 0: break
        kp = np.abs(res) <= 3 * mad
    full = [c[0], 0.0, 0.0]; k = 1
    if extX >= 3: full[1] = c[k]; k += 1
    if extY >= 3: full[2] = c[k]
    return tuple(full)
if A.local:
    tl0 = time.time()
    for s_ in range(nS):
        if isSky[s_]: continue
        for r in members[s_]:
            W = 1 + max(0, max((len(dom_march(b, k)) for (b, k) in rimOf[r]), default=0))
            localPlane[r] = fit_local(r, W)
    print(f'local planes: {len(localPlane)} fitted  ({time.time() - tl0:.1f}s)')
# ---- the 2-D geodesic domain of one sheet (S35 §14), computed on demand: storing 4 311 discs was 14 GB ----
def geo_domain(s):
    if not (A.geo and s in geoInfo): return domStop[s], None
    entries, R, closedSet = geoInfo[s]; src_ = domStop[s]
    if closedSet is None: wsrc = np.zeros(len(src_), bool)
    else: wsrc = ~np.isin(src_, closedSet)
    seen = np.zeros(N, bool); lab_ = np.zeros(N, bool); seen[src_] = True; lab_[src_] = wsrc; front = src_
    for _ in range(R):
        if len(front) == 0: break
        x_ = front % pw; y_ = front // pw; nb = []; pl_ = []
        for dx, dy in DIRS:
            okn_ = (x_ + dx >= 0) & (x_ + dx < pw) & (y_ + dy >= 0) & (y_ + dy < ph); nb.append(front[okn_] + dy * pw + dx); pl_.append(lab_[front[okn_]])
        nb = np.concatenate(nb); pl_ = np.concatenate(pl_); nb, first = np.unique(nb, return_index=True); pl_ = pl_[first]
        keep_ = band.ravel()[nb] & ~seen[nb]; nb = nb[keep_]; pl_ = pl_[keep_]; seen[nb] = True; lab_[nb] = pl_; front = nb
    seen[np.array(members[s], dtype=np.int64)] = False
    return np.flatnonzero(seen), lab_
# ---- the smoothing thin-plate sheet (--tps): the deformed plane. Unknown u over strip ∪ domain; energy
#   Σ_strip (u − disp)² / σ² + λ Σ (u_xx² + 2 u_xy² + u_yy²)
# σ = the strip's own noise (S21's estimator: third differences, MAD → σ, Var(Δ³) = 20σ²), floored at the grid's quantisation
# noise grid/√12; λ by the discrepancy principle (Morozov 1966): the strip's RMS residual equals σ. Free boundary elsewhere:
# the sheet continues the strip's shape into the hole with least bending and relaxes to an affine continuation far from it.
tpsU = {}
def tps_sheet(s_, st, dom):
    om = np.unique(np.concatenate([st, dom])); n = len(om); pos = {int(i): k for k, i in enumerate(om)}
    inO = np.zeros(N, bool); inO[om] = True; kOf = np.full(N, -1, np.int64); kOf[om] = np.arange(n)
    X = om % pw; Y = om // pw
    rows, cols, vals = [], [], []; nr = 0
    def add(coefs):
        nonlocal nr
        for j, c in coefs: rows.append(nr); cols.append(j); vals.append(c)
        nr += 1
    # bending rows (vectorised assembly)
    def stencil(offs, ws):
        nonlocal nr
        ok = np.ones(n, bool); ks = []
        for (dx, dy) in offs:
            xn = X + dx; yn = Y + dy; inside = (xn >= 0) & (xn < pw) & (yn >= 0) & (yn < ph)
            kk = np.full(n, -1, np.int64); kk[inside] = kOf[(yn[inside] * pw + xn[inside])]; ok &= kk >= 0; ks.append(kk)
        idxs = np.flatnonzero(ok); m = len(idxs)
        for kk, w in zip(ks, ws): rows.append(np.arange(nr, nr + m)); cols.append(kk[idxs]); vals.append(np.full(m, float(w)))
        nr += m
    rows = []; cols = []; vals = []
    stencil([(-1, 0), (0, 0), (1, 0)], [1, -2, 1]); stencil([(0, -1), (0, 0), (0, 1)], [1, -2, 1]); stencil([(0, 0), (1, 0), (0, 1), (1, 1)], [np.sqrt(2), -np.sqrt(2), -np.sqrt(2), np.sqrt(2)])
    B = sparse.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(nr, n))
    # data rows
    kS = kOf[st]; d = DISP.ravel()[st]
    # noise of the strip: third differences along x within the strip
    inS = np.zeros(N, bool); inS[st] = True
    sx = st % pw; sy = st // pw; ok3 = (sx + 3 < pw); t0 = st[ok3]; t1 = t0 + 1; t2 = t0 + 2; t3 = t0 + 3; ok3b = inS[t1] & inS[t2] & inS[t3]
    d3 = DISP.ravel()[t0[ok3b]] - 3 * DISP.ravel()[t1[ok3b]] + 3 * DISP.ravel()[t2[ok3b]] - DISP.ravel()[t3[ok3b]]
    sig = (np.median(np.abs(d3 - np.median(d3))) * 1.4826 / np.sqrt(20)) if len(d3) > 20 else 0.0
    gridSig = abs(float(disp(min(1.0, np.median(dQ.ravel()[st]) + 1 / 65535)) - disp(max(0.0, np.median(dQ.ravel()[st]) - 1 / 65535)))) / 2 / np.sqrt(12)
    sig = max(sig, gridSig)
    Dm = sparse.csr_matrix((np.ones(len(st)) / sig, (np.arange(len(st)), kS)), shape=(len(st), n)); b = d / sig
    BtB = (B.T @ B).tocsr(); DtD = (Dm.T @ Dm).tocsr(); Dtb = Dm.T @ b
    # SOLVER (S35 §14): Jacobi-preconditioned CG did not converge on the large systems (vermeer's wall+floor: 870 k unknowns; the
    # biharmonic operator's condition number grows as n^2) — it returned the data on the strip and ~0 on the domain, which the
    # discrepancy search then read as rms < sigma at every lambda (the "0.000" fills behind the woman in s35_mask_tps). Now:
    # smoothed-aggregation algebraic multigrid (pyamg) as the preconditioner with the bending energy's null space (the affine
    # functions 1, x, y) as the near-nullspace candidates, and the relative residual is checked after every solve.
    try: import pyamg
    except Exception: pyamg = None
    Bnull = np.stack([np.ones(n), (X - X.mean()) / max(1, X.std()), (Y - Y.mean()) / max(1, Y.std())], 1)
    def solve(lam, x0=None):
        M_ = (DtD + lam * BtB).tocsr()
        if pyamg is not None:
            ml = pyamg.smoothed_aggregation_solver(M_, B=Bnull, symmetry='symmetric', max_coarse=500); Mp = ml.aspreconditioner(cycle='V')
        else: Mp = sparse.diags(1.0 / np.maximum(M_.diagonal(), 1e-30))
        x, info = cg(M_, Dtb, x0=x0, rtol=1e-8, maxiter=2000, M=Mp)
        r_ = float(np.linalg.norm(M_ @ x - Dtb) / max(1e-300, np.linalg.norm(Dtb))); solve.worst = max(getattr(solve, 'worst', 0.0), r_)
        return x
    solve.worst = 0.0
    def rms(x): return float(np.sqrt(np.mean((x[kS] - d) ** 2)))
    # discrepancy: RMS(λ) = σ; RMS grows with λ; bracket on a log grid then bisect
    lo, hi = -8.0, 8.0; x = None; grid_ = np.linspace(lo, hi, 9); r_ = []
    for g in grid_: x = solve(10 ** g, x); r_.append(rms(x))
    r_ = np.array(r_); above = np.flatnonzero(r_ > sig)
    if len(above) == 0: lam = 10 ** hi
    elif above[0] == 0: lam = 10 ** lo
    else:
        a, bb = grid_[above[0] - 1], grid_[above[0]]
        for _ in range(6):
            mid = 0.5 * (a + bb); x = solve(10 ** mid, x)
            if rms(x) > sig: bb = mid
            else: a = mid
        lam = 10 ** (0.5 * (a + bb))
    x = solve(lam, x)
    return om, x, sig, lam, rms(x), solve.worst
if A.tps:
    tt0 = time.time()
    for s_ in range(nS):
        if isSky[s_] or isGround[s_] or isGroundSurf[s_]: continue
        st = strip_of(s_); dom = geo_domain(s_)[0]
        if len(st) < 3 or len(dom) == 0: continue
        om, x, sig, lam, rr, worst = tps_sheet(s_, st, dom); tpsU[s_] = (om, x)
        if len(dom) > 5000 or worst > 1e-6: print(f'   tps surface {s_}: {len(st)} strip, {len(dom)} domain, sigma {sig:.3e}, lambda {lam:.2e}, rms {rr:.3e}, worst relative residual {worst:.1e}{"  UNCONVERGED" if worst > 1e-6 else ""}  ({time.time() - tt0:.0f}s)')
    print(f'thin-plate sheets: {len(tpsU)} solved  ({time.time() - tt0:.1f}s)')
def harmonic_ext_fixed(dom, fixed):
    """Laplace on dom; texels in `fixed` (subset of dom) hold their value; zero flux elsewhere."""
    if len(dom) == 0: return np.zeros(0)
    idx_ = {int(i): k for k, i in enumerate(dom)}; n = len(dom)
    isF = np.zeros(n, bool); fv = np.zeros(n)
    for i, v in fixed.items():
        if i in idx_: isF[idx_[i]] = True; fv[idx_[i]] = v
    if not isF.any(): return np.zeros(n)
    rows, cols, vals = [], [], []; rhs = np.zeros(n)
    for k, i in enumerate(dom):
        if isF[k]: rows.append(k); cols.append(k); vals.append(1.0); rhs[k] = fv[k]; continue
        x, y = int(i % pw), int(i // pw); deg = 0
        for dx, dy in DIRS:
            xn, yn = x + dx, y + dy
            if not (0 <= xn < pw and 0 <= yn < ph): continue
            j = yn * pw + xn
            if j in idx_: rows.append(k); cols.append(idx_[j]); vals.append(-1.0); deg += 1
        rows.append(k); cols.append(k); vals.append(max(deg, 1))
    Lm = sparse.csr_matrix((vals, (rows, cols)), shape=(n, n))
    try: h = spsolve(Lm.tocsc(), rhs)
    except Exception: h, _ = cg(Lm, rhs)
    h = np.nan_to_num(h, nan=0.0, posinf=0.0, neginf=0.0)
    return h
def build(domains, label):
    tb = time.time()
    best = np.full(N, -np.inf); second = np.full(N, -np.inf); who = np.full(N, -1, np.int32)
    bestH = np.full(N, -np.inf); whoH = np.full(N, -1, np.int32)   # --evidence: the hedges' own order, used only where no fitted sheet reaches
    ownD = DISP.ravel(); ownT = TOL.ravel()
    for s in range(nS):
        dom = domains[s]
        if len(dom) == 0 or isGround[s]: continue
        weakSet = domWeak[s]; weakArr = None
        if A.geo and label == 'stop' and s in geoInfo: dom, weakArr = geo_domain(s)
        isHedge = ((A.evidence and hedge[s]) or fusedS[s]) and (not isSky[s])
        if isSky[s]: val = np.zeros(len(dom))
        elif A.tps:
            if s not in tpsU: continue
            om, x = tpsU[s]; look = np.full(N, np.nan); look[om] = x; val = look[dom]
            if np.isnan(val).any(): val = np.where(np.isnan(val), -np.inf, val)
        elif A.local:
            acc = np.zeros(N); wsum = np.zeros(N)
            for r in members[s]:
                pl = localPlane.get(r)
                if pl is None: continue
                for (b, k) in rimOf[r]:
                    m_ = np.array(dom_march(b, k), dtype=np.int64)
                    if len(m_) == 0: continue
                    g = np.arange(1, len(m_) + 1, dtype=float) + (abs((b % pw) - (r % pw)) + abs((b // pw) - (r // pw)))   # distance from the rim along the line
                    v_ = pl[0] + pl[1] * (m_ % pw) + pl[2] * (m_ // pw); wgt = 1.0 / g
                    np.add.at(acc, m_, wgt * v_); np.add.at(wsum, m_, wgt)
            val = np.where(wsum[dom] > 0, acc[dom] / np.maximum(wsum[dom], 1e-12), -np.inf)
        else:
            X = dom % pw; Y = dom // pw; val = planes[s, 0] + planes[s, 1] * X + planes[s, 2] * Y
            if not A.no_residual:
                resid = lambda r: float(DISP.flat[r] - (planes[s, 0] + planes[s, 1] * (r % pw) + planes[s, 2] * (r // pw)))
                # Dirichlet data sits on the ENTRY texel of each march (the band texel next to the rim's run), valued with its rim's
                # residual; entry texels are inside the domain, so they are fixed rather than treated as neighbours
                ev = {}
                for r in members[s]:
                    rr = resid(r)
                    for (bb, k) in rimOf[r]: ev[int(bb)] = rr
                val = val + harmonic_ext_fixed(dom, ev)
        # the app's candidate test (dlt > tol): only a sheet BEHIND the texel's own depth by more than the tolerance is a far side of
        # that texel; a sheet at or in front of it (the occluder's own body continued, a fringe texel's own surface) is not.
        ok = val < ownD[dom] - ownT[dom]; d = dom[ok]; v = val[ok]
        if A.mask and len(d):
            # an object's own farther parts are a far side of its own band only where nothing else is (self-occlusion may sample
            # itself, S26/S27; a clone of the object shown as its background may not): same-id texels go to the hedge tier
            sid_ = int(np.median(oid.ravel()[np.array(members[s])]))
            if sid_ > 0:
                same = oid.ravel()[d] == sid_
                if same.any():
                    ds = d[same]; vs = v[same]; bh = bestH[ds]; updh = vs > bh; bestH[ds[updh]] = vs[updh]; whoH[ds[updh]] = s
                    d = d[~same]; v = v[~same]
        if (A.twosided or A.twosided_all) and (weakArr is not None or len(weakSet)):
            wk = weakArr[d] if weakArr is not None else np.isin(d, weakSet)
            if wk.any():
                dw = d[wk]; vw = v[wk]; bh = bestH[dw]; updh = vw > bh; bestH[dw[updh]] = vw[updh]; whoH[dw[updh]] = s
                d = d[~wk]; v = v[~wk]
        if isHedge:
            bh = bestH[d]; updh = v > bh; bestH[d[updh]] = v[updh]; whoH[d[updh]] = s; continue
        # nearest shows: update best / second
        b = best[d]; upd = v > b
        second[d[upd]] = np.maximum(second[d[upd]], b[upd]); best[d[upd]] = v[upd]; who[d[upd]] = s
        second[d[~upd]] = np.maximum(second[d[~upd]], v[~upd])
    # the ground as a sheet where the app has one
    if (not A.no_ground) and meta.get('ground') and gcol is not None:
        g = meta['ground']; dom = np.nonzero(band.ravel())[0]; X = dom % pw; Y = dom // pw
        val = g['a'] + g['b'] * X + g['c'] * Y; ok = (gcol[X] > 0) & (val > 0) & (val < ownD[dom] - ownT[dom])
        d = dom[ok]; v = val[ok]; b = best[d]; upd = v > b
        second[d[upd]] = np.maximum(second[d[upd]], b[upd]); best[d[upd]] = v[upd]; who[d[upd]] = nS
        second[d[~upd]] = np.maximum(second[d[~upd]], v[~upd])
    if A.evidence or A.twosided or A.twosided_all or A.mask:
        fill = ~np.isfinite(best) & np.isfinite(bestH); best[fill] = bestH[fill]; who[fill] = whoH[fill]
        print(f'[{label}] evidence order: hedges fill {int((fill & band.ravel()).sum())} band texels no fitted sheet reached')
    reached = np.isfinite(best) & band.ravel()
    print(f'[{label}] reached {int(reached.sum())} of {int(band.sum())} band texels ({100 * reached.mean() / max(1e-9, band.mean()):.1f} %); layer 2 on {int((np.isfinite(second) & band.ravel()).sum())}  ({time.time() - tb:.1f}s)')
    return best, second, who, reached

# disparity -> normalised depth by inverting the table
dtab = np.linspace(0, 1, 8193); ztab = ze(dtab); disptab = 1 / ztab   # disparity decreases with d? ze grows with depth behind -> disp falls as d falls (d=0 far)
order = np.argsort(disptab)
def depth_of_disp(v): return np.interp(v, disptab[order], dtab[order])

results = {}
for label, doms in ([('stop', domStop)] + ([] if A.no_extend else [('extend', domExt)])):
    best, second, who, reached = build(doms, label)
    ff = dQ.ravel().copy(); ff[reached] = np.clip(depth_of_disp(best[reached]), 0, 1); ff = ff.reshape(ph, pw)
    ff2 = np.full(N, -1.0); m2 = np.isfinite(second) & band.ravel(); ff2[m2] = np.clip(depth_of_disp(second[m2]), 0, 1); ff2 = ff2.reshape(ph, pw)
    results[label] = dict(ff=ff, ff2=ff2, who=who.reshape(ph, pw), reached=reached.reshape(ph, pw))
    ff.astype(np.float32).tofile(f'{OUT}/farField_{label}.f32'); ff2.astype(np.float32).tofile(f'{OUT}/farField2_{label}.f32'); who.astype(np.int32).tofile(f'{OUT}/who_{label}.i32')
results['perline'] = dict(ff=ffL)

# ---- scoring ----
step = A.step
rgbp = f'{P}/../../..//truthkit/out/{os.path.basename(P).split("_")[0]}/rest_rgb.png'
if not os.path.exists(rgbp) and os.path.exists(f'{P}/color.png'): rgbp = f'{P}/color.png'
base = np.asarray(Image.open(rgbp).convert('RGB').resize((pw, ph))).astype(np.float32) * 0.5 if os.path.exists(rgbp) else np.zeros((ph, pw, 3), np.float32)
def walls(ff):
    # jumps: adjacent band texels differing by more than the visible step (includes real slants); kinks: second differences
    # beyond the visible step (a slant has none; a jump or a fold has one) — the seam measure that does not count a slanted floor
    m = band; out = {}
    for key, (a, b, mm) in {'v': (ff[1:, :], ff[:-1, :], m[1:, :] & m[:-1, :]), 'h': (ff[:, 1:], ff[:, :-1], m[:, 1:] & m[:, :-1])}.items():
        d = np.abs(a - b)[mm]; out[key] = dict(edges=int(mm.sum()), above=int((d > step).sum()), length=float((d[d > step] / step).sum()))
    mv = m[2:, :] & m[1:-1, :] & m[:-2, :]; sv = np.abs(ff[2:, :] - 2 * ff[1:-1, :] + ff[:-2, :])[mv]
    mh = m[:, 2:] & m[:, 1:-1] & m[:, :-2]; sh = np.abs(ff[:, 2:] - 2 * ff[:, 1:-1] + ff[:, :-2])[mh]
    out['kv'] = dict(triples=int(mv.sum()), above=int((sv > step).sum()), length=float((sv[sv > step] / step).sum()))
    out['kh'] = dict(triples=int(mh.sum()), above=int((sh > step).sum()), length=float((sh[sh > step] / step).sum()))
    return out
def truth_err(ff):
    z = np.load(A.truth); cls = z['cls']; w = z['w_disp'].astype(np.float32); dep = z['depth']; H, W, K = cls.shape; y0 = (H - ph) // 2; x0 = (W - pw) // 2
    cls_c = cls[y0:y0 + ph, x0:x0 + pw]; w_c = w[y0:y0 + ph, x0:x0 + pw]; dep_c = dep[y0:y0 + ph, x0:x0 + pw]
    vis = (cls_c >= 2) & (cls_c <= 5) & (w_c > 0); has = vis.any(-1); kk = np.argmax(vis, -1); d_true = np.take_along_axis(dep_c, kk[..., None], -1)[..., 0]
    d_app = -z_of_d(ff); m = band & has & np.isfinite(d_true); e = (d_app - d_true)[m]
    return dict(n=int(m.sum()), mean=float(e.mean()), median_abs=float(np.median(np.abs(e))), p90_abs=float(np.percentile(np.abs(e), 90)))
def kink_breakdown(ff, who):
    # vertical kinks (|second difference| > step) split by who owns the three texels: all one sheet / a sheet boundary / an own or unreached texel involved
    m = band; out = {}
    for key, (a, b, c, mm) in {'v': (ff[2:, :], ff[1:-1, :], ff[:-2, :], m[2:, :] & m[1:-1, :] & m[:-2, :]), 'h': (ff[:, 2:], ff[:, 1:-1], ff[:, :-2], m[:, 2:] & m[:, 1:-1] & m[:, :-2])}.items():
        sd = np.abs(a - 2 * b + c); k = mm & (sd > step)
        if key == 'v': w0, w1, w2 = who[2:, :], who[1:-1, :], who[:-2, :]
        else: w0, w1, w2 = who[:, 2:], who[:, 1:-1], who[:, :-2]
        own = (w0 < 0) | (w1 < 0) | (w2 < 0); same = (w0 == w1) & (w1 == w2) & ~own; bnd = ~same & ~own
        L = sd / step
        out[key] = {'same_sheet': [int((k & same).sum()), float(L[k & same].sum())], 'sheet_boundary': [int((k & bnd).sum()), float(L[k & bnd].sum())], 'own_or_unreached': [int((k & own).sum()), float(L[k & own].sum())]}
        # map: 1 same, 2 boundary, 3 own
        cm = np.zeros(ff.shape, np.uint8); pad = (slice(1, -1), slice(None)) if key == 'v' else (slice(None), slice(1, -1))
        cm[pad] = np.where(k & same, 1, np.where(k & bnd, 2, np.where(k & own, 3, 0)))
        out[key + '_map'] = cm
    return out
summary = {'scene': os.path.basename(P), 'band': int(band.sum()), 'rims': int(nR), 'surfaces': int(nS), 'step': step, 'arms': {}}
for label in [l for l in ('perline', 'stop', 'extend') if l in results]:
    r = {}
    if step: r['walls'] = walls(results[label]['ff'])
    if A.truth: r['truth'] = truth_err(results[label]['ff'])
    if label != 'perline':
        r['reached'] = int(results[label]['reached'].sum())
        if step:
            kb = kink_breakdown(results[label]['ff'], results[label]['who']); r['kinks'] = {k: v for k, v in kb.items() if not k.endswith('_map')}
            for key in ('v', 'h'):
                img = base.copy() if 'base' in globals() else np.zeros((ph, pw, 3), np.float32)
                cm = kb[key + '_map']; img[band] = img[band] * 0.5 + 90; img[cm == 1] = (255, 60, 60); img[cm == 2] = (60, 120, 255); img[cm == 3] = (255, 220, 0)
                Image.fromarray(img.clip(0, 255).astype(np.uint8)).save(f'{OUT}/kinks_{key}_{label}.png')
            print(f"   kinks by owner ({label}): v same-sheet {kb['v']['same_sheet']}, boundary {kb['v']['sheet_boundary']}, own/unreached {kb['v']['own_or_unreached']}; h same {kb['h']['same_sheet']}, boundary {kb['h']['sheet_boundary']}, own {kb['h']['own_or_unreached']}")
    summary['arms'][label] = r
    w = r.get('walls', {}).get('v', {}); tr = r.get('truth', {})
    W = r.get('walls', {}); kv = W.get('kv', {}); kh = W.get('kh', {})
    print(f"{label:8} jumps v {w.get('above', '-')} (len {w.get('length', 0):.0f}) h {W.get('h', {}).get('above', '-')} (len {W.get('h', {}).get('length', 0):.0f}) | kinks v {kv.get('above', '-')} (len {kv.get('length', 0):.0f}) h {kh.get('above', '-')} (len {kh.get('length', 0):.0f}) | truth median {tr.get('median_abs', float('nan')):.4f} m p90 {tr.get('p90_abs', float('nan')):.4f} mean {tr.get('mean', float('nan')):+.4f} (n {tr.get('n', '-')})")
rimInfo = []
for s_ in range(nS):
    rr = np.array(members[s_]); rimInfo.append({'rows': [int((rr // pw).min()), int((rr // pw).max())], 'cols': [int((rr % pw).min()), int((rr % pw).max())], 'depth': float(np.median(dQ.ravel()[rr])), 'oid': (int(np.median(oid.ravel()[rr])) if A.mask else -1), 'hedge': bool(hedge[s_]) if 'hedge' in globals() else None, 'fused': bool(fusedS[s_]), 'fusedFrac': (None if np.isnan(fusedFrac[compOfSurf[s_]]) else float(fusedFrac[compOfSurf[s_]]))})
summary['rims'] = rimInfo
summary['surfaceSizes'] = sizes.tolist(); summary['thin'] = isThin.tolist(); summary['ground'] = isGround.tolist(); summary['sky'] = isSky.tolist(); summary['stripN'] = stripN.tolist(); summary['reachMax'] = reachMax.tolist()
json.dump(summary, open(f'{OUT}/summary_{A.tag}.json', 'w'), indent=1)

# ---- figures ----
rng = np.random.default_rng(1); pal = rng.integers(60, 255, (nS + 2, 3))
img = base.copy(); who = results['stop']['who']; m = who >= 0; img[m] = pal[who[m]]
for r in rims: img[r // pw, r % pw] = (255, 255, 255)
Image.fromarray(img.clip(0, 255).astype(np.uint8)).save(f'{OUT}/surfaces_stop.png')
def depth_img(ff, name):
    v = np.clip(ff, 0, 1); img = base.copy(); img[band] = (np.stack([v, v, v], -1)[band] * 255)
    Image.fromarray(img.clip(0, 255).astype(np.uint8)).save(f'{OUT}/{name}.png')
for label in [l for l in ('perline', 'stop', 'extend') if l in results]: depth_img(results[label]['ff'], f'far_{label}')
print(f'wrote {OUT}  ({time.time() - T0:.1f}s)')
