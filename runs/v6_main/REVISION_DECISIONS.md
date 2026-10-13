# Manuscript revision decisions

The computational rerun is complete. The equality and monotonicity constraints have been relaxed in specified models; unique channel separation and fully calibrated uncertainty have not been established.

The main result is a trade-off: flexible lattice models achieve much higher upturn-test coverage with substantially wider intervals. They do not improve median absolute slope error on the common selected subset. Do not describe the rerun as a general improvement in point-estimate accuracy.

## Verified changes

- Independent-band variants infer a minority/majority mobility-prefactor ratio and separate minority temperature and scattering exponents.
- Flexible-lattice variants use a positive six-knot curve that can rise, fall or turn.
- Separate-channel variants add B(T/300)^3 while retaining the non-increasing lattice model. This is an alternative heat attribution, not a flexible lattice.
- Five estimators were trained using 600,000 simulations each (588,000 training and 12,000 validation), then tested independently and applied to the frozen 13,256-curve corpus. The 72 original release files remain unchanged.

## Common-case upturn test

Coverage below uses exactly 509 shared scored curves. Slope errors use exactly 87 shared admitted curves spanning 400–750 K with finite original four-estimate endpoints.

| Model | Lattice coverage (nominal 95%) | Median interval width (W/m/K) | Median absolute slope error |
|---|---:|---:|---:|
| baseline | 41.7% | 0.699 | 0.541 |
| mobility_spline | 97.2% | 9.983 | 0.661 |
| mobility_extra | 42.5% | 0.898 | 0.600 |
| mobility | 45.4% | 0.972 | 0.594 |
| spline | 95.2% | 6.446 | 0.822 |
| extra | 41.3% | 0.751 | 0.562 |

## What should change in the paper

1. Replace the single shared-mobility assumption with the explicit independent-band parameterisation and bounds in the tested variants. Do not call the inferred scattering exponents independently measured mechanisms.
2. Present the flexible positive lattice as the variant that removes imposed lattice monotonicity. Keep the rising extra channel distinct in every equation, table and conclusion.
3. Replace the old corpus headline with the new model-specific and common-population statistics. Different admission and positive-endpoint selections must remain visible.
4. Report same-model undercoverage, cross-model failures and interval widths. A small signed median error is not a demonstration of unbiased recovery.
5. Retain limitations concerning the Gaussian posterior, broad shape priors, measurement errors, non-parabolic bands, historical corpus filtering and missing external validation.

## Common experimental population

All models share 1528 selected curves from 649 source papers. Values are median per-curve C-minus-B slope shifts, with 95% paper-clustered intervals.

| Model | Median shift | 95% interval |
|---|---:|---:|
| baseline | -0.107 | [-0.122, -0.092] |
| mobility_spline | -0.593 | [-0.702, -0.481] |
| mobility_extra | -0.227 | [-0.242, -0.208] |
| mobility | -0.145 | [-0.165, -0.132] |
| spline | -0.373 | [-0.456, -0.308] |
| extra | -0.181 | [-0.199, -0.163] |

## What remains uncertain

The preferred attribution for any particular experimental specimen cannot be established from these comparisons alone. Same-model tests assess the stated simulator distribution, not experimental truth. Cross-model tests demonstrate that a model can reproduce total heat while assigning it incorrectly. The continuous extra-channel prior also does not constitute evidence that an extra mechanism is present.
The broad spline prior is deliberately permissive. Only one expanded knot/range specification forms the main run, and the initial narrower-prior run was superseded. The range was expanded after inspecting inherited benchmark support, so those inherited tests are development benchmarks, not untouched model-selection validation. This is not a systematic prior-sensitivity analysis or an externally validated solution to thermal identifiability.

## Reproducibility and verification

Detailed support: stress_comparison.json, comparison.json, each model’s test_diagnostics.json and supplementary_analysis.json, and cross_model/*.diagnostics.json. Retained draws and source arrays remain in this working repository. archive_verification.json records reconstruction checks; verification covers counts and bounds throughout each archive and recomputes forward channels for a stated sample of curves.
A documented cache-only change avoided repeated array decompression during bootstrapping. Before/after statistics were exactly equal on its regression check; original and amended manifests are retained in cache_fix_amendment.json.

The supplied narrow-gap baseline was replayed with the latest corrected checkpoint. Scored/admitted masks and the aggregate lattice/bipolar coverage rates matched exactly; median slope errors differed by less than 0.000001. Individual arrays were not bitwise identical, and some individual slope draws differed more. The comparison retains the archived baseline arrays; see baseline_replay/verification.json and metric_comparison.json for the detailed limits of this reproduction.
