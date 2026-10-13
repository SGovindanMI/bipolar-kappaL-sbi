"""Reconstruct every estimate from each model's own saved posterior summaries."""
import sys,json,csv,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.relaxed_analysis import estimates
from src.analysis_stats import cluster_interval
N=json.loads((ROOT/'combined/combined_numbers.json').read_text())
source=np.load(ROOT/'data/real_analysis_set.npz',allow_pickle=True)
papers=source['doi'].astype(str);rows={};provenance={}
for m in N['models']:
    path=ROOT/('data/inference_v5.npz' if m=='baseline' else f'runs/v6_main/{m}/real_inference.npz')
    with np.load(path) as p:
        curves,e=estimates(source,p)
        # Explicitly verify the reconstruction against this file, not a reference-file channel.
        q=p['quantiles'];T=p['Tgrid'];x=source['x'].astype(float)
        np.testing.assert_array_equal(curves[2],q[:,1,3])
        np.testing.assert_allclose(curves[1],np.exp(x[:,32:48])-q[:,1,5]*10**x[:,:16]*T,equal_nan=True)
        np.testing.assert_allclose(curves[3],curves[1]-q[:,1,4],equal_nan=True)
        rows[m]=(e,p['admit']&np.isfinite(e).all(1))
    provenance[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
common=np.logical_and.reduce([v[1] for v in rows.values()]);assert common.sum()==N['all_model_common']['n']
assert len(np.unique(papers[common]))==N['all_model_common']['papers']
base=rows['baseline'][0]
out={'n':int(common.sum()),'papers':len(np.unique(papers[common])),'bootstrap':{'resamples':2000,'seed':2024,'unit':'source paper'},'models':{},'provenance':provenance}
names=['A','B','C','Cprime_bip','Cprime_all'];csvrows=[]
for m,(e,mask) in rows.items():
    np.testing.assert_array_equal(e[common,0],base[common,0])
    def ci(v):return cluster_interval(v,papers,common,2000,2024)
    shifts={k:ci(e[:,i]-e[:,j]) for k,i,j in [('C_B',2,1),('Cprime_bip_B',3,1),('Cprime_all_B',4,1),('C_Cprime_all',2,4)]}
    changes={name:ci(e[:,j]-base[:,j]) for j,name in enumerate(names)}
    changes['C_B']=ci((e[:,2]-e[:,1])-(base[:,2]-base[:,1]))
    np.testing.assert_allclose(shifts['C_B'],N['corpus'][m]['all_model_common']['CB'],atol=1e-10)
    out['models'][m]={'slopes':{name:ci(e[:,j]) for j,name in enumerate(names)},'shifts':shifts,'changes_from_reference':changes}
    for i in np.flatnonzero(common):csvrows.append([int(i),papers[i],m,*e[i].tolist()])
    print(m,{k:round(v[0],4) for k,v in out['models'][m]['slopes'].items()},flush=True)
(ROOT/'combined/component_comparison.json').write_text(json.dumps(out,indent=2))
with (ROOT/'combined/component_source_data.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow(['frozen_row','source_paper','model',*names]);w.writerows(csvrows)
print('Verified: A invariant; B, C and both additive estimates reconstructed from each model; common C-B reproduces archive.')
