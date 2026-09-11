# Depth bake-off — Colab notebook (five cells, T4 GPU, ~20 minutes)

Open https://colab.research.google.com → New notebook → Runtime → Change runtime type → **T4 GPU**.
Upload the photograph's colour image as `photo.png` (Files pane, upload icon). Run the cells in order.
Each model cell is independent and prints `… FAILED: …` instead of stopping the others. Cell 5 downloads
one zip; push it to `moebiusv2` main.

## Cell 0 — helpers

```python
import numpy as np, os, json, time, torch
from PIL import Image
from IPython.display import display
IMG = "photo.png"; OUT = "bakeoff"; os.makedirs(OUT, exist_ok=True)
img = Image.open(IMG).convert("RGB"); W, H = img.size; print("photo", W, "x", H, "| cuda:", torch.cuda.is_available())
LOG = {}
def save(name, arr, kind, seconds, note=""):
    """arr: float (h,w). kind 'depth' (larger = farther; metres or relative) or 'inverse' (larger = nearer).
    Writes the raw float .npy (resampled to the photograph's size if needed) and a 16-bit inverse-depth PNG,
    bright = near, invalid/inf at the far end."""
    a = np.asarray(arr, dtype=np.float64)
    if a.shape != (H, W):
        a = np.array(Image.fromarray(a.astype(np.float32), mode="F").resize((W, H), Image.BILINEAR), dtype=np.float64)
    np.save(f"{OUT}/{name}.npy", a.astype(np.float32))
    valid = np.isfinite(a) & ((a > 0) if kind == "depth" else True)
    inv = np.where(valid, 1.0 / np.maximum(a, 1e-9), 0.0) if kind == "depth" else np.where(valid, a, np.nanmin(a[valid]))
    lo, hi = inv[valid].min(), inv[valid].max()
    d16 = np.round((inv - lo) / (hi - lo) * 65535).clip(0, 65535).astype(np.uint16)
    Image.fromarray(d16).save(f"{OUT}/{name}_disp16.png")
    LOG[name] = dict(kind=kind, shape=list(a.shape), seconds=round(seconds, 1), valid_frac=float(valid.mean()),
                     min=float(a[valid].min()), max=float(a[valid].max()), distinct16=int(len(np.unique(d16))), note=note)
    json.dump(LOG, open(f"{OUT}/log.json", "w"), indent=1); print(name, LOG[name])
    display(Image.fromarray((d16 // 257).astype(np.uint8)).resize((W // 3, H // 3)))
```

## Cell 1 — Depth Pro (Apple)

```python
try:
    !git clone -q https://github.com/apple/ml-depth-pro && pip -q install -e ml-depth-pro
    !mkdir -p checkpoints && wget -q https://ml-site.cdn-apple.com/models/depth-pro/depth_pro.pt -P checkpoints
    import depth_pro
    model, transform = depth_pro.create_model_and_transforms(device=torch.device("cuda")); model.eval()
    image, _, f_px = depth_pro.load_rgb(IMG); t0 = time.time()
    with torch.no_grad(): pred = model.infer(transform(image), f_px=f_px)
    save("depthpro", pred["depth"].cpu().numpy(), "depth", time.time() - t0, note=f"metres; focal_px={float(pred['focallength_px']):.1f}")
except Exception as e: print("DEPTH PRO FAILED:", repr(e))
```

## Cell 2 — MoGe-2 (Microsoft)

```python
try:
    !pip -q install git+https://github.com/microsoft/MoGe.git
    import cv2; from moge.model.v2 import MoGeModel
    dev = torch.device("cuda"); model = MoGeModel.from_pretrained("Ruicheng/moge-2-vitl").to(dev)
    im = cv2.cvtColor(cv2.imread(IMG), cv2.COLOR_BGR2RGB)
    x = torch.tensor(im / 255, dtype=torch.float32, device=dev).permute(2, 0, 1)
    t0 = time.time(); out = model.infer(x, fov_x=None, resolution_level=9, use_fp16=False)
    d = out["depth"].cpu().numpy().astype(np.float64); m = out["mask"].cpu().numpy().astype(bool); d[~m] = np.inf
    save("moge2", d, "depth", time.time() - t0, note=f"metres; valid={m.mean():.3f}; fx={float(out['intrinsics'][0,0]):.3f} (normalised)")
except Exception as e: print("MOGE-2 FAILED:", repr(e))
```

## Cell 3 — Pixel-Perfect Depth (NeurIPS 2025)

```python
try:
    !git clone -q https://github.com/gangweix/pixel-perfect-depth && cd pixel-perfect-depth && pip -q install -r requirements.txt
    !mkdir -p pixel-perfect-depth/checkpoints
    !wget -q https://huggingface.co/gangweix/Pixel-Perfect-Depth/resolve/main/ppd.pth -O pixel-perfect-depth/checkpoints/ppd.pth
    !wget -q "https://huggingface.co/depth-anything/Depth-Anything-V2-Large/resolve/main/depth_anything_v2_vitl.pth?download=true" -O pixel-perfect-depth/checkpoints/depth_anything_v2_vitl.pth
    t0 = time.time()
    !cd pixel-perfect-depth && python run.py --img_path ../photo.png --outdir ../ppd_vis --pred_only --save_npy
    d = np.load("pixel-perfect-depth/depth_npy/photo.npy")
    save("ppd", d, "depth", time.time() - t0, note="raw run.py --save_npy output (4 sampling steps, DA2 semantics); sign checked offline")
except Exception as e: print("PPD FAILED:", repr(e))
```

## Cell 4 — Depth Anything 3, monocular Large

```python
try:
    !git clone -q https://github.com/ByteDance-Seed/Depth-Anything-3 && cd Depth-Anything-3 && pip -q install xformers && pip -q install -e .
    import sys; sys.path.insert(0, "Depth-Anything-3")
    from depth_anything_3.api import DepthAnything3
    model = DepthAnything3.from_pretrained("depth-anything/DA3MONO-LARGE").to(device="cuda")
    t0 = time.time(); pred = model.inference([IMG])
    save("da3mono", pred.depth[0], "depth", time.time() - t0, note=f"relative depth; processed {list(pred.processed_images.shape)}")
except Exception as e: print("DA3 FAILED:", repr(e))
```

## Cell 5 — one zip to download and push

```python
!cd bakeoff && zip -q -r ../bakeoff_outputs.zip . && ls -la ../bakeoff_outputs.zip && cat log.json
from google.colab import files; files.download("bakeoff_outputs.zip")
```

Push `bakeoff_outputs.zip` to `moebiusv2` main. The rest (unzip, sign check against the DA2 map, 8-bit
requantisation, probes, seam audit, holes, sheets, note §12) runs here without you.
