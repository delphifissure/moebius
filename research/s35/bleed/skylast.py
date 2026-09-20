"""S35 §51: SKY OVER WEAK. In the layered order the sky (a background sheet at infinity) sits in the main tier, and a THING's sheet
whose march behind an occluder is open (not closed on its own component: the §18 two-sided rule) sits in the hedge tier, used
only where no main-tier sheet reaches. The sky's domain reaches almost everything, so a weak sheet never shows where the sky
does. On the sunflowers SAM auto cuts the field into pieces, the wrap test makes each a thing, their marches behind the big
head are open, and the sky fills behind the head (§46, §49). Here, from a TIER_DUMP=1 run (whoH / bestHd: the hedge tier's
winner per texel): the band texels the sky owns over a nearer tier-two candidate, by what that candidate is (a hedge, the
occluder's own object demoted, or a thing's open march), and the fill 'sky last' would give (the tier-two value where the sky
won over it). With --truth S: the kit's median |error| under the arm and under sky-last, overall and on the changed texels, by
hidden class (2 background, 3 other thing, 4/5 the occluder's own body, 6 sky).
  skylast.py <probe dir> <arm dir> [--truth S]"""
import sys, json, numpy as np
args = sys.argv[1:]; P = args.pop(0); D = args.pop(0); S = None
if args and args[0] == '--truth': args.pop(0); S = args.pop(0)
meta = json.load(open(f'{P}/meta.json')); pw, ph = meta['pw'], meta['ph']
band = np.fromfile(f'{P}/disocc.u8', np.uint8).reshape(ph, pw) > 0; dQ = np.fromfile(f'{P}/dQ.f32', np.float32).reshape(ph, pw)
ff = np.fromfile(f'{D}/farField_stop.f32', np.float32).reshape(ph, pw); who = np.fromfile(f'{D}/who_stop.i32', np.int32).reshape(ph, pw)
whoH = np.fromfile(f'{D}/whoH_stop.i32', np.int32).reshape(ph, pw); bH = np.fromfile(f'{D}/bestHd_stop.f32', np.float32).reshape(ph, pw)
oid = np.fromfile(f'{D}/oid.i32', np.int32).reshape(ph, pw); z = np.load(f'{D}/sheets_info.npz')
hedge = z['hedge']; sid = z['sid']; thing = z['thing']
isSky = z['sky'] | ((z['rimDepth'] < 0.02) & (sid == 0) & ~thing)   # the kit's sky class, or a picture's sky-valued background sheet (the sunflowers' sheet 0 at d 0.009)
# who == nS is the pseudo-sheet past the last surface (the kit's sky class from the field); it is sky, not a hedge, not a thing
isSky = np.r_[isSky, True]; hedge = np.r_[hedge, False]; sid = np.r_[sid, 0]; thing = np.r_[thing, False]
skyWin = band & (who >= 0) & isSky[np.clip(who, 0, None)]
alt = skyWin & (whoH >= 0) & (bH > ff + 0.005)          # a tier-two candidate nearer than the sky's value
kind = np.full((ph, pw), -1, np.int8)                     # 0 hedge, 1 same object (the occluder's own id), 2 a thing's open march, 3 other
h = whoH[alt]; kind[alt] = np.where(hedge[h], 0, np.where((sid[h] > 0) & (sid[h] == oid[alt]), 1, np.where(thing[h], 2, 3)))
n = band.sum(); print(f'{D.rstrip("/").split("/")[-1]}: band {n}; the sky owns {100 * skyWin.sum() / n:.1f} %; of that, over a nearer tier-two candidate {100 * alt.sum() / max(1, skyWin.sum()):.1f} % ({alt.sum()} texels = {100 * alt.sum() / n:.1f} % of the band): hedge {100 * (kind[alt] == 0).mean():.0f} %, the occluder\'s own object {100 * (kind[alt] == 1).mean():.0f} %, a thing\'s open march {100 * (kind[alt] == 2).mean():.0f} %, other {100 * (kind[alt] == 3).mean():.0f} %; candidate d p10/50/90 {np.percentile(bH[alt], [10, 50, 90]).round(3) if alt.any() else "-"}')
u, c = np.unique(whoH[alt & (kind == 2)], return_counts=True); o = np.argsort(-c)[:6]
if len(o): print('   open-march things behind the sky, top sheets (sheet, texels, rims, rim d, object id):', [(int(u[k]), int(c[k]), int(z['rims'][u[k]]) if u[k] < len(z['rims']) else -1, round(float(z['rimDepth'][u[k]]), 3) if u[k] < len(z['rims']) else -1, int(sid[u[k]])) for k in o])
ffL = ff.copy(); ffL[alt] = bH[alt]
np.save(f'{D}/skylast_ff.npy', ffL)
if S:
    K = '/home/user/moebiusv2/harness/truthkit/out'; outer, pn = meta['outer'], meta['pn']
    zt = np.load(f'{K}/{S}_env45/scope_gt.npz'); cls = zt['cls']; w = zt['w_disp']; dep = zt['depth']; H, W, _ = cls.shape; y0 = (H - ph) // 2; x0 = (W - pw) // 2
    cls = cls[y0:y0 + ph, x0:x0 + pw]; w = w[y0:y0 + ph, x0:x0 + pw]; dep = dep[y0:y0 + ph, x0:x0 + pw]
    v_ = (cls >= 2) & (cls <= 5) & (w > 0); has = v_.any(-1); kk = np.argmax(v_, -1); dT = np.take_along_axis(dep, kk[..., None], -1)[..., 0]; dT = np.where(has & np.isfinite(dT), dT, np.nan)
    cT = np.take_along_axis(cls, kk[..., None], -1)[..., 0]; skyT = band & ~has & (zt['sky_hidden'][y0:y0 + ph, x0:x0 + pw] if 'sky_hidden' in zt.files else False)
    depth_of_d = lambda d: outer * (1 - np.clip(d / pn, 0, 1) ** 2 * (3 - 2 * np.clip(d / pn, 0, 1)))
    t = band & np.isfinite(dT); e0 = np.abs(depth_of_d(ff) - dT); e1 = np.abs(depth_of_d(ffL) - dT)
    print(f'   truth: whole band median |e| arm {np.nanmedian(e0[t]):.4f} m -> sky-last {np.nanmedian(e1[t]):.4f} m; changed texels with a hidden surface {int((alt & t).sum())}: arm {np.nanmedian(e0[alt & t]) if (alt & t).any() else np.nan:.4f} -> {np.nanmedian(e1[alt & t]) if (alt & t).any() else np.nan:.4f} m; changed texels whose truth is SKY (no hidden surface): {int((alt & ~has).sum())} ({100 * (alt & ~has).sum() / max(1, alt.sum()):.0f} % of the changed)')
    for c_ in (2, 3, 4, 5):
        m = alt & t & (cT == c_)
        if m.sum() >= 50: print(f'      class {c_}: n {m.sum()}, arm {np.nanmedian(e0[m]):.4f} -> sky-last {np.nanmedian(e1[m]):.4f} m (truth depth median {np.nanmedian(dT[m]):.3f}, sky-last fill {np.nanmedian(depth_of_d(ffL[m])):.3f})')
