# Corrected dataset compared with the previous project dataset

This report is separate from the final manuscript and Supplementary Information. Those documents use only the corrected cohort. Neither project version is a separately published study.

The correction removes 225 records from the empirical analysis: 101 inconsistent paper/sample associations (including 24 mixed-paper transport triplets) and 124 records whose required transport curves need review because of conflicting temperature values. The 13,031 retained records reproduce the pinned official source export within the declared tolerances. Their transport inputs and saved posterior draws are unchanged; no network retraining or fresh posterior sampling was performed. Every empirical population, bootstrap interval, stratification, figure and table was regenerated after selection. Synthetic validation datasets are unchanged.

| Population | Previous | Corrected |
|---|---:|---:|
| Corpus records | 13,256 | 13,031 |
| Source papers | 2,754 | 2,715 |
| Reference scored | 10,320 | 10,138 |
| Reference admitted | 7,379 | 7,251 |
| Reference paired slopes | 4,312 | 4,248 |
| Reference paired papers | 1,233 | 1,216 |
| Six-model common records | 1,528 | 1,507 |
| Six-model common papers | 649 | 640 |

## Six-model results

Values below are median per-curve C minus B log-slope differences over 400–750 K. Arrows show previous → corrected. Native populations differ between models; the common population uses identical curves across all models within each dataset. The dataset populations themselves differ, so these changes are not individual-curve refitting effects.

| Model | Native records | Native C minus B | Common C minus B |
|---|---:|---:|---:|
| Reference | 4,312 → 4,248 | -0.164587 → -0.165710 | -0.106669 → -0.106703 |
| Independent bands | 5,368 → 5,292 | -0.208510 → -0.209067 | -0.145216 → -0.145071 |
| Rising channel | 3,114 → 3,065 | -0.283094 → -0.283135 | -0.180997 → -0.179829 |
| Flexible lattice | 4,225 → 4,162 | -0.576657 → -0.576471 | -0.372510 → -0.372035 |
| Independent + rising | 4,507 → 4,445 | -0.302458 → -0.304743 | -0.227007 → -0.226737 |
| Independent + flexible | 4,187 → 4,123 | -0.451579 → -0.452836 | -0.593025 → -0.592978 |

The maximum absolute change in the six common-set medians is below 0.0012. The principal direction and substantial model dependence persist. This stability does not excuse incorrect source assembly and does not establish a unique physical heat decomposition. The final paper reports the corrected values only.

## Family representation on the common population

| Inherited family label | Previous records | Corrected records | Corrected papers |
|---|---:|---:|---:|
| Ag-Te | 5 | 5 | 3 |
| Bi2Te3-type | 9 | 9 | 8 |
| Cu2Se-type | 29 | 29 | 14 |
| Mg2X-type | 143 | 138 | 59 |
| PbX-type | 55 | 55 | 30 |
| SiGe | 57 | 57 | 22 |
| SnSe-type | 1 | 1 | 1 |
| SnTe-type | 24 | 24 | 12 |
| Zn-Sb | 26 | 24 | 12 |
| filled-RE | 116 | 115 | 61 |
| half-Heusler | 87 | 87 | 45 |
| other | 660 | 651 | 268 |
| skutterudite | 316 | 312 | 137 |
| unknown | 0 | 0 | 0 |

The pre-specified threshold of 80 common curves is retained. Four named groups and the heterogeneous residual other group qualify for reported effects. The corrected family effects and paired model contrasts are in Supplementary Tables 26 and 27; component slope medians and paired differences are in Tables 28–30.

## Added data checks

Power-factor consistency is evaluated on 8,303 corrected-cohort specimens and zT consistency on 11,972. Median symmetric discrepancies are 1.46% and 2.36%; 646 and 1,185 specimens respectively exceed a 20% best-candidate median discrepancy. These are review flags, not independently validated experimental-error rates. Auxiliary transport availability and source-verification conventions are in Supplementary Tables 31–33.

The exact historical selection rule remains incomplete. An identical-feature pair with two source sample IDs is retained and shares one paper cluster. Family labels and auxiliary-field semantics still require physical interpretation. These limitations are distinct from the repaired paper/sample join and are described without presenting the previous dataset as an alternative primary analysis.

## Traceability

`data/corpus_selection.csv` maps every final row to its previous row identity. `data/corpus_provenance.json` records original and corrected file hashes. `data/source_verification.json` confirms that all final records pass the source checks. `combined/dataset_comparison.json` preserves the underlying model summaries for this comparison. The previous project deliverables remain separate; the new release requires the corrected data archive, not the old one.
