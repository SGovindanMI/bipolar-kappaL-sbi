# Manuscript and Supplementary Information audit

**Superseding source-data finding:** the later official Starrydata audit found
101 attribution discrepancies, including 24 mixed-paper transport records.
The downstream numerical/layout checks below do not certify raw-data validity.
Read `docs/STARRYDATA_AUDIT.md`. The retained manuscript needs a provenance and
population revision before submission; the source audit and sensitivity addendum
are included separately to avoid presenting historical results as corrected.

Audit date: 9 October 2026.

The audited draft is `combined/manuscript/combined_manuscript.docx`. Its separate companion is `combined/manuscript/combined_supplementary_information.docx`. The main document has seven figures, two tables and seven editable displayed equations. The Supplementary Information has 30 tables and one neural-network figure. All 30 supplementary tables are cited from the main text. Both documents retain the reference and extended-model analyses as parts of one study.

## Assessment

The principal numerical conclusions reproduce from the supplied archived arrays. This audit found reporting, notation and cross-reference issues, corrected below; it did not identify a numerical discrepancy that changes the headline results. This is an audited research draft, not a certificate of error-free science or a guarantee of journal acceptance. No training or inference was repeated, and no saved scientific array or checkpoint was changed.

## Corrections made

1. Removed the introduction's unnecessary statement about v5/v6 being unpublished implementation stages. The scientific reference-versus-extension comparison remains. Internal identifiers remain only where useful for locating code and data.
2. Clarified charge neutrality using majority/minority densities and a positive net-dopant magnitude. The physical hole/electron equation has opposite signed net doping for p-type and n-type specimens. Parentheses now make the band-gap denominator unambiguous. The implementation already used the majority/minority convention; this was a notation correction.
3. Distinguished the 509 common scored upturn cases used for coverage from the 87 common slope-eligible cases in the abstract. Higher coverage is not described as improved point accuracy.
4. Corrected Figure 5's blanket description of all panels as development benchmarks. Its inherited upturn benchmark and independently generated transfer sets are now distinguished, with the unequal transfer denominators explicit.
5. Restored main-text links and short results summaries after detailed reference-model tables had been moved to the supplement. The family-based analysis remains in the main manuscript and in both native-population and common-population supplementary tables.
6. Corrected the supplementary selection caption from “non-positive” to the actual implemented criterion, strictly negative A at any grid point. The counts are unchanged: 20 admitted + 40 scored exclusions + 321 unscored = 381 negative conventional remainders.
7. Clarified that the unipolar remainder equals lattice plus bipolar heat only when an additional thermal channel is absent. The rising-channel models retain their distinct extra contribution.
8. Replaced rounded Markdown as the source of same-model and native narrow-upturn table values with the full-precision diagnostic JSON. Displayed headline values remain unchanged; ten additional input files are now hashed.
9. Corrected the PCHIP method reference to Fritsch and Butland (1984), matching the implementation documented by [SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.PchipInterpolator.html). The paper is [A method for constructing local monotone piecewise cubic interpolants](https://doi.org/10.1137/0905021).
10. Made the supplement explicitly a companion document and corrected its data-availability wording: large per-curve arrays are in the separate data archive, while code, checkpoints and compact summaries are in the GitHub package.
11. Corrected the statement that the reference run “stores” all training examples: the release regenerates training arrays from the archived configuration and seed. Removed irrelevant earlier-implementation calibration history.
12. The rendered-page check caught an encoding error introduced during this edit in Supplementary Table 27. It was repaired before delivery. A Unicode corruption check now covers table cells as well as paragraphs.

## Numerical verification

`combined/audit_scientific_claims.py` passed 627 claim-specific checks against archived arrays. It reconstructs curve estimates and masks, checks all six models' selection and negative-remainder counts, subgroup counts and medians, and threshold-scan counts and medians. It recomputes C−B and C−A paper-bootstrap intervals for native, baseline-common and all-model-common populations; common paired changes; five reference-model shifts; five shared stress sets' coverage, widths and slope errors; same-model test counts and lattice/bipolar coverage; and all 12 cross-model transfer combinations' counts and coverage. The report is `combined/SCIENTIFIC_AUDIT.json`.

`combined/verify_family_comparison.py` independently reconstructed all 60 common-family interval triplets using 2,000 source-paper bootstrap resamples and seed 2024. Its mask, counts and source-data checks also passed. Native family interval endpoints were traced to archived summaries; the separate 60-triplet recomputation concerns the common-family analysis.

Selected reproduced quantities:

| Claim | Reproduced result |
|---|---|
| Frozen corpus | 13,256 curves; 2,754 source papers |
| Reference scored / admitted / paired | 10,320 / 7,379 / 4,312 |
| Reference median B−A slope shift | 0.002895, reported as 0.003 |
| Reference median C−B slope shift | −0.164587, reported as −0.165 |
| Common six-model experimental population | 1,528 curves; 649 papers |
| Common C−B, reference / independent + flexible | −0.106669 / −0.593025 |
| Common upturn lattice coverage, reference / independent + flexible | 41.687% / 97.213%, on 509 curves |
| Corresponding median interval widths | 0.699 / 9.983 W m−1 K−1 |
| Corresponding median absolute slope errors | 0.541 / 0.661, on 87 curves |
| Decreasing-lattice control apparent upturns | 608 of 985 admitted reference cases; zero true lattice upturns |
| Negative conventional remainders | 381 overall, with mutually exclusive groups summing correctly |

The existing numerical-token checker also passed, but token matching is weaker evidence than these contextual checks. The repository test suite passed all 23 tests with `python -m pytest tests -q`. An initial unrestricted test discovery also entered an old packaged copy under `work/`; restricting discovery to the actual `tests` directory resolved the duplicate-module collection issue.

## Scientific interpretation retained

The manuscript correctly distinguishes measured transport from model-derived channel attribution; native populations from matched populations; pointwise coverage from simultaneous coverage; and medians of differences from differences of medians. The Gaussian network architecture, precision parameterisation, sign factorisation, loss, train/validation split, optimiser, stopping rule and support rejection were checked against the source and training metadata. Family associations and scattering labels remain conditional descriptions rather than independent validation of mechanisms.

The improved lattice coverage under flexible models comes with much wider intervals and worse median absolute slope error on the common narrow-upturn subset. Transfer failures remain visible. The paper should not claim that mobility asymmetry and lattice upturns have been comprehensively “solved,” that the decomposition is uniquely identified, or that source authors' lattice values were proven wrong.

## Remaining limitations and submission needs

- The original raw database export and the implementation of the historical 407-record filter are unavailable. The audit verifies downstream frozen-array analysis, not reconstruction of that historical cohort.
- Independent experimental heat-channel truth was not supplied. Agreement with measured total heat and simulation tests cannot establish correct experimental channel separation.
- Same-model undercoverage, sensitivity to model and prior choice, single training seeds, limited noise assumptions, and missing joint/simultaneous calibration remain scientific limitations. These are disclosed rather than removed editorially.
- The reference and extended model assumptions were reviewed, but the audit is not an exhaustive proof of every numerical path or every possible physical regime.
- Author names, affiliations, contributions, funding, competing-interest declarations, and public code/data deposit identifiers still require author completion. This audit does not certify compliance with every journal-specific submission requirement.

The updated documents should therefore be described as an audited draft. The present checks support the reported model-comparison results, with the limitations above. They do not guarantee acceptance by Nature Communications.

## Document checks

All main and supplementary pages were rendered through Word and visually inspected. Figure resolution exceeds 600 dpi at the embedded manuscript sizes; the separate artwork retains 600 dpi raster exports and vector PDF/SVG files. Equations, captions, supplementary-table links and character encoding were checked. Detailed supporting tables remain in a separate Supplementary Information document rather than being appended as another manuscript.

## Repeating the audit

Restore the separate data archive into the repository before running the full array audit. Run `python combined/audit_scientific_claims.py`, `python combined/verify_family_comparison.py`, `python combined/verify_combined_manuscript.py` and `python -m pytest tests -q`. The compact family and document checks can run without the full data deposit; the array audit requires it. Rendered-page checking additionally requires the document dependencies and PDF export described in the build documentation.

## Component comparison clarification

Section 3.10 and new Supplementary Tables 28–30 explicitly show A, B, C, C′ bipolar and C′ all for every model on the identical 1,528 curves. Each estimate was reconstructed from its own model’s saved posterior summaries; A was verified identical and all six common C−B intervals reproduce the existing archive. Ninety component, paired-difference and paired-change interval triplets were calculated with 2,000 source-paper bootstrap resamples. The frozen per-curve source table and input hashes are included. No inference was repeated. The larger paired slope change in C than in B is descriptive; it does not independently establish which microscopic mechanism is responsible.
