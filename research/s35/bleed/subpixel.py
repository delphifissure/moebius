"""S47: how much of the band is a SUB-PIXEL GAP and how much is a GENUINE DISOCCLUSION?

This decides whether moving from a displaced mesh to sized splats is worth building, and it decides it with a measurement
rather than a renderer.

The splat proposal (user document, 2026-09-21) is: drop the mesh, draw one square splat per source texel, and size each
splat so that it exactly covers its own pixel at rest and grows only as much as the gap its own cell opens. Adjacent texels
separate only where DEPTH varies, and the separation in pixels is

    reveal = |ex| * | Z_far/(D+Z_far) - Z_near/(D+Z_near) | * pxPerWorld

so the spacing between two adjacent splats goes from 1 texel to 1 + reveal. Oversizing a splat by (1 + T) therefore closes
every gap below T pixels seamlessly and leaves every gap above T open and honest. That is the whole claim, and it makes the
splat size, the cliff criterion and the tear threshold one number.

What it does NOT say is how much of our band falls on each side of T, and that is what decides the value:
  * if most of the revealed AREA comes from cells opening less than T, splats close most of the band for free and the change
    is worth a lot;
  * if most of it comes from cliffs opening far more than T, splats delete a streak we can already delete (S46) and leave
    exactly the same hole to fill, so the change buys structure but no pixels.

Measured here from the depth map and the app's own parallax law, at the envelope rim, per adjacent pair, in two currencies:
the COUNT of cells (which small gaps dominate by construction) and the AREA they reveal (which is what a viewer sees).

  subpixel.py [--scenes L1,L5,L6,L7,L8,L9] [--pictures troll] [--T 1,2,4]
"""
import sys, os, json, argparse
import numpy as np
sys.path.insert(0, '/home/user/moebiusv2/harness/truthkit')
from tk import app_z_of_d

ap = argparse.ArgumentParser()
ap.add_argument('--scenes', default='L1,L5,L6,L7,L8,L9')
ap.add_argument('--pictures', default='troll')
ap.add_argument('--T', default='1,2,4')
ap.add_argument('--env', type=float, default=45.0)
# The truth kit is rendered with outer = 0.64 m at D = 0.2, a relief of 3.2, deliberately extreme so the band is large
# enough to score. The APP ships outer = 0.02 at the same D, a relief of 0.1 -- thirty-two times shallower. Since this
# measurement needs only the depth map and the law, the law can be overridden without re-rendering anything, which is the
# control that separates "the kit's scenes are hard" from "the kit's depth law is aggressive".
ap.add_argument('--outer', type=float, default=0.0, help='override the scene depth in metres (0 = use each probe\'s own)')
A = ap.parse_args()
P0 = '/home/user/moebiusv2/harness/shots/a257probe'
PROBE = {'L1': 'L1_16plane', 'L5': 'L5_16plane', 'L6': 'L6_16plane', 'L7': 'L7_16plane', 'L8': 'L8_16plane',
         'L9': 'L9_16plane', 'troll': 'troll'}
TS = [float(t) for t in A.T.split(',')]


def measure(tag):
    P = f'{P0}/{PROBE[tag]}'
    meta = json.load(open(f'{P}/meta.json'))
    pw, ph = meta['pw'], meta['ph']; outer, inner, pn = meta['outer'], meta['inner'], meta['pn']
    D = meta.get('D') or 0.2; tw = meta.get('terrariumWidth') or 0.16; th = meta.get('terrariumHeight') or 0.09
    if A.outer > 0: outer = A.outer
    dQ = np.fromfile(f'{P}/dQ.f32', np.float32).reshape(ph, pw).astype(np.float64)
    band = (np.fromfile(f'{P}/disocc.u8', np.uint8).reshape(ph, pw) > 0) if os.path.exists(f'{P}/disocc.u8') else None
    # the plate's world width, the way the app fits the layer into the frame
    la, fa = pw / ph, tw / th
    layerW = tw if la > fa else th * la
    pxPerWorld = pw / layerW
    ex = D * np.tan(np.radians(A.env))                       # the eye offset at the envelope rim
    # Z is the depth BEHIND the portal plane; the app's own law, not a re-derivation
    Z = -app_z_of_d(dQ, pn, outer, inner)
    s = Z / (D + Z)                                          # the fraction of the head motion this texel's image follows
    # horizontal adjacent pairs: the gap that opens between texel x and x+1 at the rim
    rev = np.abs(s[:, 1:] - s[:, :-1]) * ex * pxPerWorld
    # vertical too, for the vertical half of the envelope (the envelope is +-45 h and +-30 v)
    exv = D * np.tan(np.radians(30.0))
    revv = np.abs(s[1:, :] - s[:-1, :]) * exv * pxPerWorld
    out = {'tag': tag, 'pw': pw, 'ph': ph, 'outer': outer, 'D': D, 'pxPerWorld': pxPerWorld, 'ex': ex,
           'kMax': float(np.nanmax(rev)), 'relief': outer / D,
           'bandPx': int(band.sum()) if band is not None else None}
    for nm, r in (('h', rev), ('v', revv)):
        r = r[np.isfinite(r)]
        area = r.sum()
        out[nm] = {'cells': int(r.size), 'openCells': int((r > 0.01).sum()), 'areaPx': float(area),
                   'p50': float(np.percentile(r, 50)), 'p90': float(np.percentile(r, 90)),
                   'p99': float(np.percentile(r, 99)), 'max': float(r.max())}
        for T in TS:
            below = r <= T
            # WHAT SPLATS BUY OVER A TORN MESH, which is the comparison that matters. A torn mesh removes the cliff quad and
            # leaves a hole of the full reveal. A splat of size 1+T covers T pixels beyond its own, so it closes a cell
            # below T entirely and shortens every cell above T by exactly T. The mesh and the splats are otherwise identical:
            # both cover the smooth part and both leave the cliff open.
            # CORRECTED. The first version added the whole sub-T area, which double-counts: a mesh is only torn where the
            # criterion fires, so on a cell below T the quad is KEPT and already covers the gap exactly. The two
            # representations differ only on the cells above T, where the torn mesh leaves the full reveal open and a splat
            # of size 1+T leaves reveal - T. So the saving is T per torn cell and nothing else.
            saved = T * float((~below).sum())
            out[nm][f'T{T:g}'] = {'cellsBelow': float(below.mean()),
                                  'areaBelow': float(r[below].sum() / max(area, 1e-9)),
                                  'areaAbovePx': float(r[~below].sum()),
                                  'savedVsTornMesh': float(saved / max(area, 1e-9))}
    return out


rows = [measure(t) for t in (A.scenes.split(',') + A.pictures.split(',')) if t and t in PROBE]
print(f'Envelope {A.env:g} deg horizontal, 30 deg vertical. "reveal" is the gap in PIXELS that opens between two adjacent')
print('texels at the rim -- the quantity a sized splat would have to span. Splats close a gap seamlessly below T and leave')
print('it open above T, so the area share below T is exactly what the change would buy.\n')
print(f"{'':6s} {'relief':>7s} {'max reveal':>11s} | {'median':>8s} {'p90':>8s} {'p99':>8s} | "
      + ' '.join(f'{"cells<=" + str(int(t)):>11s} {"AREA<=" + str(int(t)):>11s}' for t in TS))
for r in rows:
    h = r['h']
    print(f"{r['tag']:6s} {r['relief']:7.3f} {r['kMax']:10.1f}px | {h['p50']:8.3f} {h['p90']:8.3f} {h['p99']:8.3f} | "
          + ' '.join(f"{100*h[f'T{t:g}']['cellsBelow']:10.2f}% {100*h[f'T{t:g}']['areaBelow']:10.2f}%" for t in TS))
print('\nvertical axis (30 deg):')
for r in rows:
    v = r['v']
    print(f"{r['tag']:6s} {'':7s} {v['max']:10.1f}px | {v['p50']:8.3f} {v['p90']:8.3f} {v['p99']:8.3f} | "
          + ' '.join(f"{100*v[f'T{t:g}']['cellsBelow']:10.2f}% {100*v[f'T{t:g}']['areaBelow']:10.2f}%" for t in TS))
print('\nWhat splats buy OVER A TORN MESH (both cover the smooth part, both leave the cliff open; a splat of size 1+T')
print('additionally shortens every cliff by T):')
print(f"{'':6s} " + ' '.join(f'{"T=" + str(int(t)):>10s}' for t in TS))
for r in rows:
    print(f"{r['tag']:6s} " + ' '.join(f"{100*r['h'][f'T{t:g}']['savedVsTornMesh']:9.2f}%" for t in TS))
print('\ncells<=T is the share of adjacent pairs whose gap a splat of size 1+T closes; AREA<=T is the share of the TOTAL')
print('REVEALED AREA those pairs account for. The second is the one that decides: it is the fraction of what the viewer')
print('sees opening that splats would fill for free, and 1 - it is the fraction that still needs filled content.')
json.dump(rows, open('/tmp/claude-0/-home-user-moebius/989b3965-28fd-58c7-96b5-b4b22c709919/scratchpad/subpixel.json', 'w'), indent=1)
