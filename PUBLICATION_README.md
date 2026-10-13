> Historical shorter-draft record. The complete combined paper and current assessment are documented in README.md and FINAL_REVISION_REPORT.md.

# Article-format revision

The latest manuscript is `runs/v6_main/publication/manuscript_publication.docx`; the previous `manuscript_v6_research.docx` is retained as an earlier draft. Read `PUBLICATION_READINESS.md` before describing this as submission-ready.

## Reproduce the presentation

From the repository root, with the scientific environment in `requirements-v6-environment.txt`:

```text
python -m src.publication_figures
```

Then, with Python containing python-docx and Pillow:

```text
python experiments/build_publication.py
```

This creates the main article and Supplementary Information, using the completed run diagnostics and original research-draft text. Native editable Word equations are used. Figures appear within Results, in first-citation order. The NN precision factor satisfies precision = A A-transpose; the sampler uses inverse A-transpose. Do not reinterpret A as a covariance Cholesky factor.

The four figure sets include 600 dpi PNG and RGB TIFF, plus editable PDF and SVG. `figure_source_data.csv` contains every plotted value, including training histories. Figure 2 coverage/width use 509 common scored curves; slope error uses 87 common admitted positive-endpoint cases. Figure 4 counts refer to model-specific scored cases out of 1,000, not one fixed intersection. Figure 3 error bars are paper-clustered sampling intervals, not model-choice uncertainty. Internal variant identifiers are mapped to descriptive figure labels in the figure script.

## Verification and provenance

The original corrected release v5 remains the physical reference comparator and is preserved. All five new production models and inference results are unchanged by this presentation revision. The original numerical audit lives in the parent run directory; `publication_qa.json` records the new document page, equation and embedded-resolution checks. Layout was rendered with installed Word because LibreOffice was unavailable, then inspected from PDF page images. `experiments/inspect_publication.py` regenerates these checks from exported PDFs using pypdf, pypdfium2, Pillow and lxml.

`PUBLICATION_READINESS.md` documents outstanding external validation, calibration, prior/noise robustness, corpus provenance and author/deposit requirements. The manuscript makes no claim of guaranteed acceptance or unique experimental thermal separation. Full scientific reruns are described in `REDO_README.md`; the presentation commands above do not retrain or rerun inference.
