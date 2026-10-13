# Positive-B sensitivity revision

This release adds a paragraph to manuscript Section 3.6 and Supplementary Table 34 (two panels). Original Zotero citation fields, displayed reference text and numbering are preserved. No references were added or corrected. Trailing empty paragraphs were removed to eliminate blank final pages. Figures and their original resolutions are unchanged.

Panel A compares native populations before and after excluding each model's own positive-B slopes. Panel B uses the identical 1,361-curve subset defined by nonpositive reference B within the 1,507-curve common population. Intervals are descriptive paper-cluster bootstrap intervals (2,000 resamples, seed 2024). No new neural inference or training was performed; results remain conditional on the tested models and priors.

## Reproduction

Extract the matching research-data archive into the repository root, then run:

```
python combined/positive_B_sensitivity.py
python combined/build_citation_preserving_documents.py
python combined/verify_positive_B_revision.py
python combined/verify_combined_manuscript.py
```

For a separate data tree, set BIPOLAR_DATA_ROOT to its repository root before running the sensitivity script. The old JavaScript/finalisation pipeline is historical; the current citation-preserving builder uses the frozen author-edited DOCX files under combined/manuscript_sources. Edit those source templates for future author changes, or preserve later Word edits before rebuilding. Export fresh PDFs in Word after changing DOCX files.

## Verification

The rerun reproduced the sensitivity values; masks are supplied in combined/positive_B_masks.npz. Citation-preservation and claim-specific addition checks passed. The general numerical-token checker passed with no untraceable scientific tokens; Zotero citation results and author postal addresses are now correctly excluded from the scientific scan. This token check remains weaker than claim-specific verification.

Word PDF exports were inspected using rendered page images: 32 manuscript pages and 19 supplementary pages. All seven manuscript figures and the supplementary figure retain effective resolution above 600 dpi. New text, table headers, page breaks and final pages were checked.

## Scope and outstanding matters

This is a local upload-ready repository package; no remote GitHub commit or Figshare change was made. Existing observation and inference arrays are unchanged. The source ZIP includes new derived masks and summaries, so no new large data archive is required for this sensitivity result.

Existing bibliography issues were intentionally preserved to respect the author's Zotero instruction: AdamW lacks its proceedings title and the supplementary entry still gives 2018; reference 8 includes a literal epsilon command. Correct these in Zotero rather than editing generated bibliography text. Author declarations and remaining physical-validation work are not completed by this revision.
