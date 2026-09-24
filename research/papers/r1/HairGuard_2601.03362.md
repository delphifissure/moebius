# Guardians of the Hair: Rescuing Soft Boundaries in Depth, Stereo, and Novel Views

Xiang Zhang<sup>1,2</sup> Yang Zhang<sup>2</sup> Lukas Mehl<sup>2</sup> Markus Gross<sup>1,2</sup> Christopher Schroers<sup>2</sup>  
<sup>1</sup>ETH Zürich <sup>2</sup>DisneyResearch|Studios

Figure 1. **Our Mission.** The Guardians of the Hair (**HairGuard**) aim to rescue soft boundary details, *e.g.*, thin hairs, where foreground and background are mixed in the observed color. Previous state-of-the-art approaches often suffer from missing details (see depth estimation results), degraded texture (see stereo results, displayed in anaglyph), and inconsistent geometry (see novel views) in soft boundaries. In contrast, HairGuard preserves fine-grained soft boundary details and demonstrates strong performance across diverse tasks.

## Abstract

Soft boundaries, like thin hairs, are commonly observed in natural and computer-generated imagery, but they remain challenging for 3D vision due to the ambiguous mixing of foreground and background cues. This paper introduces **Guardians of the Hair (HairGuard)**, a framework designed to recover fine-grained soft boundary details in 3D vision tasks. Specifically, we first propose a novel data curation pipeline that leverages image matting datasets for training and design a depth fixer network to automatically identify soft boundary regions. With a gated residual module, the depth fixer refines depth precisely around soft boundaries while maintaining global depth quality, allowing plug-and-play integration with state-of-the-art depth models. For view synthesis, we perform depth-based forward warping

to retain high-fidelity textures, followed by a generative scene painter that fills disoccluded regions and eliminates redundant background artifacts within soft boundaries. Finally, a color fuser adaptively combines warped and inpainted results to produce novel views with consistent geometry and fine-grained details. Extensive experiments demonstrate that HairGuard achieves state-of-the-art performance across monocular depth estimation, stereo image/video conversion, and novel view synthesis, with significant improvements in soft boundary regions.

## 1. Introduction

Driven by recent advances in foundation models and large-scale visual datasets [47, 51], significant progress has been witnessed in the field of 3D vision, including depth es-Figure 2. **Soft boundaries.** Existing depth estimation methods often struggle to capture accurate depth in soft boundaries, resulting in discontinuous depth (red box) and broken boundaries (green box). DAv2, DPro, and UDv2 represent Depth Anything V2 [70], Depth Pro [4], and UniDepthV2 [41], respectively.

timations [23, 45, 69, 80], stereo conversion [59, 76, 82], and novel view synthesis [2, 77, 81]. These techniques play a crucial role in understanding and reconstructing 3D scenes, with broad applications in robotics, autonomous driving, augmented/virtual reality (AR/VR), and film production [1, 13, 31, 36, 61]. Although existing methods have shown promising performance in general scenarios [2, 69], generating geometrically consistent and visually realistic results in scenes with soft boundaries, *e.g.*, hairs and thin structures, remains highly challenging (Fig. 1).

Soft boundaries are ubiquitous and often arise when pixels receive mixed contributions from both the foreground and background, due to thin/semi-transparent structures or alpha blending in rendering [30, 71]. Thus, they are commonly observed in natural images like shots containing animals and humans, as well as computer-generated imagery such as Fig. 1. The mixture of foreground and background pixels makes pixel-wise 3D estimation particularly challenging and ill-posed, since such regions exhibit uncertain correspondence and depth ambiguity.

Existing methods often struggle to capture accurate and fine-grained soft boundaries, as illustrated in Fig. 1. For example, the state-of-the-art monocular depth estimation method Depth Anything V2 [70] fails to extract the fine details of hairs and produces broken depth results (Fig. 1 and Fig. 2). Although the recent approach Depth Pro [4] achieves improved detail preservation in depth estimation, the estimated depth around soft boundaries often falls behind the true surface, leading to detached hairs as shown in the point cloud renders of Fig. 2 (red box). Since depth

estimation is often required by *explicit* 3D vision methods [76, 77, 81], the depth errors tend to propagate to the subsequent stages, resulting in sub-optimal performance. In the field of stereo conversion and novel view synthesis, one emerging trend is to generate new viewpoints in an *implicit* manner without depth [2, 13, 74]. By utilizing the rich prior knowledge learned in foundation generative models [47, 58], these implicit approaches can effectively handle complex occlusion and geometry in 3D world. However, due to the generative nature of the underlying foundation models, implicit 3D vision methods often suffer from hallucination issues and thus generate inconsistent texture details in soft boundaries (*e.g.*, see ReCamMaster [2] in Fig. 1). Meanwhile, most foundation generative models are designed in the latent space for computational efficiency [47, 58, 65]. Such a design often results in texture degradation due to pixel-to-latent compression [81], as illustrated by the StereoCrafter [82] results in Fig. 1.

In the realm of 2D vision, image matting provides an explicit formulation for soft boundaries by estimating an opacity map (*i.e.*, alpha matte) to model the pixel mixture along the transition between foreground and background [30, 71]. Inspired by the matting formulation, we leverage image matting datasets to improve soft boundary modeling and propose **Guardians of the Hair (HairGuard)** to rescue soft boundary details in 3D tasks. Specifically, HairGuard consists of three teammates: *depth fixer*, *scene painter*, and *color fuser*. By utilizing matting datasets in training data curation, our depth fixer learns to identify soft boundary regions and correct depth predictions with a gated residual module. This design not only enables precise depth refinement over soft boundaries, but also supports plug-and-play integration with zero-shot depth models for robust performance. For view synthesis, we first perform forward warping using the fixed depth, followed by a generative scene painter that synthesizes realistic disoccluded regions and corrects geometric errors caused by warping. Finally, to address texture hallucination and detail compression in generative models, we propose a color fuser to preserve fine-grained details and ensure geometrically consistent view synthesis via a dual skip module. As shown in Fig. 1, the components of HairGuard work collaboratively to achieve remarkable performance across different 3D vision tasks.

In a nutshell, our main contributions are three-fold:

- • We present HairGuard to capture, model, and reconstruct fine-grained soft boundary details in 3D vision tasks. Extensive experiments verify the effectiveness and superiority of HairGuard across monocular depth estimation, stereo image/video conversion, and novel view synthesis.
- • We design novel data curation strategies to leverage image matting datasets for training, enabling HairGuard to automatically identify and fix soft boundaries without relying on manually crafted cues, *e.g.*, trimaps [30, 71].- • We propose a depth fixer with a gated residual module, which enables precise depth refinement in soft boundary regions for plug-and-play enhancement. Additionally, we design a dual skip architecture in the color fuser to ensure geometrically consistent and high-quality view synthesis.

## 2. Related Work

### 2.1. Monocular Depth Estimation

Monocular depth estimation aims to infer scene geometry from a single image [7, 8, 20, 40, 46, 72, 73, 78], a fundamentally ill-posed problem due to the loss of depth cues during projection. To achieve zero-shot depth estimation, early attempts employ mixed training datasets to obtain a strong geometric prior of the scene [45, 46, 69]. Marigold also proposes to utilize the rich prior knowledge in generative foundation models, *e.g.*, Stable Diffusion [47], to efficiently approach zero-shot estimation [23]. Recently, several approaches have been proposed to improve the details of depth maps [4, 70, 80]. For example, Depth Anything V2 exploits high-quality depth supervision in synthetic datasets and learns to extract fine details from input images [70]. Meanwhile, Depth Pro designs a training protocol to combine real and synthetic datasets for metric depth estimation and fine boundary preservation. The recent approach UniDepthV2 also proposes an edge-guided loss to improve the sharpness of edges in the depth output [41]. Despite these advances, existing methods still struggle in soft boundary regions, often producing missing or discontinuous depth estimates. In contrast, our HairGuard precisely localizes soft boundaries and reconstructs fine-grained depth details, as shown in Fig. 2.

### 2.2. Stereo Conversion

The goal of stereo conversion is to generate right-view images/videos from left-view inputs [10, 36, 60, 64, 76], which has gained increasing attention due to its practical application in 3D video production and immersive media. With the rapid progress of generative foundation models [3, 47, 58], an emerging trend is to utilize learned generative and geometry priors for stereo conversion [15, 53, 76, 82]. For image-based conversion, StereoDiffusion introduces a training-free latent modification strategy using Stable Diffusion [59], and Mono2Stereo designs dual conditioning and edge-consistency losses to enhance stereo quality [76]. Recently, an increasing number of works have focused on leveraging video generative models for stereo video conversion [15, 53, 82]. For instance, StereoCrafter designs a tiled diffusion strategy to generate stereoscopic videos from high-resolution and long video inputs [82]. Based on Stable Video Diffusion [3], M2SVid devises a spatio-temporal aggregation mechanism to leverage information from neighboring frames and achieves high-quality inpainting perfor-

Figure 3. **HairGuard pipeline.** Given an input image and its estimated depth, we first design a depth fixer to refine depth predictions around soft boundary regions. The fixed depth is then used for forward warping to generate preliminary novel views, which are fed into the scene painter for disocclusion inpainting. Finally, our color fuser adaptively combines the warped and inpainted results to produce geometrically and visually consistent novel views.

mance [53]. Eye2Eye [15] further synthesizes stereo videos without explicit depth projection, effectively handling specular and transparent surfaces using video diffusion priors. However, due to the generative nature of diffusion models, current stereo conversion approaches often suffer from texture hallucination and loss of fine details, as shown in Fig. 1. To overcome these limitations, a color fuser network is designed in HairGuard to recover high-fidelity texture details.

### 2.3. Novel View Synthesis

Novel view synthesis has attracted considerable interest in computer vision community for its ability to render photo-realistic images from novel viewpoints [21, 24, 37, 55, 62, 63, 74, 77]. A popular trend is to perform 3D scene reconstruction from input images for novel view synthesis, such as Multi-Plane Image (MPI) [17, 27, 56], Neural Radiance Field (NeRF) [37, 75], and 3D Gaussian Splatting (3DGS) [24, 54, 67]. More recently, diffusion-based approaches have emerged as a powerful alternative, leveraging generative priors to produce high-fidelity novel views without requiring explicit 3D reconstruction [5, 16, 34, 49, 52, 83]. For example, ReCamMaster introduces frame-dimension conditioning to enhance view consistency in video diffusion models [2], but its results often suffer from texture inconsistency due to diffusion hallucination (*e.g.*, see Fig. 1). Another recent work, SplatDiff, integrates depth-guided pixel splatting with diffusion models to achieve high-fidelity view synthesis [81]. However, its performance is highly dependent on the quality of depth, which often contains errors around soft boundaries (Fig. 2). By comparison, our HairGuard combines a depth fixer and a color fuser to jointly correct depth inaccuracies and restore fine-grained texture details, achieving geometrically consistent and photo-realistic novel views (Fig. 1).

## 3. HairGuard

Following the formulation in image matting [30, 71], the observed image  $I$  can be expressed as an alpha compositionbetween the foreground  $I_{FG}$  and the background  $I_{BG}$ , *i.e.*,

$$I = \alpha \cdot I_{FG} + (1 - \alpha) \cdot I_{BG}, \quad (1)$$

where  $\alpha \in [0, 1]$  denotes the opacity map (alpha matte). Soft boundaries can be defined as regions with mixed foreground and background pixels, *i.e.*,  $\alpha \in (0, 1)$ , posing ambiguity in depth and color correspondence. To handle these challenging areas in depth estimation (Sec. 3.1), we design a depth fixer to automatically localize soft boundaries and refine depth predictions, as shown in Fig. 3. For view synthesis tasks (Sec. 3.2), we first perform forward warping based on the fixed depth, and then apply the generative scene painter to fill the unknown regions like disoccluded areas. Finally, our color fuser combines warped and inpainted results for high-quality view synthesis.

### 3.1. Depth Estimation

Given an image and its depth map (*e.g.*, estimation results from Depth Anything V2 [70]), our depth fixer aims to automatically identify soft boundary regions and perform precise depth correction. However, several challenges exist:

- • *High-quality annotation.* Most existing depth datasets focus on scenes with hard boundaries, lacking fine-grained depth annotations around soft boundary regions.
- • *Automatic localization.* Estimation in soft boundaries often relies on hand-crafted cues like trimaps [71], hindering generalization and applicability to complex scenes.
- • *Precise refinement.* Achieving precise depth correction in soft boundary regions without compromising the global depth quality remains an open challenge.

**Dataset Curation.** Collecting large-scale datasets with high-quality depth annotations in soft boundary regions could be time-consuming and impractical. Thus, we address the *high-quality annotation* issue by utilizing the existing image matting datasets, which contain diverse targets with soft boundaries and the corresponding opacity maps (*i.e.*, alpha mattes). As shown in Fig. 4a, we use matting datasets as foreground datasets  $\mathcal{I}_{FG} = \{(\alpha, I_{FG})\}$  and image datasets as background datasets  $\mathcal{I}_{BG} = \{(I_{BG})\}$ . Since alpha mattes usually exhibit smooth transitions in soft boundaries, we first obtain alpha masks  $M_\alpha$  by thresholding  $\alpha$  with  $\alpha_{th}$ , *i.e.*,  $M_\alpha = \{p \mid \alpha_{th} < \alpha(p)\}$ . Then, we generate foreground depth  $d_{FG}$  by

$$d_{FG} = M_\alpha \odot \text{Depth}(I_{FG}), \quad (2)$$

where  $\text{Depth}(\cdot)$  represents depth estimation methods, and a green background is added to  $I_{FG}$  to enhance the contrast in depth estimation. Afterward, we obtain the background depth as  $d_{BG} = \text{Depth}(I_{BG})$  and randomly sample two depth values from  $[d_{min}, d_{max}]$  to rescale  $d_{FG}$  for data augmentation, where  $d_{min} = \max_{p \in M_\alpha} (d_{BG}(p))$  to ensure

(a) Training data curation with matting datasets

(b) Network architecture

(c) Comparisons of output mechanisms and training strategies

Figure 4. **Depth fixer.** (a) We utilize image matting datasets to synthesize training data with fine-grained depth labels in soft boundaries. (b) Instead of relying on manually crafted cues like trimaps [71], we leverage depth maps and image semantics to automatically identify soft boundary regions. The gated residual module enables precise depth correction in soft boundary areas and thus benefits plug-and-play refinement. (c) Compared with direct prediction and vanilla residual, our gated residual combined with two-stage training achieves the best depth results.

correct depth ordering and  $d_{max}$  is a predefined constant. Finally, we blend  $d_{FG}$  and  $d_{BG}$  by depth composition:

$$d = d_{FG} \odot M_\alpha + d_{BG} \odot (1 - M_\alpha). \quad (3)$$

Using Eq. (3), one can create depth training pairs  $\{(d_{in}, d_{GT})\}$  for the depth fixer by varying the threshold$\alpha_{th}$ . A lower  $\alpha_{th}$  is used to generate depth labels  $d_{GT}$  with fine details in soft boundaries, and a higher  $\alpha_{th}$  is used to simulate depth inputs  $d_{in}$  with broken or missing depth in these regions. Additionally, we apply a random Gaussian blur to  $M_\alpha$  when generating  $d_{in}$ , but use the unblurred mask in Eq. (3) to produce  $d_{GT}$  with sharp boundaries.

**Network Design.** As illustrated in Fig. 4b, our depth fixer has two main branches: a feature branch built upon DINOv2 [39] and DPT [46] to extract deep features and image semantics, and a pixel branch based on U-Net [48] to capture local structures and boundary details. To address the *automatic localization* problem, we propose to infer soft boundaries directly from images and depth maps. In particular, we first generate explicit edge guidance  $e$  by applying the Sobel operator to the input depth, *i.e.*,  $e = \text{Sobel}(d_{in})$ , and then concatenate  $e$  with image  $I_{in}$  and depth  $d_{in}$  as inputs to the pixel branch. With this design, our depth fixer is able to focus on the regions with high depth gradients and learn to automatically identify soft boundaries with image semantics and geometric layouts.

For *precise refinement*, we propose a gated residual mechanism to refine depth only in soft boundary regions while preserving global depth quality. Specifically, we first model the soft boundary regions by predicting a gate map  $G \in [0, 1]$ , where  $G < 1$  indicates soft boundary regions. Then, the gated residual is performed to obtain the refined depth  $\hat{d}$ ,

$$\hat{d} = d_{in} \cdot G + d_{res} \cdot (1 - G), \quad (4)$$

where  $d_{res}$  is the estimated depth residual. Compared with the direct prediction of refined depth or vanilla residual approach, our gated residual better preserves sharp and fine-grained details in soft boundaries, as shown in Fig. 4c. Furthermore, the gating mechanism decouples depth estimation and soft-boundary fixing, and thus our depth fixer can be seamlessly integrated with state-of-the-art depth models to achieve robust and detail-preserving performance.

**Model Training.** Directly training the depth fixer using standard depth losses [45] tends to yield a trivial solution where the gate collapses to  $G = 1$ . Hence, we propose a two-stage strategy to learn depth refinement in a local-to-global manner. We first generate a soft boundary mask  $M_{soft}$  by thresholding the ground-truth alpha matte, *i.e.*,  $M_{soft} = \{p \mid \alpha_{min} < \alpha(p) < \alpha_{max}\}$ , with constants  $\alpha_{min}, \alpha_{max}$  determining the soft boundary areas. The learning objective for the first stage  $\mathcal{L}_{depth}^{stage1}$  is defined as

$$\mathcal{L}_{depth}^{stage1} = \mathcal{L}_1(\hat{d}, d_{GT}) + \mathcal{L}_\alpha(\hat{d} \odot M_{soft}, d_{GT} \odot M_{soft}), \quad (5)$$

where  $\mathcal{L}_1$  denotes the  $\ell_1$  loss, and  $\mathcal{L}_\alpha$  is an image matting loss from ViTMatte [71] to facilitate detail extraction. Although  $\mathcal{L}_{depth}^{stage1}$  prevents the trivial solution of  $G = 1$  by imposing stronger penalties on soft boundaries, it often introduces halo artifacts around these regions, as illustrated in

Figure 5 consists of three parts: (a) Training data curation with matting datasets, (b) Network architecture, and (c) Comparisons of warped, inpainted, and fused images.

(a) Training data curation with matting datasets: This part shows the process of generating training data. It starts with a 'FG image' (foreground image) and 'Multi-view images'. These are used for 'Image Composition' to create 'Ground-truth' images. These ground-truth images are then used for 'Inpainting Synthesis' to produce 'Synthesized inpainted images' and for 'Warping Synthesis' to produce 'Synthesized warped images and masks'.

(b) Network architecture: This part shows the architecture of the color fuser. It takes an 'Inpainted image' and a 'Warped image' as inputs. Both are processed by a 'VAE Encoder' to extract 'Deep feature'. These features are then combined in a 'Dual Skip' module, which also takes the 'Warped mask' as input. The output of the Dual Skip module is processed by a 'VAE Decoder' to produce a 'Novel view' image. The 'Novel view' is compared with the 'Ground-truth' image using a color loss  $\mathcal{L}_{color}$ .

(c) Comparisons of warped, inpainted, and fused images: This part shows three images: 'Warped Image', 'Inpainted Image', and 'Fused Image'. The 'Warped Image' has a green box highlighting redundant background colors. The 'Inpainted Image' has a red box highlighting hallucinated textures. The 'Fused Image' shows the result of combining the warped and inpainted images, which eliminates these artifacts.

Figure 5. **Color fuser.** (a) We employ image matting datasets and multi-view datasets to synthesize warped and inpainted results for training. (b) Built upon a pre-trained VAE, we design a dual skip module to leverage the merits of inpainted and warped images. (c) Our color fuser eliminates redundant background colors (green box in the warped image) and hallucinated textures (red box in the inpainted image) for high-quality view synthesis.

Fig. 4c. Thus, in the second stage, we apply the constraint  $\mathcal{L}_\alpha$  globally to improve the overall depth quality, *i.e.*,

$$\mathcal{L}_{depth}^{stage2} = \mathcal{L}_\alpha(\hat{d}, d_{GT}). \quad (6)$$

Fig. 4c shows that our two-stage training achieves fine-grained details while preserving global depth quality.

### 3.2. View Synthesis

For view synthesis, we first perform forward warping based on the fixed depth to preserve fine details and soft boundaries. However, the mixture of foreground and background in soft boundaries often introduces redundant background colors in the warped results (*e.g.*, see the green box in Fig. 5c). Since existing multi-view datasets mainly contain hard boundaries, we propose to model such characteristics by leveraging matting datasets in data curation (Fig. 5a).

**Dataset Curation.** Given a sequence of background images  $\{I_{BG}\}$  from multi-view datasets, we first predict the optical flow  $\{f_{BG}\}$  between all pairs of images via an off-the-shelfTable 1. **Zero-shot depth boundary accuracy** on the natural image matting datasets. Depth fixer can be integrated with different depth models in a plug-and-play manner for soft boundary refinement. **Best** results are marked. Please see the supplementary for more evaluation.

<table border="1">
<thead>
<tr>
<th rowspan="2">Method</th>
<th colspan="4">AIM-500</th>
<th colspan="4">P3M-10K</th>
</tr>
<tr>
<th>DBE_comp ↓</th>
<th>DBE_acc ↓</th>
<th>EP (%) ↑</th>
<th>ER (%) ↑</th>
<th>DBE_comp ↓</th>
<th>DBE_acc ↓</th>
<th>EP (%) ↑</th>
<th>ER (%) ↑</th>
</tr>
</thead>
<tbody>
<tr>
<td>Depth Anything V2 [70]</td>
<td>7.93</td>
<td>3.29</td>
<td>19.90</td>
<td>6.50</td>
<td>7.53</td>
<td>2.60</td>
<td>26.53</td>
<td>9.37</td>
</tr>
<tr>
<td><b>Depth Anything V2+Depth Fixer (Ours)</b></td>
<td><b>7.19</b></td>
<td><b>2.10</b></td>
<td><b>34.56</b></td>
<td><b>13.08</b></td>
<td><b>7.21</b></td>
<td><b>1.93</b></td>
<td><b>36.91</b></td>
<td><b>13.39</b></td>
</tr>
<tr>
<td>Depth Pro [4]</td>
<td>7.75</td>
<td>3.80</td>
<td>15.92</td>
<td>6.12</td>
<td>7.25</td>
<td>3.25</td>
<td>18.36</td>
<td>9.21</td>
</tr>
<tr>
<td><b>Depth Pro+Depth Fixer (Ours)</b></td>
<td><b>6.70</b></td>
<td><b>2.30</b></td>
<td><b>35.01</b></td>
<td><b>17.33</b></td>
<td><b>6.44</b></td>
<td><b>1.78</b></td>
<td><b>37.90</b></td>
<td><b>18.91</b></td>
</tr>
<tr>
<td>UniDepthV2 [41]</td>
<td>8.34</td>
<td>3.87</td>
<td>19.52</td>
<td>5.14</td>
<td>7.73</td>
<td>3.48</td>
<td>20.82</td>
<td>8.12</td>
</tr>
<tr>
<td><b>UniDepthV2+Depth Fixer (Ours)</b></td>
<td><b>7.49</b></td>
<td><b>2.71</b></td>
<td><b>33.06</b></td>
<td><b>10.98</b></td>
<td><b>6.89</b></td>
<td><b>2.05</b></td>
<td><b>37.71</b></td>
<td><b>15.12</b></td>
</tr>
</tbody>
</table>

optical flow estimator [66]. To synthesize the warped results of soft boundaries, we sample a foreground image  $I_{FG}$  from the matting dataset, and generate the foreground flow  $f_{FG}$  with a random displacement vector  $(u, v)$  for all pixels, ensuring purely translational motion within the image plane. Then, we perform flow composition using alpha mask  $M_\alpha$ ,

$$f = f_{FG} \odot M_\alpha + f_{BG} \odot (1 - M_\alpha). \quad (7)$$

Since the foreground only moves within the image plane, ground-truth views  $\{I_{GT}\}$  can be easily synthesized by applying Eq. (1) to the foreground  $I_{FG}$  and background images  $\{I_{BG}\}$ . Although the foreground motions are relatively simple, the background regions preserve realistic viewpoint changes and complex camera motions for robust training. Finally, we perform forward warping with flows  $\{f\}$  to generate the warped images and masks, and fine-tune our scene painter to fit the characteristics of soft boundaries while inpainting disoccluded regions. The aligned synthesis strategy in SplatDiff [81] is also applied to the background regions for precise viewpoint control.

**Color Fuser.** Although the scene painter is able to eliminate redundant background in soft boundaries, its generative nature tends to hallucinate inconsistent texture details (e.g., see the red box in Fig. 5c). To this end, we propose the color fuser to adaptively combine warped and inpainted images. As shown in Fig. 5b, we build the color fuser upon a pre-trained Variational Auto-Encoder (VAE) [42] to harness its reconstruction prior. Since VAE models often suffer from detail compression [81], a dual skip module is designed to propagate fine-grained features for fusion. Specifically, we first extract multi-scale features of the inpainted and warped images via a frozen VAE encoder. These features are then concatenated with the warped masks and fed into the VAE decoder to compensate for texture details. Based on our curated view synthesis dataset, we further synthesize input inpainted images with hallucinated textures by applying the scene painter to ground-truth images  $\{I_{GT}\}$ . Finally, we fine-tune the VAE decoder using the following objective:

$$\mathcal{L}_{color} = \mathcal{L}_1(\hat{I}, I_{GT}) + \lambda \cdot \mathcal{L}_{lips}(\hat{I}, I_{GT}), \quad (8)$$

where the balancing parameter  $\lambda = 0.1$ ,  $\hat{I}$  denotes the outputs of the color fuser, and  $\mathcal{L}_{lips}$  indicates perceptual

loss [79]. Compared with the warped and inpainted results, our color fuser produces the best novel views with high-quality texture and geometry (Fig. 5c).

## 4. Experiments and Analysis

### 4.1. Experimental Settings

**Implementation Details.** For depth fixer, we curate our training dataset with  $\alpha_{min} = 0.02$  and  $\alpha_{max} = 0.98$ . We use  $\alpha_{th} = \alpha_{min}$  when generating ground-truth depth, and randomly sample  $\alpha_{th} \sim \mathcal{U}(\alpha_{min}, \alpha_{max})$  when synthesizing input depth. We implement the depth fixer with Depth Anything V2 [70] weight initialization for the feature branch. Depth fixer is trained with AdamW optimizer [35] under  $448 \times 448$  patches, batch size 32, and  $1 \times 10^{-5}$  learning rate for 35K iterations for both stages. For scene painter, we employ the pretrained VACE model [22] based on Wan2.1-1.3B [58], and fine-tune it under  $480 \times 832$  resolution, batch size 4, and  $1 \times 10^{-5}$  learning rate for 10K iterations. Regarding the color fuser, we add extra residual blocks in VAE decoder to blend the features from dual skip module, and fine-tune under  $448 \times 448$  patches, batch size 16, and  $1 \times 10^{-5}$  learning rate for 35K iterations. The total training takes 4 days on 4 NVIDIA RTX A6000 GPUs.

**Datasets.** For training, we employ two multi-view datasets as background datasets: *RealEstate10K* [84] and *DL3DV-10K* [32], and three image matting datasets as foreground datasets: *AM-2K* [26], *Distinctions-646* [43], and *Composition-1K* [68]. For evaluation, we created a *Marvel-10K* dataset composed of 501 stereo videos from Marvel movies, with a total of 12,525 stereo pairs. We also use 5 public depth estimation benchmarks for zero-shot evaluation: *NYUv2* [38], *KITTI* [14], *ETH3D* [50], *ScanNet* [9], and *DIODE* [57]. In addition, two natural image matting datasets *AIM-500* [29] and *P3M-10K* [28] are employed to evaluate the real-world performance of HairGuard.

### 4.2. Depth Estimation

We apply depth fixer to improve 3 state-of-the-art depth estimation models: Depth Anything V2 [70], Depth Pro [4], and UniDepthV2 [41] in a plug-and-play manner, and evaluate their performance in terms of depth boundary accuracyFigure 6. **Qualitative comparisons** of depth estimation (top), point clouds (middle), and novel view synthesis (bottom). Our HairGuard better preserves soft boundary details in depth results and novel views, without artifacts like broken, detached, or hallucinated hairs.

Table 2. **Zero-shot depth estimation performance.** The depth fixer preserves the zero-shot capability of its base depth model in diverse scenarios. Metrics are shown in percentage. **Better** results are marked. Please see the supplementary for more robustness evaluations.

<table border="1">
<thead>
<tr>
<th rowspan="2">Method</th>
<th colspan="2">NYUv2</th>
<th colspan="2">KITTI</th>
<th colspan="2">ETH3D</th>
<th colspan="2">ScanNet</th>
<th colspan="2">DIODE</th>
</tr>
<tr>
<th>AbsRel ↓</th>
<th><math>\delta 1</math> ↑</th>
<th>AbsRel ↓</th>
<th><math>\delta 1</math> ↑</th>
<th>AbsRel ↓</th>
<th><math>\delta 1</math> ↑</th>
<th>AbsRel ↓</th>
<th><math>\delta 1</math> ↑</th>
<th>AbsRel ↓</th>
<th><math>\delta 1</math> ↑</th>
</tr>
</thead>
<tbody>
<tr>
<td>Depth Anything V2 [70]</td>
<td>4.27</td>
<td>97.86</td>
<td>7.97</td>
<td>94.38</td>
<td>5.25</td>
<td>98.27</td>
<td>4.15</td>
<td>97.94</td>
<td>26.24</td>
<td>75.49</td>
</tr>
<tr>
<td><b>Depth Anything V2+Depth Fixer (Ours)</b></td>
<td>4.27</td>
<td>97.86</td>
<td>7.97</td>
<td>94.38</td>
<td>5.25</td>
<td>98.27</td>
<td>4.15</td>
<td>97.94</td>
<td>26.24</td>
<td>75.49</td>
</tr>
<tr>
<td>Depth Pro [4]</td>
<td>4.29</td>
<td>97.90</td>
<td>5.98</td>
<td>96.25</td>
<td>5.23</td>
<td>96.89</td>
<td>4.11</td>
<td>97.98</td>
<td>22.20</td>
<td>76.28</td>
</tr>
<tr>
<td><b>Depth Pro+Depth Fixer (Ours)</b></td>
<td>4.29</td>
<td>97.90</td>
<td>5.98</td>
<td>96.25</td>
<td>5.23</td>
<td>96.89</td>
<td>4.11</td>
<td>97.98</td>
<td><b>22.17</b></td>
<td>76.28</td>
</tr>
<tr>
<td>UniDepthV2 [41]</td>
<td>3.40</td>
<td>98.33</td>
<td>4.67</td>
<td>97.42</td>
<td>3.31</td>
<td>99.16</td>
<td>3.08</td>
<td>98.32</td>
<td>23.94</td>
<td>75.67</td>
</tr>
<tr>
<td><b>UniDepthV2+Depth Fixer (Ours)</b></td>
<td>3.40</td>
<td>98.33</td>
<td>4.67</td>
<td>97.42</td>
<td><b>3.27</b></td>
<td>99.16</td>
<td>3.08</td>
<td>98.32</td>
<td><b>23.87</b></td>
<td><b>75.71</b></td>
</tr>
</tbody>
</table>

and zero-shot depth estimation.

**Boundary Accuracy.** Following Depth Pro [4], we employ image matting datasets to evaluate depth accuracy in soft boundaries. Edge-based metrics, *i.e.*, the completeness and accuracy of depth boundaries (DBE\_comp and DBE\_acc) [25] and the edge precision and recall (EP and ER) [19], are used to evaluate depth results in soft boundary regions. Our depth fixer better captures fine-grained depth details in soft boundaries (see depth and point cloud results in Fig. 6), and consistently yields significant improvements when integrated with different depth models (Tab. 1).

**Zero-Shot Performance.** We further test the robustness of the depth fixer on 5 unseen public datasets. Although these datasets rarely contain soft boundaries, Tab. 2 shows that our depth fixer still achieves comparable or slightly better performance under in-the-wild settings. Thanks to the proposed gated residual module, our depth fixer can adaptively

fix depth in soft boundaries while maintaining the zero-shot performance of the base depth model, allowing seamless plug-and-play integration with current and future state-of-the-art depth models.

### 4.3. Stereo Conversion

Since stereo conversion is widely applied in film production, we compare HairGuard with state-of-the-art stereo conversion and novel view synthesis approaches on the Marvel-10K dataset, which features challenging cinematic scenes and talking heads with complex hair structures. Pixel-level metrics (PSNR, SSIM, and RMSE), feature-level metrics (LPIPS [79] and DISTS [12]), and the stereo metric SIoU [76] are used for evaluation.

**Benchmarking on Marvel-10K.** We compare the performance of stereo image conversion (1 frame per sequence) and stereo video conversion (all sequence frames) in Tab. 3.Table 3. **Stereo image/video conversion performance** on the Marvel-10K dataset. The **best** and **second-best** results are marked.

<table border="1">
<thead>
<tr>
<th rowspan="2">Method</th>
<th colspan="6">Stereo Image Conversion</th>
<th colspan="6">Stereo Video Conversion</th>
</tr>
<tr>
<th>PSNR <math>\uparrow</math></th>
<th>SSIM <math>\uparrow</math></th>
<th>RMSE <math>\downarrow</math></th>
<th>LPIPS <math>\downarrow</math></th>
<th>DISTS <math>\downarrow</math></th>
<th>SIoU <math>\uparrow</math></th>
<th>PSNR <math>\uparrow</math></th>
<th>SSIM <math>\uparrow</math></th>
<th>RMSE <math>\downarrow</math></th>
<th>LPIPS <math>\downarrow</math></th>
<th>DISTS <math>\downarrow</math></th>
<th>SIoU <math>\uparrow</math></th>
</tr>
</thead>
<tbody>
<tr>
<td>StereoDiffusion [59]</td>
<td>32.70</td>
<td>0.7654</td>
<td>6.05</td>
<td>0.2177</td>
<td>0.0698</td>
<td>0.2638</td>
<td>32.71</td>
<td>0.7656</td>
<td>6.04</td>
<td>0.2172</td>
<td>0.0693</td>
<td>0.2655</td>
</tr>
<tr>
<td>Mono2Stereo [76]</td>
<td>33.65</td>
<td>0.8143</td>
<td>5.45</td>
<td>0.1973</td>
<td>0.0690</td>
<td>0.2556</td>
<td>33.63</td>
<td>0.8134</td>
<td>5.47</td>
<td>0.1980</td>
<td>0.0691</td>
<td>0.2552</td>
</tr>
<tr>
<td>StereoCrafter [82]</td>
<td>32.52</td>
<td>0.8148</td>
<td>6.13</td>
<td>0.2330</td>
<td>0.1208</td>
<td>0.2664</td>
<td>32.35</td>
<td>0.8125</td>
<td>6.25</td>
<td>0.2381</td>
<td>0.1246</td>
<td>0.2645</td>
</tr>
<tr>
<td>ViewCrafter [77]</td>
<td>30.69</td>
<td>0.6705</td>
<td>7.61</td>
<td>0.3258</td>
<td>0.1330</td>
<td>0.2085</td>
<td>30.73</td>
<td>0.6739</td>
<td>7.59</td>
<td>0.3221</td>
<td>0.1312</td>
<td>0.2101</td>
</tr>
<tr>
<td>NVS-Solver [74]</td>
<td>31.18</td>
<td>0.7108</td>
<td>7.16</td>
<td>0.3323</td>
<td>0.1793</td>
<td>0.2143</td>
<td>31.44</td>
<td>0.7220</td>
<td>6.98</td>
<td>0.3256</td>
<td>0.1743</td>
<td>0.2161</td>
</tr>
<tr>
<td>ReCamMaster [2]</td>
<td>30.44</td>
<td>0.6118</td>
<td>7.82</td>
<td>0.4082</td>
<td>0.1391</td>
<td>0.1798</td>
<td>30.41</td>
<td>0.6107</td>
<td>7.84</td>
<td>0.4106</td>
<td>0.1412</td>
<td>0.1797</td>
</tr>
<tr>
<td>SplatDiff [81]</td>
<td><b>36.23</b></td>
<td><b>0.8857</b></td>
<td><b>4.06</b></td>
<td><b>0.1116</b></td>
<td><b>0.0435</b></td>
<td><b>0.3259</b></td>
<td><b>36.24</b></td>
<td><b>0.8858</b></td>
<td><b>4.06</b></td>
<td><b>0.1114</b></td>
<td><b>0.0437</b></td>
<td><b>0.3280</b></td>
</tr>
<tr>
<td><b>HairGuard (Ours)</b></td>
<td><b>36.59</b></td>
<td><b>0.8953</b></td>
<td><b>3.91</b></td>
<td><b>0.0909</b></td>
<td><b>0.0331</b></td>
<td><b>0.3337</b></td>
<td><b>36.58</b></td>
<td><b>0.8953</b></td>
<td><b>3.92</b></td>
<td><b>0.0911</b></td>
<td><b>0.0334</b></td>
<td><b>0.3355</b></td>
</tr>
</tbody>
</table>

Although our HairGuard focuses mainly on improving soft boundaries, which usually occupy small regions in images, it consistently outperforms existing approaches in all metrics. In addition, Fig. 7 verifies the superior performance and temporal consistency of HairGuard compared with previous video-based methods.

**Ablation Study.** Tab. 4 shows the contribution of each component in our HairGuard. We first estimate depth with Depth Anything V2 [70] and use its warped results as the baseline (#1). By fixing depth in soft boundaries, depth fixer achieves better warping performance with higher SIoU (#2 vs. #1). Scene painter largely improves perceptual quality by filling disoccluded regions, but suffers from detail compression and texture hallucination (better LPIPS and worse PSNR in #3). By adaptively combining warped and inpainted images via the color fuser, HairGuard achieves the best results with high-quality textures and stereo effects.

Figure 7. **Stereo video conversion performance** on Marvel-10K.

Table 4. **Ablation on stereo image conversion** on the Marvel-10K dataset. The **best** and **second-best** results are marked. Please see the supplementary for more detailed ablation studies.

<table border="1">
<thead>
<tr>
<th rowspan="2">Exp</th>
<th rowspan="2">Depth Fixer</th>
<th rowspan="2">Scene Painter</th>
<th rowspan="2">Color Fuser</th>
<th colspan="3">Marvel-10K</th>
</tr>
<tr>
<th>PSNR <math>\uparrow</math></th>
<th>LPIPS <math>\downarrow</math></th>
<th>SIoU <math>\uparrow</math></th>
</tr>
</thead>
<tbody>
<tr>
<td>#1</td>
<td></td>
<td></td>
<td></td>
<td>36.26</td>
<td>0.1490</td>
<td>0.3097</td>
</tr>
<tr>
<td>#2</td>
<td><math>\checkmark</math></td>
<td></td>
<td></td>
<td><b>36.28</b></td>
<td>0.1458</td>
<td><b>0.3118</b></td>
</tr>
<tr>
<td>#3</td>
<td><math>\checkmark</math></td>
<td><math>\checkmark</math></td>
<td></td>
<td>35.82</td>
<td><b>0.1246</b></td>
<td>0.3015</td>
</tr>
<tr>
<td>#4</td>
<td><math>\checkmark</math></td>
<td><math>\checkmark</math></td>
<td><math>\checkmark</math></td>
<td><b>36.59</b></td>
<td><b>0.0909</b></td>
<td><b>0.3337</b></td>
</tr>
</tbody>
</table>

#### 4.4. Novel View Synthesis

**Benchmarking on Matting Datasets.** We employ 2 natural image matting datasets to evaluate the novel view synthesis performance on scenes with soft boundaries. Since ground-truth views are not available, we adopt FID [18] and the average CLIP similarity of adjacent frames (CLIP-F) [44] for

Table 5. **Novel view synthesis performance** on the natural image matting datasets. The **best** and **second-best** results are marked.

<table border="1">
<thead>
<tr>
<th rowspan="2">Method</th>
<th colspan="2">AIM-500</th>
<th colspan="2">P3M-10K</th>
</tr>
<tr>
<th>FID <math>\downarrow</math></th>
<th>CLIP-F <math>\uparrow</math></th>
<th>FID <math>\downarrow</math></th>
<th>CLIP-F <math>\uparrow</math></th>
</tr>
</thead>
<tbody>
<tr>
<td>NVS-Solver [74]</td>
<td>51.71</td>
<td>97.24</td>
<td>55.12</td>
<td>96.66</td>
</tr>
<tr>
<td>ViewCrafter [77]</td>
<td>33.43</td>
<td>99.03</td>
<td>35.40</td>
<td>98.73</td>
</tr>
<tr>
<td>ReCamMaster [2]</td>
<td>57.19</td>
<td>97.95</td>
<td>62.80</td>
<td>97.09</td>
</tr>
<tr>
<td>SplatDiff [81]</td>
<td><b>19.26</b></td>
<td><b>99.36</b></td>
<td><b>21.61</b></td>
<td><b>99.09</b></td>
</tr>
<tr>
<td><b>HairGuard (Ours)</b></td>
<td><b>18.82</b></td>
<td><b>99.38</b></td>
<td><b>21.38</b></td>
<td><b>99.11</b></td>
</tr>
</tbody>
</table>

quantitative evaluation. Fig. 6 and Tab. 5 verify the state-of-the-art performance of HairGuard in real-world scenarios.

**User Study.** We conducted a user study with 27 participants on the full evaluation sets of AIM-500 and P3M-10K datasets (1000 natural images in total, no hand-picked samples). The participants will see side-by-side novel view video results, vote for their preferred one, and indicate if it is a strong preference. 1332 votes are collected in total, and the results in Fig. 8 verify the superiority of HairGuard.

Figure 8. **User study on novel view synthesis.** A survey of 27 participants (1332 votes in total) shows the superiority of our HairGuard compared with previous state-of-the-art approaches.

## 5. Conclusion

This paper presents HairGuard to address the challenges of soft boundaries in 3D vision tasks. By utilizing image matting datasets, we train a depth fixer to automatically identify soft boundary regions and correct depth results in a plug-and-play manner. For view synthesis tasks, the scene painter and color fuser are employed to fix geometric errors in novel views while preserving high-quality texture details. Extensive experiments on monocular depth estimation, stereo image/video conversion, and novel view synthesis verify the state-of-the-art performance of HairGuard.## Supplementary Material

The supplementary material is organized as follows: We first provide more implementation details in Sec. A. Then, the model performance, including robustness, plug-and-play performance, and computational complexity, is analyzed in Sec. B. Following that, we show more experiments on the depth fixer and the color fuser in Sec. C and Sec. D, respectively. Afterward, we analyze the limitations of HairGuard and discuss potential future directions in Sec. E. In the end, more visual comparisons on ablation study, monocular depth estimation, stereo conversion, and novel view synthesis are provided in Sec. F.

### A. More Implementation Details

#### A.1. Marvel-10K Dataset

The Marvel-10K dataset consists of 501 stereo video sequences from 5 Marvel movies: *Ant-Man and the Wasp: Quantumania* (85 scenes), *Black Panther: Wakanda Forever* (83 scenes), *Doctor Strange in the Multiverse of Madness* (119 scenes), *Guardians of the Galaxy Vol. 3* (101 scenes), and *Thor: Love and Thunder* (113 scenes). Since movie frames are highly correlated within shots, we subsample them to select meaningful frames and exclude the studio intros, credits, and black frames. Each video sequence corresponds to a single shot and consists of 25 stereo pairs. For stereo conversion evaluation, we use left-view images as inputs and the right-view images as ground truth. As shown in Fig. 9, the Marvel-10K dataset features computer-generated characters, intense motions, complex lighting, and uncommon cinematic scenes, making it highly challenging and suitable for evaluating algorithms in real-world applications such as film production.

Figure 9. Example images in the Marvel-10K dataset.

#### A.2. Color Fuser

We provide more implementation details about the dual skip module in our color fuser. Given the inpainted image  $I_{inpaint}$  and the warped image  $I_{warp}$ , we first extract

multi-scale features  $\{F_{inpaint}\}, \{F_{warp}\}$  using the frozen VAE encoder. We also generate multi-scale warped masks  $\{M_{warp}\}$  by resizing the original mask to each feature scale via nearest neighbor downsampling. Finally, we use an additional residual block in the VAE decoder to fuse the skipped features and masks at each feature scale, and inject the fused feature into the VAE decoder in a residual fashion,

$$F = F_{dec} + \text{ResBlock}(F_{dec}, F_{inpaint}, F_{warp}, M_{warp}).$$

$\text{ResBlock}(\cdot)$  indicates a residual block.  $F_{dec}$  and  $F$  correspond to the original decoder feature and the fused feature, respectively. Zero initialization is applied for the additional residual blocks during training.

### B. More Analysis on Model Performance

#### B.1. Robustness and Generalization

Since our depth fixer is trained on a relatively small synthetic dataset (approximately 20K samples), one concern is its robustness and generalization ability in complex scenes. To this end, we evaluate the performance of the depth fixer on the challenging Marvel-10K dataset, which is not seen during training. As shown in Fig. 10, the depth fixer can automatically identify soft boundary regions in various scenarios. In scenes without soft boundaries (*e.g.*, the top two rows in Fig. 10), the depth fixer maintains the depth quality of the base depth model for robust zero-shot estimation. In complex scenes such as bright/dark environments, occlusions, and multiple targets (bottom three rows in Fig. 10), our depth fixer still exhibits promising performance in extracting and fixing soft boundaries, showcasing its robustness in real-world applications. This is attributed to the decoupling of depth estimation and soft-boundary refinement in our depth fixer. Thanks to the proposed gated residual mechanism, we can leverage the base depth model for zero-shot transfer and focus solely on refining soft boundaries, thereby achieving strong generalization performance with efficient training.

#### B.2. Plug-and-Play Performance

Benefiting from the gated residual module, our depth fixer can be applied to improve depth predictions from different depth models in a plug-and-play manner. As visualized in Fig. 11a, we apply the depth fixer to two depth models with different characteristics: Depth Pro captures better details but often predicts inaccurate depth values in boundaries [4], and UniDepthV2 tends to produce depth results with smoothed boundaries [41]. Despite the different distributions of depth maps, our depth fixer maintains robust performance in predicting soft boundary regions and fixing depth details.

We further evaluate the plug-and-play capability of the depth fixer on video depth models, *e.g.*, Video Depth Anything [6]. Although the depth fixer is trained only on imageFigure 10. **Performance of depth fixer under challenging scenarios.** The regions with the predicted gate  $G < 1$  indicate the estimated soft boundary regions. Even under complex environments, *e.g.*, heavy occlusion, extreme lighting conditions, and multiple targets, our depth fixer can automatically identify soft boundary regions and perform precise fixing.

Table 6. **Plug-and-play stereo image/video conversion performance** on the Marvel-10K dataset. The **best** results are marked.

<table border="1">
<thead>
<tr>
<th rowspan="2">Method</th>
<th colspan="6">Stereo Image Conversion</th>
<th colspan="6">Stereo Video Conversion</th>
</tr>
<tr>
<th>PSNR <math>\uparrow</math></th>
<th>SSIM <math>\uparrow</math></th>
<th>RMSE <math>\downarrow</math></th>
<th>LPIPS <math>\downarrow</math></th>
<th>DISTS <math>\downarrow</math></th>
<th>SIoU <math>\uparrow</math></th>
<th>PSNR <math>\uparrow</math></th>
<th>SSIM <math>\uparrow</math></th>
<th>RMSE <math>\downarrow</math></th>
<th>LPIPS <math>\downarrow</math></th>
<th>DISTS <math>\downarrow</math></th>
<th>SIoU <math>\uparrow</math></th>
</tr>
</thead>
<tbody>
<tr>
<td>SplatDiff [81]</td>
<td>36.23</td>
<td>0.8857</td>
<td>4.06</td>
<td>0.1116</td>
<td>0.0435</td>
<td>0.3259</td>
<td>36.24</td>
<td>0.8858</td>
<td>4.06</td>
<td>0.1114</td>
<td>0.0437</td>
<td>0.3280</td>
</tr>
<tr>
<td><b>SplatDiff+Depth Fixer (Ours)</b></td>
<td><b>36.38</b></td>
<td><b>0.8915</b></td>
<td><b>4.00</b></td>
<td><b>0.0974</b></td>
<td><b>0.0348</b></td>
<td><b>0.3309</b></td>
<td><b>36.39</b></td>
<td><b>0.8917</b></td>
<td><b>3.99</b></td>
<td><b>0.0972</b></td>
<td><b>0.0351</b></td>
<td><b>0.3326</b></td>
</tr>
</tbody>
</table>

datasets, it still exhibits remarkable performance in improving video depth results, as shown in Fig. 11b. Thanks to the gated residual mechanism, our depth fixer only corrects the depth in soft boundary regions while preserving the temporal consistency of video depth results. Besides, the depth fixer shows stable performance in estimating soft boundary regions even under occluded scenes (*e.g.*, see the predicted gate maps in Fig. 11b), demonstrating its robustness in complex scenarios.

In addition to enhancing depth estimation methods, our depth fixer can also be integrated with novel view synthe-

sis models for performance improvement. For instance, we combine depth fixer with the previous novel view synthesis approach SplatDiff [81], and evaluate its performance on the Marvel-10K dataset. Since the depth fixer improves the warping results by fixing soft boundary details in depth (detailed in Sec. C.1), its combination with SplatDiff shows a consistent performance gain across all metrics, as reported in Tab. 6.

### B.3. Computational Complexity

In Tab. 7, we compare the computational complexity, *i.e.*, model size, peak GPU memory, and inference speed, of(a) Plug-and-play refinement on image-based depth models

(b) Plug-and-play refinement on video-based depth models

Figure 11. **Plug-and-play performance of depth fixer.** The depth fixer can be integrated with different depth models, *e.g.*, image-based models in (a) and video-based models in (b), in a plug-and-play fashion for soft boundary refinement. Although the depth fixer is trained only on image datasets, it can be directly applied to improve video-based models such as Video Depth Anything [6], without additional re-training. Leveraging the gated residual mechanism, the depth fixer preserves the temporal consistency of the video depth model while achieving stable performance in identifying soft boundaries and recovering fine-grained details, even in complex scenes with occlusions.

HairGuard with previous state-of-the-art novel view synthesis methods. We further break down the complexity of each component in HairGuard, and the results show that the scene painter dominates the computational cost

in our framework. Since we apply the depth fixer, scene painter, and color fuser in a sequential way, the peak GPU memory of HairGuard equals that of the scene painter. As our primary contributions lie in the depth fixer andTable 7. **Complexity comparison** with previous state-of-the-art novel view synthesis methods on the Marvel-10K dataset at a resolution of  $384 \times 640$ , evaluated using an NVIDIA GeForce RTX 4090 GPU. For diffusion-based methods, we only take into account the model sizes of the latent diffusion model and the VAE model. \* means that the method runs out of memory, and thus we perform inference at a lower resolution  $256 \times 448$  for reference. The complexity of each component in HairGuard *i.e.*, depth fixer, scene painter, and color fuser, is also reported. Since the three components are applied sequentially, the peak GPU memory of HairGuard equals that of the scene painter. The **best** and **second-best** results are marked.

<table border="1">
<thead>
<tr>
<th>Method</th>
<th>Model Size</th>
<th>Peak GPU Mem.</th>
<th>Infer. Speed</th>
</tr>
</thead>
<tbody>
<tr>
<td>ViewCrafter [77]</td>
<td>2.22 B</td>
<td>14.91 G</td>
<td>47.83 s</td>
</tr>
<tr>
<td>NVS-Solver* [74]</td>
<td>2.25 B</td>
<td>21.60 G</td>
<td>100.00 s</td>
</tr>
<tr>
<td>ReCamMaster [2]</td>
<td>1.51 B</td>
<td>17.11 G</td>
<td>684.44 s</td>
</tr>
<tr>
<td>SplatDiff [81]</td>
<td>2.28 B</td>
<td>22.88 G</td>
<td>52.28 s</td>
</tr>
<tr>
<td><b>HairGuard (Ours)</b></td>
<td><b>1.86 B</b></td>
<td><b>10.65 G</b></td>
<td>95.23 s</td>
</tr>
<tr>
<td><b>Depth Fixer (Ours)</b></td>
<td>0.32 B</td>
<td>1.84 G</td>
<td>0.03 s</td>
</tr>
<tr>
<td><b>Scene Painter (Ours)</b></td>
<td>1.44 B</td>
<td>10.65 G</td>
<td>95.19 s</td>
</tr>
<tr>
<td><b>Color Fuser (Ours)</b></td>
<td>0.10 B</td>
<td>3.15 G</td>
<td>0.01 s</td>
</tr>
</tbody>
</table>

Table 8. **Warping performance** using different depth maps on the Marvel-10K dataset. Metrics are computed only on the soft boundary regions. **Best** results are marked.

<table border="1">
<thead>
<tr>
<th>Method</th>
<th>PSNR <math>\uparrow</math></th>
<th>SSIM <math>\uparrow</math></th>
<th>RMSE <math>\downarrow</math></th>
</tr>
</thead>
<tbody>
<tr>
<td>Depth Anything V2 [70]</td>
<td>30.18</td>
<td>0.4495</td>
<td>8.08</td>
</tr>
<tr>
<td><b>Depth Anything V2+Depth Fixer (Ours)</b></td>
<td><b>31.07</b></td>
<td><b>0.5140</b></td>
<td><b>7.36</b></td>
</tr>
<tr>
<td>Depth Pro [4]</td>
<td>31.12</td>
<td>0.5591</td>
<td>7.28</td>
</tr>
<tr>
<td><b>Depth Pro+Depth Fixer (Ours)</b></td>
<td><b>31.77</b></td>
<td><b>0.6144</b></td>
<td><b>6.79</b></td>
</tr>
<tr>
<td>UniDepthV2 [41]</td>
<td>31.31</td>
<td>0.5637</td>
<td>7.12</td>
</tr>
<tr>
<td><b>UniDepthV2+Depth Fixer (Ours)</b></td>
<td><b>32.23</b></td>
<td><b>0.6261</b></td>
<td><b>6.46</b></td>
</tr>
</tbody>
</table>

the color fuser, the scene painter can be replaced with a more lightweight variant for better efficiency. In summary, our HairGuard achieves state-of-the-art performance while maintaining competitive computational efficiency, as demonstrated in Tab. 7.

## C. More Experiments on Depth Fixer

### C.1. Warping Performance

In this section, we analyze the influence of the depth fixer on view synthesis tasks. To focus on the impact of depth maps, we directly assess the quality of the warped images, without applying the scene painter and color fuser. In addition, since the proposed depth fixer only modifies the depth on the predicted soft boundary regions, *i.e.*, regions with  $G < 1$ , we compute pixel-level metrics only on these regions. We apply our depth fixer in a plug-and-play fashion to improve the prediction from three state-of-the-art depth models (Depth Anything V2 [70], Depth Pro [4], and UniDepthV2 [41]), and compare the forward warping performance on the Marvel-10K dataset. As shown in Tab. 8,

Table 9. **Ablation study of depth fixer** on the Marvel-10K dataset. The ablations about gated residual, loss function, model prior, edge guidance, and alpha threshold correspond to experiments #1-3, #4-5, #6-7, #8-9, and #10-12, respectively. We use Depth Anything V2 as the base depth model [70]. Metrics are computed only on the soft boundary regions. **Best** results are marked.

<table border="1">
<thead>
<tr>
<th rowspan="2">Exp</th>
<th rowspan="2">Strategies</th>
<th colspan="3">Marvel-10K</th>
</tr>
<tr>
<th>PSNR <math>\uparrow</math></th>
<th>SSIM <math>\uparrow</math></th>
<th>RMSE <math>\downarrow</math></th>
</tr>
</thead>
<tbody>
<tr>
<td>#1</td>
<td>Direct Prediction</td>
<td>30.66</td>
<td>0.5124</td>
<td>7.67</td>
</tr>
<tr>
<td>#2</td>
<td>Vanilla Residual</td>
<td>30.37</td>
<td>0.5009</td>
<td>7.88</td>
</tr>
<tr>
<td>#3</td>
<td>Gated Residual (Ours)</td>
<td><b>31.07</b></td>
<td><b>0.5140</b></td>
<td><b>7.36</b></td>
</tr>
<tr>
<td>#4</td>
<td><math>\mathcal{L}_1</math> Only</td>
<td>30.58</td>
<td>0.5057</td>
<td>7.74</td>
</tr>
<tr>
<td>#5</td>
<td><math>\mathcal{L}_1 + \mathcal{L}_\alpha</math> (Ours)</td>
<td><b>31.07</b></td>
<td><b>0.5140</b></td>
<td><b>7.36</b></td>
</tr>
<tr>
<td>#6</td>
<td>w/o Model Prior</td>
<td>30.26</td>
<td>0.4668</td>
<td>8.00</td>
</tr>
<tr>
<td>#7</td>
<td>w/ Model Prior (Ours)</td>
<td><b>31.07</b></td>
<td><b>0.5140</b></td>
<td><b>7.36</b></td>
</tr>
<tr>
<td>#8</td>
<td>w/o Edge Guidance</td>
<td>30.66</td>
<td>0.5057</td>
<td>7.67</td>
</tr>
<tr>
<td>#9</td>
<td>w/ Edge Guidance (Ours)</td>
<td><b>31.07</b></td>
<td><b>0.5140</b></td>
<td><b>7.36</b></td>
</tr>
<tr>
<td>#10</td>
<td><math>\alpha_{th} = 0.1</math></td>
<td>30.43</td>
<td>0.4774</td>
<td>7.87</td>
</tr>
<tr>
<td>#11</td>
<td><math>\alpha_{th} = 0.05</math></td>
<td>30.55</td>
<td>0.4917</td>
<td>7.76</td>
</tr>
<tr>
<td>#12</td>
<td><math>\alpha_{th} = 0.02</math> (Ours)</td>
<td><b>31.07</b></td>
<td><b>0.5140</b></td>
<td><b>7.36</b></td>
</tr>
</tbody>
</table>

our depth fixer helps preserve more soft boundary details during forward warping, leading to consistent and significant improvements across different base depth models.

### C.2. Gated Residual

Following the same experimental setting in Sec. C.1, we compare the performance of the depth fixer with different output mechanisms. Although the direct prediction and vanilla residual mechanisms help improve the depth on the soft boundary regions, they often cover redundant background regions and fail to capture the fine-grained details, as illustrated in Fig. 4c of the main paper. By accurately localizing the soft boundary regions with the estimated gate map, our gated residual facilitates precise depth refinement and achieves the best performance as shown in Tab. 9 (#3 vs. #1-2).

### C.3. Loss Function

We train the depth fixer with the  $\ell_1$  loss  $\mathcal{L}_1$  and the image matting loss  $\mathcal{L}_\alpha$  [71]. Specifically, the image matting loss  $\mathcal{L}_\alpha$  is formulated as

$$\mathcal{L}_\alpha = \mathcal{L}_1 + \mathcal{L}_{lap} + \mathcal{L}_{gp}, \quad (9)$$

where  $\mathcal{L}_{lap}, \mathcal{L}_{gp}$  indicate the Laplacian loss [33] and the gradient loss [11], respectively. Inspired by the success of such a loss combination in the image matting task [71], we adopt it to improve the detail extraction performance of our depth fixer. To verify its effectiveness, we train an additional model with  $\mathcal{L}_1$  loss only and keep the other training settings unchanged. The results in Tab. 9 show the better performance of the proposed loss combination (#5 vs. #4).## C.4. Model Prior

Identifying soft boundary regions is a challenging task, relying on a comprehensive understanding of semantic context and geometric layout. To this end, we initialize the feature branch of our depth fixer with the pre-trained Depth Anything V2 [70], which has been trained on large-scale datasets to acquire robust image and geometry priors. Benefiting from this, our depth fixer achieves strong performance with efficient training (only  $\sim 20K$  training samples are used), as shown in Tab. 9 (#7 vs. #6).

## C.5. Edge Guidance

Object boundaries, especially regions with significant depth variations, play a crucial role in 3D tasks like view synthesis, where disocclusions and geometric distortions commonly occur. Thus, we extract edge cues from the input depth to guide the depth fixer. The depth gradients provided by the edge guidance enable more accurate localization of soft boundaries, leading to improved warping performance (#9 vs. #8 in Tab. 9).

## C.6. Alpha Threshold

The alpha threshold  $\alpha_{th}$  used in generating ground-truth depth is critical to the performance of depth fixer. As shown in Fig. 12, the model trained with a higher  $\alpha_{th}$  exhibit finer delineation of depth boundaries with less redundant background regions, but it tends to ignore the areas with low opacity, *e.g.*, very thin hair. In our design, we opt for a lower  $\alpha_{th}$  to preserve as many soft boundary details as possible, which shows the best warping performance in Tab. 9 (#12 vs. #10-11). The scene painter and the color fuser are then employed to fix redundant background regions during view synthesis, as illustrated in Fig. 5c of the main paper. Nevertheless, a higher  $\alpha_{th}$  can be used to train the depth fixer for different tasks, *e.g.*, 3D segmentation or point cloud reconstruction, where precise depth boundaries are preferred.

Table 10. **Ablation study of color fuser** on the Marvel-10K dataset. The ablations about VAE prior and skip mechanisms correspond to experiments #1-2 and #3-5, respectively. **Best** results are marked.

<table border="1">
<thead>
<tr>
<th rowspan="2">Exp</th>
<th rowspan="2">Strategies</th>
<th colspan="4">Marvel-10K</th>
</tr>
<tr>
<th>PSNR <math>\uparrow</math></th>
<th>LPIPS <math>\downarrow</math></th>
<th>DISTS <math>\downarrow</math></th>
<th>FID <math>\downarrow</math></th>
</tr>
</thead>
<tbody>
<tr>
<td>#1</td>
<td>w/o VAE Prior</td>
<td>36.61</td>
<td>0.0965</td>
<td>0.0366</td>
<td>7.99</td>
</tr>
<tr>
<td>#2</td>
<td>w/ VAE Prior (Ours)</td>
<td>36.59</td>
<td><b>0.0909</b></td>
<td><b>0.0331</b></td>
<td><b>7.19</b></td>
</tr>
<tr>
<td>#3</td>
<td>w/o Skip</td>
<td>34.96</td>
<td>0.1664</td>
<td>0.0807</td>
<td>18.11</td>
</tr>
<tr>
<td>#4</td>
<td>Sinlge Skip</td>
<td>36.46</td>
<td>0.0919</td>
<td>0.0337</td>
<td>7.34</td>
</tr>
<tr>
<td>#5</td>
<td>Dual Skip (Ours)</td>
<td><b>36.59</b></td>
<td><b>0.0909</b></td>
<td><b>0.0331</b></td>
<td><b>7.19</b></td>
</tr>
</tbody>
</table>

Figure 12. **Performance of the depth fixer trained with different alpha thresholds.** A higher threshold  $\alpha_{th}$  leads to less redundant background in the depth map (*e.g.*, green box), while a lower threshold  $\alpha_{th}$  improves the coverage of fine-grained details, *e.g.*, the very thin hair in the red box.

## D. More Experiments on Color Fuser

### D.1. VAE Prior

We build the color fuser upon a pre-trained VAE to harness its reconstruction prior for better view synthesis performance. To investigate the impact of the VAE prior, we train an additional color fuser from scratch using the same training settings. As shown in Tab. 10, the color fuser with VAE prior significantly outperforms its counterpart in visual quality (#2 vs. #1).

### D.2. Dual Skip

Based on the VAE architecture, we further design a dual skip module to utilize the fine-grained features of the inpainted and warped images. To verify its effectiveness, we train two additional variants: one without skip connections (#3 in Tab. 10) and one with a single skip connection (#4). For model #3, we expand the input channel of the VAE encoder and concatenate the inpainted image, warped image, and warped mask as its input. Regarding model #4, we add a single skip to utilize the multi-scale features of the warped images. The results in Tab. 10 show that model #4 achieves a significant performance gain over model #3 by alleviating detail compression in the VAE encoding. By further exploiting the features of inpainted images, our dual skip module yields the best reconstruction performance with high-quality texture details.Figure 13. **Failure cases.** (a) Since the depth fixer only fixes the depth in the soft boundaries (represented by the regions with gate  $G < 1$ ), it is difficult to correct depth errors beyond soft boundaries in the prediction of the base depth model. (b) Due to the limitation of single-layer depth representation, the synthesized novel view might fail to correct the geometric errors caused by forward warping.

## E. Limitation and Discussion

Despite the remarkable performance achieved by HairGuard, some limitations remain:

- • **Depth errors beyond soft boundaries:** The depth fixer relies on the gated residual mechanism to locate and fix soft boundary details, which benefits precise refinement and plug-and-play deployment. However, it is difficult for the depth fixer to correct depth errors beyond the soft boundary regions, as depicted in Fig. 13a. A possible solution is to train a depth fixer specialized for a given depth model, *e.g.*, by using the model’s predictions instead of the synthesized inputs during training. Thus, the depth fixer could better adapt to the characteristics of the base depth model and achieve better fixing performance.
- • **Single-layer depth representation:** For view synthesis, we propose a color fuser to utilize the fine-grained texture from the warped images. However, due to the single-layer depth representation, the naive forward warping approach may produce geometric distortions in complex scenes containing multiple depth layers per pixel, *e.g.*, transparent objects as shown in Fig. 13b. We attempted to address this limitation by estimating layered outputs comprising foreground color and depth, background color and depth, and an opacity map for composition. While this layered representation demonstrated advantages in certain cases, our trial experiments showed that it suffers from limited generalization capability, likely due to the increased complexity of the estimation. Thus, a potential solution is to collect large-scale training datasets to gain

a strong prior for robust performance. Another possible direction is to employ dense 3D representations, *e.g.*, 3D Gaussians [24], to handle occlusions and overlapping surfaces.

## F. More Visual Results

### F.1. Ablation Study

Fig. 14 provides visual results for the ablation study conducted in the main paper (detailed in Tab. 4 of the main paper). Since depth quality is critical for forward warping performance, depth estimation errors in Depth Anything V2 [70] often result in distorted structures in the soft boundary regions like thin hairs. By fixing depth details via the proposed depth fixer, better hair structures are preserved in the warped images, as shown in the green box of Fig. 14. The scene painter is then applied to generate realistic contents for the disoccluded regions. However, the inpainted images often exhibit different texture details due to diffusion hallucination and pixel-to-latent compression. To this end, we propose a color fuser that adaptively combines the warped and inpainted images, generating novel views with consistent geometry and high-fidelity textures.

### F.2. Monocular Depth Estimation

We provide more visual results of monocular depth estimation on the AIM-500 and P3M-10K datasets in Fig. 15 and Fig. 16, respectively. Compared with previous methods, our depth fixer shows robust performance in capturing soft boundary details across diverse targets and scenes. InFigure 14. **Visual results of ablation study** on the AIM-500 and Marvel-10K datasets. Due to depth estimation errors, the original warped images often contain broken or distorted structures in thin hairs. Our depth fixer improves the warping performance by fixing the soft boundary regions in the depth. The scene painter is employed to fill disoccluded regions in the warped images, but the inpainted results often suffer from hallucinated details that are inconsistent with the input image (*e.g.*, see hairs in the **green** box, particularly in the Marvel-10K examples). By adaptively combining the warped and inpainted images, the color fuser produces high-quality results with consistent texture and geometry.

some challenging cases with very thin hair structures, *e.g.*, top few rows of Fig. 16, the depth fixer still recovers fine-grained depth details with sharp boundaries.

### F.3. Stereo Conversion

Fig. 17 compares the stereo conversion performance of HairGuard with the state-of-the-art methods on the Marvel-10K dataset. Due to the generative nature of the underlying models, previous stereo conversion approaches often suffer from texture hallucination and degraded details in the conversion results, *e.g.*, see the top two rows in Fig. 17. By utilizing the fine-grained details of warped images via the color fuser, our HairGuard achieves high-quality stereo conversion performance with consistent geometry and texture.

### F.4. Novel View Synthesis

We show more qualitative comparisons of novel view synthesis on the challenging AIM-500 and P3M-10K datasets in Fig. 18 and Fig. 19. Previous approaches often produce hallucinated textures that are inconsistent with the

input image, *e.g.*, see ViewCrafter [77] and ReCamMaster [2] in the top few rows of Fig. 18. Although the recent method SplatDiff recovers better details [81], its performance is highly dependent on the quality of the estimated depth maps. Hence, the depth errors in soft boundary regions often lead to artifacts in the synthesized novel views, *e.g.*, top few rows in Fig. 19. In contrast, the proposed HairGuard first fixes depth in the soft boundary regions to ensure geometry consistency, and then utilizes the color fuser to recover high-fidelity texture details, achieving state-of-the-art novel view synthesis performance.

## References

1. [1] Sherwin Bahmani, Tianchang Shen, Jiawei Ren, Jiahui Huang, Yifeng Jiang, Haithem Turki, Andrea Tagliasacchi, David B Lindell, Zan Gojcic, Sanja Fidler, et al. Lyra: Generative 3d scene reconstruction via video diffusion model self-distillation. *arXiv preprint arXiv:2509.19296*, 2025. 2
2. [2] Jianhong Bai, Menghan Xia, Xiao Fu, Xintao Wang, Lianrui Mu, Jinwen Cao, Zuozhu Liu, Haoji Hu, Xiang Bai, PengfeiWan, et al. Recammaster: Camera-controlled generative rendering from a single video. In *ICCV*, 2025. [2](#), [3](#), [8](#), [12](#), [15](#)

[3] Andreas Blattmann, Tim Dockhorn, Sumith Kulal, Daniel Mendeleevitch, Maciej Kilian, Dominik Lorenz, Yam Levi, Zion English, Vikram Voleti, Adam Letts, et al. Stable video diffusion: Scaling latent video diffusion models to large datasets. *arXiv preprint arXiv:2311.15127*, 2023. [3](#)

[4] Alexey Bochkovskiy, Amaël Delaunoy, Hugo Germain, Marcel Santos, Yichao Zhou, Stephan Richter, and Vladlen Koltun. Depth pro: Sharp monocular metric depth in less than a second. In *ICLR*, 2025. [2](#), [3](#), [6](#), [7](#), [9](#), [12](#)

[5] Eric R Chan, Koki Nagano, Matthew A Chan, Alexander W Bergman, Jeong Joon Park, Axel Levy, Miika Aittala, Shalini De Mello, Tero Karras, and Gordon Wetzstein. Generative novel view synthesis with 3d-aware diffusion models. In *ICCV*, pages 4217–4229, 2023. [3](#)

[6] Sili Chen, Hengkai Guo, Shengnan Zhu, Feihu Zhang, Zilong Huang, Jiashi Feng, and Bingyi Kang. Video depth anything: Consistent depth estimation for super-long videos. In *CVPR*, pages 22831–22840, 2025. [9](#), [11](#)

[7] Weifeng Chen, Zhao Fu, Dawei Yang, and Jia Deng. Single-image depth perception in the wild. In *NIPS*, 2016. [3](#)

[8] Weifeng Chen, Shengyi Qian, David Fan, Noriyuki Kojima, Max Hamilton, and Jia Deng. Oasis: A large-scale dataset for single image 3d in the wild. In *CVPR*, pages 679–688, 2020. [3](#)

[9] Angela Dai, Angel X. Chang, Manolis Savva, Maciej Halber, Thomas Funkhouser, and Matthias Nießner. ScanNet: Richly-annotated 3d reconstructions of indoor scenes. In *CVPR*, 2017. [6](#)

[10] Peng Dai, Feitong Tan, Qiangeng Xu, David Futschik, Ruofei Du, Sean Fanello, Xiaojuan Qi, and Yinda Zhang. Svg: 3d stereoscopic video generation via denoising frame matrix. *arXiv preprint arXiv:2407.00367*, 2024. [3](#)

[11] Yutong Dai, Brian Price, He Zhang, and Chunhua Shen. Boosting robustness of image matting with context assembling and strong data augmentation. In *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition*, pages 11707–11716, 2022. [12](#)

[12] Keyan Ding, Kede Ma, Shiqi Wang, and Eero P. Simoncelli. Image quality assessment: Unifying structure and texture similarity. *IEEE TPAMI*, 44(5):2567–2581, 2022. [7](#)

[13] Ruiqi Gao, Aleksander Holynski, Philipp Henzler, Arthur Brussee, Ricardo Martin-Brualla, Pratul Srinivasan, Jonathan T Barron, and Ben Poole. Cat3d: Create anything in 3d with multi-view diffusion models. In *NeurIPS*, 2024. [2](#)

[14] Andreas Geiger, Philip Lenz, and Raquel Urtasun. Are we ready for autonomous driving? the KITTI vision benchmark suite. In *CVPR*, 2012. [6](#)

[15] Michal Geyer, Omer Tov, Linyi Jin, Richard Tucker, Inbar Mosseri, Tali Dekel, and Noah Snavely. Eye2eye: A simple approach for monocular-to-stereo video synthesis. *arXiv preprint arXiv:2505.00135*, 2025. [3](#)

[16] Zekai Gu, Rui Yan, Jiahao Lu, Peng Li, Zhiyang Dou, Chenyang Si, Zhen Dong, Qifeng Liu, Cheng Lin, Ziwei Liu, et al. Diffusion as shader: 3d-aware video diffusion for versatile video generation control. *arXiv preprint arXiv:2501.03847*, 2025. [3](#)

[17] Yuxuan Han, Ruicheng Wang, and Jiaolong Yang. Single-view view synthesis in the wild with learned adaptive multiplane images. In *ACM SIGGRAPH 2022 Conference Proceedings*, New York, NY, USA, 2022. Association for Computing Machinery. [3](#)

[18] Martin Heusel, Hubert Ramsauer, Thomas Unterthiner, Bernhard Nessler, and Sepp Hochreiter. Gans trained by a two time-scale update rule converge to a local nash equilibrium. *NeurIPS*, 30, 2017. [8](#)

[19] Junjie Hu, Mete Ozay, Yan Zhang, and Takayuki Okatani. Revisiting single image depth estimation: Toward higher resolution maps with accurate object boundaries. In *WACV*, pages 1043–1051. IEEE, 2019. [7](#)

[20] Mu Hu, Wei Yin, Chi Zhang, Zhipeng Cai, Xiaoxiao Long, Hao Chen, Kaixuan Wang, Gang Yu, Chunhua Shen, and Shaojie Shen. Metric3d v2: A versatile monocular geometric foundation model for zero-shot metric depth and surface normal estimation. *PAMI*, 2024. [3](#)

[21] Varun Jampani, Huiwen Chang, Kyle Sargent, Abhishek Kar, Richard Tucker, Michael Krainin, Dominik Kaeser, William T Freeman, David Salesin, Brian Curless, et al. Slide: Single image 3d photography with soft layering and depth-aware inpainting. In *Proceedings of the IEEE/CVF International Conference on Computer Vision*, pages 12518–12527, 2021. [3](#)

[22] Zeyinzi Jiang, Zhen Han, Chaojie Mao, Jingfeng Zhang, Yulin Pan, and Yu Liu. Vace: All-in-one video creation and editing. *arXiv preprint arXiv:2503.07598*, 2025. [6](#)

[23] Bingxin Ke, Anton Obukhov, Shengyu Huang, Nando Metzger, Rodrigo Caye Daudt, and Konrad Schindler. Repurposing diffusion-based image generators for monocular depth estimation. In *CVPR*, pages 9492–9502, 2024. [2](#), [3](#)

[24] Bernhard Kerbl, Georgios Kopanas, Thomas Leimkühler, and George Drettakis. 3d gaussian splatting for real-time radiance field rendering. *ACM Trans. Graph.*, 42(4), 2023. [3](#), [14](#)

[25] Tobias Koch, Lukas Liebel, Friedrich Fraundorfer, and Marco Korner. Evaluation of cnn-based single-image depth estimation methods. In *ECCVW*, 2018. [7](#)

[26] Jizhizi Li. *End-to-end Animal Matting*. PhD thesis, University of Sydney, 2020. [6](#)

[27] Jiaxin Li, Zijian Feng, Qi She, Henghui Ding, Changhu Wang, and Gim Hee Lee. Mine: Towards continuous depth mpi with nerf for novel view synthesis. In *ICCV*, pages 12578–12588, 2021. [3](#)

[28] Jizhizi Li, Sihan Ma, Jing Zhang, and Dacheng Tao. Privacy-preserving portrait matting. In *ACMMM*, pages 3501–3509, 2021. [6](#)

[29] Jizhizi Li, Jing Zhang, and Dacheng Tao. Deep automatic natural image matting. In *IJCAI*. International Joint Conferences on Artificial Intelligence Organization, 2021. [6](#)

[30] Jizhizi Li, Jing Zhang, and Dacheng Tao. Deep image matting: A comprehensive survey. *arXiv preprint arXiv:2304.04672*, 2023. [2](#), [3](#)- [31] Hanwen Liang, Junli Cao, Vidit Goel, Guocheng Qian, Sergei Korolev, Demetri Terzopoulos, Konstantinos N Plataniotis, Sergey Tulyakov, and Jian Ren. Wonderland: Navigating 3d scenes from a single image. *arXiv preprint arXiv:2412.12091*, 2024. 2
- [32] Lu Ling, Yichen Sheng, Zhi Tu, Wentian Zhao, Cheng Xin, Kun Wan, Lantao Yu, Qianyu Guo, Zixun Yu, Yawen Lu, et al. DL3dv-10k: A large-scale scene dataset for deep learning-based 3d vision. In *CVPR*, pages 22160–22169, 2024. 6
- [33] Anna Lischke, Guofei Pang, Mamikon Gulian, Fangying Song, Christian Glusa, Xiaoning Zheng, Zhiping Mao, Wei Cai, Mark M Meerschaert, Mark Ainsworth, et al. What is the fractional laplacian? a comparative review with new results. *Journal of Computational Physics*, 404:109009, 2020. 12
- [34] Ruoshi Liu, Rundi Wu, Basile Van Hoorick, Pavel Tokmakov, Sergey Zakharov, and Carl Vondrick. Zero-1-to-3: Zero-shot one image to 3d object. In *ICCV*, pages 9298–9309, 2023. 3
- [35] Ilya Loshchilov and Frank Hutter. Decoupled weight decay regularization. In *ICLR*, 2019. 6
- [36] Lukas Mehl, Andr  s Bruhn, Markus Gross, and Christopher Schroers. Stereo conversion with disparity-aware warping, compositing and inpainting. In *WACV*, pages 4260–4269, 2024. 2, 3
- [37] Ben Mildenhall, Pratul P. Srinivasan, Matthew Tancik, Jonathan T. Barron, Ravi Ramamoorthi, and Ren Ng. Nerf: Representing scenes as neural radiance fields for view synthesis. In *ECCV*, 2020. 3
- [38] Pushmeet Kohli, Nathan Silberman, Derek Hoiem, and Rob Fergus. Indoor segmentation and support inference from RGBD images. In *ECCV*, 2012. 6
- [39] Maxime Oquab, Timoth  e Darcet, Th  o Moutakanni, Huy Vo, Marc Szafraniec, Vasil Khalidov, Pierre Fernandez, Daniel Haziza, Francisco Massa, Alaaeldin El-Noubi, et al. Dinov2: Learning robust visual features without supervision. *arXiv preprint arXiv:2304.07193*, 2023. 5
- [40] Luigi Piccinelli, Yung-Hsu Yang, Christos Sakaridis, Mattia Segu, Siyuan Li, Luc Van Gool, and Fisher Yu. Unidepth: Universal monocular metric depth estimation. In *CVPR*, pages 10106–10116, 2024. 3
- [41] Luigi Piccinelli, Christos Sakaridis, Yung-Hsu Yang, Mattia Segu, Siyuan Li, Wim Abbeloos, and Luc Van Gool. Unidepthv2: Universal monocular metric depth estimation made simpler. *arXiv preprint arXiv:2502.20110*, 2025. 2, 3, 6, 7, 9, 12
- [42] Dustin Podell, Zion English, Kyle Lacey, Andreas Blattmann, Tim Dockhorn, Jonas M  ller, Joe Penna, and Robin Rombach. Sdxl: Improving latent diffusion models for high-resolution image synthesis. *arXiv preprint arXiv:2307.01952*, 2023. 6
- [43] Yu Qiao, Yuhao Liu, Xin Yang, Dongsheng Zhou, Mingliang Xu, Qiang Zhang, and Xiaopeng Wei. Attention-guided hierarchical structure aggregation for image matting. In *CVPR*, 2020. 6
- [44] Alec Radford, Jong Wook Kim, Chris Hallacy, Aditya Ramesh, Gabriel Goh, Sandhini Agarwal, Girish Sastry, Amanda Askell, Pamela Mishkin, Jack Clark, et al. Learning transferable visual models from natural language supervision. In *ICML*, pages 8748–8763. PmLR, 2021. 8
- [45] Ren   Ranftl, Katrin Lasinger, David Hafner, Konrad Schindler, and Vladlen Koltun. Towards robust monocular depth estimation: Mixing datasets for zero-shot cross-dataset transfer. *PAMI*, 44(3):1623–1637, 2020. 2, 3, 5
- [46] Ren   Ranftl, Alexey Bochkovskiy, and Vladlen Koltun. Vision transformers for dense prediction. In *ICCV*, pages 12179–12188, 2021. 3, 5
- [47] Robin Rombach, Andreas Blattmann, Dominik Lorenz, Patrick Esser, and Bj  rn Ommer. High-resolution image synthesis with latent diffusion models. In *CVPR*, pages 10684–10695, 2022. 1, 2, 3
- [48] Olaf Ronneberger, Philipp Fischer, and Thomas Brox. U-net: Convolutional networks for biomedical image segmentation. In *International Conference on Medical image computing and computer-assisted intervention*, pages 234–241. Springer, 2015. 5
- [49] Kyle Sargent, Zizhang Li, Tanmay Shah, Charles Herrmann, Hong-Xing Yu, Yunzhi Zhang, Eric Ryan Chan, Dmitry Lagun, Li Fei-Fei, Deqing Sun, et al. Zeronvs: Zero-shot 360-degree view synthesis from a single image. In *CVPR*, pages 9420–9429, 2024. 3
- [50] Thomas Schops, Johannes L Schonberger, Silvano Galliani, Torsten Sattler, Konrad Schindler, Marc Pollefeys, and Andreas Geiger. A multi-view stereo benchmark with high-resolution images and multi-camera videos. In *CVPR*, pages 3260–3269, 2017. 6
- [51] Christoph Schuhmann, Romain Beaumont, Richard Vencu, Cade Gordon, Ross Wightman, Mehdi Cherti, Theo Coombes, Aarush Katta, Clayton Mullis, Mitchell Wortsman, et al. Laion-5b: An open large-scale dataset for training next generation image-text models. In *NIPS*, pages 25278–25294, 2022. 1
- [52] Junyoung Seo, Kazumi Fukuda, Takashi Shibuya, Takuya Narihira, Naoki Murata, Shoukang Hu, Chieh-Hsin Lai, Seungryong Kim, and Yuki Mitsufuji. Genwarp: Single image to novel views with semantic-preserving generative warping. In *NeurIPS*, 2024. 3
- [53] Nina Shvetsova, Goutam Bhat, Prune Truong, Hilde Kuehne, and Federico Tombari. M2svid: End-to-end inpainting and refinement for monocular-to-stereo video conversion. *arXiv preprint arXiv:2505.16565*, 2025. 3
- [54] Stanislaw Szymanowicz, Eldar Insafutdinov, Chuanxia Zheng, Dylan Campbell, Jo  o F Henriques, Christian Rupprecht, and Andrea Vedaldi. Flash3d: Feed-forward generalisable 3d scene reconstruction from a single image. *arXiv preprint arXiv:2406.04343*, 2024. 3
- [55] Stanislaw Szymanowicz, Christian Rupprecht, and Andrea Vedaldi. Splatter image: Ultra-fast single-view 3d reconstruction. In *CVPR*, pages 10208–10217, 2024. 3
- [56] Richard Tucker and Noah Snavely. Single-view view synthesis with multiplane images. In *CVPR*, pages 551–560, 2020. 3
- [57] Igor Vasiljevic, Nick Kolkin, Shanyi Zhang, Ruotian Luo, Haochen Wang, Falcon Z. Dai, Andrea F. Daniele, Mohammadreza Mostajabi, Steven Basart, Matthew R. Walter,and Gregory Shakhnarovich. DIODE: A Dense Indoor and Outdoor DEpth Dataset. *arXiv preprint arXiv:1908.00463*, 2019. 6

[58] Team Wan, Ang Wang, Baole Ai, Bin Wen, Chaojie Mao, Chen-Wei Xie, Di Chen, Feiwu Yu, Haiming Zhao, Jianxiao Yang, et al. Wan: Open and advanced large-scale video generative models. *arXiv preprint arXiv:2503.20314*, 2025. 2, 3, 6

[59] Lezhong Wang, Jeppe Revall Frisvad, Mark Bo Jensen, and Siavash Arjomand Bigdeli. Stereodiffusion: Training-free stereo image generation using latent diffusion models. In *CVPR*, pages 7416–7425, 2024. 2, 3, 8

[60] Xiaodong Wang, Chenfei Wu, Shengming Yin, Minheng Ni, Jianfeng Wang, Linjie Li, Zhengyuan Yang, Fan Yang, Lijuan Wang, Zicheng Liu, et al. Learning 3d photography videos via self-supervised diffusion on single images. *arXiv preprint arXiv:2302.10781*, 2023. 3

[61] Yan Wang, Wei-Lun Chao, Divyansh Garg, Bharath Hariharan, Mark Campbell, and Kilian Q Weinberger. Pseudo-lidar from visual depth estimation: Bridging the gap in 3d object detection for autonomous driving. In *CVPR*, pages 8445–8453, 2019. 2

[62] Olivia Wiles, Georgia Gkioxari, Richard Szeliski, and Justin Johnson. Synsin: End-to-end view synthesis from a single image. In *CVPR*, pages 7467–7477, 2020. 3

[63] Felix Wimbauer, Nan Yang, Christian Rupprecht, and Daniel Cremers. Behind the scenes: Density fields for single view reconstruction. In *CVPR*, pages 9076–9086, 2023. 3

[64] Junyuan Xie, Ross Girshick, and Ali Farhadi. Deep3d: Fully automatic 2d-to-3d video conversion with deep convolutional neural networks. In *European conference on computer vision*, pages 842–857. Springer, 2016. 3

[65] Jinbo Xing, Menghan Xia, Yong Zhang, Haoxin Chen, Wangbo Yu, Hanyuan Liu, Gongye Liu, Xintao Wang, Ying Shan, and Tien-Tsin Wong. Dynamicrafter: Animating open-domain images with video diffusion priors. In *ECCV*, pages 399–417. Springer, 2025. 2

[66] Haofei Xu, Jing Zhang, Jianfei Cai, Hamid Rezatofighi, Fisher Yu, Dacheng Tao, and Andreas Geiger. Unifying flow, stereo and depth estimation. *IEEE TPAMI*, 2023. 6

[67] Haofei Xu, Songyou Peng, Fangjinhua Wang, Hermann Blum, Daniel Barath, Andreas Geiger, and Marc Pollefeys. Depthspat: Connecting gaussian splatting and depth. *arXiv preprint arXiv:2410.13862*, 2024. 3

[68] Ning Xu, Brian Price, Scott Cohen, and Thomas Huang. Deep image matting. In *Proceedings of the IEEE conference on computer vision and pattern recognition*, pages 2970–2979, 2017. 6

[69] Lihe Yang, Bingyi Kang, Zilong Huang, Xiaogang Xu, Jiashi Feng, and Hengshuang Zhao. Depth anything: Unleashing the power of large-scale unlabeled data. In *CVPR*, pages 10371–10381, 2024. 2, 3

[70] Lihe Yang, Bingyi Kang, Zilong Huang, Zhen Zhao, Xiaogang Xu, Jiashi Feng, and Hengshuang Zhao. Depth anything v2. In *NeurIPS*, 2024. 2, 3, 4, 6, 7, 8, 12, 13, 14

[71] Jingfeng Yao, Xinggang Wang, Shusheng Yang, and Baoyuan Wang. Vitmatte: Boosting image matting with pre-trained plain vision transformers. *Information Fusion*, 103: 102091, 2024. 2, 3, 4, 5, 12

[72] Wei Yin, Jianming Zhang, Oliver Wang, Simon Niklaus, Long Mai, Simon Chen, and Chunhua Shen. Learning to recover 3d scene shape from a single image. In *CVPR*, pages 204–213, 2021. 3

[73] Wei Yin, Chi Zhang, Hao Chen, Zhipeng Cai, Gang Yu, Kaixuan Wang, Xiaozhi Chen, and Chunhua Shen. Metric3d: Towards zero-shot metric 3d prediction from a single image. In *ICCV*, pages 9043–9053, 2023. 3

[74] Meng You, Zhiyu Zhu, Hui Liu, and Junhui Hou. Nvs-solver: Video diffusion model as zero-shot novel view synthesizer. In *ICLR*, 2025. 2, 3, 8, 12

[75] Alex Yu, Vickie Ye, Matthew Tancik, and Angjoo Kanazawa. pixelnerf: Neural radiance fields from one or few images. In *CVPR*, pages 4578–4587, 2021. 3

[76] Songsong Yu, Yuxin Chen, Zhongang Qi, Zeke Xie, Yifan Wang, Lijun Wang, Ying Shan, and Huchuan Lu. Mono2stereo: A benchmark and empirical study for stereo conversion. In *CVPR*, pages 21847–21856, 2025. 2, 3, 7, 8

[77] Wangbo Yu, Jinbo Xing, Li Yuan, Wenbo Hu, Xiaoyu Li, Zhipeng Huang, Xiangjun Gao, Tien-Tsin Wong, Ying Shan, and Yonghong Tian. Viewcrafter: Taming video diffusion models for high-fidelity novel view synthesis. *arXiv preprint arXiv:2409.02048*, 2024. 2, 3, 8, 12, 15

[78] Chi Zhang, Wei Yin, Billzb Wang, Gang Yu, Bin Fu, and Chunhua Shen. Hierarchical normalization for robust monocular depth estimation. In *NIPS*, pages 14128–14139, 2022. 3

[79] Richard Zhang, Phillip Isola, Alexei A Efros, Eli Shechtman, and Oliver Wang. The unreasonable effectiveness of deep features as a perceptual metric. In *CVPR*, pages 586–595, 2018. 6, 7

[80] Xiang Zhang, Bingxin Ke, Hayko Riemenschneider, Nando Metzger, Anton Obukhov, Markus Gross, Konrad Schindler, and Christopher Schroers. Betterdepth: Plug-and-play diffusion refiner for zero-shot monocular depth estimation. In *NeurIPS*, 2024. 2, 3

[81] Xiang Zhang, Yang Zhang, Lukas Mehl, Markus Gross, and Christopher Schroers. High-fidelity novel view synthesis via splatting-guided diffusion. In *SIGGRAPH*, New York, NY, USA, 2025. Association for Computing Machinery. 2, 3, 6, 8, 10, 12, 15

[82] Sijie Zhao, Wenbo Hu, Xiaodong Cun, Yong Zhang, Xiaoyu Li, Zhe Kong, Xiangjun Gao, Muyao Niu, and Ying Shan. Stereocrafter: Diffusion-based generation of long and high-fidelity stereoscopic 3d from monocular videos. *arXiv preprint arXiv:2409.07447*, 2024. 2, 3, 8

[83] Chuanxia Zheng and Andrea Vedaldi. Free3d: Consistent novel view synthesis without 3d representation. In *CVPR*, pages 9720–9731, 2024. 3

[84] Tinghui Zhou, Richard Tucker, John Flynn, Graham Fyffe, and Noah Snavely. Stereo magnification: learning view synthesis using multiplane images. *ACM Trans. Graph.*, 37(4), 2018. 6Figure 15. Qualitative comparison of depth estimation on the AIM-500 dataset.Figure 16. **Qualitative comparison of depth estimation** on the P3M-10K dataset. Human faces are manually blurred to protect privacy.Figure 17. Qualitative comparison of stereo conversion on the Marvel-10K dataset.Figure 18. Qualitative comparison of novel view synthesis on the AIM-500 dataset.Figure 19. **Qualitative comparison of novel view synthesis** on the P3M-10K dataset. Human faces are manually blurred to protect privacy.
