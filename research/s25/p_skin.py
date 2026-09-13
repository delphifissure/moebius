#!/usr/bin/env python3
"""Skin area of a far field: over every unjoined free-free edge (the seams sheetfield counts), the screen gap the two texels
open between them at the 45-degree rim = k45 * |disparity difference| texels, k45 = 0.667 * pw / float(disp(np.array([1.0]))[0])   # shift per unit of disparity, normalised so the nearest content (d = 1) shifts k45 texels at the rim (a127b) (a127b: 568 px of 851 at
45 degrees). The sum is the area (in texel-rows) of plate that must be stretched (a skin) or left open (a hole) at the rim.
Usage: p_skin.py <probe dir> <q levels> [modes...]  (reads sf3_<mode>_depth.npy written by sheetfield3/4)"""
import sys, os, json, numpy as np
d = sys.argv[1]; q = 1.0 / float(sys.argv[2]); modes = sys.argv[3:] or ['own', 'plate', 'amle']
m = json.load(open(d + '/meta.json')); pw, ph = m['pw'], m['ph']; t = m['rimT']
lut = np.fromfile(d + '/zeLut.f32', np.float32).astype(float); grid = np.arange(1025) / 1024.0
ze = lambda a: np.interp(np.clip(a, 0, 1) * 1024, np.arange(1025), lut); disp = lambda a: 1.0 / ze(a)
axis = np.fromfile(d + '/farAxis.u8', np.uint8).reshape(ph, pw); free = axis > 0
dq = np.fromfile(d + '/dQ.f32', np.float32).reshape(ph, pw).astype(float)
SKY = os.environ.get('SKY') == '1'; skym = (dq < 0.5 * q) if SKY else np.zeros((ph, pw), bool)
k45 = 0.667 * pw / float(disp(np.array([1.0]))[0])   # shift per unit of disparity, normalised so the nearest content (d = 1) shifts k45 texels at the rim (a127b)


def unjoined(a0):
    zz = ze(a0); dd = disp(a0); tl = np.abs(disp(np.minimum(1, a0 + q)) - disp(np.maximum(0, a0 - q))) + 1e-9; out = []
    for ax in (0, 1):
        if ax == 0: a, b = zz[:, :-1], zz[:, 1:]; da, db = dd[:, :-1], dd[:, 1:]; tt = np.maximum(tl[:, :-1], tl[:, 1:]); s1, s2 = skym[:, :-1], skym[:, 1:]; fr = free[:, :-1] & free[:, 1:]
        else: a, b = zz[:-1, :], zz[1:, :]; da, db = dd[:-1, :], dd[1:, :]; tt = np.maximum(tl[:-1, :], tl[1:, :]); s1, s2 = skym[:-1, :], skym[1:, :]; fr = free[:-1, :] & free[1:, :]
        j = np.maximum(a / b, b / a) <= t
        prev = np.full_like(da, np.nan); nxt = np.full_like(db, np.nan)
        if ax == 0: prev[:, 1:] = dd[:, :-2]; nxt[:, :-1] = dd[:, 2:]
        else: prev[1:, :] = dd[:-2, :]; nxt[:-1, :] = dd[2:, :]
        j = j | np.nan_to_num(np.abs(db - (2 * da - prev)) <= tt, nan=False) | np.nan_to_num(np.abs(da - (2 * db - nxt)) <= tt, nan=False)
        j = np.where(s1 | s2, s1 & s2, j)
        gap = np.where(s1 | s2, 0.0, np.abs(da - db)) * k45
        out.append((fr & ~j, gap))
    return out


for mode in modes:
    p = f'{d}/sf3_{mode}_depth.npy'
    if not os.path.isfile(p): continue
    fld = np.load(p).astype(float)
    tot_n = 0; tot_gap = 0.0; big = 0
    for un, gap in unjoined(fld):
        tot_n += int(un.sum()); tot_gap += float(gap[un].sum()); big += int((gap[un] > 2).sum())
    print(f'{os.path.basename(d)} {mode:6s}: seams {tot_n:7d} | skin area at the 45-degree rim {tot_gap:10.0f} texel-rows ({100 * tot_gap / (pw * ph):.2f} % of the plate) | seams wider than 2 texels {big}')
