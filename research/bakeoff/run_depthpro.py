import sys, os, time, torch; B=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, B); from common import *
import depth_pro
from depth_pro.depth_pro import DEFAULT_MONODEPTH_CONFIG_DICT as C
C.checkpoint_uri = f"{B}/ckpt/depth_pro.pt"
torch.set_num_threads(4)
model, transform = depth_pro.create_model_and_transforms(config=C, device=torch.device("cpu"), precision=torch.float32); model.eval()
image, _, f_px = depth_pro.load_rgb(IMG); t0 = time.time()
with torch.no_grad(): pred = model.infer(transform(image), f_px=f_px)
save("depthpro", pred["depth"].cpu().numpy(), "depth", time.time() - t0, note=f"metres; focal_px={float(pred['focallength_px']):.1f}; f_px from EXIF={f_px}")
