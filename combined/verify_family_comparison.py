"""Recompute all common-family intervals from compact per-curve verification arrays."""
import csv,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.analysis_stats import cluster_interval
P=ROOT/'runs/v6_main/publication'
d=json.loads((P/'family_comparison.json').read_text())
with np.load(P/'family_comparison_masks.npz',allow_pickle=False) as z:
    common=z['common'];papers=z['paper'];family=z['family']
    names=['baseline','mobility','extra','spline','mobility_extra','mobility_spline']
    np.testing.assert_array_equal(common,np.logical_and.reduce([z[n+'_selected'] for n in names]))
    assert common.sum()==d['all_common_n']
    assert len(np.unique(papers[common]))==d['all_common_papers']
    checks=0
    for f,g in d['families'].items():
        m=common&(family==f);assert int(m.sum())==g['n']
        assert len(np.unique(papers[m]))==g['papers'];assert g['reported']==(g['n']>=80)
        if not g['reported']:continue
        for n in names:
            v=z[n+'_C_B'];b=z['baseline_C_B']
            for key,values in [('C_B',v),('paired_change_from_reference',v-b)]:
                expected=cluster_interval(values,papers,m,n_boot=2000,seed=2024)
                np.testing.assert_allclose(expected,g['models'][n][key],rtol=0,atol=1e-12);checks+=1
    assert sum(g['n'] for g in d['families'].values())==d['all_common_n']
for row in csv.DictReader((P/'family_source_data.csv').open(encoding='utf-8')):
    g=d['families'][row['family']];v=g['models'][row['model']][row['quantity']]
    np.testing.assert_allclose([float(row[k]) for k in ['median','lower','upper']],v,rtol=0,atol=1e-12)
report={'recomputed_interval_triplets':checks,'bootstrap_resamples':2000,'seed':2024,'common_curves':d['all_common_n'],'common_papers':d['all_common_papers'],'named_groups_reported':4,'residual_groups_reported':1,'below_threshold_labels':9,'selection_and_CSV_checks':'passed'}
(ROOT/'combined/family_verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
