"""Read-only review follow-up. No retraining or replacement of published outputs."""
from pathlib import Path
import sys, json, hashlib, os
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.analysis_stats import window_slope, cluster_interval

OUT = Path(__file__).resolve().parent
DATA_ROOT = Path(os.environ.get('BIPOLAR_DATA_ROOT', str(ROOT)))
source = np.load(DATA_ROOT/'data/real_analysis_set.npz')
x = source['x']; papers = source['doi'].astype(str)
sigma = 10**x[:, :16]; total = np.exp(x[:, 32:48])
masks = {}
models = ['baseline', 'mobility', 'extra', 'spline', 'mobility_extra', 'mobility_spline']
rows = {}
inputs = {}
for model in models:
    path = DATA_ROOT/('data/inference_v5.npz' if model == 'baseline' else f'runs/v6_main/{model}/real_inference.npz')
    inputs[model] = {'path': str(path.relative_to(DATA_ROOT)).replace(chr(92), '/'), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    with np.load(path) as p:
        q = p['quantiles']; T = p['Tgrid']
        A = total - (1.5+np.exp(-np.abs(x[:,16:32])/116))*1e-8*sigma*T
        B = total-q[:,1,5]*sigma*T
        C = q[:,1,3]
        extra = q[:,1,7] if q.shape[2]>7 else np.zeros_like(C)
        curves = [A, B, C, B-q[:,1,4], B-q[:,1,4]-extra]
        slopes = np.stack([window_slope(T,c) for c in curves],axis=1)
        rows[model] = {'slopes':slopes, 'native':p['admit']&np.isfinite(slopes).all(1),
                       'scored':p['scored'], 'admit':p['admit']}
common = np.logical_and.reduce([r['native'] for r in rows.values()])
result = {'scope':'Archived posterior-median curves; new descriptive sensitivity analyses, not new inference.',
          'bootstrap':'2000 source-paper cluster resamples, seed 2024; intervals descriptive, not multiplicity-adjusted',
          'common_n':int(common.sum()), 'models':{}, 'inputs':inputs}
for model,r in rows.items():
    e=r['slopes']; result['models'][model]={}
    for label,mask in [('native',r['native']),('six_model_common',common)]:
        retained=mask&(e[:,1]<=0)
        result['models'][model][label]={
            'n':int(mask.sum()),'positive_B_count':int((mask&(e[:,1]>0)).sum()),
            'positive_B_fraction':float(np.mean(e[mask,1]>0)),
            'CB_all':cluster_interval(e[:,2]-e[:,1],papers,mask),
            'B_nonpositive_n':int(retained.sum()),
            'CB_B_nonpositive':cluster_interval(e[:,2]-e[:,1],papers,retained),
            'C_minus_Cprime_all':cluster_interval(e[:,2]-e[:,4],papers,mask)}
    # Identical subset across models, selected by reference B, avoids changing
    # the population independently for each model in the additional contrast.
    fixed=common&(rows['baseline']['slopes'][:,1]<=0)
    result['models'][model]['common_reference_B_nonpositive']={
        'n':int(fixed.sum()),'CB':cluster_interval(e[:,2]-e[:,1],papers,fixed)}
    print(model, result['models'][model],flush=True)
(OUT/'positive_B_sensitivity.json').write_text(json.dumps(result,indent=2),encoding='utf8')

np.savez_compressed(OUT/'positive_B_masks.npz', common=common, common_reference_B_nonpositive=common&(rows['baseline']['slopes'][:,1]<=0), **{m+'_native_B_nonpositive':r['native']&(r['slopes'][:,1]<=0) for m,r in rows.items()})
