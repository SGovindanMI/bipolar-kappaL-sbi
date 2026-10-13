# Carrier asymmetry and thermal-model dependence in neural transport decomposition

## Abstract

Separating lattice and bipolar heat from transport measurements depends on assumptions about carrier dynamics and thermal conduction. We compare a corrected two-band reference model with five extensions that relax shared carrier parameters, allow positive non-monotone lattice conductivity or introduce a separate rising heat channel. Each neural estimator uses 588,000 training simulations, 12,000 validation simulations and 6,000 independent test curves. On 509 commonly scored lattice-upturn cases, flexible independent-band inference increases nominal 95% lattice coverage from 41.7% to 97.2%, while widening median intervals from 0.699 to 9.983 W m⁻¹ K⁻¹. Absolute slope error does not improve on the common selected subset. Across 1,528 experimental curves from 649 papers, inferred lattice trends remain sensitive to the thermal model. Same-model undercoverage and cross-model attribution failures show that relaxed physical restrictions do not establish calibrated or unique heat-channel separation. These results identify the assumptions and external constraints needed to interpret corpus-scale neural transport inversion.

## Introduction

Conventional unipolar subtraction estimates a lattice remainder from measured total conductivity and a Lorenz prescription [1]. When both carrier types contribute, the remainder can include bipolar heat. Joint inversion of electrical and thermal curves supplies a model-assisted decomposition, but agreement with those curves does not establish the correctness of its internal channels.

Independent heat-channel constraints are valuable: low-temperature magnetic-field separation has exposed limitations of conventional Lorenz estimates in a bismuth–antimony telluride alloy [2]. Such low-temperature results do not directly validate a high-temperature corpus decomposition. Reported lattice-conductivity increases in cubic GeTe also motivate testing a lattice family that allows upturns [3].

The corrected reference release uses a floor plus a decreasing lattice power law and shared mobility/scattering parameters between bands. Its synthetic stress experiments demonstrate that departures from these restrictions can bias channel estimates. Here we relax those assumptions explicitly, retaining the corrected carrier-statistics implementation and frozen experimental corpus. Amortised inference makes repeated approximate inversion computationally practical [4,5]; its uncertainty is evaluated independently rather than assumed accurate [6].


## Results

### Neural inference and independent same-model tests

The amortised estimator reuses a trained conditional density network across observations (Fig. 1). The architecture contains three hidden layers and separate continuous-density and sign heads. Full training and sampling equations are provided in Methods. The five estimators completed 178–900 epochs; optimisation histories alone do not establish uncertainty calibration.

@FIG1

Supplementary Table 1 reports nominal 95% pointwise coverage, conditional on scored test cases. The independent-band flexible-lattice model scores 5,986 of 6,000 curves and admits 5,842; lattice and bipolar coverages are 91.7% and 92.0%. Lattice coverage across the five extensions ranges from 90.9% to 94.7%, below the nominal 95% target. Successful training alone does not establish calibration.


### Shared narrow-gap lattice-upturn test

The shared 1,000-curve test has band gaps from 0.10 to 0.50 eV and increasing true lattice heat. It directly tests the original structural restriction. The slope statistic in Supplementary Table 2 is the median model-C minus true-lattice slope on admitted fixed-window cases with finite original four-estimate endpoints. Its denominator can change across models.


The separate-extra model still imposes a non-increasing lattice. Thus this true-phonon-upturn stress tests a departure from that alternative's assumptions; a rising total can be represented without necessarily assigning it to the correct physical channel. Flexible-lattice recovery must likewise be judged from known truth and interval coverage, not total-curve agreement alone.

### Common-case stress comparisons

To separate recovery changes from selection changes, Supplementary Table 4 and Fig. 2 compare the narrow-gap lattice-upturn test on 509 curves scored by every model. Interval width is in W m^-1 K^-1. Slope errors use a further common subset of 87 admitted curves with finite original four-estimate endpoints. Absolute errors are included because a small signed median can conceal large errors of opposing signs.


The coverage increase is accompanied by a much larger median lattice interval width: 0.699 to 9.983 W m^-1 K^-1 on the same scored cases. On the 87-curve common slope subset, median absolute slope error changes from 0.541 to 0.661. Thus higher coverage does not establish generally more accurate point estimates. The much smaller signed error in the model-specific subset in Supplementary Table 2 must not be read as an improvement of the same size on fixed cases.

@FIG2

Supplementary Table 5 reports the inherited minority mobility-prefactor stress tests. The imposed ratios are 0.1 and 10; other stress-generation assumptions remain those of the corrected release. Each test's coverage denominator is the set scored by every model. For ratios of 0.1 and 10, bipolar coverage changes from 75.5% and 74.9% in the reference model to 89.4% and 90.5% with independent bands, on 790 and 648 common scored curves, respectively. These tests isolate a prefactor departure and do not exhaust all possible temperature-exponent or scattering departures.


### Experimental corpus and selection-controlled comparison

Figure 3 and Supplementary Table 3 compare median per-curve C-minus-B slope shifts. Brackets are 95% paper-clustered intervals. The all-model comparison uses 1528 curves from 649 papers. The reference median shift is −0.107 [−0.122, −0.092], compared with −0.593 [−0.702, −0.481] for independent bands with a flexible lattice and −0.227 [−0.242, −0.208] for independent bands with a rising channel. These are dimensionless slope differences, not directly measured lattice corrections. The paired change subtracts the reference model shift curve by curve on this same population.

@FIG3


Native populations differ because the posterior, admission and positive-endpoint masks change. An aggregate shift between native populations therefore combines changed inference and changed selection. The common-population comparison addresses the latter distinction within the retained subset, but does not generalise automatically to excluded or unscored curves.

### Transfer between thermal hypotheses

Every estimator is also evaluated on the same two independently generated 1,000-curve narrow-gap datasets: independent carriers with a separate rising channel, and independent carriers with a flexible lattice. Coverage in Fig. 4 and Supplementary Table 6 is conditional on each estimator's scored cases. The source model and inference model need not match. The cross-model inference uses a common recorded random seed of 7300; its finite-draw summaries can differ slightly from the separate native narrow-gap evaluations, which use model-specific inference seeds. When a flexible-lattice estimator is applied to rising-channel truth, the independent-band model has 74.5% lattice coverage on 999 scored curves, despite 99.3% total-conductivity coverage. In the reverse transfer, the independent-band rising-channel model scores only 268 curves and has 25.8% lattice coverage. This transfer comparison probes attribution when the assumed thermal family changes; it is not evidence for either family's prevalence in experimental materials.

@FIG4


### Effective scattering and secondary analyses

Supplementary Table 7 reports ambiguous effective-scattering classifications among admitted curves. Ambiguity here means a posterior probability between 0.2 and 0.8, inclusive, that the exponent is below 0.5. This is an operational summary of the model parameter, not identification of a microscopic scattering mechanism. Separate minority parameters can remain weakly constrained even when a transport curve passes the admission screen.


The released supplementary analyses additionally recompute material-family groups containing at least 80 selected curves, bipolar-fraction strata, Seebeck-rollover groups, and containment thresholds from 0 to 0.95. These are conditional descriptive comparisons, not multiple independent validations. The bipolar stratification uses the marginal-median bipolar conductivity divided by the observed total at 750 K; matched-draw fractions using model totals are retained separately.


## Discussion

These experiments replace two fixed modelling restrictions with explicit alternatives. The independent-band model removes the equality constraint on the selected mobility and scattering parameters. The flexible-lattice model removes imposed monotonicity. The separate-extra model offers a different attribution hypothesis while retaining the original lattice form. Agreement or disagreement between these alternatives is evidence about model sensitivity, not direct measurement of the separate channels.

The alternatives differ in parameter dimension, prior shape and allowed thermal range as well as in physical attribution. For example, the chosen extra-channel amplitude permits at most 0.78125 W m^-1 K^-1 at 750 K, whereas the spline nodes have a much broader support. A performance difference therefore cannot be attributed exclusively to the presence of a particular mechanism or to added flexibility, independently of these prior choices.

Within the extra-channel model, the amplitude has a continuous nonnegative prior, so strictly positive amplitude has probability one before observing data. Its posterior positivity must not be presented as evidence that a separate mechanism exists. The comparisons do not compute model probabilities or a model-averaged decomposition.

Coverage below nominal indicates that the reported intervals do not fully represent known-truth uncertainty under the corresponding test distribution. Larger model flexibility can also expose broad or non-Gaussian inverse solutions. A covariance matrix cannot by itself resolve these degeneracies. The Gaussian approximation, prior support and selected observation model must therefore remain part of the interpretation.

Wider posterior bands can also increase the containment-based admission rate. Additional admitted experimental curves must not automatically be counted as additional accurately decomposed specimens.

In the decreasing-lattice synthetic control, 608 of 985 admitted curves showed an apparent conventional upturn despite decreasing true lattice heat. That establishes a simulator-internal mechanism, not validation of every experimental decomposition. Similarly, synthetic upturn error cannot be translated into a real-corpus correction without assumptions about prevalence, effect distribution and selection. No such prevalence bound is claimed here.

### Limitations and outlook

Non-parabolic and multi-valley bands, specimen-dependent measurement errors, alternative lattice priors, and external thermal separation remain untested. Independent Hall measurements or gap measurements were not supplied as withheld validation. The lost historical corpus filter and frozen-export limitations of the corrected reference model persist. A restricted or flexible forward model can fit the observed curves while assigning heat differently.

The contribution of this study is an explicit comparison of carrier asymmetry and thermal-model flexibility using held-out simulations, shared stress tests and selection-controlled corpus statistics. The two original equality/monotonicity assumptions are relaxed in specified variants. Unique separation and fully calibrated experimental uncertainty are not established by that change alone.


## Methods

### Corpus and reference model

The frozen corpus contains 13,256 curves from 2,754 source papers in Starrydata [7]. The original 50 features comprise electrical conductivity, Seebeck coefficient and total thermal conductivity on 16 temperatures, together with the observation-window endpoints. Historical selection and digitisation limitations of the corrected manuscript remain applicable. No new raw export or source-publication audit was performed.

The features are log10 electrical conductivity, Seebeck coefficient in microvolts per kelvin, and natural-log total thermal conductivity, followed by the upper and lower temperatures divided by 1,000, in that order. Property curves are linearly interpolated within the common recorded window. The historical 407-record plausibility filter has lost its implementation; the retained sample identifiers, rather than a reconstructed general filtering rule, define that part of the frozen corpus. Historical removal of 32 extreme Seebeck records is documented rather than newly verified.

The corrected shared-band, monotone-lattice reference checkpoint and its inference arrays are retained as a frozen comparator; it was not retrained in this study. Its prior, observation model, corrected charge-neutrality solver and Fermi-integral conventions remain the reference implementation. The new analysis does not reinterpret those archived results as independent experimental validation.

### Carrier transport with independent band parameters

Charge neutrality and the two-band single-parabolic-band transport equations are retained. For band j, the non-degenerate mobility prefactor, temperature exponent and scattering exponent enter

$$
\mu_j(T,\eta_j)=\mu_{j,300}\left(\frac{T}{300\,\mathrm K}\right)^{p_j}
\frac{F_{r_j+1/2}(\eta_j)}{F_{1/2}(\eta_j)}
\frac{\Gamma(3/2)}{\Gamma(r_j+3/2)}.
$$

In the independent-band variants, log10 of the minority-to-majority non-degenerate 300 K mobility-prefactor ratio is uniform on [-1,1]. The minority temperature exponent is independently uniform on [-3.5,2] and its scattering exponent on [-1,2]. The majority prefactor retains the doping-dependent prior. These bounds are research assumptions. The prefactor ratio is not a fixed ratio of the actual mobilities at all temperatures.

The band-specific scattering exponents enter both mobility and the band transport integrals. The signed total Seebeck coefficient is conductivity-weighted. The thermal terms satisfy

$$
\kappa_{\mathrm e}=(L_p\sigma_p+L_n\sigma_n)T,
\qquad
\kappa_{\mathrm{bip}}=\frac{\sigma_p\sigma_n}{\sigma_p+\sigma_n}(S_p-S_n)^2T.
$$

The shared-band reference model is recovered when the prefactor ratio is one and the two exponents match across bands. This nesting was tested numerically, including the released mobility-ratio stress cases.

### Alternative thermal models

The extra-channel variant retains the original lattice form but adds a distinct rising contribution:

$$
\kappa=\kappa_{\mathrm e}+\kappa_{\mathrm{bip}}+\kappa_{\mathrm L}+\kappa_{\mathrm{extra}},\qquad
\kappa_{\mathrm L}=\kappa_{\min}+A(300\,\mathrm K/T)^\omega,
\qquad \kappa_{\mathrm{extra}}=B(T/300\,\mathrm K)^3.
$$

Here omega is nonnegative and B is uniform on [0,0.05] W m^-1 K^-1. The extra contribution is not automatically identified as phonon or radiative heat. A cubic rising shape is a chosen hypothesis, not a demonstrated mechanism in each specimen.

The flexible-lattice variant instead uses a positive PCHIP interpolation in log conductivity versus log temperature:

$$
\kappa_{\mathrm L}(T)=10^{g(\ln T)}\;\mathrm{W\,m^{-1}K^{-1}}.
$$

The interpolation nodes lie at 285, 400, 550, 750, 1000 and 1250 K. Their log10 conductivities are independently uniform from -3 to 2, corresponding to 0.001–100 W m^-1 K^-1. This permits increasing, decreasing and turning curves while guaranteeing positivity. It does not exactly nest the original floor-plus-power-law family in general. Knot choice and the broad independent-node prior remain assumptions requiring sensitivity assessment. An initial narrower prior is retained separately and excluded from the main tables.

The support expansion followed inspection of the inherited benchmark ranges: 44 of 1,000 narrow-gap upturn curves exceeded the initial upper bound of 30 W m^-1 K^-1, and two of 6,000 base test curves fell below the initial lower bound of 0.01 W m^-1 K^-1. Consequently, the inherited stress sets are development benchmarks rather than untouched tests of model selection. The newly generated same-model test draws are independently seeded and excluded from training and early stopping.

The unchanged base prior uses uniform log10 net carrier concentration from 16 to 21 in cm^-3, log10 majority mass from -1.3 to 0.7 and log10 minority mass from -1.7 to 1.0 in electron-mass units, and log10 band gap from -1.5 to 0.55 in eV. The majority temperature and scattering exponents have bounds [-3.5,2] and [-1,2]. The log10 mobility interval is centred at c = 3.1 - 0.5(log10 N - 17), with limits c - 1.8 and c + 1.2 in cm^2 V^-1 s^-1. Where the original lattice form is retained, log10 A is uniform on [-1,1.2], the nonnegative exponent on [0,3], and the floor on [0,0.7] W m^-1 K^-1. Each carrier sign has prior probability one half. Lower and upper window endpoints are sampled from [285,500] and [500,1250] K, rejecting spans below 200 K. The joint prior is subsequently restricted by the peak-zT condition.

### Experimental design and inference

Five variants are fitted: independent bands, a rising channel, a flexible lattice, independent bands with a rising channel, and independent bands with a flexible lattice. The continuous parameter dimensions are respectively 13, 11, 13, 14 and 16. The archived reference model has ten continuous parameters. The binary carrier-sign head is retained.

Each new model is trained on 588,000 simulations with 12,000 validation cases, using the retained three-layer 256-unit network and a dimension-adjusted full Gaussian precision head. Training has a 900-epoch cap and the original validation-based early-stopping rule. All seeds, software versions, checkpoint hashes and model priors are recorded. The Gaussian approximation and its factorisation from the carrier-sign head remain limitations.

The observation generator retains independent 2% multiplicative perturbations before interpolation. It does not represent all experimental systematics, correlated calibration errors or additive Seebeck errors. Peak zT support is checked on the 16-point window grid. At inference, 128 draws are targeted within 8,192 proposals; at least 64 are required for scoring. Admission retains the original latent-band containment threshold of 0.75. This is an operational screen, not a calibrated significance test.

### Neural density estimation and amortisation

The network approximates the simulator posterior across many possible observations, rather than optimising each experimental curve separately. Simulator generation and network training constitute the up-front cost; the trained weights are reused for all subsequent curves. This is the meaning of amortised inference. Experimental corpus curves are not training labels. This study uses an established conditional Gaussian architecture, not a newly invented neural-network algorithm.

Inputs are the 50 features specified above. The 50-dimensional input and D continuous target coordinates are standardised using means and standard deviations computed only on the 588,000 training examples. Three fully connected hidden layers each contain 256 units with SiLU activation. Four linear heads output a D-dimensional mean, D diagonal log-precision factors, D(D−1)/2 strictly lower-triangular factors and one carrier-sign logit. D is 13, 11, 13, 14 and 16 for the independent-band, rising-channel, flexible-lattice, independent-band rising-channel and independent-band flexible-lattice variants, respectively. Continuous-head weights and biases are initialised to zero; the sign head retains its default initialisation.

The conditional density factorises between standardised continuous coordinates y and binary carrier sign s given standardised input x. With sign logit a and lower-triangular factor A, the precision is A Aᵀ, not the covariance. The diagonal entries are exp(d), with d clipped to [−3,6], and the strictly lower-triangular entries are unconstrained network outputs.

@NN1

The per-example training objective is the Gaussian negative log likelihood plus binary cross entropy; its minibatch mean is minimised. The diagonal-factor term is the log-determinant contribution. No experimental channel labels enter the loss.

@NN2

Optimisation uses AdamW with initial learning rate 0.0015, weight decay 10⁻⁵ and batch size 1,024. Gradients are clipped to norm 5. Validation is evaluated in batches of 4,096. ReduceLROnPlateau halves the learning rate after its patience of six validation epochs. A checkpoint is replaced only when validation loss improves by more than 10⁻⁴; training stops after 50 epochs without such improvement or at 900 epochs. A fixed permutation with seed 3 defines the training–validation split. Training seeds are 6101, 6111, 6121, 6131 and 6141 in the variant order above. The saved checkpoint with the best qualifying validation loss is used for inference, not necessarily the last epoch.

Network training uses single precision; the physical forward model uses double precision. Random generators are seeded, deterministic PyTorch algorithms are requested, TF32 is disabled and four CPU threads are configured. The recorded environment uses PyTorch 2.11.0 with CUDA 12.8 on an NVIDIA GeForce RTX 5060 Laptop GPU. These settings record reproducibility controls and do not imply bitwise agreement across software or hardware versions. Completed epochs and selected checkpoint epochs are reported in Supplementary Table 8. Only one training seed per variant was evaluated. Reaching the epoch cap is not a convergence certificate.

At inference, continuous proposals are sampled by a triangular solve, then transformed back to the simulator coordinates. Sign proposals are sampled independently conditional on the same input. Rejection by the prior bounds and peak-zT support produces a truncated approximate neural posterior; this is not an exact Bayesian correction of the density approximation.

@NN3

The Gaussian can encode linear covariance but cannot generally express disconnected or strongly non-Gaussian solutions. Conditional independence of sign and continuous parameters is another restriction. Validation NLL is an optimisation criterion, not proof of calibrated uncertainty, and NLL values should not be ranked across targets of different dimension. Independent known-truth coverage tests, transfer tests and selection counts therefore accompany the network. Simulation-based rank calibration, flexible-density alternatives, training-seed replication and comparison with per-curve MCMC remain outstanding; none is claimed to have been completed.

### Validation and estimands

Independent same-model tests contain 6,000 curves per new estimator. Additional narrow-gap sets and shared reference model, mobility-asymmetry and lattice-upturn stress sets assess selected departures. Pointwise channel coverage is conditional on scored curves; it is distinct from simultaneous curve coverage. Unscored and admitted counts are reported explicitly. Relative-error summaries exclude truth values at or below 1e-12, with included counts recorded in the released diagnostics.

Experimental estimates preserve A as the Kim subtraction, B as subtraction using posterior median unipolar Lorenz number, and C as posterior median model lattice heat. Cprime_bip subtracts median bipolar heat from B. Cprime_all additionally subtracts median extra heat. These subtractions use marginal medians; matched-draw fractions are stored separately because medians do not generally add.

All headline slopes use positive endpoints at 400 and 750 K. Native comparison sets require finite slopes for all five estimates. Baseline-common and all-model-common sets additionally impose the corresponding comparison models' selection rules. Intervals use 2,000 paper-clustered bootstrap resamples; a nested matched-draw calculation is also released. These intervals do not integrate over physical-model choice or all measurement error.

The slope is the logarithm of the 750 K to 400 K conductivity ratio divided by the logarithm of 750/400. Positive slopes denote increasing conductivity. It is computed only when the measured window spans both temperatures; nonpositive endpoints are excluded rather than replaced with a floor.


## Data availability

The frozen experimental corpus, sample identifiers, synthetic test data, inference arrays and figure source data are included in the accompanying research archive. Experimental curves originate from Starrydata [7]; this study does not provide a newly audited raw export. A persistent public data deposit and accession identifier have not yet been established and must be supplied before submission. Availability and licensing of the original source data must be confirmed by the authors.

## Code availability

The accompanying archive contains the reference implementation, extended physical models, neural checkpoints, training histories, seeds, environment records and analysis scripts. The reference checkpoint is the corrected software release v5; it is included as a frozen comparator, not as a newly retrained model or separate published theory. New runs are stored under runs/v6_main. Reproduction instructions and source hashes are included. A public versioned repository and persistent identifier remain to be supplied by the authors.

## References

[1] Kim HS et al. Characterization of Lorenz number with Seebeck coefficient measurement. APL Materials 3, 041506 (2015). doi:10.1063/1.4908244.

[2] Candolfi C et al. Hidden in plain heat: anomalous Lorenz number in the thermoelectric alloy Bi0.4Sb1.6Te3. Nature Communications 16, 11528 (2025). doi:10.1038/s41467-025-66578-y.

[3] Kielar S et al. Anomalous lattice thermal conductivity increase with temperature in cubic GeTe correlated with strengthening of second-nearest neighbor bonds. Nature Communications 15, 6981 (2024). doi:10.1038/s41467-024-51377-8.

[4] Papamakarios G and Murray I. Fast epsilon-free inference of simulation models with Bayesian conditional density estimation. Advances in Neural Information Processing Systems 29 (2016).

[5] Cranmer K, Brehmer J and Louppe G. The frontier of simulation-based inference. PNAS 117, 30055–30062 (2020).

[6] Talts S et al. Validating Bayesian inference algorithms with simulation-based calibration. arXiv:1804.06788 (2018).

[7] Katsura Y et al. Starrydata: from published plots to shared materials data. Science and Technology of Advanced Materials: Methods 5, 2506976 (2025). doi:10.1080/27660400.2025.2506976.
