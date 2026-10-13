# Corrected bipolar transport inference repository

This version contains a corrected charge-neutrality solver and a freshly trained
conditional posterior. The version 5 results replace the original version 4T
results. Do not combine the old checkpoint with this simulator.

The manuscript reports **model-dependent decompositions**, not verified errors in
each source publication. A latent-curve fit screen is not proof of a correct
thermal decomposition or calibrated uncertainty on real materials.

## Quick reproduction from released arrays

Use Python 3.12 in a virtual environment and install `requirements.txt`.
From the repository root:

```text
python -m pytest tests -q
python -m src.verify_release
python -m src.analyse
python figures/make_figures.py
python -m src.validate
```

`analyse` writes `data/manuscript_numbers.json` and `data/results_v5.npz`.
`validate` reads the archived independent test/stress inference results and writes
`data/validation_summary.json`. Bootstrap resampling takes a few minutes.
All paths are relative to the code location, so analysis also works when invoked
from a different current directory. Use module commands from the root.

## Full computational reproduction

```text
python -m src.reproduce --retrain
```

This generates the 600,000-example simulation set, retrains the model, generates
independent diagnostics and stress datasets, performs inference and rebuilds all
results and figures. It is computationally substantial; a supported CUDA GPU is
recommended for training. Install the appropriate official PyTorch build for
your hardware. The released run used PyTorch 2.11.0 with CUDA 12.8. CPU inference
uses double-precision transport calculations. No external raw-data download is
needed to reproduce the frozen-array analysis.

To repeat inference using the released checkpoint:

```text
python -m src.reproduce
```

Every stochastic stage has a recorded seed. Retraining on other hardware or
library versions need not be bitwise identical. The released checkpoint and
inference arrays define the reported results. `data/*.json` records settings,
counts, timings and training history. The empirical ellipsoid rank map is a
**diagnostic only** and does not transform the constrained draws.

## Scientific definitions

* A: measured total minus Kim unipolar Lorenz estimate × measured conductivity × T.
* B: measured total minus posterior median unipolar Lorenz number × measured conductivity × T.
* C: posterior median of the model lattice term.
* Cprime: B minus posterior median bipolar heat.

Slopes use positive endpoints at 400 and 750 K. Main comparisons use a common
finite subset for all four estimates. Non-positive endpoints are excluded and
counted, never clipped into artificial logarithms. Main intervals bootstrap
papers present in the reported subset; nested intervals also select matched
posterior draws. They do not quantify all systematic or model uncertainty.

The sampler targets the Gaussian approximation restricted to the conditional
parameter bounds and peak zT <= 3.5 on the 16-point window. It is not an exact
posterior sampler. It retains up to 128 draws from 8,192 proposals; at least 64
are required for scoring. Admission requires >= 75% of observed points within
latent 95% bands. No observation noise is added to those bands.

## Data provenance and limits

The supplied frozen corpus contains 13,256 curves from 2,754 papers. Its raw
Starrydata snapshot is not supplied. A historical 407-record selection filter is
not recoverable as a general rule; the retained sample identifiers are preserved.
`src/build_corpus.py` reconstructs features for that identifier list when given a
compatible export; its cache is keyed to the CSV SHA-256 and parser version.
This is distinct from independently recreating every upstream selection step.
See `docs/DATA.md` and `docs/source_papers.txt` for attribution and schema.

The model uses a decreasing lattice term and shared band mobilities/scattering.
Independent base-model coverage and three explicit stress tests are archived.
They do not establish validation against withheld Hall data, independent gaps,
a flexible-lattice fit of real data or an audit of source authors' reported
conductivities. These remain open scientific limitations, stated in the manuscript.

Author information and a public repository URL were intentionally left out.
See `CITATION.md`. Original development notebooks and old derived outputs are not
included because they contain stale results and code that can overwrite the
corrected model. The replacement notebooks call the maintained modules.
