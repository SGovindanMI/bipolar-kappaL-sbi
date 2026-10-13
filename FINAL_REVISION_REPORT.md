# Final combined-draft revision

Prepared 9 October 2026 from the user-supplied combined manuscript, supplement and two GitHub archives, checked against the existing completed research runs.

## Scope and provenance

This is one unpublished project study. v5 and v6 are internal implementation-stage identifiers; neither is presented as a separately published paper. The full combined paper is the starting point, not the shorter earlier revision. All its reference-model corpus analyses, family associations, bipolar-share strata, Seebeck-rollover comparisons, fit-screen sensitivity, effective-scattering summaries, negative-remainder counts, synthetic diagnostics, transfer tests and six-model comparisons are retained in the main article or supplement.

## Changes made

- Added a common-population family analysis, a seventh main figure and Supplementary Tables 26–27. Four named groups and the heterogeneous residual other group meet the unchanged 80-curve threshold. Counts are supplied for all 14 inherited labels. The nine smaller labels were not silently dropped from the corpus or promoted into unsupported ranked estimates.
- Recomputed family medians, paired changes and 95% paper-clustered percentile intervals from existing inference outputs, with 2,000 resamples and seed 2024. No training or physical inference was repeated.
- Explicitly distinguished unpublished project stages from cited literature. Corrected the reference checkpoint epoch from stored index 889 to one-based epoch 890, retaining both identifiers for traceability.
- Shortened the abstract to 162 words. Moved ten detailed tables into Supplementary Information, retaining two main tables and seven main figures (nine main display items). All table references were updated. The supplement contains 27 tables and one figure.
- Kept figures near the relevant Results text, retained editable mathematical equations, and supplied 600 dpi raster artwork plus editable vector files. Bibliography numbering follows first citation.
- Fixed Windows Unicode console output in the manuscript checker, strengthened family-specific verification, documented the checker’s limitations, and aligned the document-package dependency with the version actually used for the final build.
- Updated the root README to cover the whole study and distinguish the compact GitHub repository from the separate large research-data archive. Added explicit checksum amendments for revised historical documentation; original physical and inference code remains unchanged.

## Verification

All 23 existing scientific tests passed. The merged input archives had valid CRCs, and the core source files matched the previously tested working copy before revision. The combined numerical summary was rebuilt from archived outputs. The manuscript numeric-token and selected headline checks passed; these are traceability checks, not a claim that arbitrary matching numbers prove contextual accuracy. The new family checker independently recomputes all 60 reported interval triplets and checks the mask intersection, counts and CSV values.

Document structure and image resolution are recorded in `combined/manuscript/FINAL_DOCUMENT_QA.json`; family verification is in `combined/family_verification.json`. Final page renderings were inspected. The GitHub/data release manifest records file-level hashes, and both ZIP archives receive CRC checks. No neural retraining or transport inference was rerun.

## Remaining author and scientific requirements

This is a complete draft of the work performed, not a guarantee of journal acceptance or of uniquely identifiable thermal channels. Author names and affiliations, corresponding-author contact, contributions, funding, acknowledgements and competing-interest declarations must be supplied by the authors. The existing supplied licence attribution is preserved and is not used to invent a manuscript author list. Permanent code/data links, licences and source-data redistribution permissions require author completion.

The manuscript retains its outstanding scientific limitations: same-model undercoverage, the Gaussian/sign factorisation, prior and thermal-family dependence, inherited development benchmarks, untested noise/prior alternatives, no new source-publication audit and no withheld external channel measurements. Family comparisons strengthen selection-controlled description; they do not substitute for external validation. More flexible lattice models can achieve wider coverage without improved absolute slope recovery.

Journal-specific length counting and final submission metadata should be checked for the selected article type. Detailed Methods and all completed analyses have been preserved, rather than removing scientific content to imply a fully submission-certified manuscript. Seven figures plus two tables keep the main display count below the ten-item guidance in the older Nature Communications quick guide. Current journal instructions govern the actual submission.

## Delivery

Upload the contents of the GitHub source ZIP as repository files. Distribute the large research-data ZIP through a suitable data deposit or release asset; extract it at the source-tree root to restore full array-based reproduction. GitHub blocks ordinary Git files over 100 MiB and warns above 50 MiB: [official GitHub guidance](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github). The package enforces a stricter 50 MB per-file source-tree limit. Nothing has been uploaded or submitted on the user's behalf.
