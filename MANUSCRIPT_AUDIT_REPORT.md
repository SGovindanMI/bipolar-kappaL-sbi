# Final corrected-cohort manuscript audit

Audit date: 10 October 2026.

The manuscript and separate Supplementary Information use 13,031 source-consistent observations from 2,715 papers. The previous-versus-corrected dataset comparison is supplied separately in docs/CORRECTED_VS_PREVIOUS.md. The historical draft audit is archived under docs/history/.

## Completed checks

- Official-source audit: all 13,031 retained observations pass the stated identity, unit, coverage and numerical agreement criteria. Source checks do not establish experimental accuracy.
- Retained input features and posterior draws exactly match their original rows. All empirical summaries, bootstrap intervals, family comparisons and figures were regenerated. Synthetic tests and trained networks are unchanged.
- Claim-specific numerical audit: 625 checks passed; family interval audit: 60 interval triplets passed. Component comparisons include all 90 interval triplets for A, B, C and model-specific subtraction estimates on the same 1,507-curve population.
- Automated test suite: 29 tests passed. Manuscript numerical traceability and headline checks passed.
- Main manuscript: 21 pages, seven figures, two tables and seven native displayed equations. Supplementary Information: 13 pages, 33 tables, one neural-network figure and two native equations. All supplementary tables are cited in the main text.
- Figures were regenerated as 600-dpi raster outputs with vector alternatives; embedded effective resolution exceeds 600 dpi. Rendered page contact sheets and full-size checks of affected sections were reviewed. FINAL_DOCUMENT_QA.json records checksums and resolutions.

## Scientific and submission limits

The historical source-selection rule is incomplete; the corpus is a list-defined convenience sample. Inherited family labels and heterogeneous source metadata need physical interpretation. One identical-feature pair is retained within a single paper-bootstrap cluster. PF and zT checks reuse transport measurements and are internal consistency diagnostics. Hall and other auxiliary measurements are catalogued but are not incorporated into the likelihood.

The model comparison describes conditional thermal decompositions; it does not establish unique channel identification or microscopic scattering mechanisms. The neural-network architecture, training and synthetic validation remain part of the article. Author details and public repository/data identifiers must be completed before submission. Editorial acceptance cannot be guaranteed.

## References and computational details revision

The main manuscript now has 22 references at relevant paragraphs and the supplement repeats its eight cited method/software references using the same numbering. All citations and bibliography entries match the reference registry. The three previously outstanding PDFs have now been supplied and their cited claims checked against the full texts. See docs/SUPPLIED_PAPERS_VERIFICATION.md for page-level evidence and interpretation limits. This targeted check required no manuscript wording changes.

System specifications distinguish the extended-run GPU/software manifests from the more limited reference-run metadata. CPU, RAM, OS, GPU memory and driver fields remain unrecorded. All 34 rendered pages were visually inspected. The 625 claim-specific checks, 60 family interval triplets, numeric traceability and 29 automated tests passed again after the citation revision. Scientific arrays were not changed.
