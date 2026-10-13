# Version 6 research rerun

The latest article-format manuscript, embedded 600 dpi figures, expanded neural methods and Supplementary Information are documented in [PUBLICATION_README.md](PUBLICATION_README.md). Read [PUBLICATION_READINESS.md](PUBLICATION_READINESS.md) for the outstanding scientific and submission requirements. Earlier research drafts below are retained for provenance.

This working tree starts from the corrected v5 release supplied with the corrected manuscript. All 72 original release checksums passed before changes; original modules and released data are retained. New functionality is in `src/relaxed*.py` and `src/redo.py`. The original manuscript is retained as `experiments/manuscript_v5_reference.docx`.

The objective is to relax two structural assumptions and measure the consequences. Adding parameters does not by itself demonstrate unique decomposition or calibrated uncertainty.

## Experiment matrix

| Variant | Carrier mobility | Lattice | Separate rising heat | Continuous parameters |
|---|---|---|---|---:|
| Archived baseline | Shared | Floor plus decreasing power law | None | 10 |
| mobility | Independent scale, temperature and scattering exponents | Baseline | None | 13 |
| extra | Shared | Baseline | B(T/300)^3 | 11 |
| spline | Shared | Positive flexible PCHIP | None | 13 |
| mobility_extra | Independent | Baseline | B(T/300)^3 | 14 |
| mobility_spline | Independent | Positive flexible PCHIP | None | 16 |

The two thermal extensions are alternative models. In the extra variant, the lattice itself remains non-increasing; a different heat channel accounts for rising thermal transport. Only the spline variant relaxes the monotonicity of the lattice. This distinction must be retained in interpretation and the manuscript.

## Physical model and priors

Both band mobilities retain the corrected Fermi-integral expression. The minority band's non-degenerate 300 K prefactor is the majority prefactor times a ratio with log10 ratio uniform in [-1,1]. Its temperature exponent is independent, uniform in [-3.5,2], and its scattering exponent is independent, uniform in [-1,2]. These are research prior choices. The ratio is a prefactor ratio, not a fixed ratio of actual mobilities at every temperature and degeneracy.

The spline is PCHIP in log10 lattice conductivity versus log temperature, at 285, 400, 550, 750, 1000 and 1250 K. Each node has an independent log-uniform conductivity prior from 0.001 to 100 W m^-1 K^-1. Exponentiation guarantees positivity; no monotonicity constraint is imposed. These intentionally permissive node priors change the prior over lattice shapes substantially. Prior sensitivity and possible non-identifiability must remain explicit limitations. The spline does not exactly nest the original floor-plus-power-law family in general.

An initial run used 0.01 to 30 W m^-1 K^-1. Inspection found that 44/1,000 inherited narrow-gap upturn curves exceed 30 and two base test curves fall below 0.01. That run is retained separately as a prior-range comparison; the expanded support covers the inherited truth ranges. Checkpoints encode their own support, preventing an older checkpoint from silently being sampled under a different prior restriction.

The separate extra term uses B uniform in [0,0.05] W m^-1 K^-1 and exponent 3. It is labelled extra heat, not lattice heat. Its amplitude/exponent bounds are assumptions; the test does not establish that all increasing transport follows T^3.

The original carrier-density prior, doping-dependent majority mobility bounds, 2% multiplicative noise, interpolated observations and peak-zT support are retained. The sign can change across temperature through band competition; no profile-fit sign guard is imposed.

## Runs and validation

The pilot used 12,000 examples and 40 epochs for the two combined models. It verifies software execution only and must not supply manuscript results.

The production protocol uses 600,000 simulations per new variant, a 588,000/12,000 training/validation split, up to 900 epochs with the original early-stopping rule, 6,000 independently seeded same-model test curves and 1,000 independently seeded narrow-gap curves. It also evaluates every new estimator on the same archived base test, low/high mobility stress, wide-gap upturn stress, and the supplied narrow-gap upturn and control sets. It then processes the frozen 13,256 experimental curves when `--real` is specified.

The posterior remains a full-covariance Gaussian with an independent sign head, now sized to each parameter schema. This approximation may be inadequate for the extended models. Report independent coverage and failure rates; do not call the extension calibrated merely because it trained successfully. Training-set size, epoch cap and architecture are experimental choices, not guarantees of convergence.

Original and new heat channels are propagated from matched parameter draws. Final-temperature lattice, bipolar and extra fractions are stored for each retained draw. The 750 K fractions are stored only for curves spanning the entire 400–750 K comparison window; other entries are missing, not zero. Nonpositive endpoints are excluded, counted and never floored.

Real-corpus results report native and baseline-common selected populations, with paper-clustered intervals. Native selection requires positive endpoints for A, B, C, Cprime_bip and Cprime_all. For spline/mobility variants without an extra channel, the last two coincide. For extra variants, the extra subtraction introduces an additional positivity requirement; common-population comparisons help expose selection changes. Original A/B/C/Cprime meanings are preserved, with Cprime_all added explicitly.

## Commands

Use a Python environment with the packages listed in `requirements-v6-environment.txt`. The recorded local environment is Python 3.11 and CUDA-enabled PyTorch 2.11.0; it differs from the release's recommended Python 3.12 environment. All baseline and extension tests passed in the local environment.

From this repository root:

```text
python -m pytest tests -q
python -m src.verify_release
python -m src.redo --mode pilot --variants mobility_extra mobility_spline
python -m src.redo --mode production --out runs/v6_main --variants mobility_spline mobility_extra mobility spline extra --real --jobs 2
python -m src.verify_redo runs/v6_main
python -m src.redo_report runs/v6_main
python -m src.redo_compare runs/v6_main
python -m src.redo_cross runs/v6_main
python -m src.redo_supplement runs/v6_main
python -m src.redo_stress_compare runs/v6_main
python -m src.redo_figures runs/v6_main
python -m src.redo_manuscript runs/v6_main
```

Use `--resume` with the exact original command after interruption. Completed stages are skipped. A partially completed training stage restarts from its recorded seed; it does not resume optimiser state. Bitwise reproducibility across hardware or software versions is not promised. Configuration and source hashes must match the saved manifest. Use a fresh output directory with `--out` if changing code or configuration.

`runs/v6_main/status.json` records overall progress; each variant has its own stage status and a log at `runs/v6_main/<variant>.log`. `runs/main_console.log` records the parent process. Two independent model workers share the available GPU. Each variant directory contains source datasets, checkpoint, training history, inference arrays, diagnostics and corpus summaries as its stages complete. The manifest records seeds indirectly through each stage's metadata, software versions, model definitions and input/source hashes. Earlier directories `v6_production` and `v6_expanded` are superseded exploratory runs; do not combine their results with the main tables.

## Manuscript revision rule

Revise the Methods to describe each tested physical model and its priors. Replace quantitative results only after the corresponding production outputs exist and have been reviewed. Compare both changing and common populations. If flexibility broadens uncertainties or weakens the original slope shift, report that outcome. Do not remove discussion of identifiability, non-parabolic bands, measurement-error assumptions, approximation error or missing external validation.

The rerun is not complete until all selected stages, the comparison report and the result-dependent manuscript revision have been checked.

## Recorded implementation amendment

During the main run, the corpus bootstrap was changed to cache the draw counts and slope arrays before its loop. The original code repeatedly decompressed those same arrays. Models, random seeds and statistical formulas are unchanged. All statistics, including the nested interval, matched exactly before and after the change on a 24-curve, 30-resample regression check. `runs/v6_main/cache_fix_amendment.json` records both source hashes; the original manifests and source are retained beside it. Completed simulations, training and inference were reused; interrupted corpus summaries were recomputed. Baseline narrow-gap inference fixtures were also added for the common-case comparison, with their hashes recorded. This amendment is explicit rather than silently treating the entire run as produced by one unchanged source version.
