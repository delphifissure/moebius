"""S39: the L7 scene as added to moebiusv2/harness/truthkit/scenes.py (registry key 'L7'). Kept here so the moebius
branch carries the definition, as L5 and L6 are. Rendered with make.py L7 --nx 800; truth with scope.py L7 --nx 800
--thx 0,5.6,11.3,16.7,22,27,31.6,36,40.1,45 --thy 0,15.7,29.4 --out out/L7_env45 (the env45 grid); object maps
truth_ids.py L7 (every piece a thing) and truth_ids.py L7 --unlabelled boulder (the click map, figure only); probe
IMG=harness/truthkit/out/L7/rest_rgb.png,harness/truthkit/out/L7/rest_depth16.png DEPTH_OUTER=0.64 DEPTH_INNER=0.0001
DEPTH_PN=0.5 FLAGS=_tearLaw=rim,_farRule=plane TAG=L7_16plane node a257_probe.js."""
import numpy as np
from tk import Quad, Sphere, Cylinder, Ellipsoid, tex_checker, tex_noise, tex_solid, tex_stripes
STUFF, THING = 1, 2

# _figure is the shared helper in scenes.py; _ground_and_sky was added with these three scenes.


def _ground_and_sky(W, H, depth):
    prims = []
    prims.append(Quad([0, -H / 2, -depth / 2], [1, 0, 0], [0, 0, 1], 3 * W, depth / 2 + 0.001, lambda p: tex_checker(p, scale=W * 0.25, c1=(0.40, 0.46, 0.28), c2=(0.30, 0.38, 0.22), axes=(0, 2)), STUFF, 'ground'))
    prims.append(Quad([0, 0, -depth], [1, 0, 0], [0, 1, 0], 3 * W, 3 * H, lambda p: tex_noise(p, scale=W * 0.4, base=(0.55, 0.7, 0.95), amp=0.08, axes=(0, 1)), STUFF, 'sky_wall'))
    return prims


def L7_boulders(W=0.16, H=0.09):
    """S38/S39, the L5 regime, sparse and large: rounded boulders RESTING ON the ground at graded depths, with a figure in
    front. L5's clumps merge into the ground through their contact, so a click-the-heads map leaves them as part of the
    ground's join group and the construction collapses; L6's crowns sit in the air and stay their own components. This scene
    keeps L5's contact but makes the pieces far larger and sparser, so the ground shows between them -- the case where the
    arm might cope. Field named boulder* for `truth_ids.py L7 --unlabelled boulder`."""
    depth = 4.0 * W
    prims = _ground_and_sky(W, H, depth)
    _figure(prims, W, H, -0.12 * W, -0.30 * W, W * 0.085, 'figure')
    rng = np.random.RandomState(70); k = 0
    for rank in range(8):
        z = -(0.55 + 0.34 * rank * (1 + 0.10 * rank)) * W
        sc = 1.0 / (1.0 + 0.28 * rank)
        for j in range(4 + rank // 3):
            x = (-1.2 + 2.4 * (j + 0.5 + 0.6 * (rng.rand() - 0.5)) / (4 + rank // 3)) * W
            r = W * (0.085 + 0.045 * rng.rand()) * sc
            g = 0.40 + 0.16 * rng.rand()
            prims.append(Ellipsoid([x, -H / 2 + r * 0.75, z + W * 0.12 * (rng.rand() - 0.5)], [r * 1.35, r * 0.8, r],
                                   tex_solid((0.34 + 0.06 * rng.rand(), g * 0.7, 0.30)), THING, f'boulder{k}')); k += 1
    return prims, {'outer': depth, 'inner': 0.0, 'element': 'L5 regime, sparse: boulders resting on the ground, figure in front'}
