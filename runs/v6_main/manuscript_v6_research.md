# Carrier asymmetry and lattice flexibility in model dependent thermal transport decomposition

Research draft generated from completed computational outputs. This manuscript describes a model-sensitivity study. Independent external validation remains outstanding.

## Abstract

Separating lattice, unipolar electronic and bipolar heat from measured electrical conductivity, Seebeck coefficient and total thermal conductivity requires physical assumptions. We extend a corrected two-band transport inference model by allowing independent band mobility prefactors, temperature exponents and scattering exponents, and by testing two alternative thermal descriptions: a positive flexible lattice curve and a separate rising thermal channel. Five newly trained estimators are compared with the released baseline. Each new estimator uses 600,000 simulator examples for training and validation and an independent 6,000-curve same-model test, together with shared stress datasets. The experimental comparison retains the frozen 13,256-curve corpus and reports changes both within model-specific selected populations and on common curves. Independent coverage, stress recovery and selection changes are reported separately. These experiments quantify sensitivity within the tested model families and priors; they do not establish unique thermal separation from three transport curves.

On 509 commonly scored narrow-gap lattice-upturn curves, nominal 95% lattice coverage changes from 41.7% for the baseline to 97.2% for the independent-band flexible-lattice model. However, the latter's independent same-model lattice and bipolar coverages are 91.7% and 92.0%, respectively, so full calibration is not established. The coverage gain is accompanied by substantially wider intervals and does not improve median absolute slope error on the common selected subset.

## 1 Introduction

Conventional unipolar subtraction estimates a lattice remainder from measured total conductivity and a Lorenz prescription [1]. When both carrier types contribute, the remainder can include bipolar heat. Joint inversion of electrical and thermal curves supplies a model-assisted decomposition, but agreement with those curves does not establish the correctness of its internal channels.

Independent heat-channel constraints are valuable: low-temperature magnetic-field separation has exposed limitations of conventional Lorenz estimates in a bismuth–antimony telluride alloy [6]. Such low-temperature results do not directly validate a high-temperature corpus decomposition. Reported lattice-conductivity increases in cubic GeTe also motivate testing a lattice family that allows upturns [7].

The corrected baseline release uses a floor plus a decreasing lattice power law and shared mobility/scattering parameters between bands. Its synthetic stress experiments demonstrate that departures from these restrictions can bias channel estimates. Here we relax those assumptions explicitly, retaining the corrected carrier-statistics implementation and frozen experimental corpus. Amortised inference makes repeated approximate inversion computationally practical [2,3]; its uncertainty is evaluated independently rather than assumed accurate [4].

## 2 Methods

### 2.1 Corpus and baseline

The frozen corpus contains 13,256 curves from 2,754 source papers in Starrydata [5]. The original 50 features comprise electrical conductivity, Seebeck coefficient and total thermal conductivity on 16 temperatures, together with the observation-window endpoints. Historical selection and digitisation limitations of the corrected manuscript remain applicable. No new raw export or source-publication audit was performed.

The features are log10 electrical conductivity, Seebeck coefficient in microvolts per kelvin, and natural-log total thermal conductivity, followed by the upper and lower temperatures divided by 1,000, in that order. Property curves are linearly interpolated within the common recorded window. The historical 407-record plausibility filter has lost its implementation; the retained sample identifiers, rather than a reconstructed general filtering rule, define that part of the frozen corpus. Historical removal of 32 extreme Seebeck records is documented rather than newly verified.

The released v5 checkpoint and arrays are retained as the baseline. Its prior, observation model, corrected charge-neutrality solver and Fermi-integral conventions remain the reference implementation. The new analysis does not reinterpret those archived results as independent experimental validation.

### 2.2 Carrier transport with independent band parameters

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

The shared-band baseline is recovered when the prefactor ratio is one and the two exponents match across bands. This nesting was tested numerically, including the released mobility-ratio stress cases.

### 2.3 Alternative thermal models

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

### 2.4 Experimental design and inference

Five variants are fitted: mobility, extra, spline, mobility_extra and mobility_spline. The continuous parameter dimensions are respectively 13, 11, 13, 14 and 16. The archived baseline has ten continuous parameters. The binary carrier-sign head is retained.

Each new model is trained on 588,000 simulations with 12,000 validation cases, using the retained three-layer 256-unit network and a dimension-adjusted full Gaussian precision head. Training has a 900-epoch cap and the original validation-based early-stopping rule. All seeds, software versions, checkpoint hashes and model priors are recorded. The Gaussian approximation and its factorisation from the carrier-sign head remain limitations.

The observation generator retains independent 2% multiplicative perturbations before interpolation. It does not represent all experimental systematics, correlated calibration errors or additive Seebeck errors. Peak zT support is checked on the 16-point window grid. At inference, 128 draws are targeted within 8,192 proposals; at least 64 are required for scoring. Admission retains the original latent-band containment threshold of 0.75. This is an operational screen, not a calibrated significance test.

### 2.5 Validation and estimands

Independent same-model tests contain 6,000 curves per new estimator. Additional narrow-gap sets and shared baseline, mobility-asymmetry and lattice-upturn stress sets assess selected departures. Pointwise channel coverage is conditional on scored curves; it is distinct from simultaneous curve coverage. Unscored and admitted counts are reported explicitly. Relative-error summaries exclude truth values at or below 1e-12, with included counts recorded in the released diagnostics.

Experimental estimates preserve A as the Kim subtraction, B as subtraction using posterior median unipolar Lorenz number, and C as posterior median model lattice heat. Cprime_bip subtracts median bipolar heat from B. Cprime_all additionally subtracts median extra heat. These subtractions use marginal medians; matched-draw fractions are stored separately because medians do not generally add.

All headline slopes use positive endpoints at 400 and 750 K. Native comparison sets require finite slopes for all five estimates. Baseline-common and all-model-common sets additionally impose the corresponding comparison models' selection rules. Intervals use 2,000 paper-clustered bootstrap resamples; a nested matched-draw calculation is also released. These intervals do not integrate over physical-model choice or all measurement error.

The slope is the logarithm of the 750 K to 400 K conductivity ratio divided by the logarithm of 750/400. Positive slopes denote increasing conductivity. It is computed only when the measured window spans both temperatures; nonpositive endpoints are excluded rather than replaced with a floor.

## 3 Results

### 3.1 Independent same-model tests

Table 1 reports nominal 95% pointwise coverage, conditional on scored test cases. Successful training alone does not establish calibration.

| Model | Scored / generated | Admitted | Lattice coverage percent | Bipolar coverage percent |
|---|---:|---:|---:|---:|
| mobility_spline | 5986/6000 | 5842 | 91.7 | 92.0 |
| mobility_extra | 5989/6000 | 5882 | 93.3 | 91.7 |
| mobility | 5998/6000 | 5856 | 94.7 | 91.8 |
| spline | 5992/6000 | 5847 | 90.9 | 92.1 |
| extra | 5993/6000 | 5887 | 93.9 | 92.1 |

### 3.2 Shared narrow-gap lattice-upturn test

The shared 1,000-curve test has band gaps from 0.10 to 0.50 eV and increasing true lattice heat. It directly tests the original structural restriction. The table's slope statistic is the median model-C minus true-lattice slope on admitted fixed-window cases with finite original four-estimate endpoints. Its denominator can change across models.

| Model | Scored | Admitted | Lattice coverage percent | Bipolar coverage percent | Slope subset n | Median slope error |
|---|---:|---:|---:|---:|---:|---:|
| mobility_spline | 999 | 998 | 97.2 | 92.9 | 343 | -0.019 |
| mobility_extra | 656 | 634 | 36.2 | 91.6 | 182 | -0.702 |
| mobility | 599 | 577 | 40.7 | 82.6 | 154 | -0.693 |
| spline | 999 | 985 | 95.4 | 88.4 | 359 | -0.058 |
| extra | 619 | 571 | 37.3 | 85.3 | 174 | -0.660 |

The separate-extra model still imposes a non-increasing lattice. Thus this true-phonon-upturn stress tests a departure from that alternative's assumptions; a rising total can be represented without necessarily assigning it to the correct physical channel. Flexible-lattice recovery must likewise be judged from known truth and interval coverage, not total-curve agreement alone.

### 3.3 Experimental corpus and selection-controlled comparison

Table 3 compares median per-curve C-minus-B slope shifts. Brackets are 95% paper-clustered intervals. The all-model comparison uses 1528 curves from 649 papers. The paired change subtracts the baseline shift curve by curve on this same population.

| Model | Native paired n | Native C minus B | All-model-common C minus B | Paired change from baseline |
|---|---:|---:|---:|---:|
| baseline | 4312 | -0.165 [-0.184, -0.150] | -0.107 [-0.122, -0.092] | 0.000 [0.000, 0.000] |
| mobility_spline | 4187 | -0.452 [-0.499, -0.407] | -0.593 [-0.702, -0.481] | -0.425 [-0.540, -0.354] |
| mobility_extra | 4507 | -0.302 [-0.322, -0.287] | -0.227 [-0.242, -0.208] | -0.094 [-0.102, -0.087] |
| mobility | 5368 | -0.209 [-0.222, -0.194] | -0.145 [-0.165, -0.132] | -0.018 [-0.024, -0.014] |
| spline | 4225 | -0.577 [-0.683, -0.504] | -0.373 [-0.456, -0.308] | -0.231 [-0.284, -0.188] |
| extra | 3114 | -0.283 [-0.308, -0.254] | -0.181 [-0.199, -0.163] | -0.065 [-0.070, -0.059] |

Native populations differ because the posterior, admission and positive-endpoint masks change. An aggregate shift between native populations therefore combines changed inference and changed selection. The common-population comparison addresses the latter distinction within the retained subset, but does not generalise automatically to excluded or unscored curves.

### 3.4 Common-case stress comparisons

To separate recovery changes from selection changes, Table 4 compares the narrow-gap lattice-upturn test on 509 curves scored by every model. Interval width is in W m^-1 K^-1. Slope errors use a further common subset of 87 admitted curves with finite original four-estimate endpoints. Absolute errors are included because a small signed median can conceal large errors of opposing signs.

| Model | Lattice coverage percent | Median interval width | Median slope error | Median absolute slope error |
|---|---:|---:|---:|---:|
| baseline | 41.7 | 0.699 | -0.541 | 0.541 |
| mobility_spline | 97.2 | 9.983 | -0.241 | 0.661 |
| mobility_extra | 42.5 | 0.898 | -0.600 | 0.600 |
| mobility | 45.4 | 0.972 | -0.594 | 0.594 |
| spline | 95.2 | 6.446 | -0.606 | 0.822 |
| extra | 41.3 | 0.751 | -0.562 | 0.562 |

The coverage increase is accompanied by a much larger median lattice interval width: 0.699 to 9.983 W m^-1 K^-1 on the same scored cases. On the 87-curve common slope subset, median absolute slope error changes from 0.541 to 0.661. Thus higher coverage does not establish generally more accurate point estimates. The much smaller signed error in the model-specific subset in Table 2 must not be read as an improvement of the same size on fixed cases.

Table 5 reports the inherited minority mobility-prefactor stress tests. The imposed ratios are 0.1 and 10; other stress-generation assumptions remain those of the corrected release. Each test's coverage denominator is the set scored by every model. These tests isolate a prefactor departure and do not exhaust all possible temperature-exponent or scattering departures.

| Model | Mobility ratio | Common scored n | Lattice coverage percent | Bipolar coverage percent |
|---|---:|---:|---:|---:|
| baseline | 0.1 | 790 | 91.8 | 75.5 |
| mobility_spline | 0.1 | 790 | 98.3 | 82.7 |
| mobility_extra | 0.1 | 790 | 89.9 | 91.2 |
| mobility | 0.1 | 790 | 95.6 | 89.4 |
| spline | 0.1 | 790 | 92.8 | 72.1 |
| extra | 0.1 | 790 | 86.1 | 77.0 |
| baseline | 10 | 648 | 91.4 | 74.9 |
| mobility_spline | 10 | 648 | 98.4 | 86.0 |
| mobility_extra | 10 | 648 | 89.9 | 91.7 |
| mobility | 10 | 648 | 96.5 | 90.5 |
| spline | 10 | 648 | 92.8 | 70.2 |
| extra | 10 | 648 | 86.6 | 76.9 |

### 3.5 Transfer between thermal hypotheses

Every estimator is also evaluated on the same two independently generated 1,000-curve narrow-gap datasets: independent carriers with a separate rising channel, and independent carriers with a flexible lattice. Coverage in Table 6 is conditional on each estimator's scored cases. The source model and inference model need not match. The cross-model inference uses a common recorded random seed of 7300; its finite-draw summaries can differ slightly from the separate native narrow-gap evaluations, which use model-specific inference seeds. This transfer comparison probes attribution when the assumed thermal family changes; it is not evidence for either family's prevalence in experimental materials.

| Inference model | Truth model | Scored / generated | Lattice coverage percent | Bipolar coverage percent |
|---|---|---:|---:|---:|
| baseline | mobility_extra | 662/1000 | 58.1 | 69.3 |
| baseline | mobility_spline | 164/1000 | 21.8 | 65.1 |
| mobility_spline | mobility_extra | 999/1000 | 74.5 | 91.6 |
| mobility_spline | mobility_spline | 996/1000 | 90.2 | 95.5 |
| mobility_extra | mobility_extra | 999/1000 | 92.6 | 94.9 |
| mobility_extra | mobility_spline | 268/1000 | 25.8 | 85.9 |
| mobility | mobility_extra | 867/1000 | 74.8 | 84.6 |
| mobility | mobility_spline | 312/1000 | 25.8 | 80.8 |
| spline | mobility_extra | 781/1000 | 62.6 | 70.8 |
| spline | mobility_spline | 741/1000 | 82.4 | 76.2 |
| extra | mobility_extra | 743/1000 | 83.7 | 75.2 |
| extra | mobility_spline | 145/1000 | 23.9 | 68.7 |

### 3.6 Effective scattering and secondary analyses

Table 7 reports ambiguous effective-scattering classifications among admitted curves. Ambiguity here means a posterior probability between 0.2 and 0.8, inclusive, that the exponent is below 0.5. This is an operational summary of the model parameter, not identification of a microscopic scattering mechanism. Separate minority parameters can remain weakly constrained even when a transport curve passes the admission screen.

| Model | Admitted n | Ambiguous majority/shared exponent | Ambiguous minority exponent |
|---|---:|---:|---:|
| mobility_spline | 10740 | 5575 | 9445 |
| mobility_extra | 8210 | 2362 | 6082 |
| mobility | 9604 | 2621 | 7891 |
| spline | 7736 | 1975 | shared parameter |
| extra | 5623 | 792 | shared parameter |

The released supplementary analyses additionally recompute material-family groups containing at least 80 selected curves, bipolar-fraction strata, Seebeck-rollover groups, and containment thresholds from 0 to 0.95. These are conditional descriptive comparisons, not multiple independent validations. The bipolar stratification uses the marginal-median bipolar conductivity divided by the observed total at 750 K; matched-draw fractions using model totals are retained separately.

## 4 Discussion

These experiments replace two fixed modelling restrictions with explicit alternatives. The independent-band model removes the equality constraint on the selected mobility and scattering parameters. The flexible-lattice model removes imposed monotonicity. The separate-extra model offers a different attribution hypothesis while retaining the original lattice form. Agreement or disagreement between these alternatives is evidence about model sensitivity, not direct measurement of the separate channels.

The alternatives differ in parameter dimension, prior shape and allowed thermal range as well as in physical attribution. For example, the chosen extra-channel amplitude permits at most 0.78125 W m^-1 K^-1 at 750 K, whereas the spline nodes have a much broader support. A performance difference therefore cannot be attributed exclusively to the presence of a particular mechanism or to added flexibility, independently of these prior choices.

Within the extra-channel model, the amplitude has a continuous nonnegative prior, so strictly positive amplitude has probability one before observing data. Its posterior positivity must not be presented as evidence that a separate mechanism exists. The comparisons do not compute model probabilities or a model-averaged decomposition.

Coverage below nominal indicates that the reported intervals do not fully represent known-truth uncertainty under the corresponding test distribution. Larger model flexibility can also expose broad or non-Gaussian inverse solutions. A covariance matrix cannot by itself resolve these degeneracies. The Gaussian approximation, prior support and selected observation model must therefore remain part of the interpretation.

Wider posterior bands can also increase the containment-based admission rate. Additional admitted experimental curves must not automatically be counted as additional accurately decomposed specimens.

The known-truth control from the preceding audit remains useful: 608 of 985 admitted curves showed an apparent conventional upturn despite decreasing true lattice heat. That establishes a simulator-internal mechanism, not validation of every experimental decomposition. Similarly, synthetic upturn error cannot be translated into a real-corpus correction without assumptions about prevalence, effect distribution and selection. No such prevalence bound is claimed here.

## 5 Limitations and conclusion

Non-parabolic and multi-valley bands, specimen-dependent measurement errors, alternative lattice priors, and external thermal separation remain untested. Independent Hall measurements or gap measurements were not supplied as withheld validation. The lost historical corpus filter and frozen-export limitations of the corrected baseline persist. A restricted or flexible forward model can fit the observed curves while assigning heat differently.

The contribution of this rerun is an explicit comparison of carrier asymmetry and thermal-model flexibility using held-out simulations, shared stress tests and selection-controlled corpus statistics. The two original equality/monotonicity assumptions are relaxed in specified variants. Unique separation and fully calibrated experimental uncertainty are not established by that change alone.

## Data and code availability

The corrected v5 release is preserved. Version 6 modules, priors, seeds, training histories, checkpoint hashes, inference arrays, matched-draw fractions, validation tables and comparison masks accompany this draft. The run manifest identifies software versions and source hashes. Pilot and superseded narrower-prior runs are labelled separately and are not the source of the main result tables. No public repository URL or author details have been invented.

## References

[1] Kim HS et al. Characterization of Lorenz number with Seebeck coefficient measurement. APL Materials 3, 041506 (2015). doi:10.1063/1.4908244.

[2] Papamakarios G and Murray I. Fast epsilon-free inference of simulation models with Bayesian conditional density estimation. Advances in Neural Information Processing Systems 29 (2016).

[3] Cranmer K, Brehmer J and Louppe G. The frontier of simulation-based inference. PNAS 117, 30055–30062 (2020).

[4] Talts S et al. Validating Bayesian inference algorithms with simulation-based calibration. arXiv:1804.06788 (2018).

[5] Katsura Y et al. Starrydata: from published plots to shared materials data. Science and Technology of Advanced Materials: Methods 5, 2506976 (2025). doi:10.1080/27660400.2025.2506976.

[6] Candolfi C et al. Hidden in plain heat: anomalous Lorenz number in the thermoelectric alloy Bi0.4Sb1.6Te3. Nature Communications 16, 11528 (2025). doi:10.1038/s41467-025-66578-y.

[7] Kielar S et al. Anomalous lattice thermal conductivity increase with temperature in cubic GeTe correlated with strengthening of second-nearest neighbor bonds. Nature Communications 15, 6981 (2024). doi:10.1038/s41467-024-51377-8.
