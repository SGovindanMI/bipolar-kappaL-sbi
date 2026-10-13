# Corrections and validation report

The manuscript and repository have been revised together. The original files in Downloads were left unchanged. The supplied frozen observations and their source attribution are preserved; the forward model, checkpoint, posterior results, figures and numerical tables are replaced by a version 5 computation.

## What the corrected results say

| Quantity | Corrected result |
|---|---:|
| Eligible curves | 13,256 |
| Scored curves | 10,320 |
| Admitted curves | 7,379 |
| Admitted papers | 2,067 |
| Admitted curves spanning 400–750 K | 4,338 |
| Common positive-endpoint comparison set | 4,312 |
| Papers in that comparison | 1,233 |
| Lorenz replacement slope shift B − A | 0.003 [0.002, 0.005] |
| Model-lattice slope shift C − B | -0.165 [-0.184, -0.150] |
| Total model-lattice shift C − A | -0.180 [-0.197, -0.167] |
| Additive shift C′ − A | -0.182 [-0.201, -0.156] |

Intervals are 95% percentile bootstrap intervals over source papers within the relevant finite subset. These quantities are model-dependent. Changes from the old release reflect retraining, a corrected solver, full stated support restriction, more draws and explicit positive-endpoint exclusions; they do not isolate the solver change alone.

## Confirmed errors corrected

1. **Charge neutrality and numerical tails.** The solver expands its root bracket, checks the residual and evaluates Fermi-integral tails without out-of-range clamping. The high-doping example resolves η ≈ 281.43 at 300 K instead of stopping at 40. Inputs are promoted to float64. The lattice floor participates consistently in lattice heat, total heat and zT.
2. **Actual independent datasets.** The new computation uses 588,000 training and 12,000 validation examples, plus separately generated 6,000-example diagnostic calibration and 6,000-example test sets. They have distinct seeds. The corrected run completed 900 epochs, selected epoch 889, and stopped by `epoch_cap`.
3. **PIT interpretation.** Empirical Mahalanobis relabelling is explicitly a diagnostic. It is not represented as a transformation applied to the reported posterior draws.
4. **Thermal totals.** Model totals and bipolar fractions use matched draws. They are not reconstructed from measured conductivity or sums of marginal channel medians.
5. **Missing posterior draws.** Scattering probabilities divide by finite retained draws only. Missing slots no longer vote against the low-r class.
6. **Lorenz sign.** The manuscript now uses B − A = (LKim − Lpost)σmeasT and regenerates its signed values.
7. **Upturn definition.** Conventional estimator A and posterior-L estimator B are reported separately. Comparing grid points 8 and 15 is called a two-point upturn indicator, not a monotonicity test.
8. **Bootstrap consistency.** A shared implementation resamples only papers in the reported finite subset, with 2,000 resamples and an explicit seed. Nested intervals select matched posterior draws per curve.
9. **Calibration claims.** Fit-screen containment is distinguished from independent synthetic coverage. The manuscript does not claim that a selected real-data subset proves calibration.
10. **Lattice dependence.** Additive C′ remains dependent on the model used to infer its electronic and bipolar terms. Claims of independence from the lattice parameterisation were removed.
11. **Nonlinear attribution.** Ratios of population medians are not used to claim a fraction of the total effect due to bipolar heat. Median curves and median draw-specific slopes are distinguished.
12. **Physical interpretation of upturns.** Rising lattice heat is no longer universally described as impossible. Alternative mechanisms and genuine lattice behaviour are acknowledged.
13. **Input-derived stratification.** Seebeck rollover is recognised as reusing a network input and as mathematically coupled to the Kim subtraction. It is not called independent or model-free validation.
14. **Family dependence.** Family-specific results are described as associations, with shared source papers counted. Intervals including zero are not presented as equivalence tests.
15. **Degenerate mobility scaling.** The explanation now includes the Fermi-integral ratio and the limiting T^(pμ−r) scaling at fixed carrier density.
16. **Reproduction instructions.** Maintained command-line modules replace hidden notebook-only dependencies. Replacement notebooks call these modules without overwriting source code. Dependencies are pinned to the tested versions; old version 4T checkpoints and derived files are excluded from the corrected archive.
17. **Corpus provenance.** Methods disclose the absent raw snapshot and lost historical 407-record selection rule. The CSV parsing cache is keyed by source content and parser version, preventing stale reuse.
18. **Small values and numerical summaries.** Non-positive endpoints are counted and excluded from logarithmic comparisons instead of floored. Figures use finite-window slope terminology, curve-level labels and revised captions. All revised tables read one generated numerical summary.

## Completed validation

- Eleven regression tests passed, covering independent Fermi quadrature, high-doping neutrality, Lorenz limits, float32 promotion, channel identities, prior draws, Gaussian geometry, constrained sampling, missing-draw classification, subset bootstrapping and cache invalidation.
- A separate 45-case band-Lorenz comparison against direct quadrature had maximum relative discrepancy below 1.2 × 10⁻⁷. The tested domain is recorded, rather than claimed as a universal bound.
- Independent final-sampler test: 5,996 of 6,000 curves scored and 5,850 passed the fit screen. Nominal 95% pointwise interval coverage was 94.2% for lattice heat, 93.2% for bipolar heat, 89.3% for unipolar L and 98.7% for total heat. Parameter coverages ranged from 84.4% to 90.5%.
- Three independently generated 1,000-example stress datasets test true lattice upturns and minority mobility multipliers 0.1 and 10. For low-true-bipolar lattice-upturn cases, false bipolar assignment occurred in 13/214 scored cases and 12/160 admitted cases, using the explicit 2% truth / 10% inference definition. Full diagnostics are archived.

A draw-count sensitivity check retained 256 draws for 509 of 512 independently
selected test cases. Using nested prefixes, lattice coverage changed from 94.4%
with 128 draws to 95.0% with 256; bipolar coverage changed from 91.8% to 93.2%.
The median absolute lattice point-estimate change was 0.0030 W m⁻¹ K⁻¹. This
supports limited point-estimate stability on that subset, not universal tail
convergence or calibrated real-data posteriors.

## Limits that editing cannot remove

This is a corrected, reproducible **working research manuscript**, not a claim that every scientific uncertainty is resolved. Empirical interval coverage can depart materially from 95%, and the Gaussian approximation remains an approximation. The increasing-lattice stress test challenges a restriction that remains in the fitted real-data model. A flexible-lattice real-data refit, broader model comparison, withheld Hall/gap validation and a source-paper audit have not been performed. The missing historical filter cannot be reconstructed as a general rule without additional source material, and the raw snapshot was not supplied.

These are disclosed limitations rather than fabricated successful checks. The manuscript's title, abstract, results and discussion have been qualified accordingly. Author names and a public repository URL were omitted as requested; the original software copyright notice is preserved.

## Files and use

- `bipolar_kappaL_manuscript_corrected.docx`: revised manuscript, ten updated tables and four regenerated figures, with native Word mathematics retained.
- `bipolar-kappaL-sbi-corrected.zip`: source, checkpoint, frozen data, new inference/validation arrays, tests, figures, reproducibility instructions and SHA-256 manifest.
- This report maps the corrections and records scientific limits. The earlier review is retained separately for comparison.

## Final delivery checks

The corrected manuscript was rendered and all 23 pages visually inspected, including native equations, ten tables and four figures. The staged repository passed all 11 regression tests and its release checks of hashes, array schemas, retained-draw masks, counts and physical fraction bounds. Frozen observations, sample identifiers and the original license were compared byte-for-byte with the supplied repository. The ZIP was checked for archive integrity and against its complete SHA-256 manifest.
