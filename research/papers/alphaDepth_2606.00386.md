# _α_ **Depth: Learning Single-Pass Soft Boundary Decomposition for Stereo Conversion** 

**Xiang Zhang**<sup>1</sup><sup>_,_2</sup> **, Yang Zhang**<sup>2</sup> **, Lukas Mehl**<sup>2</sup> **, Karlis Martins Briedis**<sup>2</sup> , **Markus Gross**<sup>1</sup><sup>_,_2</sup> , **Christopher Schroers**<sup>2</sup> 1ETH Zürich, 2DisneyResearch|Studios 



<!-- Start of picture text -->
‘ ‘ BG Colof<br>Single-Target Inputs (= gz<br>4<br>AW : Dept BG Golor,<br>a sc<br>LY ) es<br>Multi-Target Inputs fr Dept FG Color<br><!-- End of picture text -->

Figure 1: **Layered** _α_ **Depth Representation** . We introduce _α_ Depth to decompose soft boundaries ( _e.g._ , hair, thin structures, and defocus blur) for high-fidelity stereo conversion. Given an image and its depth map as inputs, our approach estimates layered information, _i.e._ , alpha, foreground/background (FG/BG) colors and depths, at _local soft boundaries_ (see non-zero alpha regions), enabling scene-level inference of multiple/overlapping targets in a single forward pass without user intervention. 

## **Abstract** 

Accurately modeling soft boundaries, _e.g._ , hair and defocus blur, is a fundamental challenge in stereo conversion due to the ambiguous blending of foreground and background. Existing depth models primarily predict single-layer depth, leading to ambiguity in depth correspondence at soft boundaries. While matting techniques can capture opacity for layered modeling, they often struggle in complex scenes with multiple targets and usually require user intervention. This paper introduces _α_ **Depth** , a layered representation that decomposes soft boundaries for high-fidelity stereo conversion. Specifically, we first resolve mixed color and depth ambiguity by estimating layered color and depth values at soft boundaries. Considering complex multi-target scenes, we design a Circular Alpha Representation (CAR) that shifts the paradigm from global target extraction to local boundary decomposition. Unlike prior matting methods restricted to a single foreground/background, CAR enables efficient scene-level inference without manual guidance. Extensive evaluations demonstrate that _α_ Depth achieves state-of-the-art performance in stereo conversion, eliminating background bleeding and structural distortions at soft boundaries. 

Preprint. 



<!-- Start of picture text -->
6 6 ®@ Layered Representation & Scene-Level Inference<br>Image Image & Manual Guidance Image Depth<br>Vv Vv<br>Depth Alpha aDepth<br>Estimation Matting Estimation<br>v Vv v<br>Depth Alpha Layered Color Alpha Layered Depth<br><!-- End of picture text -->

Figure 2: **Comparison with existing paradigms.** Depth estimation models typically assign a single depth value per pixel, struggling with mixed colors at soft boundaries and suffering from depth ambiguity. While conventional matting approaches extract instance-level soft boundaries, they usually require manual guidance ( _e.g._ , trimaps). In contrast, our layered _α_ Depth representation enables automatic scene-level decomposition. Given an image and its depth map, _α_ Depth explicitly decomposes soft boundaries into layered color, alpha, and layered depth in a single forward pass. 

## **1 Introduction** 

By lifting 2D images into 3D content, stereo conversion is critical for various immersive applications, including Virtual/Augmented Reality (VR/AR) and movie production [23, 55, 51, 7]. Recent methods have demonstrated remarkable progress in stereo conversion by leveraging foundation diffusion models to synthesize realistic novel views from monocular inputs [50, 38, 35]. For instance, Eye2eye [9] effectively utilizes diffusion priors to simulate complex view-dependent effects such as specular reflections in stereo conversion. Approaches like SplatDiff [54] and Elastic3D [24] have focused on improving the overall visual fidelity and structural consistency of the generated stereo pairs. Despite these advances, generating high-quality stereo content from monocular inputs remains challenging, particularly when dealing with intricate details in complex scenes. 

A key challenge in stereo conversion is the accurate handling of _soft boundaries_ , which naturally occur across diverse subjects ( _e.g._ , humans, animals, or computer-generated characters as shown in Fig. 1) and camera effects ( _e.g._ , defocus blur). At soft boundaries, foreground and background colors inherently mix within a single pixel, creating regions of partial transparency and resulting in ambiguous depth correspondence. Consequently, previous stereo conversion methods often struggle in recovering soft boundary details at high fidelity and produce stereo results with visual artifacts, such as halo effects, background bleeding, or unnatural floating textures around object silhouettes [55]. 

To achieve high-quality soft boundary recovery in stereo conversion, two fundamental challenges exist: **(i) Mixed Foreground and Background** : Many stereo conversion pipelines rely on monocular depth estimation for view synthesis [50, 36, 54, 56]. However, conventional depth estimators typically assign only a single depth value per pixel [44, 2, 53, 10], failing to model the layered characteristics of soft boundaries (Fig. 2). Although the recent work HairGuard [55] better captures soft boundary structures via depth refinement, it still suffers from depth ambiguity due to the single-layer depth representation. **(ii) Complex Scenes with Multiple Targets** : Alpha matting techniques can extract alpha mattes for soft boundary decomposition [48, 13, 12, 46]. However, existing matting methods generally rely on manual guidance, such as trimaps, visual prompts ( _e.g._ , points or boxes), and segmentation masks, for instance-level inference (Fig. 2). Consequently, these techniques necessitate user intervention for each target or repeated forward passes, rendering them impractical for automated stereo conversion pipelines when handling complex multi-target scenes. While auxiliary-free matting approaches like GVM [8] are emerging, they are typically designed for specific target categories ( _e.g._ , humans or animals) and thus struggle to generalize to the diverse types of soft boundaries present in complex stereo conversion scenarios ( _e.g._ , defocus blur in movie shots). 

2 

We introduce _α_ **Depth** , a novel layered representation designed to explicitly decompose local foreground and background at soft boundaries for high-fidelity stereo conversion, as shown in Fig. 2. To address the challenge of layer mixing, our _α_ Depth jointly estimates foreground and background information to model soft boundary regions. This explicitly disentangles the mixed colors and resolves depth ambiguity by allocating distinct depth and color values to the overlapping layers at soft boundaries. To enable efficient scene-level inference in complex scenarios, we introduce the Circular Alpha Representation (CAR). Unlike vanilla alpha representations that rely on global foreground and background definitions, CAR shifts the focus to modeling opacity exclusively at local soft boundaries. It treats all opaque regions (whether foreground or background) as a single unified class ( _e.g._ , see the black regions in Fig. 2). Furthermore, while resolving all occlusions might theoretically demand numerous layers, we observe that _a two-layer formulation is effective in locally separating foreground and background at soft boundaries, even in complex scenes with many layers._ This localized approach allows _α_ Depth to automatically decompose multiple overlapping targets across the entire scene in a single forward pass without user intervention. Leveraging the estimated _α_ Depth representation, we perform layered warping to synthesize initial novel views, which are subsequently refined by off-the-shelf inpainting models to generate high-fidelity stereo pairs. Finally, we introduce an efficient training data curation method that leverages existing image datasets and matting datasets to construct training pairs for _α_ Depth estimation. In summary, our main contributions are: 

- We propose a novel layered _α_ Depth representation that explicitly disentangles mixed colors and resolves depth ambiguity at soft boundaries for high-fidelity stereo conversion. 

- We design the Circular Alpha Representation (CAR) to model local soft boundary transitions rather than extracting global foregrounds, enabling efficient scene-level inference in a single forward pass without user intervention. 

## **2 Related Work** 

**Stereo Conversion.** Stereo conversion aims to synthesize high-quality stereo pairs from monocular inputs [41, 9, 4], a crucial technique for immersive media applications [23, 50]. Recent methods often leverage generative foundation models: image-based approaches [38, 50] utilize diffusion priors, _e.g._ , Stable Diffusion [33], to generate realistic stereo views, while video-based methods [56, 9, 36] design spatio-temporal mechanisms, _e.g._ , tiled diffusion strategy [56] and global spatial attention [36], for improved temporal coherence. To mitigate the texture hallucinations and geometric distortions inherent to diffusion models, several works incorporate explicit guidance mechanisms, such as texture bridge [54], guided decoding [24], and color fuser [55], for enhanced stereo conversion fidelity. However, due to the mixed foreground and background, existing approaches often struggle with soft boundaries and produce stereo results with visual artifacts like background bleeding. 

**Depth Estimation.** Monocular depth estimation predicts dense scene geometry from a single image, serving as a fundamental pillar for 3D vision tasks like stereo conversion [31, 44, 50, 54]. To achieve robust zero-shot generalization, a dominant paradigm is to train depth models on largescale datasets [17, 49, 31, 44, 39, 29]. For instance, MiDaS [32] proposes a family of depth losses to enable model training on diverse datasets. Recently, a variety of techniques are developed to combine real-world and synthetic datasets for enhanced detail extraction, such as teacher-student distillation [45, 18], edge-guided loss [28], real data refinement [40], and training protocols for fine boundary preservation [2]. Alternatively, harnessing geometric priors from pre-trained generative models has emerged as a compelling trajectory. Methods like Marigold [10], BetterDepth [53], and Pixel-Perfect Depth [42] cast depth estimation as an iterative denoising process to achieve remarkable detail recovery. Nevertheless, existing depth estimators generally assign a single depth value per pixel. This single-layer representation fundamentally fails at handling soft boundaries, suffering from depth ambiguity where foreground and background overlap. 

**Alpha Matting.** Alpha matting estimates the opacity of foreground targets, _i.e._ , alpha mattes, to extract foreground objects from their backgrounds [43, 48, 46], which potentially benefits soft boundary modeling in stereo conversion. To resolve semantic ambiguities, previous matting models usually rely on manual guidance, _e.g._ , trimaps, to explicitly define foreground and background [43, 27, 48]. Recent approaches have developed more flexible guidance, _e.g._ , segmentation masks or visual prompts, to facilitate matting for video sequences [47, 46]. To reduce human effort, auxiliaryfree methods, such as MODNet [11], RVM [19], and GVM [8], leverage pre-trained model priors, 

3 



<!-- Start of picture text -->
q<br>=<br>&<br>Video Depth Anything Warping HairGuard Warping @Depth Warping (Ours)<br><!-- End of picture text -->

(a) Visual comparison of warping performance and Epipolar Plane Images (EPIs) 



<!-- Start of picture text -->
wv VIZ<br>a d y ) AS \<br>:<br>. ea a a \<br>& BONG 2 \<br>io ase<br>Input Image Vanilla Alpha Representation Circular Alpha Representation (Ours)<br><!-- End of picture text -->

(b) Alpha valley issue (Alpha is shown only at soft regions, _i.e._ , _α ∈_ [0 _._ 02 _,_ 0 _._ 98], for comparison) 

Figure 3: **Challenges of soft boundary recovery in stereo conversion.** (a) We evaluate warping performance via Epipolar Plane Images (EPIs) extracted along the gray dashed line under uniform rightward camera motion. Direct warping with Video Depth Anything [3] struggles with depth ambiguity at soft boundaries, causing broken edges and flying pixels. Although HairGuard [55] captures better details, its single-layer depth representation often results in background bleeding and aliasing ( _e.g._ , see EPIs). By contrast, our layered representation effectively models soft boundaries to achieve superior warping and multi-view consistency. (b) Vanilla alpha representations often suffer from “alpha valleys” ( _i.e._ , alpha estimation errors at intersecting boundaries) due to their reliance on explicit global foreground and background definitions. By modeling local transitions rather than global separation, our Circular Alpha Representation (CAR) robustly handles overlapping targets to produce accurate alpha values. 

_e.g._ , diffusion priors, or temporal consistency to infer alpha mattes directly from input images. However, both paradigms exhibit critical limitations in complex scenes. Guidance-based methods necessitate user intervention or repeated forward passes for each subject, rendering them impractical for integration into automated stereo conversion pipelines. Conversely, auxiliary-free methods are generally restricted to specific semantic categories ( _e.g._ , humans) and struggle to generalize to diverse soft boundaries ( _e.g._ , defocus blur). To overcome these bottlenecks, we introduce the Circular Alpha Representation (CAR). By shifting the paradigm from global foreground extraction to local soft boundary decomposition, CAR enables _α_ Depth to automatically infer opacity across complex scenes in a single forward pass. 

## **3 Method** 

We first analyze the main challenges of soft boundary recovery in stereo conversion (Sec. 3.1), and then propose the layered _α_ Depth representation for efficient soft boundary decomposition (Sec. 3.2). 

### **3.1 Problem Analysis** 

Stereo conversion in real-world scenarios frequently encounters complex scenes characterized by multiple overlapping targets and intricate soft boundaries ( _e.g._ , hair, fur, and defocus blur). At these soft boundaries, the observed color _I_ is inherently a mixture of the foreground color _IF G_ and the background color _IBG_ , modulated by an opacity value _α ∈_ [0 _,_ 1]. Following alpha matting [48, 46], the color blending at soft boundaries can be defined as: 



Mixed colors at soft boundaries, coupled with multiple targets, introduce significant challenges: 

**Depth Ambiguity.** Based on Eq. (1), pixels within a soft boundary mix color contributions from both foreground and background layers. However, most monocular depth estimators predict only 

4 



<!-- Start of picture text -->
Wy— y +] Ame | 8saf<br>Depth —| Decoder | “| & 3 ;<br>+ Detail <<br>Edge] Encoder Detail skip Atpha<br>Extraction > Features > a<br>Semantic] co |) ee §<br>Encoder _. —ae Skip 35 Layered Color<br>Fs<br>Image Dual-Path Encoder a adJ | oeeeldeptn 23<br>—<br>Mult-Branch Decoder Layered Depth<br><!-- End of picture text -->

Figure 4: _α_ **Depth estimation pipeline.** Given an image and its corresponding depth map ( _e.g._ , from a pre-trained depth model), we employ a dual-path encoder to extract both semantic and detail features. A multi-branch decoder then processes these features for task-specific predictions. Finally, we apply circular alpha decoding to generate the estimated alpha map, which subsequently modulates and constrains the layered color and depth predictions on soft boundary regions. 

a single depth value per pixel [44, 10, 39, 42]. This single-layer representation inherently results in depth ambiguity at soft boundaries. Consequently, view transformation techniques like softmax splatting [25] struggle to project these pixels accurately, leading to broken boundaries and severe flying pixels (Fig. 3a). Although recent methods like HairGuard [55] capture finer boundary details, their single-layer depth often leads to background bleeding and aliasing artifacts (Fig. 3a). 

**Alpha Valley.** Boundaries at depth discontinuities are crucial for high-fidelity stereo conversion, as they govern the realistic rendering of occlusions and binocular parallax [50, 55]. However, complex scenes often feature multiple overlapping targets at varying depths ( _e.g._ , Fig. 3b), and even individual targets may possess intricate soft boundaries within their own structures ( _e.g._ , see alpha in the top example of Fig. 1). Existing matting methods typically rely on a global definition of foreground and background, _e.g._ , foreground defined by user inputs like trimaps or visual prompts [48, 46]. Consequently, they either require iterative user guidance for each instance or indiscriminately merge multiple targets into a single monolithic foreground, discarding vital inter-object boundary details. 

Furthermore, learning a vanilla alpha representation for multiple overlapping targets often suffers from the “ _alpha valley_ ” issue (Fig. 3b). To preserve local boundary details of overlapping foreground instances, alpha discontinuities emerge at their intersections ( _e.g._ , see alpha in Fig. 5). Since neural networks are usually biased toward smooth predictions, they often struggle to resolve these sharp transitions, yielding inaccurate alpha values (Fig. 3b). These estimation errors ultimately propagate through the stereo conversion pipeline, yielding inconsistent soft boundaries in the stereo pairs. 

### **3.2** _α_ **Depth** 

We propose a layered _α_ Depth representation to address depth ambiguity and alpha valley issues for efficient soft boundary decomposition. Instead of using manual guidance like trimaps, we directly utilize image semantics and scene geometry for _α_ Depth estimation, enabling scene-level inference without user intervention (Fig. 4). Given an input image _I_ IN and its depth map _D_ IN, we first extract depth gradients to facilitate soft boundary localization. Then, we employ a dual-path encoder to capture both high-level contextual cues and fine-grained structural details. Specifically, a detail encoder built upon UNet encoder [34] extracts multi-scale features to preserve rich textural and structural details. Concurrently, a semantic encoder (based on DINOv2 [26] with Depth Anything V2 weight initialization [45]) extracts deep semantic features for soft boundary reasoning. Finally, these features are fed into a multi-branch decoder (based on UNet decoder [34]) to predict _α_ Depth representation, which jointly estimates alpha, layered color, and layered depth at soft boundaries. 

**Circular Alpha Representation (CAR).** Traditional matting paradigms rely on a global definition of foreground and background [48, 46]. In scenarios featuring multiple overlapping objects at varying 

5 



<!-- Start of picture text -->
Vanilla Alpha Circular Alpha Encoding for Training Circular Alpha Decoding for Inference<br>il x ° fe<br>if sin@2na) i? \ Gna) a a<br>é ae Se Se a - ~<br>ow” > \ Dr<br>1 3 \ \ \ an<br>} >) {p>} a, , }<br>Discontinuity —_ — Continuous Surfaces “"™* Circular Coordinate<br><!-- End of picture text -->

Figure 5: **Circular Alpha Representation (CAR).** The vanilla alpha representation inherently suffers from sharp discontinuities at the intersecting boundaries of multiple overlapping instances. By contrast, CAR encodes the ground-truth alpha into continuous trigonometric space during training, benefiting model optimization and eliminating alpha valley issues (Fig. 3b). During inference, the predicted trigonometric components are decoded back into an alpha matte _α_ ˆ at soft boundaries. 

depths, this global assignment forces sharp discontinuities at inter-object intersecting boundaries (Fig. 5), leading to the alpha valley issue (see Fig. 3b). By contrast, the proposed CAR reformulates the task by shifting from global foreground extraction to local soft boundary decomposition. We treat all opaque regions, whether foreground or background, as a single unified class and focus on estimating opacity at semi-transparent boundaries. To achieve this, we project the ground-truth alpha map _α ∈_ [0 _,_ 1] into a continuous trigonometric space via circular alpha encoding (Fig. 5): 



By leveraging the periodicity of trigonometric functions, we wrap the linear alpha scale around a circle, mapping background ( _α_ = 0) and opaque foreground ( _α_ = 1) to the same coordinate (0 _,_ 1) in the ( _α_ sin _, α_ cos) space. This transformation collapses the discrete jump at intersecting boundaries into a continuous manifold (Fig. 5). By bridging the gap between _α_ = 0 and _α_ = 1, it eliminates boundary discontinuities and facilitates model optimization. 

During inference, the alpha decoder directly estimates the continuous trigonometric components, _i.e._ , _α_ ˆsin and _α_ ˆcos. We then apply circular alpha decoding to reconstruct alpha values _α_ ˆ _∈_ [0 _,_ 1) via the four-quadrant inverse tangent function, _i.e._ , 



As shown in Fig. 5, CAR projects opaque regions into a unified class with _α_ ˆ = 0 and focuses on estimating opacity for soft boundaries. By navigating this circular space, CAR circumvents alpha valley issues and enables scene-level soft boundary decomposition in a single forward pass. 

**Layered Representation.** To resolve depth ambiguity and color mixing, we explicitly decouple soft boundaries into local foreground (FG) and background (BG) representations. While complex scenes may theoretically require numerous global layers to account for all occlusions, we observe that _local soft boundaries can be effectively modeled using a two-layer decomposition_ , _i.e._ , locally differentiating foreground and background for each soft boundary. Thus, we adopt a two-layer representation for both color and depth at soft boundary regions. Specifically, we estimate the layered color _I_<sup>¯</sup> FG _, I_<sup>¯</sup> BG _∈_ R<sup>3</sup><sup>_×h×w_</sup> and color blending weights _W_ FG<sup>_I, W_</sup> BG<sup>_I∈_R</sup><sup>_h×w_via the color decoder.</sup> Similarly, the depth decoder predicts the layered depth _D_<sup>¯</sup> FG _, D_<sup>¯</sup> BG _∈_ R<sup>_h×w_</sup> and depth blending weights _W_ FG<sup>_D, W_</sup> BG<sup>_D∈_R</sup><sup>_h×w_.Inaddition,weestimatesoftboundaryregions</sup><sup>_S_ˆbythresholding</sup> the estimated _α_ ˆ, _i.e._ , _S_<sup>ˆ</sup> = I( _α_ th _≤ α_ ˆ _≤_ 1 _− α_ th) with _α_ th = 0 _._ 02 and I( _·_ ) denoting the indicator function. The layered prediction is then formulated via alpha-modulated blending, _i.e._ , 

_′X ′X ′X X_ ˆ _⋆_ = _W⋆ ⊙ X_<sup>¯</sup> _⋆_ + (1 _− W⋆_<sup>)</sup><sup>_⊙X_IN</sup><sup>_,_</sup> with _W⋆_ = _S_<sup>ˆ</sup> _⊙_ (1 _− W⋆_<sup>_X_)</sup><sup>_,_</sup> (4) where _X ∈{I, D}, ⋆ ∈{_ FG _,_ BG _},_ and _⊙_ denotes spatial element-wise multiplication. Eq. (4) restricts the layered modeling exclusively to the soft boundary regions _S_<sup>ˆ</sup> . For opaque regions, the 

6 



<!-- Start of picture text -->
Ground-Truth »]a .<br><4 t 1 ~ 1 ‘ 1 ~ ‘ 1<br>4 4 rf 1 t 1 4 1<br>i ai Pak’ Pate<br>a a a<br><!-- End of picture text -->

Figure 6: **Training Data Curation.** Firstly, the alpha map is processed via circular alpha encoding to yield continuous alpha labels ( _α_ sin _, α_ cos) and thresholded to produce layered masks ( _M_ FG _, M_ BG). In layered color/depth generation, foreground and background assets are composited to form the synthesized input image ( _I_ IN) and depth ( _D_ IN). Concurrently, masked blending is applied to generate ground-truth color layers ( _I_ FG _, I_ BG) and depth layers ( _D_ FG _, D_ BG) for soft boundary regions. 

original input colors and depths are retained, which preserves high-fidelity textures from _I_ IN and facilitates plug-and-play integration with state-of-the-art depth estimation models. We then project the estimated _α_ Depth representation to the target viewpoint via layered warping (see Sec. A.1 for more details). To generate the final stereo results, we employ the pretrained scene painter and color fuser from HairGuard [55] for disocclusion inpainting and texture enhancement. 

**Model Training.** We propose an efficient data curation strategy to utilize existing matting datasets for _α_ Depth training (Fig. 6). Given a foreground RGBA image from matting datasets, we first project the ground-truth alpha matte _α_ into continuous trigonometric labels _α_ sin _, α_ cos via circular alpha encoding Eq. (2). We also derive the binary foreground mask _M_ FG = I( _α ≥ α_ th) and background mask _M_ BG = I( _α ≥_ 1 _− α_ th) for layered label generation. _M_ FG captures soft boundary regions for synthesizing foreground color/depth labels, whereas _M_ BG helps preserve background information at soft boundaries. For layered color generation, we composite the foreground and background (sampled from image datasets) via standard alpha blending Eq. (1) to synthesize the input image _I_ IN. We then apply masked blending using _M_ FG and _M_ BG to generate the ground-truth layered colors _I_ FG and _I_ BG at soft boundary regions. For layered depth generation, we synthesize the input depth map _D_ IN following the depth composition protocol of HairGuard [55]. Analogously, masked blending is applied to generate ground-truth layered depths _D_ FG and _D_ BG (please see Sec. A.3 for more details). 

The _α_ Depth network is trained by jointly optimizing color, depth, and alpha representations, _i.e._ , 



where the color loss _LI_ = _L_ ( _I_<sup>ˆ</sup> FG _, I_ FG) + _L_ ( _I_<sup>ˆ</sup> BG _, I_ BG), the depth loss _LD_ = _L_ ( _D_<sup>ˆ</sup> FG _, D_ FG) + _L_ ( _D_<sup>ˆ</sup> BG _, D_ BG), and the alpha loss _Lα_ = _L_ (ˆ _α_ sin _, α_ sin) + _L_ (ˆ _α_ cos _, α_ cos). To facilitate stable multitask learning, we apply the same loss function _L_ ( _·_ ) across all modalities and follow a two-stage training scheme. The first-stage training focuses on recovering fine-grained details at local soft boundaries with _L_ ( _·_ ) defined as _L_ ( _X, X_<sup>ˆ</sup> ) = _L_ 1( _X, X_<sup>ˆ</sup> ) + _L_ m( _S ⊙ X, S_<sup>ˆ</sup> _⊙ X_ ) _,_ where _L_ 1 is _ℓ_ 1 loss, _L_ m denotes the matting loss from ViTMatte [48], and _S_ = I( _α_ th _≤ α ≤_ 1 _−α_ th) is the soft boundary mask. In the second stage, we apply the matting loss _L_ m across the entire image space for global refinement, _i.e._ , _L_ ( _X, X_<sup>ˆ</sup> ) = _L_ m( _X, X_<sup>ˆ</sup> ). 

## **4 Experiments and Analysis** 

### **4.1 Experimental Settings** 

**Implementation** . We train the _α_ Depth network with AdamW optimizer [22] under 448 _×_ 448 patches, batch size 32, and 1 _×_ 10<sup>_−_5</sup> learning rate. To curate training pairs, we sample background images from RealEstate10K [57] and DL3DV-10K [20], and use foreground images from matting 

7 



<!-- Start of picture text -->
><br><!-- End of picture text -->



<!-- Start of picture text -->
4<br><!-- End of picture text -->



<!-- Start of picture text -->
=<br><!-- End of picture text -->





<!-- Start of picture text -->
><br><!-- End of picture text -->





<!-- Start of picture text -->
=<br><!-- End of picture text -->





<!-- Start of picture text -->
><br><!-- End of picture text -->



<!-- Start of picture text -->
;<br><!-- End of picture text -->

Input Image HairGuard Warping HairGuard Result **Our Warping Our Result** Figure 7: **Visual comparisons with HairGuard [55]** in warping and stereo conversion. 

Table 1: **Stereo image/video conversion performance** . The best and second best results are marked. 

|**Method**|**Stereo Ima**|**ge Conver**|**sion(Mon**|**o2Stereo)**|**Stereo**|**Video Con**|**version(**|**Marvel-10**|**K)**|
|---|---|---|---|---|---|---|---|---|---|
||S-PSNR_↑_|S-SSIM_↑_|LPIPS_↓_|DISTS_↓_|S-PSNR_↑_|S-SSIM_↑_|LPIPS_↓_|DISTS_↓_|FVD_↓_|
|StereoDiffusion [38]|22.95|0.6407|0.2098|0.0747|23.53|0.6805|0.2173|0.0694|18.41|
|Mono2Stereo [50]|24.48|0.6933|0.1990|0.0751|25.19|0.7309|0.1979|0.0690|19.81|
|StereoCrafter [56]|24.24|0.7073|0.2334|0.1198|25.96|0.7619|0.2287|0.1231|10.05|
|SplatDiff [54]|24.78|0.7339|0.1235|0.0439|26.57|0.8006|0.0831|0.0364|2.18|
|HairGuard [55]|25.05|0.7445|0.1212|0.0444|27.10|0.8239|0.0734|0.0322|2.14|
|_α_**Depth (Ours)**|25.60|0.7554|0.1181|0.0417|28.46|0.8373|0.0699|0.0297|1.72|



datasets: AM-2K [14], Distinctions-646 [30], and Composition-1K [43]. We train the model for 50 epochs per stage, which takes approximately 6 days in total on an NVIDIA RTX A6000 GPU. 

**Evaluation** . We employ the Mono2Stereo [50] and Marvel-10K [55] datasets for stereo image/video conversion. For fair comparisons, all baselines use the same depth models: Depth Anything V2 (DAv2) [45] for Mono2Stereo and Video Depth Anything (VDA) [3] for Marvel-10K. We also employ two natural image matting datasets AIM-500 [16] and P3M-10K [15] to evaluate the performance of our circular alpha representation. 

### **4.2 Stereo Conversion** 

Tab. 1 compares _α_ Depth with state-of-the-art methods for stereo image/video conversion. Since soft boundaries usually occupy a small fraction of the image, we compute pixel-level metrics exclusively on soft regions _S_<sup>ˆ</sup> (denoted by S-PSNR and S-SSIM), alongside wholeimage perceptual metrics (LPIPS [52] and DISTS [6]). Benefiting from soft boundary 

Table 2: **Warping performance** on Marvel10K [55]. Best and second best results are marked. 

|**Method**|S-PSNR<br>S-SSIM|LPIPS<br>DISTS<br>FVD|
|---|---|---|
|VDA [3]|26.14<br>0.6718|0.1337 0.0910 7.21|
|VDA + HairGuard [55]|27.90<br>0.7328|0.1277 0.0839 9.39|
|**VDA +**_α_**Depth (Ours)**|28.68<br>0.7636|0.1190<br>0.0738<br>7.13|



decomposition, our _α_ Depth consistently outperforms previous methods and eliminates artifacts like background bleeding (Fig. 7), yielding the best video consistency (FVD [37] in Tab. 1). Finally, Tab. 2 compares our warping performance against baselines using the original depth from VDA [3] and refined depth from HairGuard [55]. While HairGuard improves soft boundary details, its single-layer depth fails to resolve depth ambiguity ( _e.g._ , mixed colors in Fig. 7). By contrast, our approach performs layered modeling on local soft boundaries and achieves the best warping performance. 

### **4.3 Alpha Matting** 

We evaluate our Circular Alpha Representation (CAR) against trimap-based (ViTMatte [48]), maskbased (MatAnyone 2 [46]), and auxiliary-free (GVM [8]) baselines. Since CAR predicts alpha values at local soft boundaries without defining global foreground/background, we apply circular alpha encoding Eq. (2) to ground-truth labels and the predictions of all baselines for fair comparisons (please see Sec. A.2 for more details). Following ViTMatte [48], we compute standard alpha metrics (SAD, Grad, Conn) exclusively within the unknown regions of trimaps. As shown in Tab. 3 and Fig. 8, CAR performs comparably to state-of-the-art methods without requiring manual guidance. Furthermore, in contrast to prior matting methods, our design is able to handle complex multi-target scenes (Fig. 3b) and capture intra-object soft boundaries ( _e.g._ , Figs. 8 top and 1 top). 

8 





<!-- Start of picture text -->
o o<br><!-- End of picture text -->





<!-- Start of picture text -->
t €f<br><!-- End of picture text -->





<!-- Start of picture text -->
€f<br><!-- End of picture text -->





<!-- Start of picture text -->
¢i<br><!-- End of picture text -->





<!-- Start of picture text -->
i n<br><!-- End of picture text -->

Input Image GVM [8] MatAnyone 2 [46] ViTMatte [48] _α_ **Depth (Ours)** Figure 8: **Visual comparisons with alpha matting methods.** 

Table 3: **Alpha matting performance** . The best and second best results are marked. 

|**Method**|**Guidance**|**Average**||**AIM-50**|**0**||**P3M-10**|**K**|
|---|---|---|---|---|---|---|---|---|
||**Type**|**Rank**|SAD_↓_|Grad_↓_|Conn_↓_|SAD_↓_|Grad_↓_|Conn_↓_|
|ViTMatte [48]|Trimap|2.17|7.44|17.82|4.07|4.06|11.27|2.29|
|GVM [8]|Auxiliary-Free|4.00|9.64|34.04|5.35|5.56|18.30|3.11|
|MatAnyone 2 [46]|Segmentation Mask|1.67|7.42|21.61|4.06|3.63|10.10|2.08|
|_α_**Depth (Ours)**|Depth|2.17|7.24|20.20|3.89|4.09|11.88|2.31|



### **4.4 Ablation Study** 

To validate our design choices, we analyze both warping and alpha matting performance in Tab. 4. **(i)** _α_ **Depth Ablation** . Compared with the baseline directly using VDA depth [3] for warping (A#1), estimating only foreground information ( _i.e._ , foreground color, depth, and alpha) at soft boundaries mitigates background bleeding and improves structural recovery (S-SSIM of A#2 in Tab. 4a). Replacing the vanilla alpha representation with our proposed CAR better handles complex scenes, yielding consistent gains (A#3 _v.s._ A#2). By additionally estimating background information, our layered _α_ Depth representation achieves the best warping performance via soft boundary decomposition (A#4). **(ii) CAR Ablation** . Tab. 4b validates the contributions of matting loss _L_ m (B#2 _v.s._ B#4) and two-stage training (B#3 _v.s._ B#4) in alpha matting performance. Unlike vanilla alpha representation that often suffers from unstable predictions due to alpha valley issues (Fig. 3b), our CAR focuses on local soft boundaries and delivers the best matting performance (B#1 _v.s._ B#4). 

Table 4: **Ablation study** . (a) Effects of Alpha Estimation (AE), Circular Alpha Representation (CAR), and Layered Representation (LR) on warping performance. (b) Impacts of different strategies on alpha matting. The best and second best results are marked. Please see Sec. F for visual results. (a) _α_ Depth ablation. (b) CAR ablation. 

|ID|AE|CAR|LR|**M**|**arvel-10K**||ID|Strateies||**P3M-10**|**K**|
|---|---|---|---|---|---|---|---|---|---|---|---|
|||||S-SSIM_↑_|LPIPS_↓_|DISTS_↓_||g|SAD_↓_|Grad_↓_|Conn_↓_|
|A#1||||0.6718|0.1337|0.0910|B#1|Vanilla Alpha Representation|4.47|12.41|2.42|
|A#2|✓|||0.7165|0.1346|0.0869|B#2|_ℓ_1 Loss Only|4.36|12.54|2.48|
|A#3|✓|✓||0.7214|0.1280|0.0819|B#3|Single-Stage Training|4.29|11.77|2.43|
|A#4|✓|✓|✓|0.7636|0.1190|0.0738|B#4|**CAR (Ours)**|4.09|11.88|2.31|



## **5 Conclusion** 

This paper proposes _α_ Depth, a layered representation designed to resolve depth ambiguity and color mixing at soft boundaries for stereo conversion. By leveraging our Circular Alpha Representation (CAR), _α_ Depth bypasses the discontinuities of vanilla alpha in complex scenes, enabling automatic scene-level decomposition in a single forward pass. Extensive experiments verify the effectiveness of CAR, showing state-of-the-art boundary fidelity of _α_ Depth in stereo conversion. 

9 

## **References** 

- [1] Jianhong Bai, Menghan Xia, Xiao Fu, Xintao Wang, Lianrui Mu, Jinwen Cao, Zuozhu Liu, Haoji Hu, Xiang Bai, Pengfei Wan, et al. Recammaster: Camera-controlled generative rendering from a single video. In _ICCV_ , 2025. 

- [2] Alexey Bochkovskiy, Amaël Delaunoy, Hugo Germain, Marcel Santos, Yichao Zhou, Stephan Richter, and Vladlen Koltun. Depth pro: Sharp monocular metric depth in less than a second. In _ICLR_ , 2025. 

- [3] Sili Chen, Hengkai Guo, Shengnan Zhu, Feihu Zhang, Zilong Huang, Jiashi Feng, and Bingyi Kang. Video depth anything: Consistent depth estimation for super-long videos. In _CVPR_ , pages 22831–22840, 2025. 

- [4] Peng Dai, Feitong Tan, Qiangeng Xu, David Futschik, Ruofei Du, Sean Fanello, Xiaojuan Qi, and Yinda Zhang. Svg: 3d stereoscopic video generation via denoising frame matrix. _arXiv preprint arXiv:2407.00367_ , 2024. 

- [5] Yutong Dai, Brian Price, He Zhang, and Chunhua Shen. Boosting robustness of image matting with context assembling and strong data augmentation. In _CVPR_ , pages 11707–11716, 2022. 

- [6] Keyan Ding, Kede Ma, Shiqi Wang, and Eero P. Simoncelli. Image quality assessment: Unifying structure and texture similarity. _IEEE TPAMI_ , 44(5):2567–2581, 2022. 

- [7] Ruiqi Gao, Aleksander Holynski, Philipp Henzler, Arthur Brussee, Ricardo Martin-Brualla, Pratul Srinivasan, Jonathan T Barron, and Ben Poole. Cat3d: Create anything in 3d with multi-view diffusion models. In _NeurIPS_ , 2024. 

- [8] Yongtao Ge, Kangyang Xie, Guangkai Xu, Li Ke, Mingyu Liu, Longtao Huang, Hui Xue, Hao Chen, and Chunhua Shen. Generative video matting. In _SIGGRAPH_ , pages 1–10, 2025. 

- [9] Michal Geyer, Omer Tov, Linyi Jin, Richard Tucker, Inbar Mosseri, Tali Dekel, and Noah Snavely. Eye2eye: A simple approach for monocular-to-stereo video synthesis. _arXiv preprint arXiv:2505.00135_ , 2025. 

- [10] Bingxin Ke, Anton Obukhov, Shengyu Huang, Nando Metzger, Rodrigo Caye Daudt, and Konrad Schindler. Repurposing diffusion-based image generators for monocular depth estimation. In _CVPR_ , pages 9492–9502, 2024. 

- [11] Zhanghan Ke, Jiayu Sun, Kaican Li, Qiong Yan, and Rynson WH Lau. Modnet: Real-time trimap-free portrait matting via objective decomposition. In _AAAI_ , volume 36, pages 1140–1147, 2022. 

- [12] Beomyoung Kim, Chanyong Shin, Joonhyun Jeong, Hyungsik Jung, Se-Yun Lee, Sewhan Chun, DongHyun Hwang, and Joonsang Yu. Zim: Zero-shot image matting for anything. In _ICCV_ , pages 23828–23838, 2025. 

- [13] Jiachen Li, Jitesh Jain, and Humphrey Shi. Matting anything. In _CVPR_ , pages 1775–1785, 2024. 

- [14] Jizhizi Li. _End-to-end Animal Matting_ . PhD thesis, University of Sydney, 2020. 

- [15] Jizhizi Li, Sihan Ma, Jing Zhang, and Dacheng Tao. Privacy-preserving portrait matting. In _ACMMM_ , pages 3501–3509, 2021. 

- [16] Jizhizi Li, Jing Zhang, and Dacheng Tao. Deep automatic natural image matting. In _IJCAI_ . International Joint Conferences on Artificial Intelligence Organization, 2021. 

- [17] Zhengqi Li and Noah Snavely. Megadepth: Learning single-view depth prediction from internet photos. In _CVPR_ , pages 2041–2050, 2018. 

- [18] Haotong Lin, Sili Chen, Junhao Liew, Donny Y Chen, Zhenyu Li, Guang Shi, Jiashi Feng, and Bingyi Kang. Depth anything 3: Recovering the visual space from any views. _arXiv preprint arXiv:2511.10647_ , 2025. 

- [19] Shanchuan Lin, Linjie Yang, Imran Saleemi, and Soumyadip Sengupta. Robust high-resolution video matting with temporal guidance. In _WACV_ , pages 238–247, 2022. 

- [20] Lu Ling, Yichen Sheng, Zhi Tu, Wentian Zhao, Cheng Xin, Kun Wan, Lantao Yu, Qianyu Guo, Zixun Yu, Yawen Lu, et al. Dl3dv-10k: A large-scale scene dataset for deep learning-based 3d vision. In _CVPR_ , pages 22160–22169, 2024. 

- [21] Anna Lischke, Guofei Pang, Mamikon Gulian, Fangying Song, Christian Glusa, Xiaoning Zheng, Zhiping Mao, Wei Cai, Mark M Meerschaert, Mark Ainsworth, et al. What is the fractional laplacian? a comparative review with new results. _Journal of Computational Physics_ , 404:109009, 2020. 

10 

- [22] Ilya Loshchilov and Frank Hutter. Decoupled weight decay regularization. In _ICLR_ , 2019. 

- [23] Lukas Mehl, Andrés Bruhn, Markus Gross, and Christopher Schroers. Stereo conversion with disparityaware warping, compositing and inpainting. In _WACV_ , pages 4260–4269, 2024. 

- [24] Nando Metzger, Prune Truong, Goutam Bhat, Konrad Schindler, and Federico Tombari. Elastic3d: Controllable stereo video conversion with guided latent decoding. In _CVPR_ , 2026. 

- [25] Simon Niklaus and Feng Liu. Softmax splatting for video frame interpolation. In _CVPR_ , pages 5437–5446, 2020. 

- [26] Maxime Oquab, Timothée Darcet, Théo Moutakanni, Huy Vo, Marc Szafraniec, Vasil Khalidov, Pierre Fernandez, Daniel Haziza, Francisco Massa, Alaaeldin El-Nouby, et al. Dinov2: Learning robust visual features without supervision. _arXiv preprint arXiv:2304.07193_ , 2023. 

- [27] GyuTae Park, SungJoon Son, JaeYoung Yoo, SeHo Kim, and Nojun Kwak. Matteformer: Transformerbased image matting via prior-tokens. In _CVPR_ , pages 11696–11706, 2022. 

- [28] Luigi Piccinelli, Christos Sakaridis, Yung-Hsu Yang, Mattia Segu, Siyuan Li, Wim Abbeloos, and Luc Van Gool. Unidepthv2: Universal monocular metric depth estimation made simpler. _arXiv preprint arXiv:2502.20110_ , 2025. 

- [29] Luigi Piccinelli, Yung-Hsu Yang, Christos Sakaridis, Mattia Segu, Siyuan Li, Luc Van Gool, and Fisher Yu. Unidepth: Universal monocular metric depth estimation. In _CVPR_ , pages 10106–10116, 2024. 

- [30] Yu Qiao, Yuhao Liu, Xin Yang, Dongsheng Zhou, Mingliang Xu, Qiang Zhang, and Xiaopeng Wei. Attention-guided hierarchical structure aggregation for image matting. In _CVPR_ , June 2020. 

- [31] René Ranftl, Alexey Bochkovskiy, and Vladlen Koltun. Vision transformers for dense prediction. In _ICCV_ , pages 12179–12188, 2021. 

- [32] René Ranftl, Katrin Lasinger, David Hafner, Konrad Schindler, and Vladlen Koltun. Towards robust monocular depth estimation: Mixing datasets for zero-shot cross-dataset transfer. _PAMI_ , 44(3):1623–1637, 2020. 

- [33] Robin Rombach, Andreas Blattmann, Dominik Lorenz, Patrick Esser, and Björn Ommer. High-resolution image synthesis with latent diffusion models. In _CVPR_ , pages 10684–10695, 2022. 

- [34] Olaf Ronneberger, Philipp Fischer, and Thomas Brox. U-net: Convolutional networks for biomedical image segmentation. In _International Conference on Medical image computing and computer-assisted intervention_ , pages 234–241. Springer, 2015. 

- [35] Guibao Shen, Yihua Du, Wenhang Ge, Jing He, Chirui Chang, Donghao Zhou, Zhen Yang, Luozhou Wang, Xin Tao, and Ying-Cong Chen. Stereopilot: Learning unified and efficient stereo conversion via generative priors. _arXiv preprint arXiv:2512.16915_ , 2025. 

- [36] Nina Shvetsova, Goutam Bhat, Prune Truong, Hilde Kuehne, and Federico Tombari. M2svid: End-to-end inpainting and refinement for monocular-to-stereo video conversion. _arXiv preprint arXiv:2505.16565_ , 2025. 

- [37] Thomas Unterthiner, Sjoerd Van Steenkiste, Karol Kurach, Raphael Marinier, Marcin Michalski, and Sylvain Gelly. Towards accurate generative models of video: A new metric & challenges. _arXiv preprint arXiv:1812.01717_ , 2018. 

- [38] Lezhong Wang, Jeppe Revall Frisvad, Mark Bo Jensen, and Siavash Arjomand Bigdeli. Stereodiffusion: Training-free stereo image generation using latent diffusion models. In _CVPR_ , pages 7416–7425, 2024. 

- [39] Ruicheng Wang, Sicheng Xu, Cassie Dai, Jianfeng Xiang, Yu Deng, Xin Tong, and Jiaolong Yang. Moge: Unlocking accurate monocular geometry estimation for open-domain images with optimal training supervision. In _CVPR_ , pages 5261–5271, 2025. 

- [40] Ruicheng Wang, Sicheng Xu, Yue Dong, Yu Deng, Jianfeng Xiang, Zelong Lv, Guangzhong Sun, Xin Tong, and Jiaolong Yang. Moge-2: Accurate monocular geometry with metric scale and sharp details. In _NIPS_ , 2025. 

- [41] Junyuan Xie, Ross Girshick, and Ali Farhadi. Deep3d: Fully automatic 2d-to-3d video conversion with deep convolutional neural networks. In _European conference on computer vision_ , pages 842–857. Springer, 2016. 

11 

- [42] Gangwei Xu, Haotong Lin, Hongcheng Luo, Xianqi Wang, Jingfeng Yao, Lianghui Zhu, Yuechuan Pu, Cheng Chi, Haiyang Sun, Bing Wang, Guang Chen, Hangjun Ye, Sida Peng, and Xin Yang. Pixel-perfect depth with semantics-prompted diffusion transformers. In _NIPS_ , 2025. 

- [43] Ning Xu, Brian Price, Scott Cohen, and Thomas Huang. Deep image matting. In _Proceedings of the IEEE conference on computer vision and pattern recognition_ , pages 2970–2979, 2017. 

- [44] Lihe Yang, Bingyi Kang, Zilong Huang, Xiaogang Xu, Jiashi Feng, and Hengshuang Zhao. Depth anything: Unleashing the power of large-scale unlabeled data. In _CVPR_ , pages 10371–10381, 2024. 

- [45] Lihe Yang, Bingyi Kang, Zilong Huang, Zhen Zhao, Xiaogang Xu, Jiashi Feng, and Hengshuang Zhao. Depth anything v2. In _NeurIPS_ , 2024. 

- [46] Peiqing Yang, Shangchen Zhou, Kai Hao, and Qingyi Tao. Matanyone 2: Scaling video matting via a learned quality evaluator. In _CVPR_ , 2026. 

- [47] Peiqing Yang, Shangchen Zhou, Jixin Zhao, Qingyi Tao, and Chen Change Loy. Matanyone: Stable video matting with consistent memory propagation. In _CVPR_ , pages 7299–7308, 2025. 

- [48] Jingfeng Yao, Xinggang Wang, Shusheng Yang, and Baoyuan Wang. Vitmatte: Boosting image matting with pre-trained plain vision transformers. _Information Fusion_ , 103:102091, 2024. 

- [49] Wei Yin, Xinlong Wang, Chunhua Shen, Yifan Liu, Zhi Tian, Songcen Xu, Changming Sun, and Dou Renyin. Diversedepth: Affine-invariant depth prediction using diverse data. _arXiv preprint arXiv:2002.00569_ , 2020. 

- [50] Songsong Yu, Yuxin Chen, Zhongang Qi, Zeke Xie, Yifan Wang, Lijun Wang, Ying Shan, and Huchuan Lu. Mono2stereo: A benchmark and empirical study for stereo conversion. In _CVPR_ , pages 21847–21856, 2025. 

- [51] Wangbo Yu, Jinbo Xing, Li Yuan, Wenbo Hu, Xiaoyu Li, Zhipeng Huang, Xiangjun Gao, Tien-Tsin Wong, Ying Shan, and Yonghong Tian. Viewcrafter: Taming video diffusion models for high-fidelity novel view synthesis. _arXiv preprint arXiv:2409.02048_ , 2024. 

- [52] Richard Zhang, Phillip Isola, Alexei A Efros, Eli Shechtman, and Oliver Wang. The unreasonable effectiveness of deep features as a perceptual metric. In _CVPR_ , pages 586–595, 2018. 

- [53] Xiang Zhang, Bingxin Ke, Hayko Riemenschneider, Nando Metzger, Anton Obukhov, Markus Gross, Konrad Schindler, and Christopher Schroers. Betterdepth: Plug-and-play diffusion refiner for zero-shot monocular depth estimation. In _NeurIPS_ , 2024. 

- [54] Xiang Zhang, Yang Zhang, Lukas Mehl, Markus Gross, and Christopher Schroers. High-fidelity novel view synthesis via splatting-guided diffusion. In _SIGGRAPH_ , SIGGRAPH Conference Papers ’25, New York, NY, USA, 2025. Association for Computing Machinery. 

- [55] Xiang Zhang, Yang Zhang, Lukas Mehl, Markus Gross, and Christopher Schroers. Guardians of the hair: Rescuing soft boundaries in depth, stereo, and novel views. In _CVPR_ , 2026. 

- [56] Sijie Zhao, Wenbo Hu, Xiaodong Cun, Yong Zhang, Xiaoyu Li, Zhe Kong, Xiangjun Gao, Muyao Niu, and Ying Shan. Stereocrafter: Diffusion-based generation of long and high-fidelity stereoscopic 3d from monocular videos. _arXiv preprint arXiv:2409.07447_ , 2024. 

- [57] Tinghui Zhou, Richard Tucker, John Flynn, Graham Fyffe, and Noah Snavely. Stereo magnification: learning view synthesis using multiplane images. _ACM Trans. Graph._ , 37(4), July 2018. 

12 

## **Appendix** 

We provide more technical details, experimental results, ablation studies, and qualitative visualizations to support the contributions of our _α_ Depth approach. Detailed contents are listed as follows: 

## **Contents** 

|**A**<br>**M**|**ore Implementation Details**|**13**|
|---|---|---|
|A.1|Layered Warping with_α_Depth Representation . . . . . . . . . . . . . . . . . .|. . . . . . . .<br>13|
|A.2|Matting Evaluation Details . . . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . .<br>14|
|A.3|Training Data Curation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . .<br>14|
|A.4|Matting Loss_L_m . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . .<br>14|
|**B**<br>**M**|**ore Experimental Results**|**15**|
|B.1|Pixel-Level Metrics on Full Image . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . .<br>15|
|B.2|Computational Complexity . . . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . .<br>15|
|B.3|Vanilla Alpha Representation_v.s._Circular Alpha Representation<br>. . . . . . . .|. . . . . . . .<br>15|
|B.4|Matting Performance under Different Depth Inputs<br>. . . . . . . . . . . . . . .|. . . . . . . .<br>15|
|B.5|Performance under Different Camera Trajectories . . . . . . . . . . . . . . . .|. . . . . . . .<br>15|
|**C**<br>**M**|**ore Ablation Studies**|**16**|
|C.1|Impact of Multi-Branch Decoder . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . .<br>16|
|C.2|Impact of Semantic Encoder . . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . .<br>17|
|C.3|Impact of Depth Edge Extraction . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . .<br>18|
|**D**<br>**Li**|**mitations and Discussions**|**19**|
|**E**<br>**Di**|**scussion of Societal Impacts**|**19**|
|**F**<br>**Vi**|**sualization of Ablation Models**|**20**|
|**G**<br>**Vi**|**sualization of**_α_**Depth Results**|**20**|
|**H**<br>**M**|**ore Visual Comparisons**|**20**|
|H.1|Stereo Conversion<br>. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . .<br>20|
|H.2|Alpha Matting<br>. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|. . . . . . . .<br>20|



## **A More Implementation Details** 

### **A.1 Layered Warping with** _α_ **Depth Representation** 

Previous stereo conversion approaches often employ techniques like softmax splatting [25] for view transformation [23, 36, 50, 55]. To support the layered representation of _α_ Depth, we extend the softmax splatting to first jointly project the foreground layer with premultiplied alpha, _i.e._ , 



where Project( _·_ ) represents depth-guided softmax splatting [23] to handle occlusions. The joint projection ensures that _α_ ˜ aligns with the foreground color _I_<sup>˜</sup> FG. We then separately project the background layer 



Finally, we generate the warped view _I_<sup>˜</sup> via alpha compositing on soft boundary regions: 



Since our _α_ Depth model only estimates layered information for soft boundary regions, with zero _α_ ˜ for opaque regions, Eq. (8) performs alpha composition only on soft boundaries. Thus, the warped image _I_<sup>˜</sup> preserves the 

13 

geometry estimated from state-of-the-art depth models [42, 40, 18], while recovering high-fidelity structures on soft boundaries. 

### **A.2 Matting Evaluation Details** 

We provide more details for the matting evaluation protocol used in Sec. 4.3. Since our _α_ Depth representation uses zero to represent opaque regions without differentiating foreground or background, directly computing alpha metrics cannot reflect our detail extraction performance on soft boundary regions. Thus, we first apply circular alpha encoding (Eq. (2)) to project ground-truth alpha labels and the alpha estimation results of all baselines into the continuous trigonometric space. This maps the foreground ( _α_ = 1) and background ( _α_ = 0) to the same coordinate (0 _,_ 1) in the ( _α_ sin _, α_ cos) space, benefiting the evaluation on soft boundary regions. Then, we compute alpha metrics on the trigonometric space, _i.e._ , 



where (ˆ _α_ sin _,_ ˆ _α_ cos) and ( _α_ sin _, α_ cos) represent the estimated result and ground-truth label, respectively. SAD( _·_ ) _,_ Grad( _·_ ) _,_ Conn( _·_ ) indicate the commonly used Sum of Absolute Differences (SAD), Gradient loss (Grad), and Connectivity loss (Conn) [48]. We also follow ViTMatte to only compute the metrics on the unknown regions of the official trimap in the matting datasets [48]. 

For the input guidance to matting baselines, we employ the official trimaps for the trimap-based method ViTMatte [48]. The recent approach MatAnyone 2 requires binary segmentation masks as guidance, which are not available in AIM-500 [16] and P3M-10K [15]. Thus, we generate binary masks by thresholding the ground-truth alpha maps, _i.e._ , I(0 _._ 5 _≤ α_ ). Compared with previous methods, our _α_ Depth model directly infers soft boundary regions from image semantics and geometry layout, achieving comparable matting performance (see Tab. 3) without requiring manual guidance. 

### **A.3 Training Data Curation** 

We provide more implementation details in training data curation (Fig. 6). Given the original foreground image _I_ FG<sup>ori(unpremultiplied,</sup><sup>_i.e._, not mixed with background colors) from matting datasets and the original background</sup> image _I_ BG<sup>orifrom image datasets, we first apply alpha composition to generate the input image,</sup> 



For the ground-truth layered color _I_ FG _, I_ BG, we perform masked blending based on the binary foreground and background masks _M_ FG = I( _α ≥ α_ th) _, M_ BG = I( _α ≥_ 1 _− α_ th), _i.e._ , 



Regarding depth data generation, we first follow HairGuard to obtain high-quality depth _D_ FG<sup>ori</sup><sup>_, D_</sup> BG<sup>oriusing</sup> pre-trained depth models, and then generate the input depth map _D_ IN via depth composition [55]. For the groundtruth depth labels _D_ FG _, D_ BG, we perform masked blending based on the same foreground and background masks _M_ FG _, M_ BG, _i.e._ , 



As shown in Fig. 6, the generated _I_ FG _/D_ FG and _I_ BG _/D_ BG preserve foreground and background information on soft boundary regions, respectively. 

### **A.4 Matting Loss** _L_ m 

To enhance the detail extraction performance of _α_ Depth, we adopt the matting loss _L_ m introduced in ViTMatte [48]. Specifically, _L_ m is composed of three terms: 



where _Llap_ , and _Lgp_ denote the Laplacian loss [21] and the gradient loss [5], respectively. Since this matting loss is designed for single-channel data ( _e.g._ , alpha mattes), it can be directly applied to supervise our depth predictions. For the foreground and background color outputs, we compute _L_ m independently across each color channel and average the results. 

14 

Table 5: **Pixel-level metrics on full image** . The best and second best results are marked. 

|**Method**|**Mono2St**|**ereo[50]**|**Marvel-**|**10K[55]**|
|---|---|---|---|---|
||PSNR_↑_|SSIM_↑_|PSNR_↑_|SSIM_↑_|
|**Stereo Conversion**|||||
|StereoDiffusion [38]|26.04|0.7656|26.34|0.7541|
|Mono2Stereo [50]|28.19|0.8132|28.15|0.7980|
|StereoCrafter [56]|29.27|0.8340|28.06|0.7855|
|SplatDiff [54]|32.37|0.9284|30.40|0.8909|
|HairGuard [55]|33.09|0.9316|30.88|0.8911|
|_α_**Depth (Ours)**|33.31|0.9326|31.03|0.8942|
|**Warping Peformance**|||||
|DAv2 [45] / VDA [3]|29.35|0.8888|27.04|0.9055|
|DAv2 / VDA + HairGuard [55]|29.35|0.8889|27.06|0.9068|
|**DAv2 / VDA +**_α_**Depth (Ours)**|29.38|0.8891|27.38|0.9094|



Table 6: **Number of parameters for each component in** _α_ **Depth network.** 

|**Dual-Path Encoder**|**M**|**ulti-Branch Decod**|**er**|**Ttl**|
|---|---|---|---|---|
|Detail Encoder<br>Semantic Encoder|Alpha Decoder|Color Decoder|Depth Decoder|**oa**|
|1.17 M<br>319.46 M|2.65 M|2.65 M|2.65 M|328.58 M|



## **B More Experimental Results** 

### **B.1 Pixel-Level Metrics on Full Image** 

Following the experimental settings in Tabs. 1 and 2, we additionally provide pixel-level metrics computed on the full image. Tab. 5 verifies the state-of-the-art performance of _α_ Depth in both warping and stereo conversion. 

### **B.2 Computational Complexity** 

Tab. 6 breaks down the number of parameters for each component of our _α_ Depth network. Additionally, for an input size of 448 _×_ 640, the model requires 607.87 MB of peak GPU memory and achieves an inference speed of 0.0153 seconds per image on an NVIDIA GeForce RTX 4090 GPU. 

### **B.3 Vanilla Alpha Representation** **_v.s._ Circular Alpha Representation** 

Due to the discontinuity in alpha labels ( _e.g._ , see the left part of Fig. 5), learning to predict vanilla alpha representation in complex scenes often suffer from alpha valley issues (Fig. 3b), resulting in inaccurate alpha estimation. To verify this, we employ the _α_ Depth network and train a variant model for vanilla alpha prediction under the same training settings. Fig. 9 compares the performance of vanilla alpha representation and our Circular Alpha Representation (CAR) under video inputs. It is evident that vanilla alpha representation often struggles at the intersections of multiple foreground targets, leading to unstable performance. In contrast, by focusing on local soft boundaries, our CAR achieves remarkable temporal consistency despite relying on an image-based model. 

### **B.4 Matting Performance under Different Depth Inputs** 

Depth estimation performance is essential for high-quality stereo conversion because it directly influences geometry and parallax of the synthesized views. Since our _α_ Depth focuses on soft boundary decomposition without modifying the original geometry and texture in the opaque regions, the pre-trained _α_ Depth model can be integrated with state-of-the-art depth methods in a plug-and-play manner. Tab. 7 shows that our _α_ Depth achieves comparable performance when using depth maps from different depth models. Despite the different depth characteristics, our _α_ Depth shows stable and consistent performance in capturing soft boundary details, even in regions where the depth model fails ( _e.g._ , see little dandelions in Fig. 10). This is because our _α_ Depth leverages both image semantics and geometry layouts for soft boundary decomposition, achieving robust performance. 

### **B.5 Performance under Different Camera Trajectories** 

We test the performance of our _α_ Depth under different camera trajectories with larger viewpoint changes. Two categories of camera motions are employed: (i) We first apply a horizontal swing motion to simulate different baseline lengths in stereo conversion settings. (ii) For more flexible camera motion, we follow ReCamMaster [1] 

15 



























































































































<!-- Start of picture text -->
Input Video Vanilla Alpha CAR (Ours) Input Video Vanilla Alpha CAR (Ours)<br><!-- End of picture text -->

Figure 9: **Stability comparisons** between vanilla alpha representation and circular alpha representation (CAR). Vanilla alpha representation often suffers from alpha valley issues and thus produces unstable results. By contrast, our CAR shows consistent performance when processing video inputs. Regions outside _α ∈_ [0 _._ 02 _,_ 0 _._ 98] are masked out for better comparison. 

to test the robustness of our _α_ Depth method with 10 types of different trajectories. Tab. 8 verifies the state-ofthe-art performance of _α_ Depth under different camera motions. Existing depth models often struggle at soft boundaries due to depth ambiguity, leading to broken structures at soft boundary regions. Although the recent approach HairGuard [55] refines depth to capture soft boundary details, the improved warping still suffers from background bleeding artifacts, as illustrated in Fig. 11. By decomposing soft boundaries via _α_ Depth, our method achieves the best performance in soft boundary preservation. 

## **C More Ablation Studies** 

### **C.1 Impact of Multi-Branch Decoder** 

As shown in Fig. 4, we employ a multi-branch decoder to estimate different modalities, _i.e._ , alpha, depth, and color, in our _α_ Depth representation. This benefits the network by explicitly decoupling the distinct structural and textural characteristics of each modality, preventing feature interference during task-specific predictions. To verify this, we train an additional variant to directly estimate _α_ Depth representation via a unified decoder. 

16 



<!-- Start of picture text -->
Depth Input Depth Input Depth Input Depth Input<br>- (DAv2 [45]) (DPro [2]) (PPD [42]) (MoGe-2 [40])<br>i}i}i}i}<br>Input Image 4aad f 4ntf 4edf 4alf<br>Alpha Alpha Alpha Alpha<br>(+ DAv2 [45]) (+ DPro [2]) (+ PPD [42]) (+ MoGe-2 [40])<br>“a”"_@. a<br>Depth Input Depth Input Depth Input Depth Input<br>(DAv2 [45]) (DPro [2]) (PPD [42]) (MoGe-2 [40])<br>Input Image aa - \ ‘-_ \ -_ \ jf ~ \<br>} } } }<br>Alpha Alpha Alpha Alpha<br>(+ DAv2 [45]) (+ DPro [2]) (+ PPD [42]) (+ MoGe-2 [40])<br><!-- End of picture text -->

Figure 10: **Alpha estimation performance** under different depth inputs. We generate input depth using state-of-the-art models, including Depth Anything V2 (DAv2) [45], Depth Pro (DPro) [2], Pixel-Perfect Depth (PPD) [42], and MoGe-2 [40]. Despite different characteristics exhibited in depth inputs, our _α_ Depth shows stable performance in alpha estimation and soft boundary detail extraction. 

Table 7: **Matting performance of** _α_ **Depth** with different depth models. The best and second best results are marked. 

|**Deth Model**||**AIM-500**|||**P3M-10**|**K**|
|---|---|---|---|---|---|---|
|**p **|SAD_↓_|Grad_↓_|Conn_↓_|SAD_↓_|Grad_↓_|Conn_↓_|
|Depth Anything V2 [45]|7.24|20.20|3.89|4.09|11.88|2.31|
|Depth Pro [2]|7.22|20.35|3.88|4.15|12.20|2.34|
|MoGe-2 [40]|7.34|21.09|3.95|4.19|12.47|2.36|
|Pixel-Perfect Depth [42]|7.37|20.76|3.95|4.18|12.24|2.36|



As demonstrated in Tab. 9, removing the multi-branch decoder leads to a consistent drop in alpha matting performance across all metrics. Specifically, the full model with the multi-branch decoder improves the SAD metric from 8.22 to 7.24 on the AIM-500 dataset [16], and from 4.36 to 4.09 on the P3M-10K dataset [15], validating its effectiveness in accurately extracting soft boundary details. 

### **C.2 Impact of Semantic Encoder** 

In the proposed _α_ Depth network, we employ a semantic encoder to extract high-level semantics and a detail encoder to capture soft boundary details (Fig. 4). The semantic encoder leverages pre-trained image priors to extract deep semantic features, which are essential for high-level soft boundary reasoning. Tab. 10 presents the ablation study of the semantic encoder on the Marvel-10K dataset [55], following the same experimental setups in Tab. 4a. Removing the semantic encoder results in a noticeable performance drop in warping performance, with S-PSNR decreasing from 28.68 to 27.35 and S-SSIM dropping from 0.7636 to 0.7147. This degradation 

17 



<!-- Start of picture text -->
Frame#1 Frame#2 Frame#3<br>(Original [45]) (Original [45]) (Original [45])<br>Input Image<br>Frame#1 Frame#2 Frame#3<br>(+ HairGuard [55]) (+ HairGuard [55]) (+ HairGuard [55])<br>Camera Motion<br>Frame#1 Frame#2 Frame#3<br>(+ Ours) (+ Ours) (+ Ours)<br><!-- End of picture text -->

Figure 11: **Warping performance under large viewpoint changes** . This example employs the camera motion (arc left with rotation) from ReCamMaster [1]. Due to depth ambiguity in soft boundary regions, the warping results using the original depth from Depth Anything V2 [45] often contain broken structures. Although HairGuard refines depth to better preserve soft boundary details [55], its results often suffer from background bleeding. The proposed _α_ Depth achieves the best warping performance with high-fidelity soft boundary details. 

Table 8: **Warping performance (FID** _↓_ **)** under different camera trajectories on natural image matting datasets. We apply horizontal swing motion to simulate different baseline lengths in stereo conversion. We also employ 10 different camera trajectories from the evaluation protocol of ReCamMaster [1] to compare the warping performance under larger and more flexible viewpoint changes. The best and second best results are marked. 

|**Method**|**A**|**IM-500**|**P3**|**M-10K**|
|---|---|---|---|---|
||Horizontal Swing|ReCamMaster Motion|Horizontal Swing|ReCamMaster Motion|
|DAv2 [45]|41.75|36.99|49.50|48.47|
|DAv2 + HairGuard [55]|38.49|36.00|45.71|47.17|
|**DAv2 +**_α_**Depth (Ours)**|34.43|34.26|35.47|43.58|



indicates that high-level contextual cues and semantic understanding are vital for the network to resolve depth ambiguity and correctly decompose soft boundaries in complex scenes. 

### **C.3 Impact of Depth Edge Extraction** 

Depth edge extraction provides explicit geometric priors by extracting depth gradients from the input depth map, which serves as strong cues for soft boundary localization (Fig. 4). We empirically found that depth edges are crucial for the convergence of the network during training. Removing this component can lead to training instability or even divergence. This is likely because depth edges provide a strong initialization for soft boundary localization and thus alleviate the difficulty of multi-task learning. As shown in Tab 10, omitting the edge extraction module severely impacts the warping performance, leading to a 2.54 dB drop in S-PSNR. This emphasizes the necessity of explicit boundary cues in guiding the network to focus on soft boundary regions. 

18 

Table 9: **Ablation of multi-branch decoder** on matting datasets. The best results are marked. 

|**Method**|SAD_↓_|**AIM-500**<br>Grad_↓_|Conn_↓_|SAD_↓_|**P3M-10K**<br>Grad_↓_|Conn_↓_|
|---|---|---|---|---|---|---|
|w/o Multi-Branch Decoder|8.22|25.95|4.55|4.36|14.05|2.51|
|**w/ Multi-Branch Decoder (Ours)**|7.24|20.20|3.89|4.09|11.88|2.31|



Table 10: **Ablation of edge extraction and semantic encoder** on Marvel-10K [55]. The best and second best results are marked. 

|**Method**|S-PSNR_↑_|**Marvel-**<br>S-SSIM_↑_|**10K**<br>LPIPS_↓_|DISTS_↓_|
|---|---|---|---|---|
|w/o Edge Extraction|26.14|0.6718|0.1337|0.0910|
|w/o Semantic Encoder|27.35|0.7147|0.1269|0.0839|
|**Full Model (Ours)**|28.68|0.7636|0.1190|0.0738|



## **D Limitations and Discussions** 

Although _α_ Depth effectively resolves soft boundaries in stereo conversion, some limitations remain: 

**Dependence on Initial Depth Maps** . Our method adopts a plug-and-play design that can be integrated with various state-of-the-art monocular depth estimation models. Although _α_ Depth effectively decomposes local foreground and background at soft boundary regions, the global scene structure and scale remain heavily dependent on the quality of the initial input depth map. If the underlying depth model fails in extreme scenarios ( _e.g._ , severe geometric distortions), our approach may struggle to fully correct the errors in the base geometry. To address this issue, future research could explore end-to-end joint optimization strategies by integrating our module with foundational depth models. This would allow the explicit boundary priors extracted by _α_ Depth to back-propagate and iteratively correct global geometric distortions. Alternatively, introducing a confidenceaware fusion mechanism could enable the network to selectively rely on deep image semantics when the input depth exhibits low reliability. 

**Two-Layer Representation** . Our approach models local soft boundaries based on the observation that a twolayer decomposition (foreground and background) is generally sufficient to resolve local occlusions. However, in some complex scenes where multiple semi-transparent boundaries overlap at the same pixel ( _i.e._ , three or more overlapping layers), the current two-layer model might not fully capture all layered information. In future works, extending our framework to support an arbitrary number of overlapping layers presents an exciting avenue. This could be achieved through an iterative layer-peeling mechanism, where foreground layers are sequentially stripped away. Furthermore, integrating local volumetric representations ( _e.g._ , localized radiance fields) at intersecting boundaries could model complex multi-layer semi-transparencies. 

**Video Consistency** . Although the proposed Circular Alpha Representation (CAR) demonstrates remarkable temporal consistency when processing video inputs ( _e.g._ , see Fig. 9), the current _α_ Depth framework operates fundamentally as an image-based model. Due to the lack of explicit temporal constraints, _α_ Depth may produce results with flickering artifacts, especially in dynamic scenes where depth changes rapidly. Specifically, because _α_ Depth prioritizes capturing soft boundaries at depth discontinuities, it may fail to resolve boundaries at low depth gradients ( _e.g._ , when two targets move close together in depth). Future extensions of this work could explore integrating spatio-temporal modules, _e.g._ , spatio-temporal attention, to further stabilize the layered predictions across video sequences. 

## **E Discussion of Societal Impacts** 

Our work on high-fidelity stereo conversion presents several positive societal impacts, primarily by democratizing the creation of immersive 3D content. By automating soft boundary decomposition in complex scenes, our _α_ Depth framework significantly lowers the barrier for creators in the Virtual and Augmented Reality (VR/AR), immersive education, and entertainment industries. This enables the efficient and low-cost transformation of legacy monocular media into engaging 3D experiences. However, we also acknowledge potential negative impacts associated with this technology. The ability to synthesize highly realistic stereo views could be misused to create immersive 3D disinformation, making fabricated content appear more physically credible. Additionally, the unauthorized stereo conversion of individuals or private scenes from casually captured 2D photos could raise privacy concerns. 

19 













<!-- Start of picture text -->
Input Image Model A#1 Model A#2 Model A#3 Model A#4<br>Input Image Model B#1 Model B#2 Model B#3 Model B#4<br><!-- End of picture text -->

Figure 12: **Visual comparisons of ablation models in Tab. 4.** 

## **F Visualization of Ablation Models** 

Fig. 12 provides qualitative results for the ablation models detailed in Tab. 4. Due to depth ambiguity at soft boundaries, the baseline model (A#1) often generates warped images exhibiting broken boundaries and flying pixels. Although incorporating alpha estimation improves the structure of soft boundaries, the alpha valley issue inherent to the vanilla alpha representation tends to degrade warping performance ( _e.g._ , see the bottom region of A#2 in Fig. 12). By contrast, the proposed circular alpha representation circumvents this issue, effectively preserving image structures and soft boundary details (A#3). Finally, when combined with the layered representation, our _α_ Depth faithfully recovers background information at soft boundaries, achieving the best warping performance (A#4). 

Furthermore, the bottom row of Fig. 12 illustrates the qualitative impacts of the different alpha matting strategies evaluated in Tab. 4b. When employing the vanilla alpha representation (B#1), the network suffers from the alpha valley issue, which leads to unstable predictions and noticeable artifacts when extracting complex structures. Relying solely on the _L_ 1 loss without the matting loss _L_ m (B#2) fails to adequately capture fine-grained details, resulting in blurred and degraded soft boundaries. Similarly, utilizing single-stage training without the subsequent global refinement (B#3) yields noisy alpha predictions. By contrast, our full model (B#4) effectively overcomes these limitations and extracts intricate soft boundary details. 

## **G Visualization of** _α_ **Depth Results** 

Fig. 13 illustrates the results estimated by _α_ Depth in typical stereo conversion scenarios. Our method demonstrates robust performance even in complex scenes, such as dark environments (top example) and highly dynamic multi-target situations (middle example), highlighting its practical value for real-world applications. 

## **H More Visual Comparisons** 

### **H.1 Stereo Conversion** 

In Figs. 14 and 15, we present additional qualitative comparisons evaluating warping and stereo conversion performance. When utilizing original depth maps estimated from Video Depth Anything [3], direct view transformation techniques struggle with the depth ambiguity at soft boundaries, frequently resulting in broken edges and flying pixels. While recent refinement approaches like HairGuard [55] capture finer boundary details, their reliance on a single-layer depth representation still leads to visible background bleeding and aliasing artifacts during warping. Furthermore, when comparing final stereo conversion results, existing state-of-the-art methods often struggle to maintain structural consistency at these intricate boundaries. In contrast, our _α_ Depth framework explicitly addresses these limitations by employing a layered representation that decouples soft boundaries into local foreground and background. By disentangling the mixed colors and resolving depth ambiguities, our method achieves superior fidelity in warping and stereo conversion results. 

### **H.2 Alpha Matting** 

Fig. 16 provides further visual comparisons of our Circular Alpha Representation (CAR) against state-of-the-art alpha matting baselines, including GVM [8], MatAnyone 2 [46], and ViTMatte [48]. Conventional matting techniques generally rely on explicit global definitions of foreground and background, necessitating manual guidance such as user-provided trimaps ( _e.g._ , ViTMatte [48]) or segmentation masks ( _e.g._ , MatAnyone 2 [46]) 

20 











<!-- Start of picture text -->
Input Image  I IN Alpha α ˆ Background Depth D ˆ BG Background Color I ˆ BG<br>Input Depth  D IN Soft Boundary Region S ˆ Foreground Depth D ˆ FG Foreground Color I ˆ FG<br>Input Image  I IN Alpha α ˆ Background Depth D ˆ BG Background Color I ˆ BG<br>Input Depth  D IN Soft Boundary Region S ˆ Foreground Depth D ˆ FG Foreground Color I ˆ FG<br>Input Image  I IN Alpha α ˆ Background Depth D ˆ BG Background Color I ˆ BG<br>Input Depth  D IN Soft Boundary Region S ˆ Foreground Depth D ˆ FG Foreground Color I ˆ FG<br><!-- End of picture text -->

Figure 13: **Visualization of** _α_ **Depth results** on Marvel-10K dataset [55]. 

for instance-level inference. While auxiliary-free methods like GVM [8] reduce user effort, they are typically optimized for specific semantic categories and struggle to generalize to the diverse types of soft boundaries in complex scenes. As demonstrated in Fig. 16, our approach achieves comparable performance in extracting intricate soft boundary details with state-of-the-art matting methods, without any user intervention. 

21 











<!-- Start of picture text -->
Input Image VDA Warping [3] HairGuard Warping [55] α Depth Warping (Ours)<br>Input Depth StereoCrafter Result [56] HairGuard Result [55] α Depth Result (Ours)<br>Input Image VDA Warping [3] HairGuard Warping [55] α Depth Warping (Ours)<br>i Li i Z Li? Lu SH L<br>Input Depth StereoCrafter Result [56] HairGuard Result [55] α Depth Result (Ours)<br>Input Image VDA Warping [3] HairGuard Warping [55] α Depth Warping (Ours)<br>Input Depth StereoCrafter Result [56] HairGuard Result [55] α Depth Result (Ours)<br>i p p ? | 7<br>‘ti ‘k * iz<br>Input Image VDA Warping [3] HairGuard Warping [55] α Depth Warping (Ours)<br>i )<br>“h4 ‘i<br>mM 1<br>Input Depth StereoCrafter Result [56] HairGuard Result [55] α Depth Result (Ours)<br><!-- End of picture text -->

Figure 14: **Visual comparisons** in warping and stereo conversion, part one. 

22 











<!-- Start of picture text -->
Input Image VDA Warping [3] HairGuard Warping [55] α Depth Warping (Ours)<br>Input Depth StereoCrafter Result [56] HairGuard Result [55] α Depth Result (Ours)<br>Input Image VDA Warping [3] HairGuard Warping [55] α Depth Warping (Ours)<br>Input Depth StereoCrafter Result [56] HairGuard Result [55] α Depth Result (Ours)<br>Input Image VDA Warping [3] HairGuard Warping [55] α Depth Warping (Ours)<br>Input Depth StereoCrafter Result [56] HairGuard Result [55] α Depth Result (Ours)<br>Input Image VDA Warping [3] HairGuard Warping [55] α Depth Warping (Ours)<br>Input Depth StereoCrafter Result [56] HairGuard Result [55] α Depth Result (Ours)<br><!-- End of picture text -->

Figure 15: **Visual comparisons** in warping and stereo conversion, part two. 

23 















<!-- Start of picture text -->
W<br><!-- End of picture text -->











<!-- Start of picture text -->
0<br><!-- End of picture text -->





















<!-- Start of picture text -->
ee<br><!-- End of picture text -->









<!-- Start of picture text -->
M e ore tt aW re AALS. Ua r tVa o t e<br>ak B e B k e e e<br>ok<br>Input Image GVM [8] MatAnyone 2 [46] ViTMatte [48] α Depth (Ours)<br>w t o t a e<br>Figure 16: Visual comparisons with alpha matting methods.<br><!-- End of picture text -->

24 

