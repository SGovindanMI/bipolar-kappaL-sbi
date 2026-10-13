# Verification of the three supplied papers

Checked 10 October 2026 against the current corrected-dataset manuscript and its reference registry. All three bibliographic identities match. The existing citations are supported; the manuscript and supplementary documents are unchanged.

## [2] Putatunda and Singh (2019)

Journal pages 50-54: Eq. (1) is the Kim estimate under a single parabolic band and acoustic-phonon scattering. The paper tests constant-time and acoustic-phonon scattering with realistic electronic structures. This supports the Introduction's statement that applicability depends on carrier/scattering regime and non-parabolic structure.

Equations (4) and (7) distinguish the open-circuit Lorenz number from the uncorrected second-moment definition. Comparisons must use matching definitions; the very large uncorrected values are not errors in the Kim approximation. Table 2's material-specific deviations are not error bars for our Starrydata corpus. The paper also finds reasonable agreement in some cases; it does not establish universal failure of the formula. Our present cautious wording is appropriate.

## [5] Kim et al. (2017)

Pages 3-5: electronic subtraction uses the approximate Lorenz number; a two-parabolic-band model estimates bipolar conduction by fitting electrical conductivity and Seebeck coefficient. Equation (5) separates electronic, lattice and bipolar contributions. Table 1 fixes the gap at 0.145 eV and uses material-specific band parameters. Page 8 records room-temperature Hall measurements; page 4 describes their crosscheck role.

This supports citing a single-material, model-assisted decomposition in the Introduction and validation discussion. It does not provide independently measured lattice or bipolar ground truth, nor validate our flexible lattice or neural inference model. Hall constraints are a useful future extension when sample-matched data are available, not a reason to claim they were used here.

## [21] Goldsmid and Sharp (1999)

Pages 869-872 derive the approximate relation Eg ~ 2 e |S|max Tmax. The temperature range must capture the relevant Seebeck maximum. Pages 870-871 explicitly explore mobility/effective-mass ratios, scattering, doping and narrow-gap statistics. An assumption of equal electron and hole mobilities is not required throughout the original paper.

The limitations paragraph correctly calls these estimates approximate and retains Gibbs et al. [22] for further limitations. Applying this estimator to the same Seebeck data used in inference cannot furnish independent experimental validation. The paper's indicative error discussion is not a universal uncertainty bound for our samples.

## Outcome

Retain all three citations and the current manuscript wording. Updated the reference access records and reproducible authoring source. No new scientific result, model parameter, dataset or training change follows from this literature check. The review resolves the three outstanding PDF-access requests; it is not a new audit of all numerical arrays. Historical CPU, RAM and operating-system specifications remain unrecorded, as already stated in the supplement.
