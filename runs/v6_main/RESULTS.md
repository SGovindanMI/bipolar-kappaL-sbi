# Extended transport model rerun

Run mode: **production**. Computational status: **complete**.

These are conditional model comparisons. A completed run does not establish identifiability or calibrated uncertainty.

## Independent same-model synthetic tests

| Model | Test curves | Scored | Admitted | Lattice coverage | Bipolar coverage | Lattice median absolute relative error |
|---|---:|---:|---:|---:|---:|---:|
| mobility_spline | 6000 | 5986 | 5842 | 91.7% | 92.0% | 0.183 |
| mobility_extra | 6000 | 5989 | 5882 | 93.3% | 91.7% | 0.057 |
| mobility | 6000 | 5998 | 5856 | 94.7% | 91.8% | 0.035 |
| spline | 6000 | 5992 | 5847 | 90.9% | 92.1% | 0.181 |
| extra | 6000 | 5993 | 5887 | 93.9% | 92.1% | 0.058 |

Coverage is nominal 95% pointwise coverage conditional on scored curves. Relative errors exclude truth values at or below 1e-12 and report the included point count in the detailed JSON.

## Shared narrow-gap lattice-upturn stress test

| Model | Scored | Admitted | Lattice coverage | Bipolar coverage | Median fixed-window lattice slope error | Four-estimate subset n |
|---|---:|---:|---:|---:|---:|---:|
| mobility_spline | 999 | 998 | 97.2% | 92.9% | -0.019 | 343 |
| mobility_extra | 656 | 634 | 36.2% | 91.6% | -0.702 | 182 |
| mobility | 599 | 577 | 40.7% | 82.6% | -0.693 | 154 |
| spline | 999 | 985 | 95.4% | 88.4% | -0.058 | 359 |
| extra | 619 | 571 | 37.3% | 85.3% | -0.660 | 174 |

## Frozen experimental corpus

| Model | Admitted | Native paired | Baseline-common paired | Native C-minus-B shift | Common C-minus-B shift |
|---|---:|---:|---:|---:|---:|
| mobility_spline | 10559 | 4123 | 2638 | -0.453 | -0.523 |
| mobility_extra | 8074 | 4445 | 3434 | -0.305 | -0.297 |
| mobility | 9440 | 5292 | 3867 | -0.209 | -0.207 |
| spline | 7608 | 4162 | 3326 | -0.576 | -0.677 |
| extra | 5520 | 3065 | 2811 | -0.283 | -0.273 |

Native populations can change with the model and endpoint masks. The common subset additionally requires baseline admission and finite baseline estimates. Detailed JSON includes paper-clustered intervals and a nested interval; these do not include physical-model uncertainty.

## Interpretation requirements

- Review undercoverage and unscored cases before interpreting experimental posterior intervals.
- Compare native and common populations; do not attribute selection-induced changes solely to physical decomposition.
- Keep the extra rising channel distinct from lattice heat.
- Treat flexible-lattice results as sensitive to knot placement and node priors until those alternatives are tested.
- Retain external-validation and non-parabolic-band limitations.
- Pilot results cannot replace production manuscript results.
