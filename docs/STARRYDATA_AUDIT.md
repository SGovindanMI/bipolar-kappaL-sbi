# Source verification of the analysed corpus

All 13,031 records from 2,715 papers pass the declared current-export identity, canonical-unit, temperature-coverage and numerical-reproduction checks. The exact checked snapshot, files and SHA-256 digests are in `combined/starrydata_audit/source_provenance.json`. The final verification output is in `data/source_verification.json`.

Match on paper DOI plus sample ID and verify its SID. Compare all 16 points using ≤1% relative differences for sigma and kappa (with a 0.001 S/m absolute allowance near zero sigma) and ≤1 microvolt/K for Seebeck. Endpoint rounding tolerance is 0.0001 K. Identical repeated points may collapse; conflicting temperatures in an otherwise unusable required curve are not silently interpolated. Additional rejected auxiliary candidates do not invalidate an independently matching required-channel triplet.

The cohort is defined by its released specimen list, not a fully recovered database-wide selection algorithm. The source checks do not establish physical validity or independent replication. Two separately indexed records have identical feature vectors and share a paper cluster. Auxiliary PF/ZT checks are described in Supplementary Tables 31–33. Hall data and source-reported thermal components are not likelihood constraints or independent ground truth.

The comparison with the previous corpus is supplied separately in `docs/CORRECTED_VS_PREVIOUS.md`; it is not part of the manuscript or Supplementary Information.
