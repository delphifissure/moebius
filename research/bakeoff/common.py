import numpy as np, os, json, time
from PIL import Image
IMG = "/home/user/moebiusv2/defaultImgColor.png"; OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
img = Image.open(IMG).convert("RGB"); W, H = img.size
def save(name, arr, kind, seconds, note=""):
    """arr float (h,w). kind 'depth' (larger = farther) or 'inverse' (larger = nearer). Writes raw .npy (resampled to the
    photograph if needed) and a 16-bit inverse-depth PNG, bright = near, invalid/inf at the far end; appends to log.json."""
    a = np.asarray(arr, dtype=np.float64); native = list(a.shape)
    if a.shape != (H, W): a = np.array(Image.fromarray(a.astype(np.float32), mode="F").resize((W, H), Image.BILINEAR), dtype=np.float64)
    np.save(f"{OUT}/{name}.npy", a.astype(np.float32))
    valid = np.isfinite(a) & ((a > 0) if kind == "depth" else True)
    inv = np.where(valid, 1.0 / np.maximum(a, 1e-9), 0.0) if kind == "depth" else np.where(valid, a, np.nanmin(a[valid]))
    lo, hi = inv[valid].min(), inv[valid].max()
    d16 = np.round((inv - lo) / (hi - lo) * 65535).clip(0, 65535).astype(np.uint16)
    Image.fromarray(d16).save(f"{OUT}/{name}_disp16.png")
    lp = f"{OUT}/log.json"; LOG = json.load(open(lp)) if os.path.exists(lp) else {}
    LOG[name] = dict(kind=kind, native_shape=native, seconds=round(seconds, 1), valid_frac=float(valid.mean()), min=float(a[valid].min()), max=float(a[valid].max()), distinct16=int(len(np.unique(d16))), note=note)
    json.dump(LOG, open(lp, "w"), indent=1); print(name, LOG[name], flush=True)
