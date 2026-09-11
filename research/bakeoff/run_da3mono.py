import sys, os, time, torch; B=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, B); sys.path.insert(0, f"{B}/Depth-Anything-3/src"); from common import *
from depth_anything_3.api import DepthAnything3
torch.set_num_threads(4)
model = DepthAnything3.from_pretrained("depth-anything/DA3MONO-LARGE").to(device="cpu").eval()
t0 = time.time()
with torch.no_grad(): pred = model.inference([IMG], process_res=1008, process_res_method="upper_bound_resize")
save("da3mono", pred.depth[0], "depth", time.time() - t0, note=f"relative depth; process_res=1008 (default 504); processed {list(pred.processed_images.shape)}")
