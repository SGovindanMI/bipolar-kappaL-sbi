# Corrected observations and aligned inference arrays

`real_analysis_set.npz` contains 13,031 source-consistent records from 2,715 papers, with 50 features per record. `analysis_set_sids.csv` and `source_papers.txt` identify the analysed specimens and papers. `corpus_selection.csv` maps corrected rows to their retained original row identities; `corpus_provenance.json` records source and corrected hashes. All empirical statistics and artwork have been rebuilt from this corpus.

The corresponding six posterior archives preserve the matched draws for these unchanged observations. Their embedded inference metadata describe the original draw-generation run, including its original source hash and timing; those fields are historical execution provenance, not a claim that a new inference run was performed. The corrected array hashes and row selection are recorded separately. Synthetic training, calibration and stress datasets are unchanged.

Source checks against the pinned official export are documented in `docs/STARRYDATA_AUDIT.md`. The exact historical list-selection rule remains incomplete. Passing the source checks does not certify experimental accuracy, material labels or physical identifiability.

`inference_v5.npz` contains, in observation row order:
- theta: (curves,128,10), float32 storage; unused slots are NaN.
- ptype: sampled majority sign; meaningful only in retained slots.
- nok: number of valid retained draws; attempted and box_hits describe proposals.
- quantiles: (curves,3,7,16), quantiles .025,.5,.975. Channels are sigma (S/m),
  S (microV/K), total kappa, lattice kappa, bipolar kappa, unipolar L, electronic kappa.
- explained: observed-point containment in the latent bands.
- scored and admit: explicit sample-count and fit-screen masks.
- Tgrid: temperature grid in K.
- slope_draws: matched-draw slopes in order A,B,C,Cprime, with NaN for undefined
  positive-endpoint comparisons or windows not spanning 400--750 K.
- bipolar, model-bipolar and model-total ratios at 750 K: matched draws; measured
  and model denominators are distinct. No sums of marginal medians are used.
- metadata: model version, seeds, proposal budget, count thresholds and timing.

`results_v5.npz` contains all-curve A/B/C/Cprime summaries and explicit masks.
`manuscript_numbers.json` is the source of all revised numerical tables.
`posterior_v5.pt` contains tensor weights, normalisers and simple metadata and is
loaded using weights_only=True. JSON files record the final training outcome and
history. `fermi_v5.npz` is a deterministic numerical integration cache.

Independent datasets (`calibration_v5`, `test_v5`) and the three `stress_*`
datasets contain theta, noisy features, true heat channels and generation
metadata. Truth order is lattice kappa, bipolar kappa, unipolar L, total kappa.
Their inference files use the same sampler/schema as real data.
`validation_summary.json` reports independent test and stress coverage. An
empirical ellipsoid rank map is diagnostic only, not a posterior transformation.

Stored posterior parameters are promoted to float64 by the forward model.
NaN draws are excluded from probability denominators. Band intervals are pointwise
latent intervals, not simultaneous confidence bands or noisy predictive intervals.
