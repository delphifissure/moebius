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
for _v in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'): os.environ.setdefault(_v, '1')   # S35 §19: forked plate workers oversubscribed BLAS threads (S15: 29 s serial -> 336 s with 3 workers)
import numpy as np
from scipy import ndimage, sparse
from scipy.sparse.linalg import spsolve, cg
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument('probe'); ap.add_argument('--truth'); ap.add_argument('--step', type=float); ap.add_argument('--q', type=float, default=1 / 65535)
ap.add_argument('--out'); ap.add_argument('--tag', default='sheets'); ap.add_argument('--no-ground', action='store_true'); ap.add_argument('--no-residual', action='store_true'); ap.add_argument('--no-extend', action='store_true'); ap.add_argument('--drop-thin2', action='store_true', help='a surface thin along both axes is not extrapolated at all'); ap.add_argument('--local', action='store_true', help='sheet = Shepard blend of local tangent planes fitted around each rim texel (2-D windows), instead of one plane + pinned residual'); ap.add_argument('--mask', help='object-id PNG (0 = background): texels of different ids are never joined, so an object is its own surface and never part of its background'); ap.add_argument('--merge', action='store_true', help='merge a visible fragment into an adjacent surface when its texels lie within the join tolerance of that surface\'s fitted plane (regional join instead of pairwise)'); ap.add_argument('--evidence', action='store_true', help='a sheet extrapolated at constant depth along a thin axis is a hedge, not a measurement: where a fully fitted sheet also lies behind the texel, the fitted sheet shows'); ap.add_argument('--twosided', action='store_true', help='an OBJECT surface (mask id > 0) passes behind an occluder only where its own rims close the span on both sides of the line (S3 kind-2: a same-surface pair is a positive detection); a one-sided march of an object sheet is a hedge'); ap.add_argument('--twosided-all', action='store_true', help='the two-sided rule for every surface, not only masked objects (backgrounds end at corners too); the ground plane is the exception'); ap.add_argument('--fused', action='store_true', help='a visible component whose boundary to other mask ids is depth-JOINED on the majority of its length is fused with its neighbours (DA3 gives a narrow background gap between two near objects the objects\' depth); its sheet is a hedge, never a measurement'); ap.add_argument('--planeprior', action='store_true', help="the thin plate is pulled toward its own face's plane on the domain with weight 1/visible step, against the strip data at weight 1/sigma: the plate is free to bend where the data supports it and relaxes to the plane where it does not"); ap.add_argument('--smooth', action='store_true', help="faceting: adjacent planar patches of one surface are rejoined when their planes differ by less than the visible step over the smaller patch's own extent (a crease test, not a flatness test), so a smoothly curved surface is one face again and only real creases stay split"); ap.add_argument('--budget', action='store_true', help="per-texel error budget: the fitted slope is shrunk by its own predicted standard error against the visible step, so a sheet continues its slope only as far as its own fit supports it and relaxes to its constant beyond that; continuous, no new constant"); ap.add_argument('--faces', action='store_true', help="faceting: every facet of one join-law component is extended over that component's whole 2-D domain instead of its own disc, so the layered order picks the nearest facet everywhere and the sheet is continuous, with creases where the facets' planes cross"); ap.add_argument('--reach', action='store_true', help="where a sheet ends: it continues into the hole no farther than the surface itself extends outside it (geodesic radius of its own visible patch from its rims), instead of as far as the hole is deep"); ap.add_argument('--geo', action='store_true', help='2-D domain: a sheet claims the band texels within geodesic reach of its rims through the band (reach = its own longest march) instead of the along-line marches only'); ap.add_argument('--patches', action='store_true', help='split every visible component into planar patches (region growing; a texel joins while one plane fits the patch within the visible step tolAt); patches are the surfaces'); ap.add_argument('--tps', action='store_true', help='sheet = smoothing thin plate over strip + domain, data weighted by the strip noise, lambda by the discrepancy principle')
ap.add_argument('--color', action='store_true', help="per-sheet colour (S35 §25): every band texel's colour is its OWN sheet's visible colour continued over the texels that sheet owns (harmonic extension per sheet), never a per-line rim window; the source's anti-aliased fringe at each silhouette is measured on the picture and left unanchored")
ap.add_argument('--rgb', help='the source colour image (defaults to <dump>/color.png)')
ap.add_argument('--things', action='store_true', help='things/surfaces classifier (S35 §22, opt-in): every visible unit (mask segment or depth component) that is in front of a neighbour becomes a two-sided thing, the rest background. Fixes the sunflower staircase, S9 and S2; wrong on the troll (x-ray to the deepest surface behind him), on vermeer with the automatic mask (the floor voted a thing) and on S15 (a canopy behind its own trunk) -- see the note'); ap.add_argument('--jobs', type=int, default=3, help='parallel workers for the thin-plate solves (forked; the parent holds ~4 GB on vermeer and each worker adds the matrices of one face)'); ap.add_argument('--plain', action='store_true', help='turn the adopted construction off and run the bare per-surface plane arm (for A/B against the old arms)')
ap.add_argument('--no-smooth', action='store_true'); ap.add_argument('--no-tps', action='store_true'); ap.add_argument('--no-prior', action='store_true'); ap.add_argument('--no-patches', action='store_true')
ap.add_argument('--no-evidence', action='store_true'); ap.add_argument('--no-geo', action='store_true'); ap.add_argument('--no-fused', action='store_true'); ap.add_argument('--no-twosided', action='store_true'); ap.add_argument('--no-drop-thin2', action='store_true')
A = ap.parse_args()
# ---- ADOPTED DEFAULTS (S35 §18). The construction recommended in §17 is what runs when no flags are given: object mask (when
# one is supplied) -> fusion by body match -> planar patches -> crease-test merge into faces -> no-area rule -> 2-D geodesic
# domain -> thin plate with the plane prior on merged faces, plane elsewhere -> specks dropped -> evidence order -> two-sided
# for masked objects. Every part has a --no-<part> switch, and --plain turns the lot off for an A/B against the earlier arms.
if not A.plain:
    A.patches = not A.no_patches; A.smooth = not A.no_smooth; A.tps = not A.no_tps; A.planeprior = not A.no_prior
    A.evidence = not A.no_evidence; A.geo = not A.no_geo; A.fused = not A.no_fused; A.drop_thin2 = not A.no_drop_thin2
    A.twosided = bool(A.mask) and not A.no_twosided; A.no_extend = True
    # the rim-pinned harmonic residual is OFF by default (S35 §19): §11 measured that following each rim's residual brings the
    # map's own noise back into the sheet, and the §14 recommendation ran without it. It also turned out to be the whole cost of
    # the layered order — a sparse Laplace solve per sheet, assembled in Python (sunflowers: 59.5 s of the 62.9 s pass). Off, the
    # kit is unchanged to within solver noise (S2 0.0121, S9 0.0320, S15 0.0717, S26 0.0252) and the pass costs 3.3 s.
    A.no_residual = True
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
_dt = np.linspace(0, 1, 4097); _dsp = disp(_dt); _ord = np.argsort(_dsp)
def depth_of_disp_early(v): return float(np.interp(v, _dsp[_ord], _dt[_ord])) if np.isfinite(v) else float('nan')
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
oid = np.zeros((ph, pw), np.int32)
if A.mask:
    # S35 object-aware surfaces: an object mask (SAM, S28/S29) separates the occluder from its background where the depth map
    # joins them (contact points, ramps); pairs of different ids are unjoined, so runs, components and strips stop at the mask
    oid = np.asarray(Image.open(A.mask)); oid = oid[..., 0] if oid.ndim == 3 else oid
    if oid.shape != (ph, pw): oid = np.asarray(Image.fromarray(oid).resize((pw, ph), Image.NEAREST))
    oid = oid.astype(np.int32)
jh0 = jh.copy(); jv0 = jv.copy()   # the depth law's own verdict on every pair, kept for the fusion test (--fused)
if A.things:
    # THINGS AND SURFACES (S35 §22). A segmentation says where the pieces are, not which of them are bounded things. SAM's
    # automatic mode labels the sky, the ground plain and every brick as a segment (starwatcher: the sky is 40 % of the picture
    # and passes the 60 % background cut; S9: 205 segments, the bricks and the tiles among them), and leaves the tangled part
    # of a thicket unlabelled (sunflowers: 26 % of the picture), which "unlabelled = background" then extends into every hole.
    # The depth map says which is which, and it says it for every visible UNIT: a SAM segment where there is one, a join-law
    # component of the depth map otherwise. A unit is a THING if it is in front of at least one neighbouring unit along the
    # majority of their shared boundary AND by the two units' median depths (the local and the global verdict must agree: at the
    # horizon DA3 puts the distant field farther than the sky, so by boundary pairs alone the sky was "in front"; the floor is
    # nearer than the wall by medians but joined to it along the crease); neighbours whose shared boundary is shorter than the
    # median shared boundary of that unit do not vote. Things keep or get an id; surfaces become background. No constant.
    tb0 = time.time()
    from scipy.sparse.csgraph import connected_components as _cc
    bg = (oid == 0).ravel(); Ih_ = idx[:, :-1].ravel(); Jh_ = idx[:, 1:].ravel(); Iv_ = idx[:-1, :].ravel(); Jv_ = idx[1:, :].ravel()
    okh_ = jh0.ravel() & bg[Ih_] & bg[Jh_]; okv_ = jv0.ravel() & bg[Iv_] & bg[Jv_]
    adj_ = sparse.coo_matrix((np.ones(int(okh_.sum()) + int(okv_.sum())), (np.r_[Ih_[okh_], Iv_[okv_]], np.r_[Jh_[okh_], Jv_[okv_]])), shape=(N, N))
    nC_, cbg = _cc(adj_, directed=False)
    unit = np.where(bg, 256 + cbg, oid.ravel()).astype(np.int64); nU = int(unit.max()) + 1
    cutH_ = (unit.reshape(ph, pw)[:, :-1] != unit.reshape(ph, pw)[:, 1:]); cutV_ = (unit.reshape(ph, pw)[:-1, :] != unit.reshape(ph, pw)[1:, :])
    T_ = np.r_[idx[:, :-1][cutH_], idx[:-1, :][cutV_], idx[:, 1:][cutH_], idx[1:, :][cutV_]]; U_ = np.r_[idx[:, 1:][cutH_], idx[1:, :][cutV_], idx[:, :-1][cutH_], idx[:-1, :][cutV_]]
    dT = DISP.ravel()[T_]; dU = DISP.ravel()[U_]; tl_ = np.maximum(TOL.ravel()[T_], TOL.ravel()[U_]); uT = unit[T_]; uU = unit[U_]
    key_ = uT * nU + uU; uk_, inv_ = np.unique(key_, return_inverse=True)
    nAB = np.bincount(inv_, minlength=len(uk_)); fAB = np.bincount(inv_, weights=(dT > dU + tl_), minlength=len(uk_)); bAB = np.bincount(inv_, weights=(dT < dU - tl_), minlength=len(uk_))
    ua_ = uk_ // nU; ub_ = uk_ % nU
    # per-unit median disparity and tolerance (sort-based, vectorised)
    order_ = np.argsort(unit, kind='stable'); us_ = unit[order_]; starts_ = np.r_[0, np.flatnonzero(us_[1:] != us_[:-1]) + 1]; ends_ = np.r_[starts_[1:], len(us_)]
    medD = np.full(nU, np.nan); medT = np.full(nU, np.nan); px_ = np.zeros(nU, np.int64)
    dso = DISP.ravel()[order_]; tso = TOL.ravel()[order_]
    for a_, b_ in zip(starts_, ends_): medD[us_[a_]] = np.median(dso[a_:b_]); medT[us_[a_]] = np.median(tso[a_:b_]); px_[us_[a_]] = b_ - a_
    gFront = medD[ua_] > medD[ub_] + np.maximum(medT[ua_], medT[ub_])
    # per unit: neighbours with boundary >= that unit's median boundary, in front locally and globally
    thing = np.zeros(nU, bool); rel_order = np.argsort(ua_, kind='stable'); ua_s = ua_[rel_order]; st2 = np.r_[0, np.flatnonzero(ua_s[1:] != ua_s[:-1]) + 1]; en2 = np.r_[st2[1:], len(ua_s)]
    for a_, b_ in zip(st2, en2):
        sel_ = rel_order[a_:b_]; n_ = nAB[sel_]; med_ = np.median(n_)
        thing[ua_s[a_]] = bool(((n_ >= med_) & (fAB[sel_] > bAB[sel_]) & gFront[sel_]).any())
    thing[0] = False
    if os.environ.get('THINGS_DIAG'):
        # the vote behind each large unit's verdict: its neighbours with a boundary at or above the unit's median boundary
        for u_ in np.argsort(-px_)[:int(os.environ['THINGS_DIAG'])]:
            if px_[u_] == 0: continue
            sel_ = np.flatnonzero(ua_ == u_); med_ = np.median(nAB[sel_]); rows_ = []
            for j_ in sel_[np.argsort(-nAB[sel_])][:6]:
                rows_.append(f'{"seg " + str(int(ub_[j_])) if ub_[j_] < 256 else "comp " + str(int(ub_[j_]) - 256)}({int(px_[ub_[j_]])}px, d {depth_of_disp_early(medD[ub_[j_]]):.3f}) n {int(nAB[j_])}{"*" if nAB[j_] >= med_ else ""} front {int(fAB[j_])} behind {int(bAB[j_])} gFront {int(gFront[j_])}')
            print(f'   DIAG {"seg " + str(int(u_)) if u_ < 256 else "comp " + str(int(u_) - 256)} ({int(px_[u_])} px, d {depth_of_disp_early(medD[u_]):.3f}) -> {"THING" if thing[u_] else "surface"}; median boundary {med_:.0f}; ' + ' | '.join(rows_))
    newId = np.zeros(nU, np.int32); k_ = 1
    for u_ in np.flatnonzero(thing): newId[u_] = k_; k_ += 1
    oid = newId[unit].reshape(ph, pw)
    nSeg = int((px_[1:256] > 0).sum()); nSegT = int(thing[1:256].sum()); nRem = int((px_[256:] > 0).sum()); nRemT = int(thing[256:].sum())
    print(f'things and surfaces: labelled segments {nSeg} -> {nSegT} things; unlabelled depth components {nRem} -> {nRemT} things; {k_ - 1} things in all, the rest background  ({time.time() - tb0:.1f}s)')
    big_ = np.argsort(-px_)[:10]
    for u_ in big_:
        if px_[u_] == 0: continue
        print(f'   unit {"seg " + str(int(u_)) if u_ < 256 else "comp " + str(int(u_) - 256)}: {int(px_[u_])} px, median depth {depth_of_disp_early(medD[u_]):.3f} -> {"thing" if thing[u_] else "surface"}')
    if k_ > 1 and not A.mask: A.mask = 'things'; A.twosided = not A.no_twosided
if A.mask:
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
    patch0 = comp.copy()
    curvedFace = None
    if A.smooth:
        # UNDOING THE FACETING (S35 §17). The patch grower cuts a smoothly curved surface into planar slabs (vermeer's floor
        # into row strips at 0.047 and 0.084), and 96-98 % of the far field's jump length is between facets of ONE surface.
        # Two facets belong to one smooth face when the step between their planes is invisible over the distance they span:
        # |slope_A - slope_B| * L <= tolAt, with L the smaller facet's own extent sqrt(area) — slope times length is a depth,
        # compared against the same visible step the patches were cut with, so nothing new is introduced. A real crease
        # (wall against floor) fails it by orders of magnitude and stays split. Merging never crosses a join-law break.
        ts0 = time.time(); dv_ = DISP.ravel()
        for it in range(6):
            nC = int(comp.max()) + 1
            cnt = np.bincount(comp, minlength=nC).astype(float)
            Xf = (np.arange(N) % pw).astype(float); Yf = (np.arange(N) // pw).astype(float)
            S1 = cnt; Sx = np.bincount(comp, weights=Xf, minlength=nC); Sy = np.bincount(comp, weights=Yf, minlength=nC)
            Sxx = np.bincount(comp, weights=Xf * Xf, minlength=nC); Sxy = np.bincount(comp, weights=Xf * Yf, minlength=nC); Syy = np.bincount(comp, weights=Yf * Yf, minlength=nC)
            Sv = np.bincount(comp, weights=dv_, minlength=nC); Sxv = np.bincount(comp, weights=Xf * dv_, minlength=nC); Syv = np.bincount(comp, weights=Yf * dv_, minlength=nC)
            PL = np.zeros((nC, 3))
            for c_ in range(nC):
                n_ = S1[c_]
                if n_ < 1: continue
                M_ = np.array([[n_, Sx[c_], Sy[c_]], [Sx[c_], Sxx[c_], Sxy[c_]], [Sy[c_], Sxy[c_], Syy[c_]]]); r_ = np.array([Sv[c_], Sxv[c_], Syv[c_]])
                try: PL[c_] = np.linalg.solve(M_ + 1e-9 * np.eye(3), r_)
                except np.linalg.LinAlgError: PL[c_] = (Sv[c_] / n_, 0.0, 0.0)
            Ih = idx[:, :-1].ravel(); Jh = idx[:, 1:].ravel(); Iv = idx[:-1, :].ravel(); Jv = idx[1:, :].ravel()
            PI = np.r_[Ih, Iv]; PJ = np.r_[Jh, Jv]
            okp = (comp[PI] != comp[PJ]) & (compJ[PI] == compJ[PJ]) & (dQ.ravel()[PI] >= skyQ) & (dQ.ravel()[PJ] >= skyQ)
            PI = PI[okp]; PJ = PJ[okp]
            if len(PI) == 0: break
            a_ = np.minimum(comp[PI], comp[PJ]); b_ = np.maximum(comp[PI], comp[PJ])
            key = a_ * nC + b_; uk = np.unique(key)
            ca = (uk // nC).astype(np.int64); cb = (uk % nC).astype(np.int64)
            L_ = np.sqrt(np.minimum(cnt[ca], cnt[cb]))                      # the smaller facet's own extent, in texels
            dm = np.hypot(PL[ca, 1] - PL[cb, 1], PL[ca, 2] - PL[cb, 2])     # slope difference, disparity per texel
            tolC = np.bincount(comp, weights=TOL.ravel(), minlength=nC) / np.maximum(cnt, 1.0); tolP = np.minimum(tolC[ca], tolC[cb])
            mergeable = (dm * L_) <= tolP
            par = np.arange(nC)
            def find(u):
                while par[u] != u: par[u] = par[par[u]]; u = par[u]
                return u
            nM = 0
            for i_ in np.flatnonzero(mergeable):
                ra, rb = find(int(ca[i_])), find(int(cb[i_]))
                if ra != rb: par[max(ra, rb)] = min(ra, rb); nM += 1
            if nM == 0: print(f'   smooth pass {it + 1}: nothing merged'); break
            roots = np.array([find(c_) for c_ in range(nC)]); comp = roots[comp]
            _, comp = np.unique(comp, return_inverse=True); comp = comp.astype(np.int64)
            print(f'   smooth pass {it + 1}: {nM} facet pairs merged, {int(comp.max()) + 1} faces  ({time.time() - ts0:.1f}s)')
        nComp = int(comp.max()) + 1
        # a face still made of ONE patch is planar by the patch grower's own test (its plane fits it within the visible step), so
        # it needs no plate; only merged faces are curved. This is the construction's own criterion, and it takes the thin-plate
        # solves on the sunflower field from 6 853 to the few hundred faces that are actually curved.
        curved = np.zeros(nComp, bool)
        for c0_ in range(nComp):
            pass
        pc_ = np.unique(np.stack([comp, patch0], 1), axis=0)[:, 0]
        cnts_ = np.bincount(pc_, minlength=nComp); curvedFace = cnts_ > 1
        print(f'   curved faces (merged from more than one patch): {int(curvedFace.sum())} of {nComp}')
        print(f'smooth faces: {nComp} from the patch grower\'s cut  ({time.time() - ts0:.1f}s)')
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
groupOf = (compJ[np.array([members[s][0] for s in range(nS)], dtype=np.int64)] if (A.patches and A.faces) else np.arange(nS))
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
# SPEED (S35 §19). Three costs were measured on vermeer: the marches were a Python while-loop over 339 M texel steps; the
# extend-arm domain ran a full-image np.isin for every surface although --no-extend is the default and it is never read; and
# nine surfaces in ten are specks that the very next rules drop. Now: the march length in each of the four directions comes
# from four cumulative scans over the band, the march itself is a contiguous row or column SLICE marked at C speed, the
# extend domain is built only when it is asked for, and a surface whose face is under three texels or one texel wide in
# either axis is marked dropped before any of it (its strip is a subset of its face, so the three-texel and no-area rules
# would drop it anyway — the same verdict, reached without the work).
_bandF = band.astype(np.int32)
runL = np.zeros((ph, pw), np.int32); runR = np.zeros((ph, pw), np.int32); runU = np.zeros((ph, pw), np.int32); runD = np.zeros((ph, pw), np.int32)
for x_ in range(pw): runL[:, x_] = np.where(band[:, x_], (runL[:, x_ - 1] if x_ else 0) + 1, 0)
for x_ in range(pw - 1, -1, -1): runR[:, x_] = np.where(band[:, x_], (runR[:, x_ + 1] if x_ < pw - 1 else 0) + 1, 0)
for y_ in range(ph): runU[y_, :] = np.where(band[y_, :], (runU[y_ - 1, :] if y_ else 0) + 1, 0)
for y_ in range(ph - 1, -1, -1): runD[y_, :] = np.where(band[y_, :], (runD[y_ + 1, :] if y_ < ph - 1 else 0) + 1, 0)
RUN = [runL, runR, runU, runD]   # DIRS[k] = (dx, dy); the march steps by (-dx, -dy)
_boxes = ndimage.find_objects(comp.reshape(ph, pw) + 1)
preDrop = np.zeros(nS, bool)
for s in range(nS):
    c_ = compOfSurf[s]; bx = _boxes[c_] if c_ < len(_boxes) else None
    if compSize[c_] < 3 or bx is None or (bx[0].stop - bx[0].start) < 2 or (bx[1].stop - bx[1].start) < 2: preDrop[s] = True
print(f'pre-dropped surfaces (face under three texels or one texel wide): {int(preDrop.sum())} of {nS}')
_mark = np.zeros((ph, pw), bool); _wmark = np.zeros((ph, pw), bool)
for s in range(nS):
    if preDrop[s]:
        domStop[s] = np.zeros(0, np.int64); domWeak[s] = np.zeros(0, np.int64); domExt[s] = np.zeros(0, np.int64); continue
    holes = set(); y0m = ph; y1m = -1; x0m = pw; x1m = -1; anyWeak = False
    isObj = A.twosided_all or ((oidArr is not None) and (oidArr.flat[members[s][0]] > 0))
    twoSided = isObj and (A.twosided or A.twosided_all)
    for r in members[s]:
        for (b, k) in rimOf[r]:
            dx, dy = DIRS[k]; bx_ = b % pw; by_ = b // pw; n = int(RUN[k][by_, bx_])
            if n <= 0: continue
            if k == 0: ys, ye, xs, xe = by_, by_ + 1, bx_ - n + 1, bx_ + 1
            elif k == 1: ys, ye, xs, xe = by_, by_ + 1, bx_, bx_ + n
            elif k == 2: ys, ye, xs, xe = by_ - n + 1, by_ + 1, bx_, bx_ + 1
            else: ys, ye, xs, xe = by_, by_ + n, bx_, bx_ + 1
            _mark[ys:ye, xs:xe] = True
            y0m = min(y0m, ys); y1m = max(y1m, ye); x0m = min(x0m, xs); x1m = max(x1m, xe)
            if twoSided:
                xx, yy = bx_ - dx * n, by_ - dy * n; closed = False; bid = oidArr.flat[b] if oidArr is not None else -1
                # The span is closed when the march, skipping the occluder's own id, exits onto this sheet's own join-law component.
                # Three S15-motivated variants were tried and FALSIFIED (S35 §22): closed = the same THING on the far side, closed on
                # ANY axis, and a self-occlusion stop (the first own-id texel behind the band texel closes the span). None brought S15
                # under 3 m and together they broke vermeer (v jumps 5 539 -> 16 788, the table's own folds behind the table) and
                # the troll (the skin behind the troll). The adopted rule below is the one §18 measured.
                # The span is closed when the march, skipping the occluder's own id, exits onto this sheet's own join-law component
                # (the §18 rule). FALSIFIED variants (S35 §22), all aimed at S15's canopy behind its own trunk: closed = the same
                # THING on the far side; closed on ANY axis; a self-occlusion stop (the first own-id texel behind the band texel
                # closes the span) with same-id demotion lifted on the self-revealed band. None brought S15 under 3 m; together they
                # broke vermeer (v jumps 3 339 -> 16 788: the table's own folds behind the table) and the troll (his skin behind him).
                while 0 <= xx < pw and 0 <= yy < ph:
                    i3 = yy * pw + xx; c_ = comp[i3]
                    if compSize[c_] >= 3 and not band[yy, xx] and not (oidArr is not None and oidArr.flat[i3] == bid and bid > 0): closed = (c_ == compOfSurf[s]); break
                    xx -= dx; yy -= dy
                if not closed: _wmark[ys:ye, xs:xe] = True; anyWeak = True
                cs_ = closeStat.setdefault(s, {'closed': 0, 'open': 0, 'exit': {}}); cs_['closed' if closed else 'open'] += 1
                if not closed:
                    if not (0 <= xx < pw and 0 <= yy < ph): ek = 'edge'
                    else:
                        eo = int(oidArr.flat[yy * pw + xx]) if oidArr is not None else 0
                        ek = ('bg d=%.2f' % dQ.flat[yy * pw + xx]) if eo == 0 else ('thing %d d=%.2f' % (eo, dQ.flat[yy * pw + xx]))
                    cs_['exit'][ek] = cs_['exit'].get(ek, 0) + 1
            reachMax[s] = max(reachMax[s], n)
            if not A.no_extend: holes.add(int(holeLab[by_, bx_]))
            if dx != 0: reachX[s] = max(reachX[s], n)
            else: reachY[s] = max(reachY[s], n)
    if y1m < 0: domStop[s] = np.zeros(0, np.int64); domWeak[s] = np.zeros(0, np.int64); domExt[s] = np.zeros(0, np.int64); continue
    sub = _mark[y0m:y1m, x0m:x1m]; yy_, xx_ = np.nonzero(sub); dom_ = (yy_ + y0m) * pw + (xx_ + x0m); sub[:] = False
    if anyWeak:
        subw = _wmark[y0m:y1m, x0m:x1m]; yw_, xw_ = np.nonzero(subw); domWeak[s] = np.sort((yw_ + y0m) * pw + (xw_ + x0m)); subw[:] = False
    else: domWeak[s] = np.zeros(0, np.int64)
    domStop[s] = dom_
    domExt[s] = (np.nonzero(np.isin(holeLab.ravel(), list(holes)) & band.ravel())[0] if not A.no_extend else np.zeros(0, np.int64))
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
    print(f'closure (things): closed {sum(cs["closed"] for cs in closeStat.values())}, open {sum(cs["open"] for cs in closeStat.values())} marches')
    for s_, cs in sorted(closeStat.items(), key=lambda kv: -(kv[1]['closed'] + kv[1]['open']))[:3]:
        top = sorted(cs['exit'].items(), key=lambda kv: -kv[1])[:6]
        print(f'   thing surface {s_} (id {int(oidArr.flat[members[s_][0]]) if oidArr is not None else 0}, rim depth {np.median(dQ.ravel()[np.array(members[s_])]):.3f}, {len(members[s_])} rims): closed {cs["closed"]}, open {cs["open"]}; open exits: ' + ', '.join(f'{k} x{v}' for k, v in top))
comp.astype(np.int32).tofile(f'{OUT}/comp.i32')
np.asarray(groupOf, dtype=np.int32).tofile(f'{OUT}/groupOf.i32')   # join-law component of each surface, for the faceting instrument
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
hedge = np.zeros(nS, bool); planes = np.zeros((nS, 3)); budget = {}; isSky = np.zeros(nS, bool); stripN = np.zeros(nS, int); isThin = np.zeros(nS, bool); isGround = np.zeros(nS, bool); isGroundSurf = np.zeros(nS, bool)
for s in range(nS):
    if all(dQ.flat[r] < skyQ for r in members[s]): isSky[s] = True; continue
    if preDrop[s]: isGround[s] = True; continue   # the three-texel / no-area verdict, already reached above
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
    if A.budget:
        # PER-TEXEL ERROR BUDGET (S35 §17). The thin rule asks once, at the farthest reach, whether the strip can carry a slope;
        # a sheet that passes then applies its slope everywhere in its disc. The pairs that make the seams are sheets with a
        # handful of rims whose planes run far past their own data (sunflowers: 2 rims, strip 126, rim depth 0.408, fill 0.532).
        # The same budget per texel: the least-squares fit gives the slope's covariance, so the predicted standard error of the
        # value at a texel is known; where it exceeds the visible step the slope is not evidence there. The value is the
        # posterior compromise between "slope measured" and "no slope": v0 + w (slope . d), w = step^2 / (step^2 + se^2), which
        # is the plane where the fit supports it, the constant where it does not, and continuous in between.
        res2 = V - Amat @ c; kp = keep if keep.any() else np.ones(len(st), bool)
        sig2 = float(np.mean(res2[kp] ** 2)) if kp.sum() > len(cols) else 0.0
        try: XtXi = np.linalg.pinv(Amat[kp].T @ Amat[kp])
        except Exception: XtXi = np.zeros((len(cols), len(cols)))
        Sig = sig2 * XtXi
        xb = float(X.mean()); yb = float(Y.mean()); v0 = float(full[0] + full[1] * xb + full[2] * yb)
        sxx = sxy = syy = 0.0; k2 = 1
        if useX: sxx = float(Sig[k2, k2]); k2 += 1
        if useY:
            syy = float(Sig[k2, k2])
            if useX: sxy = float(Sig[1, k2])
        budget[s] = (xb, yb, v0, sxx, sxy, syy, float(np.median(TOL.ravel()[np.array(members[s])])))
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
_gcache = {}
def _bfs(entries, R, wsrc=None, srcTex=None):
    seen = np.zeros(N, bool); lab_ = np.zeros(N, bool)
    src_ = entries if srcTex is None else srcTex
    seen[src_] = True
    if wsrc is not None: lab_[src_] = wsrc
    front = src_
    for _ in range(R):
        if len(front) == 0: break
        x_ = front % pw; y_ = front // pw; nb = []; pl_ = []
        for dx, dy in DIRS:
            okn_ = (x_ + dx >= 0) & (x_ + dx < pw) & (y_ + dy >= 0) & (y_ + dy < ph); nb.append(front[okn_] + dy * pw + dx); pl_.append(lab_[front[okn_]])
        nb = np.concatenate(nb); pl_ = np.concatenate(pl_); nb, first = np.unique(nb, return_index=True); pl_ = pl_[first]
        keep_ = band.ravel()[nb] & ~seen[nb]; nb = nb[keep_]; pl_ = pl_[keep_]; seen[nb] = True; lab_[nb] = pl_; front = nb
    return seen, lab_
_gdcache = {}
def geo_domain(s):
    if not (A.geo and s in geoInfo): return domStop[s], None
    if _gdcache.get('s') == s: return _gdcache['v']   # the plate stage and the layered order ask for the same disc
    entries, R, closedSet = geoInfo[s]; src_ = domStop[s]
    if A.faces and closedSet is None:
        # FACETING (S35 §17): the steps between facets of one surface come from domain truncation, not from the facets
        # disagreeing — each facet's plane stops at its own disc and the next texel belongs to another facet's plane (70 % of
        # the sunflowers' vertical jumps and 86 % of the horizontal ones are between different owners, median 6-10 steps).
        # Every facet of a join-law component is therefore given that component's whole domain; the layered order then picks the
        # nearest facet at every texel, which is continuous, and the creases fall where two facets' planes cross — for vermeer's
        # wall and floor that crossing IS the wall's foot, because the floor plane continued upward recedes behind the wall.
        g = int(groupOf[s])
        if _gcache.get('g') != g:
            ss = np.flatnonzero(groupOf == g); ss = [int(t) for t in ss if t in geoInfo]
            en = np.unique(np.concatenate([geoInfo[t][0] for t in ss])); Rg = max(geoInfo[t][1] for t in ss)
            seen, _ = _bfs(en, Rg)
            rr = np.concatenate([np.array(members[t], dtype=np.int64) for t in ss]); seen[rr] = False
            _gcache.clear(); _gcache['g'] = g; _gcache['dom'] = np.flatnonzero(seen)
        return _gcache['dom'], None
    if closedSet is None: wsrc = np.zeros(len(src_), bool)
    else: wsrc = ~np.isin(src_, closedSet)
    # SPEED (S35 §19): "band texels within geodesic distance R of the marches" is a geodesic dilation, which scipy does in C.
    # The two-colour version (fitted against weak, for masked objects under the two-sided rule) still needs the step-by-step
    # walk because a texel takes the status of the nearest march, so it keeps the Python loop — but that is the minority of
    # surfaces, and the majority now costs one call instead of R frontier passes (vermeer's ordering: 421 s -> see below).
    _cross = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)
    if not wsrc.any():
        seed = np.zeros((ph, pw), bool); seed.ravel()[src_] = True
        seen = ndimage.binary_dilation(seed, structure=_cross, iterations=max(1, R), mask=band).ravel(); lab_ = None
    else:
        seen, lab_ = _bfs(entries, R, wsrc=wsrc, srcTex=src_)
    seen[np.array(members[s], dtype=np.int64)] = False
    _gdcache.clear(); _gdcache['s'] = s; _gdcache['v'] = (np.flatnonzero(seen), lab_)
    return _gdcache['v']
# ---- the smoothing thin-plate sheet (--tps): the deformed plane. Unknown u over strip ∪ domain; energy
#   Σ_strip (u − disp)² / σ² + λ Σ (u_xx² + 2 u_xy² + u_yy²)
# σ = the strip's own noise (S21's estimator: third differences, MAD → σ, Var(Δ³) = 20σ²), floored at the grid's quantisation
# noise grid/√12; λ by the discrepancy principle (Morozov 1966): the strip's RMS residual equals σ. Free boundary elsewhere:
# the sheet continues the strip's shape into the hole with least bending and relaxes to an affine continuation far from it.
tpsU = {}
def tps_sheet(s_, st, dom):   # s_ is the face; --planeprior uses planes[s_]
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
    if A.planeprior:
        # THE PLATE'S FREE BOUNDARY (S35 §17). With nothing to hold it, the plate bulges over the hole and a small face wins the
        # layered order far from its own data (S15: a 165-texel face took 11 930 band texels at 2.2 m error; the same face's
        # PLANE takes almost none). The face's plane is the statement "no bending beyond what was measured", so it enters as a
        # prior on the domain at weight 1 / visible step, against the strip's data at weight 1 / sigma. Since sigma is far below
        # the step the data rules on the strip, and the prior rules where the plate would otherwise be free.
        kD_ = kOf[dom]; stepv = float(np.median(TOL.ravel()[st])); pv = planes[s_][0] + planes[s_][1] * (dom % pw) + planes[s_][2] * (dom // pw)
        Pm = sparse.csr_matrix((np.ones(len(dom)) / stepv, (np.arange(len(dom)), kD_)), shape=(len(dom), n))
        DtD = (DtD + (Pm.T @ Pm)).tocsr(); Dtb = Dtb + Pm.T @ (pv / stepv)
    # SOLVER (S35 §14): Jacobi-preconditioned CG did not converge on the large systems (vermeer's wall+floor: 870 k unknowns; the
    # biharmonic operator's condition number grows as n^2) — it returned the data on the strip and ~0 on the domain, which the
    # discrepancy search then read as rms < sigma at every lambda (the "0.000" fills behind the woman in s35_mask_tps). Now:
    # smoothed-aggregation algebraic multigrid (pyamg) as the preconditioner with the bending energy's null space (the affine
    # functions 1, x, y) as the near-nullspace candidates, and the relative residual is checked after every solve.
    try: import pyamg
    except Exception: pyamg = None
    Bnull = np.stack([np.ones(n), (X - X.mean()) / max(1, X.std()), (Y - Y.mean()) / max(1, Y.std())], 1)
    # SPEED (S35 §18): the multigrid hierarchy is a PRECONDITIONER, so CG converges to the same solution whichever lambda it was
    # built at — only the iteration count changes, and the relative residual is asserted after every solve. Rebuilding it for
    # each of the sixteen lambdas in the discrepancy search was most of the bake: it is now rebuilt only when lambda has moved
    # more than two decades from the build point.
    _pc = {'lam': None, 'M': None}
    def solve(lam, x0=None):
        M_ = (DtD + lam * BtB).tocsr()
        if pyamg is not None:
            if _pc['lam'] is None or abs(np.log10(lam) - np.log10(_pc['lam'])) > 2:
                _pc['lam'] = lam; _pc['M'] = pyamg.smoothed_aggregation_solver(M_, B=Bnull, symmetry='symmetric', max_coarse=500).aspreconditioner(cycle='V')
            Mp = _pc['M']
        else: Mp = sparse.diags(1.0 / np.maximum(M_.diagonal(), 1e-30))
        x, info = cg(M_, Dtb, x0=x0, rtol=1e-8, maxiter=2000, M=Mp)
        r_ = float(np.linalg.norm(M_ @ x - Dtb) / max(1e-300, np.linalg.norm(Dtb)))
        if r_ > 1e-6 and pyamg is not None:   # the reused hierarchy was too far off: rebuild at this lambda and redo
            _pc['lam'] = lam; _pc['M'] = pyamg.smoothed_aggregation_solver(M_, B=Bnull, symmetry='symmetric', max_coarse=500).aspreconditioner(cycle='V')
            x, info = cg(M_, Dtb, x0=x0, rtol=1e-8, maxiter=2000, M=_pc['M']); r_ = float(np.linalg.norm(M_ @ x - Dtb) / max(1e-300, np.linalg.norm(Dtb)))
        solve.worst = max(getattr(solve, 'worst', 0.0), r_)
        return x
    solve.worst = 0.0
    def rms(x): return float(np.sqrt(np.mean((x[kS] - d) ** 2)))
    # DISCREPANCY SEARCH (Morozov): lambda such that the strip's RMS residual equals its own noise sigma. rms(lambda) is
    # monotone, so a secant in (log lambda, log rms) finds it in a handful of solves instead of the nine-point grid plus six
    # bisections the first version used — sixteen solves per face was most of the bake. Warm-started, bracketed, and it falls
    # back to bisection if the secant leaves the bracket.
    lo, hi = -8.0, 8.0; x = None
    def ev(g, x0):
        xx = solve(10 ** g, x0); return xx, rms(xx)
    x, r0 = ev(0.0, None); pts = [(0.0, r0)]
    if r0 > sig:                       # too stiff already: walk down
        g = 0.0
        while g > lo and r0 > sig:
            g -= 3.0; x, r0 = ev(g, x); pts.append((g, r0))
        a, b = g, min(g + 3.0, hi)
    else:                              # too free: walk up
        g = 0.0; r1 = r0
        while g < hi and r1 <= sig:
            g += 3.0; x, r1 = ev(g, x); pts.append((g, r1))
        a, b = max(g - 3.0, lo), g
    for _ in range(4):
        ra = [r for gg, r in pts if abs(gg - a) < 1e-9]; rb = [r for gg, r in pts if abs(gg - b) < 1e-9]
        if ra and rb and ra[0] > 0 and rb[0] > 0 and abs(np.log10(rb[0]) - np.log10(ra[0])) > 1e-12:
            t = (np.log10(sig) - np.log10(ra[0])) / (np.log10(rb[0]) - np.log10(ra[0])); gm = a + t * (b - a)
            if not (min(a, b) + 1e-3 < gm < max(a, b) - 1e-3): gm = 0.5 * (a + b)
        else: gm = 0.5 * (a + b)
        x, rm = ev(gm, x); pts.append((gm, rm))
        if abs(rm - sig) <= 0.05 * sig: a = b = gm; break
        if rm > sig: b = gm
        else: a = gm
    lam = 10 ** (0.5 * (a + b))
    x = solve(lam, x)
    return om, x, sig, lam, rms(x), solve.worst
def _tps_job(s_):
    st = strip_of(s_); dom = geo_domain(s_)[0]
    if len(st) < 3 or len(dom) == 0: return (s_, None, None, 0.0, 0.0, 0.0, 0.0, len(st), len(dom))
    om, x, sig, lam, rr, worst = tps_sheet(s_, st, dom)
    return (s_, np.asarray(om, dtype=np.int64), np.asarray(x, dtype=np.float64), sig, lam, rr, worst, len(st), len(dom))
if A.tps:
    tt0 = time.time()
    faces_ = [int(s_) for s_ in (np.argsort(groupOf, kind='stable') if A.faces else range(nS))
              if not (isSky[s_] or isGround[s_] or isGroundSurf[s_]) and not (curvedFace is not None and not curvedFace[compOfSurf[s_]])]
    # SPEED (S35 §19): the faces are independent solves, so they run in forked workers (copy-on-write globals; each worker
    # allocates only its own face's matrices). Largest faces first so the long pole starts at once.
    faces_.sort(key=lambda s_: -int(compSize[compOfSurf[s_]]))
    def _take(res):
        s_, om, x, sig, lam, rr, worst, nst, ndom = res
        if om is None: return
        tpsU[s_] = (om, x)
        if ndom > 5000 or worst > 1e-6: print(f'   tps surface {s_}: {nst} strip, {ndom} domain, sigma {sig:.3e}, lambda {lam:.2e}, rms {rr:.3e}, worst relative residual {worst:.1e}{"  UNCONVERGED" if worst > 1e-6 else ""}  ({time.time() - tt0:.0f}s)')
    if A.jobs > 1 and len(faces_) > 1:
        import multiprocessing as mp
        with mp.get_context('fork').Pool(min(A.jobs, len(faces_))) as pool:
            for res in pool.imap_unordered(_tps_job, faces_, chunksize=1): _take(res)
    else:
        for s_ in faces_: _take(_tps_job(s_))
    print(f'thin-plate sheets: {len(tpsU)} solved with {min(A.jobs, max(1, len(faces_)))} workers  ({time.time() - tt0:.1f}s)')
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
    tb = time.time(); _prof = {'geo': 0.0, 'val': 0.0, 'gate': 0.0, 'order': 0.0}
    best = np.full(N, -np.inf); second = np.full(N, -np.inf); who = np.full(N, -1, np.int32)
    bestH = np.full(N, -np.inf); whoH = np.full(N, -1, np.int32)   # --evidence: the hedges' own order, used only where no fitted sheet reaches
    ownD = DISP.ravel(); ownT = TOL.ravel()
    for s in (np.argsort(groupOf, kind='stable') if A.faces else range(nS)):
        s = int(s); dom = domains[s]
        if len(dom) == 0 or isGround[s]: continue
        weakSet = domWeak[s]; weakArr = None
        _t0 = time.time()
        if A.geo and label == 'stop' and s in geoInfo: dom, weakArr = geo_domain(s)
        _prof['geo'] += time.time() - _t0; _t0 = time.time()
        isHedge = ((A.evidence and hedge[s]) or fusedS[s]) and (not isSky[s])
        if isSky[s]: val = np.zeros(len(dom))
        elif A.tps and s in tpsU:
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
            if A.budget and s in budget:
                xb, yb, v0, sxx, sxy, syy, stp = budget[s]
                dxb = X - xb; dyb = Y - yb; var = sxx * dxb * dxb + 2 * sxy * dxb * dyb + syy * dyb * dyb
                w_ = stp * stp / (stp * stp + np.maximum(var, 0.0)); val = v0 + w_ * (planes[s, 1] * dxb + planes[s, 2] * dyb)
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
        _prof['val'] += time.time() - _t0; _t0 = time.time()
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
        _prof['gate'] += time.time() - _t0; _t0 = time.time()
        b = best[d]; upd = v > b
        second[d[upd]] = np.maximum(second[d[upd]], b[upd]); best[d[upd]] = v[upd]; who[d[upd]] = s
        second[d[~upd]] = np.maximum(second[d[~upd]], v[~upd])
        _prof['order'] += time.time() - _t0
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
    print('   build profile: ' + ', '.join(f'{k} {v:.1f}s' for k, v in _prof.items()))
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

# ---- per-sheet colour (S35 §25) ----
# The app colours a band texel from the rim its own LINE found, with a window sized by the depth fit, and lets a membrane
# spread those values across the band; §24 measured what that costs — the colour follows a per-line far-side choice, so a
# texel can be washed with a surface 400 texels away, and neighbouring lines disagree. Here the colour comes from the SHEET
# that owns the texel: the sheet's own visible colour, continued over the texels it owns, and nothing else. The continuation
# is the harmonic extension (Perez, Gangnet & Blake 2003) of that sheet's visible colour, solved per sheet, so no two
# surfaces ever mix and there is no per-line ring at all.
# The one quantity it needs is the BLEND FRINGE: the source's own edges are anti-aliased, so the surface's texels at its
# silhouette are mixtures of it and the occluder. Anchoring the extension there paints the occluder into the band (§23's
# measurement: the first far texel is occluder-coloured in 52-62 % of rims). The fringe's width is measured from this
# picture, not assumed: at every step edge, the number of leading texels on the far side that are closer to the near side's
# colour than to the far side's own colour; the picture's fringe is the median over its edges. Those texels join the
# unknowns, so the extension is anchored only on clean colour, and they keep their source colour in the output (they are
# visible at rest; only band texels are written).
if A.color:
    tC0 = time.time()
    rgbc = A.rgb or (f'{P}/color.png' if os.path.exists(f'{P}/color.png') else None)
    if rgbc is None or not os.path.exists(rgbc): print('[colour] no source colour image; --color skipped')
    else:
        _im = Image.open(rgbc).convert('RGB')
        COL = np.asarray(_im if _im.size == (pw, ph) else _im.resize((pw, ph), Image.BILINEAR)).astype(np.float64).reshape(N, 3)
        who = results['stop']['who'].ravel(); bandF = band.ravel()
        # the colour's unit is the VISIBLE SURFACE, not the planar patch: colour does not obey planarity, and a wall split
        # into facets by the depth fit is one painted surface. (With patches as the surfaces, the owner of a band texel is
        # rarely the same patch as the visible texel beside it, so grouping by patch left 88 % of vermeer's band with no
        # value to extend from and blotched it with per-patch colour models.)
        cgrp = compJ if A.patches else comp
        grpOfSheet = np.array([int(cgrp[members[s_][0]]) if len(members[s_]) else -1 for s_ in range(nS)] + [-1], dtype=np.int64)
        # build() marks the app's fitted GROUND plane with the owner index nS: it is a plane, not a visible component, so its
        # colour comes from the surface its own visible texels belong to (the floor)
        if gtex is not None:
            gv = np.flatnonzero((gtex > 0) & ~band.ravel())
            if len(gv): grpOfSheet[nS] = int(np.bincount(cgrp[gv]).argmax())
        # 1 the blend fringe, measured on this picture's own step edges
        idx2 = np.arange(N).reshape(ph, pw); prof = []
        for ax_ in (0, 1):
            I_ = (idx2[:, :-1] if ax_ == 0 else idx2[:-1, :]).ravel(); Jn = (idx2[:, 1:] if ax_ == 0 else idx2[1:, :]).ravel()
            jn = (jh0 if ax_ == 0 else jv0).ravel(); st_ = 1 if ax_ == 0 else pw
            for near, far, sgn in ((I_, Jn, +1), (Jn, I_, -1)):           # 'far' is the background side, stepping away by sgn
                m_ = (~jn) & (DISP.ravel()[near] > DISP.ravel()[far] + TOL.ravel()[far])
                f_ = far[m_]; n_ = near[m_]
                if not len(f_): continue
                pos = (f_ % pw) if ax_ == 0 else (f_ // pw); lim = pw if ax_ == 0 else ph
                ok = (pos + sgn * 11 >= 0) & (pos + sgn * 11 < lim)
                f_ = f_[ok]; n_ = n_[ok]
                if not len(f_): continue
                o_ = COL[n_]; ref = np.median(np.stack([COL[f_ + sgn * k * st_] for k in range(4, 12)], 0), 0)
                good = np.linalg.norm(o_ - ref, axis=1) > 24
                if not good.any(): continue
                o_ = o_[good]; ref = ref[good]; f2 = f_[good]
                cnt = np.zeros(len(f2), np.int64); alive = np.ones(len(f2), bool)
                for k in range(4):
                    ck = COL[f2 + sgn * k * st_]
                    c_ = alive & (np.linalg.norm(ck - o_, axis=1) < np.linalg.norm(ck - ref, axis=1))
                    cnt += c_; alive &= c_
                prof.append(cnt)
        fringe = int(np.median(np.concatenate(prof))) if prof else 0
        nEdge = int(sum(len(p) for p in prof))
        # 2 the fringe set: visible texels within `fringe` steps of a step edge (any 4-neighbour not joined and nearer)
        stepEdge = np.zeros((ph, pw), bool)
        stepEdge[:, :-1] |= (~jh0) & (DISP.reshape(ph, pw)[:, 1:] > DISP.reshape(ph, pw)[:, :-1] + TOL.reshape(ph, pw)[:, :-1])
        stepEdge[:, 1:] |= (~jh0) & (DISP.reshape(ph, pw)[:, :-1] > DISP.reshape(ph, pw)[:, 1:] + TOL.reshape(ph, pw)[:, 1:])
        stepEdge[:-1, :] |= (~jv0) & (DISP.reshape(ph, pw)[1:, :] > DISP.reshape(ph, pw)[:-1, :] + TOL.reshape(ph, pw)[:-1, :])
        stepEdge[1:, :] |= (~jv0) & (DISP.reshape(ph, pw)[:-1, :] > DISP.reshape(ph, pw)[1:, :] + TOL.reshape(ph, pw)[1:, :])
        fr = ndimage.binary_dilation(stepEdge, np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]), iterations=fringe) if fringe > 0 else stepEdge.copy()
        fringeF = fr.ravel() & ~bandF
        # 3 the unknowns: band texels a sheet owns, plus the fringe texels of those sheets' components
        sheetOf = np.full(N, -1, np.int64)     # the colour GROUP of each unknown (a visible surface), not the sheet index
        okB = bandF & (who >= 0); sheetOf[okB] = grpOfSheet[who[okB]]
        okF = fringeF.copy(); sheetOf[okF] = cgrp[okF]
        unk = (okB & (sheetOf >= 0)) | (okF & (sheetOf >= 0))
        okB = okB & (sheetOf >= 0)
        uIdx = np.full(N, -1, np.int64); uu = np.flatnonzero(unk); uIdx[uu] = np.arange(len(uu)); nU = len(uu)
        # 4 the Laplacian over the unknowns; a neighbour is coupled only if it is an unknown of the SAME sheet, and is a
        #   Dirichlet value only if it is a clean visible texel of that sheet's component
        rowsL = [np.arange(nU)]; colsL = [np.arange(nU)]; valsL = [np.zeros(nU)]; rhs = np.zeros((nU, 3)); deg = np.zeros(nU)
        X_ = uu % pw; Y_ = uu // pw; sU = sheetOf[uu]
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            xn = X_ + dx; yn = Y_ + dy; ins = (xn >= 0) & (xn < pw) & (yn >= 0) & (yn < ph)
            nb = np.full(nU, -1, np.int64); nb[ins] = yn[ins] * pw + xn[ins]
            same = ins & (nb >= 0)
            isU = same.copy(); isU[same] = (uIdx[nb[same]] >= 0) & (sheetOf[nb[same]] == sU[same])
            isD = same & ~isU
            if isD.any():
                cleanD = isD.copy(); nbD = nb[isD]
                cleanD[isD] = (~bandF[nbD]) & (~fringeF[nbD]) & (cgrp[nbD] == sU[isD])
                isD = cleanD
            deg += isU + isD
            if isU.any():
                k_ = np.flatnonzero(isU); rowsL.append(k_); colsL.append(uIdx[nb[k_]]); valsL.append(-np.ones(len(k_)))
            if isD.any():
                k_ = np.flatnonzero(isD); rhs[k_] += COL[nb[k_]]
        valsL[0] = deg
        # THE SHEET'S OWN COLOUR MODEL. Ownership is by depth, not by adjacency: the sheet that shows behind a texel is often
        # not the surface next to it, so most owned regions touch no visible texel of their owner and the extension has
        # nothing to anchor on (sunflowers: 86 % of the owned band). For those the colour is the same construction the depth
        # uses — the sheet's own plane, here per channel over its clean visible texels — evaluated at the texel and clipped
        # to the range that sheet actually shows, so the wash carries the surface's own colour and gradient and never a
        # colour it never had. Where the sheet IS adjacent, the harmonic extension decides and this is not used.
        # THE SURFACE'S OWN COLOUR MODEL. Ownership is by depth, not adjacency: the surface that shows behind a texel is
        # often not the one beside it (S9: every band texel is owned by a quad it does not touch), so the extension has
        # nothing to propagate from. Those texels take their surface's own colour model — a plane per channel over its clean
        # visible texels, clipped to the range that surface actually shows, the same construction the depth uses — and stay
        # coupled to the Laplacian, so the field is smoothed rather than stamped.
        # (The nearest clean sample of the same surface was tried instead and is worse against the kit's hidden-layer
        # colour: S9 146 -> 181, S26 91 -> 96, S15 53.8 -> 53.3, S2 unchanged. Rejected.)
        cmod = {}
        def sheet_color(s_, xx, yy):
            m_ = cmod.get(int(s_))
            if m_ is None:
                t_ = np.flatnonzero((cgrp == s_) & ~fringeF & ~bandF)
                if len(t_) < 3: t_ = np.flatnonzero(cgrp == s_)
                cx = t_ % pw; cy = t_ // pw; V_ = COL[t_]
                if len(t_) >= 3:
                    Am = np.stack([np.ones(len(t_)), cx - cx.mean(), cy - cy.mean()], 1)
                    cc_, *_ = np.linalg.lstsq(Am, V_, rcond=None)
                    m_ = (cc_, cx.mean(), cy.mean(), V_.min(0), V_.max(0))
                else:
                    med_ = np.median(V_, 0) if len(t_) else np.zeros(3)
                    m_ = (np.stack([med_, np.zeros(3), np.zeros(3)]), 0.0, 0.0, med_, med_)
                cmod[int(s_)] = m_
            cc_, mx_, my_, lo_, hi_ = m_
            A_ = np.stack([np.ones(len(xx)), xx - mx_, yy - my_], 1)
            return np.clip(A_ @ cc_, lo_, hi_)
        # a texel with no neighbour at all inside its own sheet (a speck) takes its sheet's colour model
        lone = deg <= 0
        if lone.any():
            valsL[0] = np.where(lone, 1.0, deg)
            k_ = np.flatnonzero(lone)
            for s_ in np.unique(sU[k_]):
                kk = k_[sU[k_] == s_]; rhs[kk] = sheet_color(s_, X_[kk], Y_[kk])
        Lm = sparse.csr_matrix((np.concatenate(valsL), (np.concatenate(rowsL), np.concatenate(colsL))), shape=(nU, nU))
        # components of the unknown graph with no Dirichlet value anywhere (a sheet whose whole visible edge is fringe):
        # pin them to that sheet's clean median, else the solve is singular there
        nCmp, lab = connected_components(Lm, directed=False)
        anyD = np.zeros(nCmp, bool); np.logical_or.at(anyD, lab, rhs.any(1))
        pinned = ~anyD[lab]
        if pinned.any():
            dg = Lm.diagonal().copy(); dg[pinned] += 1.0; Lm.setdiag(dg)
            k_ = np.flatnonzero(pinned)
            for s_ in np.unique(sU[k_]):
                kk = k_[sU[k_] == s_]; rhs[kk] = rhs[kk] + sheet_color(s_, X_[kk], Y_[kk])
        import pyamg
        ml = pyamg.smoothed_aggregation_solver(Lm.tocsr(), max_coarse=500); Mp = ml.aspreconditioner(cycle='V')
        sol = np.zeros((nU, 3))
        for ch in range(3):
            x_, info = cg(Lm, rhs[:, ch], rtol=1e-6, maxiter=500, M=Mp); sol[:, ch] = x_
        outC = COL.copy()
        outC[uu[bandF[uu]]] = np.clip(sol[bandF[uu]], 0, 255)
        Image.fromarray(outC.reshape(ph, pw, 3).astype(np.uint8)).save(f'{OUT}/color_stop.png')
        # scored against the kit's own hidden-layer COLOUR where there is one (scope_gt rgb), beside the app's per-line fill
        if A.truth and os.path.exists(A.truth):
            z_ = np.load(A.truth); cls_ = z_['cls']; w_ = z_['w_disp'].astype(np.float32); rgb_ = z_['rgb']
            H_, W_, K_ = cls_.shape; y0_ = (H_ - ph) // 2; x0_ = (W_ - pw) // 2
            cc = cls_[y0_:y0_ + ph, x0_:x0_ + pw]; ww = w_[y0_:y0_ + ph, x0_:x0_ + pw]; rr = rgb_[y0_:y0_ + ph, x0_:x0_ + pw]
            vis_ = (cc >= 2) & (cc <= 5) & (ww > 0); has_ = vis_.any(-1); kk_ = np.argmax(vis_, -1)
            cTrue = np.take_along_axis(rr, kk_[..., None, None], 1)[:, 0] if False else rr[np.arange(ph)[:, None], np.arange(pw)[None, :], kk_]
            m_ = band & has_
            def cerr(img):
                e = np.abs(img.reshape(ph, pw, 3)[m_].astype(np.float64) - cTrue[m_].astype(np.float64)).sum(1)
                return f'median {np.median(e):5.1f} mean {e.mean():5.1f} p90 {np.percentile(e, 90):5.1f}'
                
            print(f'[colour truth] {int(m_.sum())} band texels with a known hidden colour; |fill - truth| (L1 over channels): sheets {cerr(outC)}')
            if os.path.exists(f'{P}/plateColor.u8'):
                ap_ = np.fromfile(f'{P}/plateColor.u8', np.uint8).reshape(ph, pw, 4)[..., :3]
                print(f'[colour truth]   the app per-line fill on the same texels: {cerr(ap_.reshape(N, 3))}; the source (a clone): {cerr(COL)}')
        (bandF & (who >= 0)).astype(np.uint8).tofile(f'{OUT}/colorMask_stop.u8')
        print(f'[colour] blend fringe {fringe} texels (median over {nEdge} step edges); {int(okB.sum())} band texels coloured from their own sheet, '
              f'{int((okF & (sheetOf >= 0)).sum())} fringe texels solved with them, {int(pinned.sum())} carried by their surface own colour model, '
              f'{int((bandF & (who < 0)).sum())} band texels no sheet owns (kept)  ({time.time() - tC0:.1f}s)')

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
