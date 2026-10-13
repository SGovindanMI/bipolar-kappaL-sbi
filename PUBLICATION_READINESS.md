> Historical shorter-draft record. The complete combined paper and current assessment are documented in README.md and FINAL_REVISION_REPORT.md.

# Publication readiness assessment

Assessed 9 October 2026 against the completed computational records and the official Nature Communications/Nature Portfolio guidance linked below.

**Verdict: a substantially improved article-format research draft, but not yet a submission-ready claim of validated or uniquely identifiable thermal decomposition. Acceptance by Nature Communications cannot be guaranteed.** Journal editors must also judge novelty, breadth and significance; this audit cannot determine their decision. A narrower model-sensitivity paper is supported more strongly than a claim that the original physical limitations have been solved.

## What this revision delivers

- A 149-word unreferenced abstract, Introduction, Results, Discussion, expanded Methods, separate Data and Code availability statements, and references numbered in first-citation order.
- Four figures embedded immediately after relevant discussion, each regenerated from the stored results at 600 dpi, with RGB TIFF/PNG and editable PDF/SVG alternatives. They are not enlarged versions of earlier 200 dpi images. Embedded Word images retain more than 600 effective dpi at the chosen width.
- Eight supplementary tables, including actual completed and selected training epochs. Detailed numerical evidence has not been removed to make the narrative more favourable.
- Neural architecture, input/target normalisation, Gaussian precision parameterisation, binary-sign factorisation, training loss, optimiser, seeds, stopping rules, posterior sampling and approximation limitations.
- Plotted source data, reproducible generation scripts and document/image verification records. This revision does not retrain the models or change inference arrays.

## Is v5 included?

Yes. The original corrected v5 checkpoint and inference arrays remain the frozen reference comparator in all-model common-population comparisons and shared/cross-model stress tests. The scientific narrative calls this the shared-band, monotone-lattice reference model. Code availability explicitly identifies software release v5 and the newer run location. A software version is not a separate physical theory or a published external comparator. Five new extensions were trained; the reference was not retrained here. The original release files remain in the repository.

## Evidence and its limits

| Finding | What the completed results support | What they do not support |
|---|---|---|
| Upturn stress, 509 common scored curves | Lattice coverage 41.7% to 97.2%; median width 0.699 to 9.983 W m⁻¹ K⁻¹ | Generally improved point accuracy: absolute slope error increases 0.541 to 0.661 on 87 common selected curves |
| Independent same-model tests | Flexible independent-band lattice/bipolar coverage 91.7%/92.0% on 5,986 scored cases | Full nominal 95% calibration; simultaneous curve coverage; guaranteed experimental coverage |
| Mobility-prefactor stress | Independent bands improve bipolar coverage on the tested fixed common populations | Resolution of all mobility, band-structure or scattering misspecification |
| Cross-hypothesis tests | Total-curve fit can coexist with poor channel attribution; reverse transfer has severe scoring attrition | Identification of which thermal mechanism actually occurs in a specimen |
| Experimental common population | Thermal-model-dependent estimates on 1,528 curves from 649 papers | Known experimental channel truth, unbiased corpus-wide corrections or automatic generalisation to excluded curves |
| Neural training | Five reproducible single-seed runs and retained best checkpoints | Novel network architecture, convergence proof, multimodal posterior fidelity or training-seed robustness |

## Scientific work still needed

These are this assessment's recommendations for supporting the intended claims, not a claim that the journal mandates these exact experiments.

1. **External validation and physical identifiability.** Establish a small, traceable benchmark with independent Hall/carrier, band-gap or thermal-channel constraints and specimen-level provenance. Evaluate held-out constraints without using them to tune the reported conclusions. Do not imply that low-temperature literature examples validate this high-temperature corpus.
2. **Posterior reliability.** Add simulation-based rank calibration and conditional coverage checks, diagnose failure regions, and compare representative curves with per-curve Bayesian inference/MCMC. Check sign–parameter dependence and Gaussian inadequacy. A flexible conditional density is a candidate remedy, not an already demonstrated improvement. Include several training seeds and posterior-draw sensitivity; the shared-band spline run hit the 900-epoch cap.
3. **Prior and model sensitivity.** Vary lattice-node priors, knot placement, extra-channel amplitude/shape and realistic noise models. The current extra-channel and spline supports differ greatly. The inherited stress sets informed the support expansion, so reserve genuinely untouched departure tests for final claims.
4. **Corpus audit and selection.** Resolve or transparently bound the lost historical 407-record filter, verify representative digitised curves against source publications, and document missingness, exclusions and paper/specimen dependence. Report both common and native populations without interpreting larger admission as better recovery.
5. **Novelty and scope.** Strengthen the connection to a specific scientific question and independent physical evidence. The present neural architecture is conventional amortised Gaussian density estimation. Do not market it as a new neural algorithm or claim the upturn/mobility issues are fully removed.

## Submission items still requiring author information

Author names, affiliations, corresponding-author contact, author contributions, funding/acknowledgements and competing-interest declarations were not provided. They have not been invented. The authors must establish a public versioned code/data deposit, persistent identifiers, licences and source-data redistribution rights, then replace the explicitly pending availability text. The journal's applicable software/reporting checklist must be completed for the final deposited version. No journal submission or public publication has been performed.

## Journal guidance checked

- [Nature Communications: how to submit](https://www.nature.com/ncomms/submit/how-to-submit). Search-indexed current guidance requests vector line art, or 1,200 dpi if vector line art cannot be supplied. **600 dpi alone is therefore not the complete figure-delivery criterion**: editable vector artwork accompanies the requested 600 dpi images. The full page redirected to a blocked publisher authentication route during this audit; no blanket compliance certification is made.
- [Nature research figure specifications](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/). Fully accessible guidance supports editable vectors, embedded fonts, labelled axes and accessible colour use. The figures use a colour-blind-accessible palette and embedded Type 42 PDF fonts; source vectors are provided.
- [Nature Communications policy guide](https://www.nature.com/ncomms/submit/policy). Separate data and code access statements are relevant to the initial checks. The current draft explicitly records the missing permanent deposits.
- [Nature Communications resources](https://www.nature.com/ncomms/submit/resources). Links to the software checklist and computational reporting guidance.
- [2019 quick submission guide](https://www.nature.com/documents/ncomms-submission-guide.pdf). This older guide suggests an approximately 150-word abstract and up to ten display items. It informed conservative formatting, but is not represented as proof of all current article limits.

The next consequential step is scientific validation and author/deposit completion, not further cosmetic polishing. The current draft is suitable for co-author review and planning those tests; it should not be presented as guaranteed to pass editorial or peer review.
