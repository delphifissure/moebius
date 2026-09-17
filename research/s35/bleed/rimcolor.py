"""Test A on the app's own fill. For every band texel with a far rim (farRimJ), the fill colour is the mean of the source colour
over the rim's window (rim texel j, w texels outward along the axis). Questions: (1) is the rim texel's colour closer to the
occluder's edge colour (the texel on the near side of the step) than to the far run's own colour (median of the window's
tail)? (2) how many leading texels of the window are occluder-coloured? (3) where is the colour edge relative to the depth
edge (max colour gradient along the axis within +-6 texels of the step)?"""
import sys, json, numpy as np
from PIL import Image
D, C = sys.argv[1], sys.argv[2]
meta = json.load(open(f'{D}/meta.json')); pw, ph = meta['pw'], meta['ph']; N = pw * ph
dQ = np.fromfile(f'{D}/dQ.f32', np.float32); dis = np.fromfile(f'{D}/disocc.u8', np.uint8) > 0
J = np.fromfile(f'{D}/farRimJ.i32', np.int32).reshape(N, 2); W = np.fromfile(f'{D}/farRimW.i32', np.int32).reshape(N, 2); ax = np.fromfile(f'{D}/farAxis.u8', np.uint8)
col = np.asarray(Image.open(C).convert('RGB').resize((pw, ph), Image.BILINEAR)).astype(np.float32).reshape(N, 3)
lum = col.mean(1)
# unique (rim j, side, axis) pairs: side -1 for slot A (window runs toward -), +1 for slot B
res = {}
for slot, side in ((0, -1), (1, +1)):
    ok = dis & (J[:, slot] >= 0) & (ax > 0)
    j = J[ok, slot]; w = W[ok, slot]; a = ax[ok]
    key = j.astype(np.int64) * 4 + (slot * 2) + (a - 1); uk, first = np.unique(key, return_index=True)
    j = j[first]; w = w[first]; a = a[first]
    st = np.where(a == 1, 1, pw) * side              # step along the window's direction (outward from the occluder)
    jx = j % pw; jy = j // pw
    # the occluder edge texel = one step back (toward the band texel); guard the frame
    back = j - st; okb = (back >= 0) & (back < N)
    if a[0] == 1 if len(a) else True: pass
    okb &= np.where(a == 1, (jx - side >= 0) & (jx - side < pw), (jy - side >= 0) & (jy - side < ph))
    j, w, a, st, back = j[okb], w[okb], a[okb], st[okb], back[okb]
    n = len(j); K = 12
    prof = np.full((n, K), np.nan, np.float32)      # luminance profile from the rim texel outward
    for k in range(K):
        t = j + st * k; jx2 = (j % pw) + (k * side if True else 0)
        inside = (t >= 0) & (t < N) & np.where(a == 1, ((j % pw) + side * k >= 0) & ((j % pw) + side * k < pw), ((j // pw) + side * k >= 0) & ((j // pw) + side * k < ph))
        prof[inside, k] = lum[t[inside]]
    fg = lum[back]                                   # occluder edge luminance
    tail = np.nanmedian(prof[:, 4:K], axis=1)        # the far run's own luminance
    valid = np.isfinite(tail) & np.isfinite(prof[:, 0]) & (np.abs(fg - tail) > 8)   # only steps with a colour contrast to speak of
    p0 = prof[valid, 0]; f = fg[valid]; tl = tail[valid]
    closerFG = np.abs(p0 - f) < np.abs(p0 - tl)
    # leading contaminated texels: consecutive texels from the rim that are closer to fg than to the tail
    cont = np.zeros(valid.sum(), int); alive = np.ones(valid.sum(), bool)
    for k in range(K):
        pk = prof[valid, k]; c = np.isfinite(pk) & (np.abs(pk - f) < np.abs(pk - tl)) & alive; cont += c; alive &= c
    # window mean contamination: share of the app's window (w texels) that is contaminated
    wv = np.minimum(w[valid], K); share = np.minimum(cont, wv) / np.maximum(1, wv)
    # colour edge vs depth edge: gradient of the profile including 3 texels back into the occluder
    back3 = np.stack([lum[np.clip(j - st * k, 0, N - 1)] for k in (3, 2, 1)], 1)
    P = np.concatenate([back3, prof[:, :8]], 1)[valid]          # positions -3..-1 (occluder), 0 (rim), 1..7
    g = np.abs(np.diff(P, axis=1)); g = np.nan_to_num(g, nan=-1); pos = np.argmax(g, axis=1) - 3 + 0.5   # edge between texel pos and pos+1; depth edge is at -0.5
    res[slot] = dict(n=int(valid.sum()), closerFG=float(closerFG.mean()), cont_mean=float(cont.mean()), cont_p50=float(np.median(cont)), cont_p90=float(np.percentile(cont, 90)),
                     share_p50=float(np.median(share)), share_mean=float(share.mean()), w_p50=float(np.median(w[valid])), edge_off_p50=float(np.median(pos)), edge_off_frac_pos=float((pos > 0).mean()),
                     hist=np.bincount(np.clip(cont, 0, 8), minlength=9).tolist())
tot = sum(r['n'] for r in res.values())
print(f'{D.split("/")[-1]}: {tot} rim windows with colour contrast (both slots); app window w median {res[0]["w_p50"]:.0f}/{res[1]["w_p50"]:.0f}')
for slot, r in res.items():
    print(f'  slot {slot}: rim texel closer to the OCCLUDER colour than to its own run: {100*r["closerFG"]:.1f} %; occluder-coloured leading texels mean {r["cont_mean"]:.2f} p50 {r["cont_p50"]:.0f} p90 {r["cont_p90"]:.0f} (hist 0..8+: {r["hist"]}); share of the window contaminated: mean {100*r["share_mean"]:.1f} % p50 {100*r["share_p50"]:.1f} %; colour edge offset from the depth edge (texels, + = inside the far run): median {r["edge_off_p50"]:+.1f}, positive in {100*r["edge_off_frac_pos"]:.0f} %')
