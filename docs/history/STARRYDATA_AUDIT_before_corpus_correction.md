# Starrydata source-data audit and incorporation report

Audit completed: 10 October 2026 (export snapshot: 9 October). **The preserved manuscript is not submission-ready: the source assembly requires correction.** The findings below supersede earlier statements that sampled numerical reproduction established provenance. All historical arrays remain unchanged; the new analyses are explicitly labelled sensitivity analyses.

## What was verified

The official ThermoelectricMaterials export in dated release `data-20261008` reports database snapshot `2026-10-09 02:00:01 UTC+0900 (JST)`. All three downloaded tables match the publisher's SHA-256 checksums and row counts: 157,066 curves, 55,484 sample rows and 9,523 paper rows. These are current export counts, not the counts of the historical selection. Every one of the 13,256 frozen integer sample IDs occurs in the current export, but integer-ID presence alone is insufficient.

Matching paper DOI plus sample ID (and verifying that this pair maps to one SID), canonical property labels, SI units and temperature coverage reproduces all three frozen transport channels within declared tolerances for **13,031/13,256 records (98.30%)**. Tolerances are a maximum 1% relative difference for conductivity and thermal conductivity, with a 0.001 S/m absolute floor for conductivity near zero, and 1 microvolt/K for Seebeck coefficient, on all 16 points. A 0.0001 K endpoint allowance addresses stored-window rounding. This is numerical/source agreement, not proof that the original measurements are physically correct. Identical repeated points are collapsed; conflicting repeated temperatures are rejected. No extrapolation is accepted beyond that endpoint-rounding allowance.

## Demonstrated disparities

1. **101 incorrect paper/sample associations.** The current export does not contain these frozen DOI/sample-ID pairs. A separately archived export explains the mechanism. The old parser grouped on integer sample ID alone and updated its metadata while adding properties. Of these 101 records, **77 have all three selected transport channels from one paper but a different recorded DOI**, and **24 combine transport channels from different papers**. The archived single-ID join reproduces every mixed-paper record to a maximum mixed-feature absolute difference below 0.000035. This establishes an assembly problem, not merely later database growth. Family labels and paper-cluster bootstrap assignments on these records need review as well.
2. **124 additional records fail the strict reconstruction check** for ambiguous/insufficient raw curves or mismatch of the remaining usable candidates. All 124 have conflicting repeated temperatures in at least one candidate essential channel; detailed, possibly overlapping reasons are in `per_sample_audit.csv`. In particular, a multivalued temperature curve must not be sorted and treated automatically as a single-valued function: it may represent branches or multiple conditions. These are review flags, not 124 proven erroneous experiments.
3. **One pair has identical full feature vectors**: sample IDs 38993 and 39000, DOI `10.1016/j.jallcom.2017.01.350`. Whether this is duplicated digitization or distinct specimens needs the paper. A deduplicated sensitivity is included.
4. A raw relative-error test initially flags sample 44981 because its first conductivity is approximately zero. Its absolute difference is approximately 0.0000025 S/m, caused by endpoint rounding; it passes the stated absolute tolerance and is not treated as a large physical discrepancy.
5. The exact original source snapshot and the missing 407-sample plausibility filter remain unrecovered. The diagnostic archive is tagged `data-20260715`, but its manifest states `2026-06-30 02:00:02 UTC+0900 (JST)` and contains 155,923 curves, not the legacy count of 155,638. Therefore it must not be called the exact original export. Its unsafe join nevertheless reproduces 13,250 rows within 0.001 in mixed feature units, and all 13,256 recorded last-property metadata DOIs. Mixed-unit comparison here diagnoses the legacy algorithm only; the current audit uses channel-specific tolerances.

The upstream maintainers document identifier collisions in April–September 2026 exports and recommend composite paper/sample keys. The present finding concerns our actual 101 affected associations; the upstream percentage must not be applied to this corpus. See [official identifier notice](https://github.com/starrydata/starrydata_datasets) and [download/schema documentation](https://starrydata.github.io/hp/en/manual/download/).

## Effect on the main conclusion

No neural-network retraining or posterior inference was run. We reused each model's saved posterior summaries and excluded every record failing the strict current-export check. The reference admitted population decreases from 7,379 to 7,251; the reference native five-estimate slope population decreases from 4,312 to 4,248. Its median C minus B changes from −0.164587 to −0.165710 (paper-bootstrap 95% interval [−0.184000, −0.150645]).

The all-model common population decreases from 1,528 curves/649 papers to 1,507 curves/640 papers. The median differences remain negative and change by less than 0.0012:

| Model | Original common n=1,528 | Verified common n=1,507 | Verified 95% paper-bootstrap interval |
|---|---:|---:|---:|
| Reference | -0.106669 | -0.106703 | [-0.122208, -0.092053] |
| Independent mobility | -0.145216 | -0.145071 | [-0.164136, -0.131263] |
| Rising heat channel | -0.180997 | -0.179829 | [-0.197289, -0.162312] |
| Flexible lattice | -0.372510 | -0.372035 | [-0.456262, -0.307836] |
| Mobility + rising heat | -0.227007 | -0.226737 | [-0.242078, -0.207414] |
| Mobility + flexible lattice | -0.593025 | -0.592978 | [-0.701346, -0.475905] |

Intervals use 2,000 paper-cluster bootstrap resamples, seed 2024. `sensitivity.json` also reports native populations for all six models, exact-feature deduplication, an exploratory exclusion of derived-property consistency flags, and family-specific results. Small family groups are descriptive; a degenerate interval for a one-paper or one-sample group is not evidence of precision. Stability of these contrasts does not certify every other manuscript result, the corrected family attribution, the physical decomposition, or neural-network calibration. The original manuscript tables have not been silently replaced with different populations.

## What transport and other data are available

The following counts come from the downloaded files, not from the live website. A match means a paper/sample identity match; it does not guarantee complete temperature overlap, usable units, experimental independence or a valid measurement.

| Property | Current export curve rows | Matched frozen samples | Matched verified samples |
|---|---:|---:|---:|
| Seebeck coefficient | 37,622 | 13,155 | 13,031 |
| Electrical conductivity | 20,371 | 8,277 | 8,229 |
| Electrical resistivity | 19,386 | 4,905 | 4,826 |
| Thermal conductivity | 23,598 | 13,155 | 13,031 |
| Power factor | 17,545 | 8,403 | 8,341 |
| ZT | 20,832 | 12,142 | 12,031 |
| Lattice thermal conductivity | 6,829 | 4,560 | 4,532 |
| Electronic thermal conductivity | 647 | 487 | 487 |
| Carrier concentration | 2,062 | 915 | 908 |
| Carrier mobility | 1,381 | 715 | 714 |
| Hall coefficient | 687 | 103 | 101 |
| Hall mobility | 499 | 201 | 199 |
| Thermal diffusivity | 67 | 16 | 16 |
| Lorenz number | 5 | 4 | 4 |
| Density | 5 | 3 | 3 |
| Specific heat capacity (J/gK) | 6 | 6 | 6 |

The full `property_inventory.csv` preserves all property/unit variants and counts overlap separately for the frozen, reference-admitted, six-model-common and verified-input populations, including temperature-in-kelvin availability. The broader database also covers magnetic, battery and dielectric properties; project membership alone does not make those data relevant to thermoelectric inference.

Useful sample descriptors include material form, fabrication process, measurement method, relative density, grain size and source material-family tags. `matched_sample_metadata.json` preserves available raw descriptors joined by paper and sample. These are incomplete and heterogeneous. Among matched metadata rows for verified inputs, DataType includes 10,273 labelled Experiment, 52 Reference, 12 NeedCheck and other/unknown/missing entries. These labels should be reviewed before calling all rows independent experiments. Form includes films, powder and a module as well as bulk specimens; the intended material scope needs an explicit rule. Missing metadata does not mean a specimen is invalid. No automatic replacement of the project's family labels was performed.

## Useful additions incorporated now

**Power-factor and ZT consistency checks:** compare archived auxiliary curves with PF = S² sigma and ZT = S² sigma T / kappa calculated from the frozen inputs, over overlapping grids with at least five usable points. The metric is the median symmetric relative difference, 2|reported − reconstructed|/(|reported| + |reconstructed|). If several candidate curves exist, all are released and the summary uses the best matching candidate; this is deliberately optimistic and is not independent validation. The median per-sample discrepancy is 1.46% for PF across 8,355 specimens and 2.37% for ZT across 12,072. Even the best candidate exceeds a 20% median difference for 653 PF and 1,195 ZT specimens (overlap possible). That threshold is a review heuristic, not an error rate or automatic exclusion rule. An additional sensitivity excludes flagged verified samples: the common population becomes 1,383, and the reference C minus B median is −0.107663. All six results are saved.

**Ancillary validation inventory:** carrier concentration, mobility and Hall coefficient are promising for testing transport assumptions. They have now been linked to existing specimens with source figure IDs, units and property labels in `matched_curve_manifest.csv`. They have not been added to the likelihood. Hall-inferred concentration is not automatically the model's net dopant density; two-carrier interpretation, Hall factors, scattering assumptions and sample conditions need explicit treatment. Therefore the mobility issue cannot be declared solved by the availability of these curves.

**Source-reported lattice/electronic conductivity:** retained as possible method-comparison benchmarks, not independent ground truth for our inferred decomposition, because they may themselves use Lorenz subtraction or other model assumptions. Published Lorenz curves are too sparse and method-dependent to establish corpus-wide accuracy.

**Thermal diffusivity / density / heat capacity:** a possible future thermal-conductivity consistency check requires compatible units, density type and the same specimen/temperature. The export includes suspicious labels (density `kg*m**3`, heat capacity embedded in the property name with unit `-`); they are not auto-converted or inserted into the model. The archive does not support claiming that this additional physical check is complete.

## Required manuscript changes and remaining work

- Replace any claim that all frozen records have validated raw provenance. Report the 101 association errors, strict audit criteria, snapshot/hash, exclusion/sensitivity populations and unrecovered original selection step.
- Quarantine the 24 mixed-paper inputs. They cannot be repaired by changing a DOI. Recover separate specimens' complete channels from the source export and source figures if they are to be reinstated. Changing their inputs requires fresh posterior inference; network retraining is necessary only if the simulator/observation model changes.
- Review and correct the other 77 attributions and their material-family labels before reinstatement. Recompute paper-cluster intervals and family tables for any corrected attribution, even if transport values are unchanged.
- Resolve the 124 other flagged records and the exact-feature duplicate using source figures and measurement conditions. Alternatively, adopt a documented conservative exclusion population and propagate it consistently through every empirical figure/table and all counts; the sensitivity supplied here alone is not that full rewrite.
- Add the PF/ZT checks to Supplementary Information as internal consistency diagnostics. Add Hall/carrier/mobility availability and material/measurement descriptors as an ancillary-validation opportunity with explicit limitations. Do not present derived PF, ZT or source-subtracted lattice conductivity as independent experimental confirmation.
- Preserve the family-based analysis, using corrected attributions and explicit common populations. The new family sensitivity is supplied but does not replace verification of family labels.

No raw measurement was fabricated, no missing Hall constraint was imputed, and the frozen corpus remains unchanged for auditability. Current code adds exhaustive audit, source retrieval with pinned hashes, review manifests, sensitivity analysis and fail-closed identity/unit/window guards to the legacy rebuild path. The GitHub bundle is a research revision with a clearly flagged historical manuscript, not a submission-certified release.

## Reproduction

```text
python tools/fetch_starrydata_audit.py
python combined/audit_starrydata.py --export work/starrydata_audit
python combined/audit_starrydata_historical.py
python combined/starrydata_sensitivity.py
python combined/build_starrydata_report.py
python -m pytest tests -q
```

The main research-data deposit must be extracted first, as for the existing analyses. The report builder also verifies the saved dated manifest when available. Source URLs and hashes are in `source_provenance.json`; outputs are in `combined/starrydata_audit/`. Raw exports stay under ignored `work/`. The scientific audit figure is provided as a 600-dpi PNG and a vector PDF.
