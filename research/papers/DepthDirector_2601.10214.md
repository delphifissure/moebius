# **Beyond Inpainting: Unleash 3D Understanding for Precise Camera-Controlled Video Generation** 

Dong-Yu Chen, Yixin Guo, Shuojin Yang, Tai-Jiang Mu<sup>_†_</sup> , Shi-Min Hu BNRist, Department of Computer Science and Technology, Tsinghua University Beijing 100084, China 

Project webpage: https://eleanor6725.github.io/DepthDirector/ 



<!-- Start of picture text -->
Ne a ey ae<br>ae<br>7 o4,)) fe) oa<br>~ my _ Or lal Tart 7s a. oF ‘i<br>Input View<br>Target View<br>Synthesized<br>Input View<br>Target View<br>Synthesized<br><!-- End of picture text -->

Figure 1. **Example results synthesized by DepthDirector.** DepthDirector re-shoots the source video with novel camera trajectories. By fully leveraging the 3D understanding ability of video diffusion models, we are the first framework that achieves both precise camera controllability and consistent content preservation. We visualized the novel camera trajectories alongside the video frames. 

## **Abstract** 

_Camera control has been extensively studied in conditioned video generation; however, performing precisely altering the camera trajectories while faithfully preserving the video content remains a challenging task. The mainstream approach to achieving precise camera control is warping a 3D representation according to the target trajectory. However, such methods fail to fully leverage the 3D priors of video diffusion models (VDMs) and often fall into the Inpainting Trap, resulting in subject inconsistency and degraded generation quality. To address this problem, we propose DepthDirector, a video re-rendering framework with precise camera controllability. By leveraging the depth video from explicit 3D representation as camera-control guidance, our method can faithfully reproduce the dynamic scene of an input video under novel camera trajectories._ 

_Specifically, we design a View-Content Dual-Stream Condition mechanism that injects both the source video and the warped depth sequence rendered under the target viewpoint into the pretrained video generation model. This geometric guidance signal enables VDMs to comprehend camera movements and leverage their 3D understanding capabilities, thereby facilitating precise camera control and consistent content generation. Next, we introduce a lightweight LoRA-based video diffusion adapter to train our framework, fully preserving the knowledge priors of VDMs. Additionally, we construct a large-scale multi-camera synchronized dataset named MultiCam-WarpData using Unreal Engine 5, containing 8K videos across 1K dynamic scenes. Extensive experiments show that DepthDirector outperforms existing methods in both camera controllability and visual quality. Our code and dataset will be publicly available._ 

> _†_ Corresponding authors. taijiang@tsinghua.edu.cn 

1 

## **1. Introduction** 

Recent advances in video generation, particularly video diffusion models (VDMs), have enabled high-quality, contentcontrollable video synthesis from diverse inputs such as text, images, and videos [12, 18, 60]. Within this rapidly evolving field, camera control is crucial for generating expressive and cinematic videos. It not only helps content creators and cinematographers in framing scene content and dictating global motion, but also craft specific atmospheres and emphasize character emotions. However, in video generation, precise modification of camera trajectories while faithfully preserving video content remains a significant challenge. 

Currently, the straight-forward solution to achieving camera control is to directly use camera parameters as implicit input conditions[1, 3, 4, 19, 47, 63], encoding position and orientation through ray embeddings[1] or relative pose encoder[3, 4]. Although these methods can generate videos with different camera poses, their control mechanisms lack physical consistency and precision. Worse still, to learn the correspondence between camera parameters and scene layout, such methods often rely on large-scale, high-quality, multi-view synchronized rendered datasets [3, 4, 37, 47] (e.g., **136K** videos for ReCamMaster) to implicitly learn 3D consistency. In contrast, we propose a new method that achieves superior performance with merely about **5.8%** of the training cost (using **8K** video sequences). 

Some methods [17, 22, 39, 46, 54, 61] can achieve precise control of camera trajectories through explicit geometry-based guidance and generate final results via video **inpainting** . However, this mechanism fundamentally caps the quality of the generated content at that of the warped RGB video. Our study reveals that unavoidable inaccuracies in 3D geometry estimated from monocular videos introduce distortions and artifacts into the warped RGB sequence, subsequently leading to subject inconsistency and degraded fidelity in the generated results, as illustrated in Fig. 2. This issue stems not from the unrealistic rendering effect of explicit 3D representations (e.g., flying pixels in point clouds in GEN3C[39] and TrajectoryCrafter[61]), but from unreliable depth information derived from monocular video. This is also why approaches like EX-4D[22] could not solve the problem in essence even after injecting occlusion-aware mask by depth watertight meshes[22]. We term this the **Inpainting Trap** , which is essentially a **shortcut** in VDMs. It bypasses understanding of the 3D/4D world and camera transformations, only inpaints a new video that possesses the same distortion as the warped video. 

Instead, we hypothesize that 3D representations are inherently imperfect, and thus we focus on designing a new geometry guidance signal that can compensate for these errors, rather than relying solely on error-prone RGB-level 



<!-- Start of picture text -->
Video Depth<br>Estimation<br>warp video warp depth<br>sensitive insensitive<br>Only  RGB level geometry level Beyond<br>Inpainting Inpainting<br>distorted artifact consistent subject preservation<br>unaware of camera movement leverage 3D understanding<br>Warping-Based method: EX-4D DepthDirector<br>Input Video<br>Warp Result<br>Synthesized Video<br><!-- End of picture text -->

Figure 2. **Limitations of warping-based methods** . Even with SOTA video depth estimators [9, 23, 50, 52], reprojected pixels exhibit noisy artifacts due to inaccurate 3D geometry. It leads to unrecoverable distortion to the identity and details of the subject, especially on human faces, which is sensitive to detailed geometry. 

guidance. To this end, we propose DepthDirector, which injects temporally consistent and detail-error-robust warped depth rendered from explicit 3D representations under the target view, guiding the VDMs to achieve precise camera control. Building upon this mechanism, we integrate the VDMs’ world-understanding prior to re-rendering the video, ensuring precise camera controllability and consistent content preservation, thereby going **beyond inpainting** . As shown in Fig. 2, by introducing the new conditional mechanism, face identity can be effectively preserved for challenging human-centric scenes. 

Specifically, we propose a View–Content Dual-Stream Condition mechanism, in which the source video is used as the content branch containing complex motion and dynamic details, while the warped depth sequence rendered under the target viewpoint serves as the view branch. The warped depth not only provides essential scene layout information for the novel view but also acts as a geometric anchor for querying content from the source video, thereby ensuring consistency in both viewpoint and content of the generated video. 

we introduce a lightweight LoRA-based video diffusion adapter to fine-tune our framework. This efficiently integrates geometric information from the warped-depth condition into the pretrained video diffusion model, producing visually coherent and realistic results while keeping computational costs manageable. 

We construct a multi-camera synchronized video dataset, named MultiCam-WarpData, using Unreal Engine 5, which contains **8K** realistic videos with ground truth depth, 

2 

shooted from **1K** different dynamic scenes. This dataset enables the model to more effectively learn the interplay among the camera control, geometry perception and dynamic content. 

Experimental results show that our method outperforms state-of-the-art approaches, and achieves both precise camera controllability and consistent content preservation. 

## **2. Related Works** 

**Video Diffusion Models.** Video generation model has evolved from early approaches like Make-A-Video [44] and Gen-1 [40] to more sophisticated models. SVD [6] and VideoCrafter [7, 8] enhanced temporal coherence, while large-scale models such as Hunyuan Video [13], CogVideoX [60], and Wan [12] achieve impressive spatiotemporal consistency and 3D understanding ability. **Video Depth Estimation** Recovering depth from monocular video has been widely studied. A line of works focuses on estimating temporally consistent depth without camera estimation. VDA[9] builds upon transformer model and enforce temporal consistency by additional loss. DepthCrafter[23] and ChronoDepth[42] finetune video diffusion models[6] to yield high-quality depth sequences. GeometryCrafter[57] extends this paradigm to predict perframe point map enabling camera intrinsic estimation. Another line of works[14, 29, 34, 50, 52] directly regresses per-frame depth maps and camera parameters in a feedforward manner. These methods leverage multi-task learning and large-scale datasets to achieve superior performance; however, the estimated depth maps still suffer from low resolution and inaccuracy. 

**Implicit Camera Conditioned Video Generation** In camera-controlled video generation [2, 18, 59, 63, 64], researchers aim to directly incorporate camera parameters into video generation models to control the output viewpoint video. Camera extrinsics are injected into the diffusion model via direct parameter concatenation [53], Pl¨ucker Embedding [1, 2, 19, 31, 45], training camera encoder [3, 4, 47] and reference video [37]. Since the correspondence between camera parameters and generated views isn’t straight-forward, they [3, 4, 37, 47] typically rely on large-scale multi-view rendered datasets [3, 4, 37, 47] to implicitly learn 3D consistency and suffer from substantial camera control errors. 

**Explicit Camera Conditioned Video Generation** To leverage explicit geometry reconstructed from input videos and incorporate precise camera conditioning, existing methods achieve camera control by using an anchor video [17, 26, 39, 54, 61, 62]. Some earlier works [5, 17, 56] leverage 3D point tracking [28, 55] to inject camera movements, which can cause artifacts if tracking fails. In order to inject 3D information, another line of works [20, 22, 39, 54, 61, 62] uses a warp-and-inpaint strategy. They reconstruct a 

per-frame 3D representation and repaint on a warped video of target trajectories. However, these methods are prone to produce artifacts from noisy warps. A concurrent work WorldForge [46] designs a training-free method to mitigate the noisy artifacts, while our method introduces a new conditioning mechanism that injects camera viewpoints informed by explicit geometry, enabling higher video generation quality and achieving more accurate camera control than implicit camera conditioned approaches. 

## **3. Method** 

As shown in Fig.3, the goal of our DepthDirector framework is to generate novel-view videos _VT_ = _{It}_<sup>_T_</sup> _t_ =1<sup>from</sup> an input monocular video _VS_ = _{It}_<sup>_S_</sup> _t_ =1<sup>and a target camera</sup> trajectory _{Pt}_<sup>_T_</sup> _t_ =1<sup>.Itconsistsoffourkeysteps:(1)con-</sup> structing an explicit dynamic 3D mesh representation and rendering depth of novel views from it. (2) Injecting both input source video and warped depth video as generating conditions through a dual-stream conditional mechanism. (3) Using a lightweight video diffusion adapter to fine-tune the model for generating videos that are physically and geometrically consistent as well as temporally coherent. (4) Building a multi-camera synchronized video dataset to train our model. 

### **3.1. Preliminary: Text-to-Video Base Model** 

Our study is conducted over Wan 2.2 pre-trained text/image-to-video foundation model[49]. This architecture comprises a 3D Variational Auto-Encoder (VAE) [30] for latent space mapping and a series of transformer blocks for sequence modeling. Each basic transformer block consists of 3D spatial-temporal attention, cross-attention, and feed-forward network (FFN). The text prompt embedding _c_ text is obtained by T5 encoder _εT_ 5 [38] and injected into the model through cross-attention. We adopt the Rectified Flow [36] framework to train the diffusion transformer, enabling the generation of data sample **_x_** from an initial Gaussian sample **_z_** _∈N_ ( **0** _,_ **_I_** ). Specifically, for a data point **_x_** , we construct its noised version **_x_** _t_ at timestep _t_ as 



The training objective is a simple MSE loss: 



where the velocity **_v_** _θ_ is parameterized by the network _θ_ . 

### **3.2. Warped Depth for Camera Control** 

To provide precise camera controllability, we first construct an explicit 3D representation for each frame. Given the input video _VS_ = _{It}_<sup>_N_</sup> _t_ =1<sup>,weestimateasequenceof</sup> temporally consistent relative depth maps _DS_ = _{Dt}_<sup>_N_</sup> _t_ =1 via monocular video depth estimation[23]. To project the 

3 



<!-- Start of picture text -->
petting a dog on the floor.Text prompt: a man is  T5 Encoder<br>Source Video<br>…<br>Lift to 3D Mesh<br>re7 Noise Latent jm G 5Oftre "e c<br>su ug<br>Render Depth<br>Feature Integration<br>c<br>Output Video<br>FErepr 2 'g<br>Content Token Noise Token View Token<br>Frozen Modules Trainable Modules<br>VAE<br>Encoder Patchify<br>LoRA LoRA<br>DiT Block DiT Block<br>Concatenation<br>Frame Dimension<br>Patchify<br>VAE  Encoder VAE<br>VAE  Encoder Linear Projection Decoder<br><!-- End of picture text -->

Figure 3. **Architecture overview of DepthDirector** . We render depth video and occlusion mask video under target camera viewpoint from an explicit 3D mesh, injecting it into the noise latent by projection and addition. Source video is frame-wise concatenated alongside to provide content reference. Then a LoRA-based video diffusion adapter is trained to generate video following novel camera trajectories. 

depth map to 3D space, we additionally leverage 3D foundation model[52] to estimate the camera extrinsics _PS_ = _{Pt}_<sup>_N_</sup> _t_ =1<sup>,intrinsics</sup><sup>_K_and multi-view consistent per-frame</sup> depth maps _XS_ = _{Xt}_<sup>_N_</sup> _t_ =1<sup>.Therelativedepthmaps</sup><sup>_DS_</sup> exhibit high resolution and richer details, whereas the depth maps _XS_ share the same coordinate system as the estimated camera poses. Therefore, we align _DS_ with _XS_ by solving for an optimal scale and shift bias factor _s, b_ for inverse depth value: 



Given camera extrinsics _PS_ , intrinsics _K_ and the depth map consistent with camera space, a 3D point cloud can be built. In order that the rendered depth includes less noisy artifacts, we transform the point cloud into a 3D mesh by connecting adjacent pixel points following EX-4D [22]. Then we render the depth _D_<sup>_r_</sup> = _{d_<sup>_r_</sup> _t_<sup>_}N_</sup> _t_ =1<sup>andocclusionmask</sup> _M_<sup>_r_</sup> = _{Mt_<sup>_r}N_</sup> _t_ =1<sup>ofthe3Dmeshundertargetcameratra-</sup> jectory _PT_ = _{Pt}_<sup>_N_</sup> _t_ =1<sup>.Thedepthofthe3Dmeshata</sup> novel view contains occluded parts and out of frame regions, where the occlusion mask _M_<sup>_r_</sup> will be labeled zero. Therefore, _D_<sup>_r_</sup> and _M_<sup>_r_</sup> provide sufficient informations to represent the camera movements and target view layout. 

To inject this geometric informations into the noise latent **_x_** _t_ , the depth should be encoded into the same domain as the video. Therefore, we fit the rendered depth value _D_<sup>_r_</sup> into RGB domain, and the pretrained video VAE can be leveraged to encode depth video. We first normalize the raw 

depth values into [0 _,_ 1] in log space, and then map into RGB values by a predefined colormap. 

### **3.3. View-Content Dual-Stream Condition** 

Having the colored depth video _D_<sup>_r_</sup> and masks _M_<sup>_r_</sup> from dynamic 3D mesh, as well as the source video _VS_ , we learn a conditional distribution using a conditional video diffusion model. We build upon Wan model[49] originally designed for text-guided image-to-video (I2V) generation. We leverage its 3D VAE for video compression/decompression and its DiT blocks for vision-text token processing. 

To adapt the I2V model for our task, re-generating videos with desired camera trajectories, we propose a dual-stream conditioning strategy to leverage both the 3D mesh renders and the source video. First, we encode _D_<sup>_r_</sup> and _M_<sup>_r_</sup> using the VAE encoder, concatenating them channel-wise, and project them into view tokens **_x_** _v_ in noise latent space through a linear projector _Fc_ . Then, we integrate the view tokens **_x_** _v_ with noise latent projection tokens **_x_** _t_ by addition, seamlessly incorporating geometric priors into the video synthesis pipeline. 

Since the 3D mesh renders only convey the geometric scene layout of the novel trajectory, we inject the source video to provide rich appearance details and dynamic motions. To achieve better synchronization and content consistency with the source video, we concatenate the source video tokens with the target video tokens along the frame dimension. 



4 



<!-- Start of picture text -->
Input Frame Warped Mask Warped Depth Target Frame<br><!-- End of picture text -->

Figure 4. Illustration of our dataset: MultiCam-WarpData. where **_x_** _s ∈_ R<sup>_b×f×s×d_</sup> is the VAE compressed latent of source video, **_x_** _i ∈_ R<sup>_b×_2</sup><sup>_f×s×d_</sup> is the input of diffusion transformer. In other words, the input token number is doubled compared to the vanilla video generation process. Furthermore, we do not introduce additional attention layers for feature aggregation between the source and the target videos, since self-attention is already performed across all tokens in the 3D (spatial-temporal) attention layers. 

### **3.4. Lightweight Adapter for Video Diffusion** 

Instead of finetuning the entire video diffusion model, we utilize a Low-Rank Adaptation (LoRA) [21] approach with a small rank. This allows the pre-trained video diffusion model to remain frozen while only updating the adapter parameters. 

The training process adheres to the original flow matching objective[11], ensuring rapid convergence and stable performance without requiring extensive computational resources. This design effectively combines geometry-aware conditioning with high-quality video synthesis, maintaining temporal coherence across frames. The model is trained to predict flow matching velocity, and the training objective is defined as: 



here **_z_** , **_x_** , **_x_** _t_ , _ω_ ( _t_ ) denotes the ground-truth noise, groundtruth data, noisy latents, and training weight at diffusion timestep _t_ , respectively. _VS_ is the input video. **_v_** _θ_ denotes our denoising model with parameters _θ_ . 

### **3.5. MultiCam-WarpData Video Dataset** 

To re-render the source videos based on novel camera trajectories, paired multi-view video data is required for training. Specifically, the training data should include multiple shots captured in the same scene simultaneously, alongside with the ground-truth depth map to generate view condition. Acquiring such data in real-world scenarios is extremely costly, and publicly available multi-view synchronized datasets [3, 4, 16, 27, 37, 41, 58] are also limited by the diversity of scenes, constrained camera movements and lack of geometry information, making them unsuitable for our task. Therefore we chose to leverage the 

rendering engine to generate the training data following ReCamMaster[4]. 

We build the entire data rendering pipeline in Unreal Engine 5 [15]. Specifically, we first collect multiple 3D environments as “backgrounds”. Then, we place animated characters within these environments as the “main subjects” of the videos. We then position multiple cameras facing the subjects and moving along predefined trajectories to simulate the process of simultaneous shooting. This allows us to render datasets with synchronized cameras that include dynamic objects. To scale up the data volume, we construct a set of camera movement rules for automatically batch generation of natural and diverse camera trajectories. Additionally, we randomly combined different characters and actions across different video sets. As shown in Fig.4, for each dynamic scene, we render RGB value and depth value under 8 random camera trajectories, and build training datapairs consists of warped depth video, source view video and target view video. 

Specifically, during inference, the depth scales of different input videos vary significantly. To mitigate this issue, we introduce random scaling and shifting operations before mapping the raw depth values to the RGB domain, enhancing the model’s robustness to depth-scale variations. Moreover, thanks to the dual-stream injection mechanism, the model can adaptively balance geometric and appearance information, effectively alleviating the depth distribution gap between training and inference. 

In total, we obtain 8K visually-realistic videos shot from 1K different dynamic scenes in 40 high-quality 3D environments with 8K different camera trajectories. Each video has a resolution of 576 _×_ 1024 and 81 frames. 

## **4. Experiments** 

### **4.1. Implementation Details** 

Our approach builds upon the Wan2.2-TI2V-5B model[12, 49]. The video diffusion backbone remains frozen during training, while our lightweight adapter employs a LoRA rank of 32. Input videos are resized to a resolution of 576 _×_ 1024 with 81 frames per sequence. The adapter is optimized using the AdamW optimizer with a learning rate of 1 _×_ 10<sup>_−_4</sup> . Our method is implemented on 8 NVIDIA A100 GPUs. Training is completed in 4 days, and inference generates each video in approximately 4 minutes using 50 denoising steps. Please refer to the supplementary material for additional implementation details and more analysis. 

### **4.2. Evaluation** 

**Metrics and Dataset** For evaluation, we randomly sampled 200 in-the-wild web videos from Koala dataset[51], which include diverse dynamic scenes and also challenging human-centric scenes. To evaluate both camera controlla- 

5 



<!-- Start of picture text -->
Tern TT SI TT SI ccf 268 oo<br>a dnl Yi V F<br>MS AAA eS rn ey ef a =<br>Mg ee ) oe oa Ss<br>Ua LS ween 5 i 358 8 c<br>( 0 ae PN rssrm S/he 14)<br>Input<br>Target View<br>Ours<br>EX-4D<br>ReCamMaster<br>CamCloneMaster<br><!-- End of picture text -->

Figure 5. **Qualitative comparison with state-of-the-art methods.** DepthDirector achieves both precise camera controllability and content preservation. 

Table 1. Quantitative comparison with state-of-the-art methods on camera accuracy, identity preservation and view synchronization. 

|Method<br>|<br>|Camera Accura<br>|cy<br>|Identity P<br><br>|reservation<br><br>|View Sync<br><br><br>|hronization<br><br>~~|~~|
|---|---|---|---|---|---|---|---|
||RotErr_↓_<br>|TransErr_↓_<br>|CamMC_↓_<br>|RS_↑_<br><br>||IFS_↑_<br>|Mat.Pix. _↑_<br><br>||CLIP-V_↑_|
|TrajectoryCrafter|0.828|0.310|1.171|0.5672|0.9169|275.3|0.9119|
|GEN3C|1.166|0.256|1.649|0.6252|0.9515|721.7|0.9136|
|EX4D|**0.637**|**0.167**|**0.897**|0.6269|0.9279|947.5|0.9150|
|ReCamMaster|5.840|1.055|8.253|0.6403|0.9519|479.4|**0.9201**|
|CamCloneMaster|6.418|1.027|9.064|0.5928|0.9426|507.9|0.9057|
|Ours|**2.542**|**0.388**|**3.596**|**0.6887**|**0.9661**|**988.7**|0.9197|



bility and novel-view synthesis capabilities, we assess our model using two trajectories that rotate _±_ 30<sup>_◦_</sup> around the main subject along the horizontal axis for each video. 

To evaluate camera trajectory accuracy, we employ the state-of-the-art camera parameters estimation model MegaSaM[33] to extract camera rotation _Ri_ and translation _Ti_ for the _i_ -th frame in the video. We then compute the Rotation Distance (RotErr), Translation Error (TransErr), and Camera Motion Consistency (CamMC), following CamI2V[63]. For content preservation evaluation, we assess human identity preservation metrics for all evaluation videos with human faces. We employ ArcFace[10] embedding similarity to assess two key aspects. First, Reference Similarity (RS) calculates the similarity between the first frame of source video and generated frames to evaluate identity preservation. Second, InterFrame Similarity 

(IFS) quantifies the similarity between consecutive video frames to evaluate the stability of identity features during camera movements. To evaluate our method in terms of view synchronization[4, 37], we utilize the state-of-the-art image matching method GIM[43] to compute the number of matching pixels with confidence exceeding a predefined threshold, denoted as Mat. Pix.. Additionally, we calculate the average CLIP similarity between source and target frames at the same timestamps, denoted as CLIP-V[31]. We also evaluate our method on VBench [25] metrics for comprehensive perceptual quality measurement. 

**Comparison Baselines** For comparative evaluation, we involve the state-of-the-art methods capable of cameracontrollable video synthesis, including warping-based methods[22, 39, 61], and implicit camera conditioned methods[4, 37]. Other earlier methods[5, 17, 26, 56, 62] are 

6 



<!-- Start of picture text -->
Input  Target View Warp Result Ours TrajectoryCrafter GEN3C EX-4D<br>View<br><!-- End of picture text -->

Figure 6. **Qualitative comparison with warping-based methods** . Our method preserves facial identity under camera view changes, while other methods produce distorted artifacts. 

Table 2. Quantitative comparison with state-of-the-art methods on VBench [25] metrics. 

|Method|Subject<br>Consistency_↑_|Background<br>Consistency_↑_|Motion<br>Smoothness_↑_|Aesthetic<br>Quality_↑_|Imaging<br>Quality_↑_|
|---|---|---|---|---|---|
|GEN3C|95.04|93.46|99.29|53.65|73.76|
|TrajectoryCrafter|94.74|93.46|98.52|52.55|73.64|
|EX-4D|94.51|93.11|98.24|53.06|**74.08**|
|ReCamMaster|95.17|91.85|99.35|54.08|69.93|
|CamCloneMaster|94.11|91.48|99.27|53.21|71.01|
|Ours|**95.29**|**94.66**|**99.41**|**55.67**|73.90|



omitted for their relatively inferior performance. To ensure fair comparisons, all methods are evaluated using identical camera trajectories. And all warping-based methods receive the same depth estimation results as inputs, eliminating any advantage from differing geometric priors. For CamCloneMaster, we render reference videos under target trajectories with Unreal Engine 5. 

**Quantitative Comparison** Quantitative results are presented in Table.1, Table.2. For camera accuracy, warpingbased methods achieve nearly zero error, because they directly perform inpainting on the warped video of target views. Compared with warping-based methods[22, 39, 61], DepthDirector reaches a comparable accuracy, much lower than that of comparable implicit camera conditioned methods[4, 37]. This demonstrates that DepthDirector possess precise camera controllability. While in terms of identity preservation and view synchronization, DepthDirector demonstrates superior performance against all baseline methods, highlighting our method’s ability to leverage the 3D understanding of VDMs to generate 3D consistent re- 

sults. For comprehensive perceptual quality, DepthDirector achieves the best performance on nearly all VBench metrics. 

**Qualitative Comparison** As shown in Fig. 5, warpingbased methods can strictly follow the target trajectories, due to the inaccurate warped video. And implicit methods fail to accurately align with the desired camera views. Compared with them, DepthDirector slightly sacrifices the camera accuracy but can generate 3D consistent content tightly aligned with the target views. As shown in Fig. 7, DepthDirector outperforms the implicit methods on background consistency by a large margin. This is because the warped depth video provides richer geometric cues, helping the model preserve the scene geometry and appearance details. However, directly inferring camera movements for complex background remains challenging for implicit methods, because the correspondence between camera parameters and scene layout is hard to learn. Fig. 6 demonstrates that warping-based methods greatly suffer from inaccurate warped video, especially on human faces. How- 

7 

Table 3. Quantitative comparison for ablation study. 

|Camera<br>Accuracy<br>|Iden<br>Preser<br><br>|tity<br>vation<br><br><br>|View<br>Synchronization<br>VBench<br><br>~~|~~<br>~~|~~<br>~~|~~|
|---|---|---|---|
|Method<br>Rot<br>Err <sup>_↓_</sup><br>Trans<br>Err <sup>_↓_</sup><br>|RS_↑_<br><br>|IFS_↑_<br><br><br>|Mat.Pix. _↑_<br>CLIP-V_↑_<br>Cons.<br>Subj.<sup>_↑_</sup><br>Cons.<br>Bg. <sup>_↑_</sup><br><br>~~|~~<br>~~|~~<br>~~|~~<br>|
|w/ Wan2.1-1.3B<br>**2.366**<br>**0.334**<br>wo/ Content Condition<br>2.614<br>0.370<br>Ours<br>2.542<br>0.388|0.6370<br>0.5804<br>**0.6887**|0.9541<br>0.9628<br>**0.9661**<br>|636.8<br>0.9117<br>94.80<br>92.38<br>772.0<br>0.9115<br>95.17<br>94.55<br>**988.7**<br>**0.9197**<br>**95.29**<br>**94.66**<br>~~|~~<br>~~|——~~|
|View||Input<br>View||
|View||Target<br>View||
|Master<br>i)<br>‘~.*||Full<br>Model<br>wo\<br>Content<br>Condition<br><br>|VE pepe<br>vebe<sup>yes</sup>|





<!-- Start of picture text -->
Input View<br>Target  View<br>Ours<br>ReCam- Master<br>Master<br>CamClone-<br><!-- End of picture text -->

Figure 8. **Ablation Study on Model Design.** Model without injecting source video cannot recover the dynamic expression change of source video. 

Figure 7. **Qualitative comparison with implicit-controlled methods** . Our method generates consistent background, while baseline methods fail to preserve the environment details from input views. 

lower score on identity preservation, consistency metrics in VBench and View Synchronization are attributed to the weaker capacity of the base model and lower generation resolution. 

ever, our method can go **beyond inpainting** , leveraging its 3D understanding ability to generate 3D consistent human subject. 

## **5. Conclusion** 

In this paper, we propose DepthDirector, a framework for reproducing dynamic scenes from input videos under novel camera trajectories. We achieve both precise camera controlability and consistent content preservation. Our key idea is to leverage warped depth video as the camera-view condition. We design a View-Content Dual-Stream Condition mechanism that injects warped depth video to guide viewpoint changes and frame-wise concatenates source video for content reference. Our framework enables video diffusion models to go beyond inpainting and unleash their 3D understanding capabilities, faithfully generating videos of unseen views that are accurately aligned with the target camera trajectory. 

### **4.3. Ablation Study** 

We carefully ablate the key components of our framework to validate their effectiveness. 

**Ablation on Model Design** In our key designs of the ViewContent Dual-Stream Condition mechanism, we propose to inject warped depth video as the view condition and source video as the content condition. To validate the effectiveness, we compare our full model with models without injecting source video. As shown in Fig.8, models without injecting source video fail to preserve detailed motions, such as facial expressions. Table 3 shows that models without injecting source video achieve lower view synchronization score. **Ablation on Base Model** We switch our base model from Wan2.2-TI2V-5B[49] to Wan2.1-T2V-1.3B[48], and train at a resolution of 843 _×_ 480. Table 3 shows that changing to a lighter base model doesn’t affect the camera accuracy (Model (b)), demonstrating that our method is effective and applicable to other video generation models. The slightly 

## **References** 

- [1] Sherwin Bahmani, Ivan Skorokhodov, Guocheng Qian, Aliaksandr Siarohin, Willi Menapace, Andrea Tagliasacchi, David B Lindell, and Sergey Tulyakov. Ac3d: Analyzing 

8 

   - and improving 3d camera control in video diffusion transformers. _arXiv preprint arXiv:2411.18673_ , 2024. 2, 3 

- [2] Sherwin Bahmani, Ivan Skorokhodov, Aliaksandr Siarohin, Willi Menapace, Guocheng Qian, Michael Vasilkovsky, Hsin-Ying Lee, Chaoyang Wang, Jiaxu Zou, Andrea Tagliasacchi, et al. Vd3d: Taming large video diffusion transformers for 3d camera control. _arXiv preprint arXiv:2407.12781_ , 2024. 3 

- [3] Jianhong Bai, Menghan Xia, Xintao Wang, Ziyang Yuan, Xiao Fu, Zuozhu Liu, Haoji Hu, Pengfei Wan, and Di Zhang. Syncammaster: Synchronizing multi-camera video generation from diverse viewpoints. _arXiv preprint arXiv:2412.07760_ , 2024. 2, 3, 5 

- [4] Jianhong Bai, Menghan Xia, Xiao Fu, Xintao Wang, Lianrui Mu, Jinwen Cao, Zuozhu Liu, Haoji Hu, Xiang Bai, Pengfei Wan, and Di Zhang. Recammaster: Camera-controlled generative rendering from a single video, 2025. 2, 3, 5, 6, 7, 1 

- [5] Weikang Bian, Zhaoyang Huang, Xiaoyu Shi, Yijin Li, FuYun Wang, and Hongsheng Li. Gs-dit: Advancing video generation with pseudo 4d gaussian fields through efficient dense 3d point tracking. _arXiv preprint arXiv:2501.02690_ , 2025. 3, 6 

- [6] Andreas Blattmann, Tim Dockhorn, Sumith Kulal, Daniel Mendelevitch, Maciej Kilian, Dominik Lorenz, Yam Levi, Zion English, Vikram Voleti, Adam Letts, et al. Stable video diffusion: Scaling latent video diffusion models to large datasets. _arXiv preprint arXiv:2311.15127_ , 2023. 3 

- [7] Haoxin Chen, Menghan Xia, Yingqing He, Yong Zhang, Xiaodong Cun, Shaoshu Yang, Jinbo Xing, Yaofang Liu, Qifeng Chen, Xintao Wang, Chao Weng, and Ying Shan. Videocrafter1: Open diffusion models for high-quality video generation, 2023. 3 

- [8] Haoxin Chen, Yong Zhang, Xiaodong Cun, Menghan Xia, Xintao Wang, Chao Weng, and Ying Shan. Videocrafter2: Overcoming data limitations for high-quality video diffusion models. In _Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition_ , pages 7310– 7320, 2024. 3 

- [9] Sili Chen, Hengkai Guo, Shengnan Zhu, Feihu Zhang, Zilong Huang, Jiashi Feng, and Bingyi Kang. Video depth anything: Consistent depth estimation for super-long videos. _arXiv:2501.12375_ , 2025. 2, 3 

- [10] Jiankang Deng, Jia Guo, Jing Yang, Niannan Xue, Irene Kotsia, and Stefanos Zafeiriou. Arcface: Additive angular margin loss for deep face recognition. _IEEE Trans. Pattern Anal. Mach. Intell._ , 44(10):5962–5979, 2022. 6 

- [11] Patrick Esser, Sumith Kulal, Andreas Blattmann, Rahim Entezari, Jonas M¨uller, Harry Saini, Yam Levi, Dominik Lorenz, Axel Sauer, Frederic Boesel, Dustin Podell, Tim Dockhorn, Zion English, Kyle Lacey, Alex Goodwin, Yannik Marek, and Robin Rombach. Scaling rectified flow transformers for high-resolution image synthesis, 2024. 5 

- [12] WanTeam et al. Wan: Open and advanced large-scale video generative models. _arXiv preprint arXiv:2503.20314_ , 2025. 2, 3, 5 

- [13] Weijie Kong et. al. Hunyuanvideo: A systematic framework for large video generative models, 2024. 3 

- [14] Xianze Fang, Jingnan Gao, Zhe Wang, Zhuo Chen, Xingyu Ren, Jiangjing Lyu, Qiaomu Ren, Zhonglei Yang, Xiaokang Yang, Yichao Yan, and Chengfei Lyu. Dens3r: A foundation model for 3d geometry prediction. _arXiv preprint arXiv:2507.16290_ , 2025. 3 

- [15] Epic Games. Unreal engine 5. https : / / www . unrealengine.com/en-US/unreal-engine-5, 2022. 5 

- [16] Kristen Grauman, Andrew Westbury, Lorenzo Torresani, Kris Kitani, Jitendra Malik, Triantafyllos Afouras, Kumar Ashutosh, Vijay Baiyya, Siddhant Bansal, Bikram Boote, et al. Ego-exo4d: Understanding skilled human activity from first-and third-person perspectives. In _Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition_ , pages 19383–19400, 2024. 5 

- [17] Zekai Gu, Rui Yan, Jiahao Lu, Peng Li, Zhiyang Dou, Chenyang Si, Zhen Dong, Qifeng Liu, Cheng Lin, Ziwei Liu, et al. Diffusion as shader: 3d-aware video diffusion for versatile video generation control. _arXiv preprint arXiv:2501.03847_ , 2025. 2, 3, 6 

- [18] Yuwei Guo, Ceyuan Yang, Anyi Rao, Zhengyang Liang, Yaohui Wang, Yu Qiao, Maneesh Agrawala, Dahua Lin, and Bo Dai. Animatediff: Animate your personalized textto-image diffusion models without specific tuning. _arXiv preprint arXiv:2307.04725_ , 2023. 2, 3 

- [19] Hao He, Yinghao Xu, Yuwei Guo, Gordon Wetzstein, Bo Dai, Hongsheng Li, and Ceyuan Yang. Cameractrl: Enabling camera control for text-to-video generation. _arXiv preprint arXiv:2404.02101_ , 2024. 2, 3, 1 

- [20] Chen Hou, Guoqiang Wei, Yan Zeng, and Zhibo Chen. Training-free camera control for video generation. _arXiv preprint arXiv:2406.10126_ , 2024. 3 

- [21] Edward J Hu, Yelong Shen, Phillip Wallis, Zeyuan AllenZhu, Yuanzhi Li, Shean Wang, Lu Wang, and Weizhu Chen. Lora: Low-rank adaptation of large language models. _arXiv preprint arXiv:2106.09685_ , 2021. 5 

- [22] Tao Hu, Haoyang Peng, Xiao Liu, and Yuewen Ma. Ex-4d: Extreme viewpoint 4d video synthesis via depth watertight mesh, 2025. 2, 3, 4, 6, 7, 1 

- [23] Wenbo Hu, Xiangjun Gao, Xiaoyu Li, Sijie Zhao, Xiaodong Cun, Yong Zhang, Long Quan, and Ying Shan. Depthcrafter: Generating consistent long depth sequences for open-world videos. In _CVPR_ , 2025. 2, 3, 1 

- [24] Jiahui Huang, Qunjie Zhou, Hesam Rabeti, Aleksandr Korovko, Huan Ling, Xuanchi Ren, Tianchang Shen, Jun Gao, Dmitry Slepichev, Chen-Hsuan Lin, Jiawei Ren, Kevin Xie, Joydeep Biswas, Laura Leal-Taixe, and Sanja Fidler. Vipe: Video pose engine for 3d geometric perception. In _NVIDIA Research Whitepapers arXiv:2508.10934_ , 2025. 2 

- [25] Ziqi Huang, Yinan He, Jiashuo Yu, Fan Zhang, Chenyang Si, Yuming Jiang, Yuanhan Zhang, Tianxing Wu, Qingyang Jin, Nattapol Chanpaisit, et al. Vbench: Comprehensive benchmark suite for video generative models. In _Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition_ , pages 21807–21818, 2024. 6, 7 

- [26] Wonjoon Jin, Qi Dai, Chong Luo, Seung-Hwan Baek, and Sunghyun Cho. Flovd: Optical flow meets video diffu- 

9 

sion model for enhanced camera-controlled video synthesis. _arXiv preprint arXiv:2502.08244_ , 2025. 3, 6 

- [27] Hanbyul Joo, Hao Liu, Lei Tan, Lin Gui, Bart Nabbe, Iain Matthews, Takeo Kanade, Shohei Nobuhara, and Yaser Sheikh. Panoptic studio: A massively multiview system for social motion capture. In _Proceedings of the IEEE international conference on computer vision_ , pages 3334–3342, 2015. 5 

- [28] Nikita Karaev, Ignacio Rocco, Benjamin Graham, Natalia Neverova, Andrea Vedaldi, and Christian Rupprecht. Cotracker: It is better to track together. In _European Conference on Computer Vision_ , pages 18–35. Springer, 2024. 3 

- [29] Nikhil Keetha, Norman M¨uller, Johannes Sch¨onberger, Lorenzo Porzi, Yuchen Zhang, Tobias Fischer, Arno Knapitsch, Duncan Zauss, Ethan Weber, Nelson Antunes, Jonathon Luiten, Manuel Lopez-Antequera, Samuel Rota Bul`o, Christian Richardt, Deva Ramanan, Sebastian Scherer, and Peter Kontschieder. MapAnything: Universal feedforward metric 3D reconstruction, 2025. arXiv preprint arXiv:2509.13414. 3 

- [30] Diederik P Kingma and Max Welling. Auto-encoding variational bayes, 2022. 3 

- [31] Zhengfei Kuang, Shengqu Cai, Hao He, Yinghao Xu, Hongsheng Li, Leonidas Guibas, and Gordon Wetzstein. Collaborative video diffusion: Consistent multi-video generation with camera control. _arXiv preprint arXiv:2405.17414_ , 2024. 3, 6 

- [32] Samuli Laine, Janne Hellsten, Tero Karras, Yeongho Seol, Jaakko Lehtinen, and Timo Aila. Modular primitives for high-performance differentiable rendering. _ACM Transactions on Graphics_ , 39(6), 2020. 1 

- [33] Zhengqi Li, Richard Tucker, Forrester Cole, Qianqian Wang, Linyi Jin, Vickie Ye, Angjoo Kanazawa, Aleksander Holynski, and Noah Snavely. Megasam: Accurate, fast, and robust structure and motion from casual dynamic videos. _arXiv preprint arXiv:2412.04463_ , 2024. 6 

- [34] Chenguo Lin, Yuchen Lin, Panwang Pan, Yifan Yu, Honglei Yan, Katerina Fragkiadaki, and Yadong Mu. Movies: Motion-aware 4d dynamic view synthesis in one second. _arXiv preprint arXiv:2507.10065_ , 2025. 3 

- [35] Haotong Lin, Sili Chen, Jun Hao Liew, Donny Y. Chen, Zhenyu Li, Guang Shi, Jiashi Feng, and Bingyi Kang. Depth anything 3: Recovering the visual space from any views. _arXiv preprint arXiv:2511.10647_ , 2025. 2 

- [36] Yaron Lipman, Ricky T. Q. Chen, Heli Ben-Hamu, Maximilian Nickel, and Matthew Le. Flow matching for generative modeling. In _International Conference on Learning Representations (ICLR)_ , 2023. 3 

- [37] Yawen Luo, Jianhong Bai, Xiaoyu Shi, Menghan Xia, Xintao Wang, Pengfei Wan, Di Zhang, Kun Gai, and Tianfan Xue. Camclonemaster: Enabling reference-based camera control for video generation, 2025. 2, 3, 5, 6, 7, 1 

- [38] Colin Raffel, Noam Shazeer, Adam Roberts, Katherine Lee, Sharan Narang, Michael Matena, Yanqi Zhou, Wei Li, and Peter J. Liu. Exploring the limits of transfer learning with a unified text-to-text transformer, 2023. 3 

- [39] Xuanchi Ren, Tianchang Shen, Jiahui Huang, Huan Ling, Yifan Lu, Merlin Nimier-David, Thomas M¨uller, Alexander Keller, Sanja Fidler, and Jun Gao. Gen3c: 3d-informed world-consistent video generation with precise camera control. In _Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition_ , 2025. 2, 3, 6, 7, 1 

- [40] RunwayML. Gen-1: The next step forward for generative ai, 2023. Accessed May 7, 2025. 3 

- [41] Amir Shahroudy, Jun Liu, Tian-Tsong Ng, and Gang Wang. Ntu rgb+ d: A large scale dataset for 3d human activity analysis. In _Proceedings of the IEEE conference on computer vision and pattern recognition_ , pages 1010–1019, 2016. 5 

- [42] Jiahao Shao, Yuanbo Yang, Hongyu Zhou, Youmin Zhang, Yujun Shen, Vitor Guizilini, Yue Wang, Matteo Poggi, and Yiyi Liao. Learning temporally consistent video depth from video diffusion priors, 2024. 3 

- [43] Xuelun Shen, Zhipeng Cai, Wei Yin, Matthias M¨uller, Zijun Li, Kaixuan Wang, Xiaozhi Chen, and Cheng Wang. Gim: Learning generalizable image matcher from internet videos. In _The Twelfth International Conference on Learning Representations_ , 2024. 6, 1 

- [44] Uriel Singer, Adam Polyak, Thomas Hayes, Xi Yin, Jie An, Songyang Zhang, Qiyuan Hu, Harry Yang, Oron Ashual, Oran Gafni, Devi Parikh, Sonal Gupta, and Yaniv Taigman. Make-a-video: Text-to-video generation without text-video data. In _The Eleventh International Conference on Learning Representations_ , 2023. 3 

- [45] Vincent Sitzmann, Semon Rezchikov, William T. Freeman, Joshua B. Tenenbaum, and Fredo Durand. Light field networks: Neural scene representations with single-evaluation rendering. In _Proc. NeurIPS_ , 2021. 3 

- [46] Chenxi Song, Yanming Yang, Tong Zhao, Ruibo Li, and Chi Zhang. Worldforge: Unlocking emergent 3d/4d generation in video diffusion model via training-free guidance, 2025. 2, 3 

- [47] Basile Van Hoorick, Rundi Wu, Ege Ozguroglu, Kyle Sargent, Ruoshi Liu, Pavel Tokmakov, Achal Dave, Changxi Zheng, and Carl Vondrick. Generative camera dolly: Extreme monocular dynamic novel view synthesis. In _European Conference on Computer Vision_ , pages 313–331. Springer, 2024. 2, 3 

- [48] Wan-AI. Wan2.1-t2v-1.3b: Text-to-video generation model. https://huggingface.co/Wan- AI/Wan2.1T2V-1.3B, 2025. 8 

- [49] Wan-AI. Wan2.2-ti2v-5b: Text-to-video generation model. https://huggingface.co/Wan- AI/Wan2.2TI2V-5B, 2025. 3, 4, 5, 8 

- [50] Jianyuan Wang, Minghao Chen, Nikita Karaev, Andrea Vedaldi, Christian Rupprecht, and David Novotny. Vggt: Visual geometry grounded transformer. In _Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition_ , 2025. 2, 3 

- [51] Qiuheng Wang, Yukai Shi, Jiarong Ou, Rui Chen, Ke Lin, Jiahao Wang, Boyuan Jiang, Haotian Yang, Mingwu Zheng, Xin Tao, Fei Yang, Pengfei Wan, and Di Zhang. Koala-36m: A large-scale video dataset improving consistency between fine-grained conditions and video content, 2024. 5 

10 

- [52] Yifan Wang, Jianjun Zhou, Haoyi Zhu, Wenzheng Chang, Yang Zhou, Zizun Li, Junyi Chen, Jiangmiao Pang, Chunhua Shen, and Tong He. _π_<sup>3</sup> : Scalable permutation-equivariant visual geometry learning, 2025. 2, 3, 4, 1 

- [53] Zhouxia Wang, Ziyang Yuan, Xintao Wang, Yaowei Li, Tianshui Chen, Menghan Xia, Ping Luo, and Ying Shan. Motionctrl: A unified and flexible motion controller for video generation. In _ACM SIGGRAPH 2024 Conference Papers_ , pages 1–11, 2024. 3, 1 

- [54] Zun Wang, Jaemin Cho, Jialu Li, Han Lin, Jaehong Yoon, Yue Zhang, and Mohit Bansal. EPiC: Efficient Video Camera Control Learning with Precise Anchor-Video. _arXiv preprint arXiv:2505.21876_ , 2025. 2, 3 

- [55] Yuxi Xiao, Qianqian Wang, Shangzhan Zhang, Nan Xue, Sida Peng, Yujun Shen, and Xiaowei Zhou. Spatialtracker: Tracking any 2d pixels in 3d space. In _Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition_ , pages 20406–20417, 2024. 3 

- [56] Zeqi Xiao, Wenqi Ouyang, Yifan Zhou, Shuai Yang, Lei Yang, Jianlou Si, and Xingang Pan. Trajectory attention for fine-grained video motion control. In _The Thirteenth International Conference on Learning Representations_ , 2025. 3, 6 

- [57] Tian-Xing Xu, Xiangjun Gao, Wenbo Hu, Xiaoyu Li, SongHai Zhang, and Ying Shan. Geometrycrafter: Consistent geometry estimation for open-world videos with diffusion priors. _arXiv preprint arXiv:2504.01016_ , 2025. 3, 2 

- [58] Zhen Xu, Yinghao Xu, Zhiyuan Yu, Sida Peng, Jiaming Sun, Hujun Bao, and Xiaowei Zhou. Representing long volumetric video with temporal gaussian hierarchy. _ACM Transactions on Graphics_ , 43(6), 2024. 5 

- [59] Shiyuan Yang, Liang Hou, Haibin Huang, Chongyang Ma, Pengfei Wan, Di Zhang, Xiaodong Chen, and Jing Liao. Direct-a-video: Customized video generation with userdirected camera movement and object motion. In _ACM SIGGRAPH 2024 Conference Papers_ , pages 1–12, 2024. 3 

- [60] Zhuoyi Yang, Jiayan Teng, Wendi Zheng, Ming Ding, Shiyu Huang, Jiazheng Xu, Yuanming Yang, Wenyi Hong, Xiaohan Zhang, Guanyu Feng, et al. Cogvideox: Text-to-video diffusion models with an expert transformer. _arXiv preprint arXiv:2408.06072_ , 2024. 2, 3 

- [61] Mark YU, Wenbo Hu, Jinbo Xing, and Ying Shan. Trajectorycrafter: Redirecting camera trajectory for monocular videos via diffusion models, 2025. 2, 3, 6, 7, 1 

- [62] David Junhao Zhang, Roni Paiss, Shiran Zada, Nikhil Karnad, David E Jacobs, Yael Pritch, Inbar Mosseri, Mike Zheng Shou, Neal Wadhwa, and Nataniel Ruiz. Recapture: Generative video camera controls for user-provided videos using masked video fine-tuning. _arXiv preprint arXiv:2411.05003_ , 2024. 3, 6 

- [63] Guangcong Zheng, Teng Li, Rui Jiang, Yehao Lu, Tao Wu, and Xi Li. Cami2v: Camera-controlled image-to-video diffusion model. _arXiv preprint arXiv:2410.15957_ , 2024. 2, 3, 6 

- [64] Sixiao Zheng, Zimian Peng, Yanpeng Zhou, Yi Zhu, Hang Xu, Xiangru Huang, and Yanwei Fu. Vidcraft3: Camera, object, and lighting control for image-to-video generation. _arXiv preprint arXiv:2502.07531_ , 2025. 3 

11 

# **Beyond Inpainting: Unleash 3D Understanding for Precise Camera-Controlled Video Generation** 

# Supplementary Material 

## **A. Details of Data Construction** 

**Scene Components** We collected 40 different 3D environment assets from https://www.fab.com. To ensure data diversity, the selected scenes cover a variety of indoor and outdoor settings, such as city streets, forests, office rooms, and countryside. For the main characters, we collected 200 different human 3D models as characters and 1000 different animations to drive the collected characters. **Camera Trajectories** We create camera trajectories as diverse as possible to cover various situations. We use the character’s chest position(around 150 _cm_ height above the ground) as the camera look-at point, and randomly sample the camera’s starting point in front of the character, ensuring the distance to the character is within the range of [2 _m,_ 5 _m_ ] and the pitch/yaw angles are within 10 degrees. From a given camera’s starting point, we selected multiple random camera trajectories. 1 to 3 points are sampled in space, and the camera moves from the initial position through these points as the movement trajectory. The total movement distance is randomly selected within the range of [0 _._ 5 _,_ 1 _._ 5] times of the initial distance. The rotation angles are randomly selected within 40 degrees in pitch angle and 20 degrees in yaw angle. We also shot with a static camera as the input source video. 

**Warping Construction** For each dynamic scene, we sample 8 random camera trajectories and render the RGB value and raw depth value for each frame. We select the static camera or a random camera trajectory video as the source video, and construct the 3D mesh based on its ground-truth depth. We adopt Nvdiffrast[32] to render the occlusion mask _M_<sup>_r_</sup> and depth _D_<sup>_r_</sup> . For the rendered depth, we first clip it within the near-far range [0 _._ 5 _,_ 100], and then normalize it into [0 _,_ 1] in log space: 



We use matplotlib.cm.get_cmap(’spectral_r’) as the color-mapping to encode the raw depth value into the RGB domain. 

## **B. Evaluation Details** 

**Baselines** We implement all baselines following their opensource code. For a fair comparison, we use the same depth estimation method[23] for all warping-based methods [22, 39, 61] and align the depth map with Pi3[52] as proposed in our main paper. We compare the impact of different depth 



<!-- Start of picture text -->
ENSle1 oi<br><!-- End of picture text -->

Figure B1. **Reference Video for CamCloneMaster** 

estimation methods in Fig.B3. For ReCamMaster[4], we transform the target camera parameters into centimeters to match its scale requirement. For CamCloneMaster[37], we use synthetic videos following the target camera trajectories as reference videos, as shown in Fig. B1. 

**Metrics** For RotError [19], we evaluate per-frame camerato-world rotation accuracy by the relative angles between ground truth rotations _Ri_ and estimated rotations _R_<sup>˜</sup> _i_ of generated frames. We report the accumulated rotation error across all frames in radians. 



For TransError [19], we evaluate per-frame camera trajectory accuracy by the camera location in the world coordinate system, i.e. the translation component of camera-toworld matrices. We report the sum of _L_ 2 distance between ground truth translations _Ti_ and generated translations _T_<sup>˜</sup> _i_ for all frames. 



For CamMC [53]. We also evaluate camera pose accuracy by directly calculating _L_ 2 similarity of per-frame rotations and translations as a whole. We sum up the results of all frames. 



For Mat.Pix.(Matching Pixels)[4, 37], we first normalize the generated videos to the resolution of 1024 _×_ 576 and then adopt GIM [43] to compute the number of matching pixels with confidence exceeding a predefined threshold, 0 _._ 95. 

1 

Table A1. Ablation study on Model Design. 

|P|Identity<br>reservation|VB|ench|
|---|---|---|---|
|Method<br>RS|_↑_<br>IFS_↑_<br>|Cons.<br>Subj.<sup>_↑_</sup>|Cons.<br>Bg. <sup>_↑_</sup>|
|Model (a)<br>0.59<br>|54<br>0.9606<br>|94.80<br>|94.57<br>|
|Model (b)<br>0.64<br>|63<br>0.9621<br>|95.20<br>|94.43<br>|
|Full Model<br>**0.68**<br>|**87**<br>**0.9661**<br>|**95.29**<br>|**94.66**<br>|
|Input Video<br>||||
|Warp Video<br>~~P~~|||S|
|EX-4D<br>||||
|Model (a)||||
|Model (b)||||
|Full Model||||



Figure B2. **Ablation Study on Model Design.** Model (a) adopts the same condition mechanism as EX-4D [22] (without source video concatenation, using the warped RGB video as condition), trained on our MultiCam-WarpData dataset. Model (b) adopts source video concatenation and uses warped RGB video as condition. These models try to repaint and correct the inaccurate warped video. However, they still generate artifacts due to the Inpainting Trap, for example the distortion of the hair (left), the blurry face expression(center) and the unnatural head position(right). 

## **C. More Analysis** 

### **C.1 Different Choises of Video Depth Estimation** 

We carefully evaluate different video depth estimation methods and investigate its impact on warping-based method[22, 39, 61] and our method. We chose the current state-of-the-art monocular video depth estimation methods: Video-Depth-Anything(VDA)[9], DepthCrafter[23] and GeometryCrafter[57], alongside with 3D foundation models: VGGT[50], Pi3[52], ViPE[24] and DA3[35]. For methods without camera intrinsics estimation, VDA and DepthCrafter, we project the depth map to point clouds 

with two strategies: (1) following TrajectoryCrafter [61] and EX-4D [22] to treat the depth map as inverse depth and use a fixed focal length: focal = 500 to project into 3D space, and (2) align the depth map with Pi3 [52] as proposed in our main paper. As shown in Fig.B3, our method DepthDirector demonstrates superior robustness to different input. Due to the inherent inaccuracy of monocular depth estimation, the warp results from these SOTA video estimation methods contain distortion and artifacts without exception. Therefore, all warping-based methods generate distorted human faces. 

### **C.2 Ablation Study on Model Design** 

We extend more experiments on our model design to demonstrate how each component contributes to the goal of going beyond inpainting. We train Model (a), which replaces the warped depth video with the warped RGB video and removes the source video concatenation in our ViewContent Dual-Stream Condition mechanism, thus maintaining the same as EX-4D[22]. The differences between Model (a) and EX-4D are: (1) different base models, and (2) EX-4D only uses monocular video datasets to train the inpainting ability, whereas Model (a) uses a multi-camera dataset(our MultiCam-WarpData) for training. And Model (b) adds the source video concatenation based on Model (a) and still uses warped RGB video as condition. As shown in Fig.B2 and Table.A1, due to the effectiveness of our View-Content Dual-Stream Condition mechanism and the high-quality multi-camera information of our MultiCamWarpData dataset, the Model (a) and Model (b) both try to learn repainting and correction based on the inaccurate warped video. Training with multi-camera dataset helps Model (a) to learn repainting and correction instead of solely inpainting. The content branch of our Dual-Stream Condition (source video concatenation) further helps Model (b) to maintain content preservation, achieving better repainting results. However, the correction is still hard to learn due to the Inpainting Trap, and these models still generate unnatural artifacts and cannot fully recover the details. Compared with them, our Full Model can generate consistent content with high fidelity, demonstrating the necessity of depth condition. Since our Full Model leverages depth information as viewpoint guidance, it is capable of going beyond inpainting and fully unleashing the 3D understanding ability of VDMs. 

## **D. More Results** 

More synthesized results of DepthDirector are presented in Fig.B4. 

2 



<!-- Start of picture text -->
UT iE<br>> 5itl<br>SRR<br>eis as<br>tcl<br>Input Frame Target Frame Target Frame DepthDirector TrajectoryCrafter EX-4D GEN3C<br>Normal Map Depth Video Warp Video<br>Aligned<br>DepthCrafter<br>VDA Aligned<br>DepthCrafter Fixed Focal<br>VDA<br>Fixed Focal<br>Pi3<br>VGGT<br>Crafter<br>Geometry-<br>ViPE<br>DA3<br><!-- End of picture text -->

Figure B3. **Different Choises of Video Depth Estimation.** We visualize the input frame normal map derived from estimated depth map, warped depth map, warped video based on estimated depth map and the generated results of our methods and warping-based methods. Due to the inherent inaccuracy of monocular depth estimation, the warp results from these SOTA video estimation methods contain distortion and artifacts without exception. 

## **E. Limitations** 

Our framework enables video diffusion models to go beyond inpainting and unleash their 3D understanding capabilities, faithfully generating videos of unseen views that are accurately aligned with the target camera trajectory. There are nevertheless some limitations. Concatenating source and target video tokens improves generation quality, but increases computational demands. Additionally, our framework cannot directly generate trajectories of 360 degree rotation, because warped depth video loses too much information at large viewpoint changes. However, an autoregressive generation manner could be leveraged to handle this situation. We leave this for future work. 

3 



Figure B4. **More Results of our method.** 

4 

