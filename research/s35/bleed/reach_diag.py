"""S35 §30: is there a reach law in the truth? Per sheet: how far from its entries (geodesic j) the truth's first hidden surface is
still this sheet's own primitive, against the sheet's own visible extent E and the hole reach R. reach_diag.py <dir>..."""
import sys, numpy as np
np.set_printoptions(linewidth=200)
allper = []
for d in sys.argv[1:]:
    z = np.load(f'{d}/reach_diag.npz'); R = z['rows']; cols = list(map(str, z['cols'])); c = {k: i for i, k in enumerate(cols)}
    s = R[:, c['s']].astype(int); j = R[:, c['j']]; E = R[:, c['E']]; Rh = R[:, c['R']]; mt = R[:, c['match']] > 0; won = R[:, c['won']] > 0; err = R[:, c['err_m']]; thing = R[:, c['thing']] > 0; cs = R[:, c['compSize']]; rims = R[:, c['rims']]
    name = d.rstrip('/').split('rd_')[-1]
    print(f'=== {name}: {len(np.unique(s))} sheets, {len(R)} texels; won {int(won.sum())}, match among won {100*mt[won].mean():.1f} %')
    # global: match among won and error, j <= E vs j > E, j <= 2E
    for lab, m in (('j<=E', j <= E), ('E<j<=2E', (j > E) & (j <= 2 * E)), ('j>2E', j > 2 * E)):
        mw = m & won
        print(f'   {lab:9}: texels {int(m.sum()):8d} match {100*mt[m].mean() if m.any() else float("nan"):5.1f} % | won {int(mw.sum()):7d} match {100*mt[mw].mean() if mw.any() else float("nan"):5.1f} % |err| med {np.median(np.abs(err[mw])) if mw.any() else float("nan"):.3f} m; won & wrong: {int((mw & ~mt).sum())}')
    # per sheet: the truth's reach J* = p90 of j among matched texels (>= 20 matched), against E
    print('   per sheet (>= 20 matched texels):  s  thing    E    R rims  comp | matched  J50  J90  Jmax  J90/E | match rate at j<=E, E<j<=2E, j>2E')
    for si in np.unique(s):
        m = s == si; mm = m & mt
        if mm.sum() < 20: continue
        jm = j[mm]; Ei = E[m][0]; Ri = Rh[m][0]
        r1 = mt[m & (j <= Ei)].mean() if (m & (j <= Ei)).any() else np.nan; r2 = mt[m & (j > Ei) & (j <= 2 * Ei)].mean() if (m & (j > Ei) & (j <= 2 * Ei)).any() else np.nan; r3 = mt[m & (j > 2 * Ei)].mean() if (m & (j > 2 * Ei)).any() else np.nan
        allper.append((name, int(si), bool(thing[m][0]), Ei, Ri, int(mm.sum()), np.percentile(jm, 50), np.percentile(jm, 90), jm.max(), r1, r2, r3))
        print(f'      {si:4d} {int(thing[m][0]):5d} {Ei:5.0f} {Ri:4.0f} {rims[m][0]:4.0f} {cs[m][0]:6.0f} | {int(mm.sum()):6d} {np.percentile(jm,50):5.0f} {np.percentile(jm,90):5.0f} {jm.max():5.0f} {np.percentile(jm,90)/max(Ei,1):6.2f} | {r1:.2f} {r2:.2f} {r3:.2f}')
if allper:
    A = np.array([(p[3], p[4], p[5], p[6], p[7], p[8]) for p in allper], float); th = np.array([p[2] for p in allper])
    ratio = A[:, 4] / np.maximum(A[:, 0], 1)
    print(f'\n=== all {len(allper)} sheets: J90/E median {np.median(ratio):.2f} (p25 {np.percentile(ratio,25):.2f} p75 {np.percentile(ratio,75):.2f}); things {int(th.sum())}: median {np.median(ratio[th]) if th.any() else float("nan"):.2f}; surfaces {int((~th).sum())}: median {np.median(ratio[~th]) if (~th).any() else float("nan"):.2f}')
    for lo, hi in ((0, 5), (5, 15), (15, 40), (40, 100), (100, 1e9)):
        m = (A[:, 0] >= lo) & (A[:, 0] < hi)
        if m.any(): print(f'   E in [{lo},{hi}): {int(m.sum()):3d} sheets, J90 median {np.median(A[m,4]):5.0f}, J90/E median {np.median(ratio[m]):.2f}, J90/R median {np.median(A[m,4]/np.maximum(A[m,1],1)):.2f}')
