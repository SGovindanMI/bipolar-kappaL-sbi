# Reference and computing-environment audit

Checked 10 October 2026. The revised documents contain 22 references, numbered by first appearance and attached to relevant statements. Own results remain supported by archived arrays; external citations support methods and physical context, not this project’s numerical outcomes.

## Supplied full texts verified

The three previously outstanding PDFs were supplied and checked on 10 October 2026. Bibliographic identity, the cited physical claims and key equations were checked against the full texts; relevant equation and table pages were also inspected visually. References [2], [5] and [21] can be retained as currently cited. No manuscript or supplementary wording correction is required by this targeted review. This does not establish independent experimental validation of our inferred components or guarantee publication acceptance.

Detailed evidence and limitations: [SUPPLIED_PAPERS_VERIFICATION.md](SUPPLIED_PAPERS_VERIFICATION.md). File fingerprints: [SUPPLIED_PAPERS_VERIFICATION.json](SUPPLIED_PAPERS_VERIFICATION.json). Uploaded PDFs and extracted full texts are not included in the public release.

Kim’s Lorenz-estimator article and the Gibbs gap-estimator paper are reproduced in the accessible author thesis (chapters 8 and 7). The published articles, not the thesis, are cited in the manuscript. The Talts reference is explicitly a preprint. Papamakarios–Murray is methodological precedent and is not presented as the exact single-Gaussian implementation used here.

## Verified system information

The extended-run manifests agree on Python 3.11.9, NumPy 2.4.6, SciPy 1.17.1, PyTorch 2.11.0+cu128, CUDA 12.8 and NVIDIA GeForce RTX 5060 Laptop GPU. The reference run independently records CUDA execution and the same PyTorch build. The GPU model is not separately recorded for the reference run. CPU model, RAM, OS version, GPU memory and driver version remain unrecorded. No current-machine inspection has been substituted for historical evidence.

Training code confirms four CPU threads, requested deterministic algorithms, disabled TF32 and the default cuBLAS workspace setting. The source correction reuses unchanged posterior draws; no training was rerun for this citation revision.

## Reference register

### [1] Kim, H.-S., Gibbs, Z. M., Tang, Y., Wang, H. & Snyder, G. J. Characterization of Lorenz number with Seebeck coefficient measurement. APL Materials 3, 041506 (2015). doi:10.1063/1.4908244

Source: https://thesis.caltech.edu/9780/1/Kim_Hyun-Sik_2016_Thesis_Final.pdf
Access and scope: Author thesis, chapter 8 reproduces the article; publisher endpoint inaccessible.
Placement: 1. Introduction

### [2] Putatunda, A. & Singh, D. J. Lorenz number in relation to estimates based on the Seebeck coefficient. Materials Today Physics 8, 49–55 (2019). doi:10.1016/j.mtphys.2019.01.001

Source: https://www.sciencedirect.com/science/article/abs/pii/S2542529318301561
Access and scope: Full text verified from user-supplied PDF (7 pages; journal pages 49-55). Equations (4) and (7) distinguish open-circuit conductivity; pages 51-54 and Table 2 support scattering- and band-structure-dependent departures from the Kim estimate. No universal error bound or corpus-specific correction follows.
Placement: 1. Introduction

### [3] Wang, S., Yang, J., Toll, T., Yang, J., Zhang, W. & Tang, X. Conductivity-limiting bipolar thermal conductivity in semiconductors. Scientific Reports 5, 10136 (2015). doi:10.1038/srep10136

Source: https://www.nature.com/articles/srep10136
Access and scope: Publisher full text; bipolar expression and minority-conductivity dependence.
Placement: 1. Introduction; 2.2 Forward model; 2.7 Extended carrier and thermal models; 6. Remaining validation needs

### [4] Thesberg, M., Kosina, H. & Neophytou, N. On the Lorenz number of multiband materials. Physical Review B 95, 125206 (2017). doi:10.1103/PhysRevB.95.125206

Source: https://www.iue.tuwien.ac.at/pdf/ib_2017/JB2017_Thesberg_1.pdf
Access and scope: Author-hosted full paper; multiband Lorenz-number variation.
Placement: 1. Introduction

### [5] Kim, H.-S., Lee, K. H., Yoo, J., Youn, J., Roh, J. W., Kim, S.-i. & Kim, S. W. Effect of substitutional Pb doping on bipolar and lattice thermal conductivity in p-type Bi0.48Sb1.52Te3. Materials 10, 763 (2017). doi:10.3390/ma10070763

Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC5551806/
Access and scope: Full text verified from user-supplied PDF (9 pages). Pages 3-5, Eq. (5), Table 1 and Fig. 4 support model-assisted bipolar decomposition; page 8 records Hall measurements. Not independent component ground truth.
Placement: 1. Introduction; 6. Remaining validation needs

### [6] Kuo, J. J., Wood, M., Slade, T. J., Kanatzidis, M. G. & Snyder, G. J. Systematic over-estimation of lattice thermal conductivity in materials with electrically-resistive grain boundaries. Energy & Environmental Science 13, 1250–1258 (2020). doi:10.1039/C9EE03921J

Source: https://pubs.rsc.org/en/content/getauthorversionpdf/c9ee03921j
Access and scope: Author manuscript accessible; grain-boundary subtraction bias.
Placement: 1. Introduction

### [7] Candolfi, C., Wiendlocha, B., Ohorodniichuk, V., Levinský, P., Migot, S., Steciuk, G., Terzi, I., Wieder, A., Dauscher, A., El Oualid, S. & Lenoir, B. Hidden in plain heat: anomalous Lorenz number in the thermoelectric alloy Bi0.4Sb1.6Te3. Nature Communications 16, 11528 (2025). doi:10.1038/s41467-025-66578-y

Source: https://www.nature.com/articles/s41467-025-66578-y
Access and scope: Publisher full text; low-temperature high-field separation and inelastic-scattering interpretation.
Placement: 1. Introduction; 3.2 Comparison of four lattice estimates; 6. Remaining validation needs

### [8] Papamakarios, G. & Murray, I. Fast ε-free inference of simulation models with Bayesian conditional density estimation. Advances in Neural Information Processing Systems 29, 1028–1036 (2016). https://proceedings.neurips.cc/paper/2016/hash/6aca97005c68f1206823815f66102863-Abstract.html

Source: https://proceedings.neurips.cc/paper/2016/hash/6aca97005c68f1206823815f66102863-Abstract.html
Access and scope: Proceedings abstract and linked full paper; methodological precedent, not the exact implemented architecture.
Placement: 1. Introduction

### [9] Cranmer, K., Brehmer, J. & Louppe, G. The frontier of simulation-based inference. PNAS 117, 30055–30062 (2020). doi:10.1073/pnas.1912789117

Source: https://arxiv.org/html/1911.01429v3
Access and scope: Author full text and journal DOI verified; methodological overview.
Placement: 1. Introduction

### [10] Talts, S., Betancourt, M., Simpson, D., Vehtari, A. & Gelman, A. Validating Bayesian inference algorithms with simulation-based calibration. arXiv:1804.06788 (2018).

Source: https://arxiv.org/abs/1804.06788
Access and scope: Author preprint; cited as SBC methodology, not as a claim that full SBC was performed.
Placement: 1. Introduction; 2.5 Calibration; 6. Remaining validation needs; Supplementary computational details

### [11] Hermans, J., Delaunoy, A., Rozet, F., Wehenkel, A., Begy, V. & Louppe, G. A trust crisis in simulation-based inference? Your posterior approximations can be unfaithful. Transactions on Machine Learning Research (2022). https://openreview.net/forum?id=LHAbHkt6Aq

Source: https://arxiv.org/html/2110.06581v3
Access and scope: Author full text and published TMLR PDF; posterior overconfidence and coverage diagnostics.
Placement: 1. Introduction; 2.5 Calibration; 6. Remaining validation needs; Supplementary computational details

### [12] Kielar, S., Li, C., Huang, H., Hu, R., Slebodnick, C., Alatas, A. & Tian, Z. Anomalous lattice thermal conductivity increase with temperature in cubic GeTe correlated with strengthening of second-nearest neighbor bonds. Nature Communications 15, 6981 (2024). doi:10.1038/s41467-024-51377-8

Source: https://www.nature.com/articles/s41467-024-51377-8
Access and scope: Publisher full text; calculated lattice upturn and experimental comparison in cubic GeTe.
Placement: 1. Introduction; 3.3 Association with inferred bipolar heat

### [13] Katsura, Y., Kumagai, M., Mato, T., Takada, Y., Ando, Y., Fujita, E., Hosono, F., Koyama, E., Mudasar, F., Phuong, T. N. T., Saito, N., Sakamoto, Y., Tanaka, A., Yana, D., Kimura, K., Tsuda, K. & Demura, M. Starrydata: from published plots to shared materials data. Science and Technology of Advanced Materials: Methods 5, 2506976 (2025). doi:10.1080/27660400.2025.2506976

Source: https://www.tandfonline.com/doi/full/10.1080/27660400.2025.2506976
Access and scope: Publisher full text; database design and digitisation. Current cohort counts are this project’s measurements.
Placement: 2.1 Corpus; 6. Remaining validation needs

### [14] Elfwing, S., Uchibe, E. & Doya, K. Sigmoid-weighted linear units for neural network function approximation in reinforcement learning. Neural Networks 107, 3–11 (2018). doi:10.1016/j.neunet.2017.12.012

Source: https://arxiv.org/pdf/1702.03118
Access and scope: Author full paper; journal metadata verified on publisher page. Citation credits the activation only.
Placement: 2.4 Amortised posterior; Supplementary computational details

### [15] Loshchilov, I. & Hutter, F. Decoupled weight decay regularization. International Conference on Learning Representations (2019). https://openreview.net/forum?id=Bkg6RiCqY7

Source: https://arxiv.org/pdf/1711.05101
Access and scope: Author full paper; AdamW method. Hyperparameters are this project’s recorded choices.
Placement: 2.4 Amortised posterior; Supplementary computational details

### [16] Harris, C. R. et al. Array programming with NumPy. Nature 585, 357–362 (2020). doi:10.1038/s41586-020-2649-2

Source: https://www.nature.com/articles/s41586-020-2649-2
Access and scope: Publisher full text; software attribution.
Placement: 2.4 Amortised posterior; Supplementary computational details

### [17] Virtanen, P. et al. SciPy 1.0: fundamental algorithms for scientific computing in Python. Nature Methods 17, 261–272 (2020). doi:10.1038/s41592-019-0686-2

Source: https://www.nature.com/articles/s41592-019-0686-2
Access and scope: Publisher full text; software attribution.
Placement: 2.4 Amortised posterior; Supplementary computational details

### [18] Paszke, A. et al. PyTorch: an imperative style, high-performance deep learning library. Advances in Neural Information Processing Systems 32 (2019). https://arxiv.org/abs/1912.01703

Source: https://arxiv.org/abs/1912.01703
Access and scope: Author paper record; framework attribution. Run versions come from local manifests, not this paper.
Placement: 2.4 Amortised posterior; Supplementary computational details

### [19] Lueckmann, J.-M., Boelts, J., Greenberg, D., Gonçalves, P. & Macke, J. Benchmarking simulation-based inference. Proceedings of Machine Learning Research 130, 343–351 (2021). https://proceedings.mlr.press/v130/lueckmann21a.html

Source: https://proceedings.mlr.press/v130/lueckmann21a/lueckmann21a.pdf
Access and scope: Proceedings full paper; complementary diagnostics and no uniformly best algorithm.
Placement: 2.5 Calibration; 6. Remaining validation needs; Supplementary computational details

### [20] Fritsch, F. N. & Butland, J. A method for constructing local monotone piecewise cubic interpolants. SIAM Journal on Scientific and Statistical Computing 5, 300–304 (1984). doi:10.1137/0905021

Source: https://anthonylloyd.github.io/public/interp/pchip/A_method_for_constructing_local_monotone_picewise_cubic_interpolants_fritsch1984.pdf
Access and scope: Publisher metadata verified; complete published five-page article accessed through a PDF mirror. Supports local shape-preserving interpolation, including piecewise-monotone data.
Placement: 2.7 Extended carrier and thermal models

### [21] Goldsmid, H. J. & Sharp, J. W. Estimation of the thermal band gap of a semiconductor from Seebeck measurements. Journal of Electronic Materials 28, 869–872 (1999). doi:10.1007/s11664-999-0211-y

Source: https://link.springer.com/article/10.1007/s11664-999-0211-y
Access and scope: Full text verified from user-supplied PDF (4 pages; journal pages 869-872). Approximate Seebeck-maximum gap relation; pages 870-871 examine mobility, effective-mass and scattering dependence and narrow-gap statistics. Not an independent validation using the same Seebeck data.
Placement: 5. Limitations

### [22] Gibbs, Z. M., Kim, H.-S., Wang, H. & Snyder, G. J. Band gap estimation from temperature dependent Seebeck measurement—Deviations from the 2e|S|maxTmax relation. Applied Physics Letters 106, 022112 (2015). doi:10.1063/1.4905922

Source: https://thesis.caltech.edu/9780/1/Kim_Hyun-Sik_2016_Thesis_Final.pdf
Access and scope: Author thesis chapter 7 reproduces the article; author institutional record verifies DOI. Supports mobility-ratio and narrow-gap limitations.
Placement: 5. Limitations

The Fritsch–Butland paper was subsequently retrieved in full from a PDF mirror; its publisher metadata and method description agree. No PDF is now requested for that reference.
