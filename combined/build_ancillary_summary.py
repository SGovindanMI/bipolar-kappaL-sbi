"""Rebuild final-cohort ancillary summaries from the archived source-audit rows.

The source audit rows use original_row identifiers; corpus_selection.csv supplies
the immutable mapping into the corrected corpus. They are source diagnostics,
not model predictions or independent channel labels.
"""
import json
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'combined/starrydata_audit'
mapping=pd.read_csv(ROOT/'data/corpus_selection.csv');good=set(mapping.original_row)
a=pd.read_csv(P/'derived_property_consistency.csv');a=a[a.frozen_row.isin(good)];out={}
for prop,g in a.groupby('property'):
    b=g.groupby('frozen_row').median_symmetric_relative_difference.min()
    out[prop]={'n':len(b),'curves':len(g),'median_difference':float(b.median()),'flag_n':int((b>.2).sum())}
inv=pd.read_csv(P/'property_inventory.csv')
out['inventory']=inv[['property','unit','verified_inputs_samples','verified_inputs_temperature_K_samples']].rename(columns={'verified_inputs_samples':'samples','verified_inputs_temperature_K_samples':'temperature_K_samples'}).to_dict('records')
out['definitions']={'threshold':.2,'minimum_overlap_points':5,'statistic':'Best-candidate per-sample median symmetric relative difference','note':'Derived-data consistency, not independent validation or a measurement error diagnosis.'}
(ROOT/'data/ancillary_summary.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print('Rebuilt ancillary summaries for',len(good),'selected records.')
