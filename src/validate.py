"""Independent diagnostics for the released constrained sampler."""
import json,numpy as np,torch
from scipy.stats import chi2
from pathlib import Path
try:from .posterior import load,ROOT
except ImportError:from posterior import load,ROOT

def ellipsoid(z,m,c):
    with torch.no_grad():
        x=torch.tensor(z['x']);y=torch.tensor(z['theta'][:,:10]);mu,A,dg,logit=m((x-c['xm'])/c['xs']);v=torch.bmm(A.transpose(1,2),((y-c['ym'])/c['ys']-mu).unsqueeze(-1)).squeeze(-1)
    return (v*v).sum(1).numpy()

def main():
    torch.set_num_threads(4);m,c=load();cal=np.load(ROOT/'data/calibration_v5.npz');test=np.load(ROOT/'data/test_v5.npz');dc=ellipsoid(cal,m,c);dt=ellipsoid(test,m,c);levels=[.5,.9,.95,.99];limits=np.quantile(dc,levels)
    result=dict(ellipsoid=dict(levels=levels,raw_test_coverage=[float((dt<=chi2.ppf(v,10)).mean()) for v in levels],diagnostic_rank_map_test_coverage=[float((dt<=v).mean()) for v in limits],calibration_thresholds=limits.tolist(),note='Rank map is diagnostic only; it is not applied to the constrained sampler.'))
    for name in ['test_v5','stress_lattice_upturn','stress_mobility_low','stress_mobility_high']:
        z=np.load(ROOT/f'data/{name}.npz');p=np.load(ROOT/f'data/{name}_inference.npz');q=p['quantiles'];scored=p['scored'];admit=p['admit'];true=z['truth'];channel_ids=[3,4,5,2]
        cov=(true>=q[:,0,channel_ids])&(true<=q[:,2,channel_ids]);bias=q[:,1,channel_ids]-true
        result[name]=dict(n=len(scored),scored=int(scored.sum()),admitted=int(admit.sum()),parameter_95_coverage_on_scored=p['parameter_cover'][scored].mean(0).tolist(),derived_95_pointwise_coverage_on_scored=dict(zip(['kappa_L','kappa_bip','L_uni','kappa_total'],cov[scored].mean((0,2)).tolist())),derived_median_relative_error_on_scored=dict(zip(['kappa_L','kappa_bip','L_uni','kappa_total'],np.nanmedian(bias[scored]/np.maximum(np.abs(true[scored]),1e-10),axis=(0,2)).tolist())))
        if name=='stress_lattice_upturn':
            eligible=true[:,1,-1]/true[:,3,-1]<.02;false=q[:,1,4,-1]/true[:,3,-1]>.1
            result[name]['false_bipolar_assignment']=dict(definition='True bipolar heat below 2% and inferred median above 10% of true total at Thi; genuine lattice upturn generated outside fitted prior',eligible_scored=int((eligible&scored).sum()),false_scored=int((eligible&scored&false).sum()),eligible_admitted=int((eligible&admit).sum()),false_admitted=int((eligible&admit&false).sum()))
    (ROOT/'data/validation_summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
