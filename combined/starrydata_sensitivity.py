"""Existing-posterior sensitivity to input audit flags; no retraining or inference."""
import sys,json
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.relaxed_analysis import estimates
from src.analysis_stats import cluster_interval
P=ROOT/'combined/starrydata_audit'
with np.load(ROOT/'data/real_analysis_set.npz',allow_pickle=True) as z:f={k:z[k] for k in z.files}
a=pd.read_csv(P/'per_sample_audit.csv');h=pd.read_csv(P/'historical_join_audit.csv');c=pd.read_csv(ROOT/'combined/component_source_data.csv')
good=a.verified_within_tolerance.to_numpy();n=len(good);papers=f['doi'];family=f['family']
# Remove redundant identical inputs in an additional sensitivity only.
_,unique=np.unique(f['x'],axis=0,return_index=True);dedup=np.zeros(n,bool);dedup[unique]=True
extra=pd.read_csv(P/'derived_property_consistency.csv');flags=extra.groupby(['frozen_row','property']).median_symmetric_relative_difference.min();bad=set(flags[flags>.2].index.get_level_values(0))
strict=good&~np.isin(np.arange(n),list(bad))
cohorts={'verified':good,'verified_deduplicated':good&dedup,'verified_and_no_derived_flag':strict}
out={'caveat':'Sensitivity analyses retain original posterior estimates. They do not repair mixed inputs or validate physical identifiability. Derived-property flags are exploratory and not measurement-error diagnoses.',
 'mixed_transport_rows':int(h.mixed_papers.sum()),'mixed_transport_verified':int((h.mixed_papers.to_numpy()&good).sum()),
 'populations':{},'models':{},'families':{}}
for name,mask in cohorts.items():out['populations'][name]={'n':int(mask.sum()),'papers':len(np.unique(papers[mask]))}
for model in c.model.unique():
    path=ROOT/('data/inference_v5.npz' if model=='baseline' else f'runs/v6_main/{model}/real_inference.npz')
    with np.load(path) as p:
        _,e=estimates(f,p);admit=p['admit'];native=admit&np.isfinite(e).all(1)
    common=np.isin(np.arange(n),c.frozen_row.unique());v=e[:,2]-e[:,1]
    mm={}
    for label,mask in [('original_native',native),('original_common',common),*[(name+'_native',native&m) for name,m in cohorts.items()],*[(name+'_common',common&m) for name,m in cohorts.items()]]:
        mm[label]={'n':int(mask.sum()),'papers':len(np.unique(papers[mask])),'C_minus_B':cluster_interval(v,papers,mask)}
    out['models'][model]=mm
    out['families'][model]={str(fam):{'n':int((common&good&(family==fam)).sum()),'original_n':int((common&(family==fam)).sum()),'C_minus_B':cluster_interval(v,papers,common&good&(family==fam))} for fam in np.unique(family[common])}
    print(model,mm['original_common']['C_minus_B'],mm['verified_common']['C_minus_B'],flush=True)
(P/'sensitivity.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
