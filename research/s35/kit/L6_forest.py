"""S35 §56: the L6 scene as added to moebiusv2/harness/truthkit/scenes.py (registry key 'L6'; committed there locally on
main, 2026-09-20). Kept here so the moebius branch carries the definition. Recipe, as for L5:
  python3 make.py L6 --nx 800
  python3 scope.py L6 --nx 800 --thx 0,5.6,11.3,16.7,22,27,31.6,36,40.1,45 --thy 0,15.7,29.4 --out out/L6_env45
  python3 truth_ids.py L6                     -> truth_ids_all.png   (every tree labelled)
  python3 truth_ids.py L6 --unlabelled tree   -> truth_ids_click.png (the figure only: the troll's click mask)
  IMG=harness/truthkit/out/L6/rest_rgb.png,harness/truthkit/out/L6/rest_depth16.png DEPTH_OUTER=0.64 DEPTH_INNER=0.0001 \
    DEPTH_PN=0.5 FLAGS=_tearLaw=rim,_farRule=plane TAG=L6_16plane node a257_probe.js
Visible step 1.312e-3; band 126 588 texels (35.2 % of the frame)."""
import numpy as np
from tk import Quad, Sphere, Cylinder, Canopy, tex_checker, tex_noise, tex_solid, tex_stripes
STUFF, THING = 1, 2


def _figure(prims, W, H, x, z, r, name):
    """A standing figure: a capsule body and a sphere head, feet on the floor at y = -H/2 (scenes.py helper, copied)."""
    prims.append(Cylinder([x, -H / 2, z], [x, H * 0.2, z], r, lambda p: tex_stripes(p, scale=W * 0.02, c1=(0.8, 0.55, 0.45), c2=(0.5, 0.3, 0.3), axis=1), THING, name + '_body'))
    prims.append(Sphere([x, H * 0.2 + 0.9 * r, z], 0.9 * r, lambda p: tex_checker(p, scale=W * 0.015, c1=(0.9, 0.7, 0.55), c2=(0.6, 0.4, 0.3), axes=(1, 2)), THING, name + '_head'))


def L6_forest_graded(W=0.16, H=0.09):
    """S35 §56: the TROLL's configuration in exact truth. L1/L4 put their leaf layer in one narrow slab (0.5-0.7 W) with a flat
    wall 1.2 W behind; the troll stands before a forest that recedes continuously, so behind him the truth is foliage, trunks,
    ground and sky at many depths and never one plane. Here: a figure at 0.3 W, then forty trees (a trunk and a porous crown
    each) in ten ranks from 0.5 W to 3.2 W, shrinking with distance and dense enough to close the canopy across the frame, over
    a ground plane with a sky wall at 4 W. The forest is named tree* so that `truth_ids.py L6 --unlabelled tree` gives the map
    the troll has under a click mask (the figure labelled, the forest left as depth components), and `truth_ids.py L6` labels
    every tree."""
    depth = 4.0 * W
    prims = []
    prims.append(Quad([0, -H / 2, -depth / 2], [1, 0, 0], [0, 0, 1], 3 * W, depth / 2 + 0.001, lambda p: tex_checker(p, scale=W * 0.25, c1=(0.40, 0.46, 0.28), c2=(0.30, 0.38, 0.22), axes=(0, 2)), STUFF, 'ground'))
    prims.append(Quad([0, 0, -depth], [1, 0, 0], [0, 1, 0], 3 * W, 3 * H, lambda p: tex_noise(p, scale=W * 0.4, base=(0.55, 0.7, 0.95), amp=0.08, axes=(0, 1)), STUFF, 'sky_wall'))
    _figure(prims, W, H, -0.13 * W, -0.30 * W, W * 0.075, 'figure')
    rng = np.random.RandomState(56); k = 0
    for rank in range(10):
        z = -(0.50 + 0.28 * rank * (1 + 0.09 * rank)) * W          # ten ranks, 0.5 W to 3.2 W, spacing growing with distance
        sc = 1.0 / (1.0 + 0.30 * rank)                              # trees shrink with distance
        nT = 4 + rank // 3
        for j in range(nT):
            x = (-1.15 + 2.3 * (j + 0.5 + 0.7 * (rng.rand() - 0.5)) / nT) * W
            z_ = z + W * 0.10 * (rng.rand() - 0.5)
            th = H * (0.30 + 0.12 * rng.rand()) * sc                # trunk height
            prims.append(Cylinder([x, -H / 2, z_], [x, -H / 2 + th, z_], W * 0.020 * sc, tex_solid((0.34, 0.24, 0.17)), THING, f'tree{k}_trunk'))
            g = 0.42 + 0.14 * rng.rand()
            prims.append(Canopy([x, -H / 2 + th + H * 0.30 * sc, z_], [W * 0.34 * sc, H * 0.46 * sc, W * 0.10 * sc], 90, W * 0.020 * sc,
                                tex_solid((0.20, g, 0.17)), seed=56 + k, name=f'tree{k}_crown')); k += 1
    return prims, {'outer': depth, 'inner': 0.0, 'element': 'layer family: a figure before a forest receding continuously (the troll)'}

