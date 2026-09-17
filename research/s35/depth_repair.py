"""S35 §27: segmentation-consistent depth. A monocular depth map loses thin structure (starwatcher's staff: the shaft above the
hand and the lantern's loop sit at the sky's depth, so they split from the figure and stay on the plate). The segmentation
knows better: SAM's sky segment excludes the staff exactly. Rule, no constant:
  a texel that is NOT in segment S, lies at S's depth (within S's own spread, never under the visible step), belongs to a
  4-connected component of such texels whose outer boundary is MOSTLY S (enclosed by it) and which touches a texel NEARER
  than S by more than the step (it hangs off a foreground thing), and whose colour is closer to that nearest foreground
  texel's colour than to S's own median colour, is a texel of that thing whose depth failed. It takes the depth of
  the nearest texel that is nearer than S.
Applied for every SAM segment. Writes the repaired 16-bit depth and a report.
  depth_repair.py <depth16.png> <sam.png> <color.png> <quantum> <out16.png> [--diag crop.png y0 y1 x0 x1]"""
import sys, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
dP, sP, cP, Q, oP = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), sys.argv[5]
d16 = np.asarray(Image.open(dP)).astype(np.float64); d16 = d16[..., 0] if d16.ndim == 3 else d16
d = d16 / 65535.0; ph, pw = d.shape
sam = np.asarray(Image.open(sP)); sam = sam[..., 0] if sam.ndim == 3 else sam
if sam.shape != d.shape: sam = np.asarray(Image.fromarray(sam).resize((pw, ph), Image.NEAREST))
col = np.asarray(Image.open(cP).convert('RGB').resize((pw, ph), Image.BILINEAR)).astype(np.float64)
out = d.copy(); fixed = np.zeros(d.shape, bool); report = []
cross = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)
decided = np.zeros(d.shape, bool)                       # a texel absorbed into a segment or repaired is settled
# the picture's far limit = the farthest SURFACE: among segments that are the majority of the unlabelled-or-S material at
# their own depth (a real surface, not a fragment), the one with the smallest median depth. (The raw minimum of the map is a
# few stray texels and disqualified the sunflowers' sky and vermeer's wall.)
def _isSurface(sid_):
    inS_ = sam == sid_
    if inS_.sum() < 4: return None
    dS_ = np.median(d[inS_]); tol_ = max(Q, np.median(np.abs(d[inS_] - dS_)) * 1.4826)
    atS_ = (sam == 0) & (np.abs(d - dS_) <= tol_)
    return dS_ if int(inS_.sum()) > int(atS_.sum()) else None
_surf = [(_isSurface(i), i) for i in np.unique(sam) if i > 0]; _surf = [t for t in _surf if t[0] is not None]
dFar = min(t[0] for t in _surf) if _surf else float(np.min(d))
ids = sorted([i for i in np.unique(sam) if i > 0], key=lambda i: -int((sam == i).sum()))   # largest surface first
for sid in ids:
    inS = sam == sid
    if inS.sum() < 4: continue
    dS = np.median(d[inS]); spreadS = np.median(np.abs(d[inS] - dS)) * 1.4826
    tolS = max(Q, spreadS)                      # S's own depth spread, never under the visible step
    atS = (sam == 0) & ~decided & (np.abs(d - dS) <= tolS)  # UNLABELLED, undecided, at S's depth (other segments are their own things)
    nearer = d > dS + Q                          # material in front of S
    if not atS.any() or not nearer.any(): continue
    # ONLY A SURFACE ENCLOSES. A segment is the surface of its depth layer only if it is the majority of the unlabelled-or-S
    # material at that depth; a rock or a hut on the plain (a segment of 6 000 texels with 32 000 unlabelled plain texels at
    # its depth) is a fragment and encloses nothing. Without this, starwatcher's horizon pieces repaired 26 000 plain texels.
    if int(inS.sum()) <= int(atS.sum()): continue
    # ONLY THE FARTHEST SURFACE. Nothing opaque can sit AT the sky's depth in front of the sky, so an unlabelled thing there
    # is a depth failure; but a loaf on a table is legitimately at the table's depth (vermeer: 14 536 texels of bread and
    # basket would have moved). The rule applies to the surface at the picture's far limit only.
    if dS > dFar + tolS: continue
    dist, (iy, ix) = ndimage.distance_transform_edt(~nearer, return_indices=True)
    cS = np.median(col[inS], 0)
    ay, ax_ = np.nonzero(atS); fy, fx = iy[ay, ax_], ix[ay, ax_]
    toFG = np.linalg.norm(col[ay, ax_] - col[fy, fx], axis=1); toS = np.linalg.norm(col[ay, ax_] - cS, axis=1)
    # THE HALO: SAM's segment stops short of a silhouette by a texel or two, leaving unlabelled texels that are S in depth
    # and colour; they are S (starwatcher: 5 883 such texels ring the figure, with the staff's ink inside the ring)
    halo = np.zeros(d.shape, bool); halo[ay[toS <= toFG], ax_[toS <= toFG]] = True
    S2 = inS | halo; decided |= halo
    rest = atS & ~halo
    if not rest.any(): continue
    lab, n = ndimage.label(rest, cross)
    touchN = ndimage.binary_dilation(nearer, cross) & rest
    okN = np.zeros(n + 1, bool); okN[np.unique(lab[touchN])] = True
    # ENCLOSED BY S: the majority of the component's outer boundary is S (a thin thing inside the sky), not merely touching
    # it (a small segment at the sky's depth would otherwise make the whole sky a candidate: 312 k texels on starwatcher)
    cS_ = np.zeros(n + 1, np.int64); cO_ = np.zeros(n + 1, np.int64)
    # (the contact with the NEARER thing it hangs off does not count against enclosure: the figure's ink outline is a ring with
    #  the sky on one side and the figure on the other, and it is the figure's — left at the sky's depth it bakes a black
    #  outline of the figure into the sky)
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        nl = np.roll(np.roll(lab, dy, 0), dx, 1); ns = np.roll(np.roll(S2, dy, 0), dx, 1); nn = np.roll(np.roll(nearer, dy, 0), dx, 1)
        contact = (lab > 0) & (nl != lab)
        cS_ += np.bincount(lab[contact & ns], minlength=n + 1); cO_ += np.bincount(lab[contact & ~ns & ~nn], minlength=n + 1)
    okB = cS_ > cO_
    cand = rest & okB[lab] & okN[lab]
    if not cand.any(): continue
    cy, cx = np.nonzero(cand)
    out[cy, cx] = d[iy[cy, cx], ix[cy, cx]]; fixed[cy, cx] = True; decided[cy, cx] = True
    report.append((int(sid), int(inS.sum()), float(dS), int(halo.sum()), int(rest.sum()), int(cand.sum())))
Image.fromarray(np.clip(np.round(out * 65535), 0, 65535).astype(np.uint16)).save(oP)
print(f'repaired {int(fixed.sum())} texels of {ph * pw}; per segment (id, size, depth, halo absorbed, other texels at its depth, repaired):')
for r in sorted(report, key=lambda r: -r[5])[:12]: print('   ', r)
if '--map' in sys.argv:
    mp = sys.argv[sys.argv.index('--map') + 1]
    Image.fromarray(np.where(fixed[..., None], np.array([255, 60, 60], np.uint8), (col * 0.4).astype(np.uint8))).save(mp); print('wrote', mp)
if '--diag' in sys.argv:
    k = sys.argv.index('--diag'); name = sys.argv[k + 1]; y0, y1, x0, x1 = map(int, sys.argv[k + 2:k + 6])
    def gam(a): return (np.clip(a, 0, 1) ** 0.5 * 255).astype(np.uint8)
    panels = [('colour', col.astype(np.uint8)), ('depth before', np.stack([gam(d)] * 3, -1)), ('depth after', np.stack([gam(out)] * 3, -1)),
              ('repaired texels', np.where(fixed[..., None], np.array([255, 60, 60], np.uint8), (col * 0.35).astype(np.uint8)))]
    sc = max(1, 1400 // ((x1 - x0) * 4)); W = (x1 - x0) * sc; H = (y1 - y0) * sc
    sh = Image.new('RGB', (W * 4 + 30, H + 16), (20, 20, 20)); dr = ImageDraw.Draw(sh)
    for i, (nm, a) in enumerate(panels): sh.paste(Image.fromarray(np.ascontiguousarray(a[y0:y1, x0:x1])).resize((W, H), Image.NEAREST), (i * (W + 10), 16)); dr.text((i * (W + 10) + 3, 2), nm, fill=(255, 255, 0))
    sh.save(name); print('wrote', name)
