# Bipolar heat and model-dependent lattice thermal conductivity

This repository accompanies one unpublished study of a **13,031-record, 2,715-paper** thermoelectric corpus. Reference and extended models are stages of this project; internal v5/v6 labels do not denote separately published studies.

The manuscript and separate Supplementary Information are in `combined/manuscript/`. All empirical results use the corrected corpus. Seven main figures, two main tables, 33 supplementary tables and the neural-network supplementary figure are included. Raster artwork is 600 dpi, with vector versions alongside it.

## Release contents

The GitHub ZIP contains code, checkpoints, document sources, final documents, figures, summaries and small verification fixtures. The separate **corrected** data ZIP supplies observations, retained draws and synthetic arrays. Extract that ZIP into the repository root. Do not substitute the previous data deposit or commit large arrays to ordinary Git history. Release checksums identify both parts.

## Reproduce and verify

Use `requirements-v6-environment.txt` for scientific analysis and `combined/requirements-documents.txt` plus `combined/package.json` for document generation. Historical dependency files are retained for provenance.

```text
python -m pytest tests -q
python combined/verify_combined_manuscript.py
python combined/verify_family_comparison.py
python combined/verify_references_environment.py
```

With the full corrected data deposit, the following additionally check the archived arrays and regenerate empirical results without neural retraining:

```text
python combined/audit_scientific_claims.py
python tools/refresh_corpus_analysis.py
python combined/build_ancillary_summary.py
```

Build documents after the analyses and figures are current:

```text
node combined/build_manuscript.js
python combined/finalize_documents.py
python combined/add_source_methods.py
python combined/add_references_environment.py
python combined/verify_combined_manuscript.py
```

Run finalisation and the source-methods addition once after each fresh build. Word can export both documents to PDF. `combined/audit_final.py` checks captions, cross-references, image resolution and rendered files. A claim-specific array audit supplements numeric-token traceability.

## Data provenance

`data/corpus_provenance.json` records the corrected source hash; `data/corpus_selection.csv` maps retained observations to original row identities. Posterior draws were retained for unchanged observations; no retraining or fresh inference was required for row exclusion. `docs/DATA.md` distinguishes original execution metadata from corrected array provenance. The dataset comparison is separate from the manuscript and SI, in `docs/CORRECTED_VS_PREVIOUS.md`. Earlier source-audit records are explicitly historical.

Official Starrydata files are pinned to release `data-20261008`, database snapshot 9 October 2026. `tools/fetch_starrydata_audit.py` retrieves hash-checked source files; `combined/audit_starrydata.py --export work/starrydata_audit --out work/current_source_audit` checks the current cohort. `docs/STARRYDATA_AUDIT.md` describes the criteria. Auxiliary data support internal consistency checks, not independent thermal-channel ground truth.

## Scientific scope

The study reports conditional model-dependent thermal decompositions. It does not identify microscopic scattering mechanisms or uniquely separate bipolar and lattice heat. Family labels are inherited; synthetic coverage, prior sensitivity, source selection and experimental-error limitations are discussed in the article. Author details and public code/data deposit identifiers must be completed before submission. No journal acceptance is implied.

The final document build adds 22 claim-linked references and archived computing specifications. See `docs/REFERENCE_AUDIT.md` for citation access limits and `data/computational_environment.json` for recorded versus unrecorded system fields.
