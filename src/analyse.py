"""Regenerate the manuscript statistics from version 5 matched-draw results."""
import json,warnings
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
try:
    from . import temodel as tm
    from .analysis_stats import cluster_interval,finite_probability,window_slope,interpolate
except ImportError:
    import temodel as tm
    from analysis_stats import cluster_interval,finite_probability,window_slope,interpolate
ROOT=Path(__file__).resolve().parents[1]

def main():
    z=np.load(ROOT/'data/real_analysis_set.npz',allow_pickle=True);pfile=np.load(ROOT/'data/inference_v5.npz');p={k:pfile[k] for k in pfile.files};pfile.close();x=z['x'];doi=z['doi'].astype(str);family=z['family'].astype(str);T=p['Tgrid'];q=p['quantiles'];admit=p['admit'];scored=p['scored'];sig=10**x[:,:16];kap=np.exp(x[:,32:48]);S=x[:,16:32]
    A=kap-tm.L_kim(S*1e-6)*sig*T;B=kap-q[:,1,5]*sig*T;C=q[:,1,3];Cp=B-q[:,1,4];curves=[A,B,C,Cp];e=np.stack([window_slope(T,y) for y in curves],axis=1);span=(T[:,0]<=400)&(T[:,-1]>=750);window=admit&span
    # All displayed comparisons use a common finite A/B/C/Cprime endpoint set.
    paired=window&np.isfinite(e).all(1);frac=interpolate(T,q[:,1,4],750)/interpolate(T,kap,750)
    def ci(v,m,seed=2024):return cluster_interval(v,doi,m,2000,seed)
    def med(v,m):return float(np.nanmedian(v[m])) if np.any(m) else None
    def group(m):
        m=m&np.isfinite(e).all(1);d=e[:,2]-e[:,1]
        return dict(n=int(m.sum()),papers=int(len(np.unique(doi[m]))),A=med(e[:,0],m),B=med(e[:,1],m),C=med(e[:,2],m),Cp=med(e[:,3],m),CB=ci(d,m),CA=ci(e[:,2]-e[:,0],m),CpB=ci(e[:,3]-e[:,1],m),CpA=ci(e[:,3]-e[:,0],m),rho=float(spearmanr(frac[m],d[m]).statistic) if m.sum()>2 else None)
    classes=finite_probability(p['theta'][:,:,8]);class_masks=[classes>.8,classes<.2,(classes>=.2)&(classes<=.8)]
    result=dict(model_version=tm.MODEL_VERSION,n=len(x),papers=len(np.unique(doi)),scored=int(scored.sum()),admitted=int(admit.sum()),admitted_papers=len(np.unique(doi[admit])),unscored=int((~scored).sum()),excluded=int((scored&~admit).sum()),window=int(window.sum()),paired=int(paired.sum()),window_nonpositive_excluded=int((window&~paired).sum()),window_papers=len(np.unique(doi[paired])),bootstrap=dict(resamples=2000,seed=2024,unit='paper within the reported finite subset',estimand='median over curves'),slopes={name:ci(e[:,i],paired) for i,name in enumerate(['A','B','C','Cp'])},shifts={name:ci(e[:,i]-e[:,j],paired) for name,i,j in [('BA',1,0),('CB',2,1),('CA',2,0),('CpB',3,1),('CpA',3,0)]})
    result['strata']={name:group(paired&m) for name,m in [('below_2',frac<.02),('2_to_10',(frac>=.02)&(frac<.1)),('10_to_100',(frac>=.1)&(frac<=1.)),('above_100',frac>1.)]}
    result['families']={f:group(paired&(family==f)) for f in np.unique(family) if (paired&(family==f)).sum()>=80}
    result['shared_family_papers']=sum(len(np.unique(family[paired&(doi==d)]))>1 for d in np.unique(doi[paired]))
    ab=np.abs(S);ip=ab.argmax(1);interior=(ip>0)&(ip<15);roll=np.where(interior,(ab.max(1)-ab[:,-1])/np.maximum(ab.max(1),1e-12),-1.)
    result['rollover']={name:group(paired&m) for name,m in [('none',roll<0),('below_5',(roll>=0)&(roll<.05)),('5_to_15',(roll>=.05)&(roll<.15)),('above_15',roll>=.15)]}
    result['thresholds']={str(th):group(scored&span&(p['explained']>=th)) for th in [0,.3,.4,.5,.6,.7,.75,.8,.85,.9,.95]}
    result['classes']={name:dict(n=int((admit&m).sum()),fraction=float(m[admit].mean())) for name,m in zip(['phonon_like','impurity_like','ambiguous'],class_masks)}
    # Mean/fraction intervals need their own statistic; median binary intervals are invalid.
    def mean_ci(values,mask):
        v=np.asarray(values)[mask];d=doi[mask];_,inv=np.unique(d,return_inverse=True);g=[np.flatnonzero(inv==i) for i in range(inv.max()+1)];rng=np.random.default_rng(2024);out=[]
        for _ in range(2000):out.append(np.mean(v[np.concatenate([g[i] for i in rng.integers(0,len(g),len(g))])]))
        return [float(v.mean()),*np.quantile(out,[.025,.975]).tolist()]
    for name,m in zip(['phonon_like','impurity_like','ambiguous'],class_masks):result['classes'][name]['ci']=mean_ci(m,admit)
    result['rollover_upturn_A']={name:dict(n=int((admit&m).sum()),ci=mean_ci(A[:,-1]>A[:,8],admit&m)) for name,m in [('none',roll<0),('below_5',(roll>=0)&(roll<.05)),('5_to_15',(roll>=.05)&(roll<.15)),('above_15',roll>=.15)]}
    result['upturn']={name:dict(n=int((admit&(v[:,-1]>v[:,8])).sum()),ci=mean_ci(v[:,-1]>v[:,8],admit),bipolar_median_up=med(q[:,1,4,-1]/kap[:,-1],admit&(v[:,-1]>v[:,8])),bipolar_median_other=med(q[:,1,4,-1]/kap[:,-1],admit&~(v[:,-1]>v[:,8]))) for name,v in [('A',A),('B',B)]}
    result['negative_A']={name:dict(n=int((m&(A.min(1)<0)).sum()),denominator=int(m.sum()),fraction=float((A[m].min(1)<0).mean())) for name,m in [('all',np.ones(len(x),bool)),('admitted',admit),('excluded',scored&~admit),('unscored',~scored)]}
    result['lorenz_change_BminusA_at_Tlo']=np.quantile((B-A)[admit,0],[.1,.5,.9]).tolist()
    result['r_median']=ci(np.nanmedian(p['theta'][:,:,8],axis=1),admit)
    obs=np.stack([sig,S,kap],axis=1);contained=(obs>=q[:,0,:3])&(obs<=q[:,2,:3]);result['property_coverage']={name:contained[m].mean((0,2)).tolist() for name,m in [('admitted',admit),('excluded',scored&~admit)]}
    result['temperature_admission']={f'{lo}-{hi}':dict(n=int((scored&(T[:,-1]>=lo)&(T[:,-1]<(hi+(.01 if hi==1250 else 0)))).sum()),ci=mean_ci(admit,scored&(T[:,-1]>=lo)&(T[:,-1]<(hi+(.01 if hi==1250 else 0))))) for lo,hi in [(500,700),(700,900),(900,1100),(1100,1250)]}
    # Model totals and model fractions are calculated draw by draw, never as sums of marginal medians.
    result['median_model_total_over_measured_750']=med(interpolate(T,q[:,1,2],750)/interpolate(T,kap,750),paired)
    bad=paired&(frac>1.)
    result['above_unity_diagnostics']=dict(n=int(bad.sum()),papers=int(len(np.unique(doi[bad]))),model_bipolar_fraction_range=[float(np.nanmin(p['model_bipfrac_draws'][bad])),float(np.nanmax(p['model_bipfrac_draws'][bad]))] if bad.any() else [],median_model_total_ratio_range=np.quantile(np.nanmedian(p['model_total_ratio_draws'][bad],axis=1),[0,1]).tolist() if bad.any() else [])
    # Nested uncertainty: a paper bootstrap and one matched parameter draw per unique curve.
    sd=p['slope_draws'];result['paired_draw_nonpositive_counts']={name:int((~np.isfinite(sd[paired,:,i]) & (np.arange(sd.shape[1])[None,:]<p['nok'][paired,None])).sum()) for i,name in enumerate(['A','B','C','Cp'])};ids=np.flatnonzero(paired);groups=[ids[doi[ids]==d] for d in np.unique(doi[ids])];rng=np.random.default_rng(2025);nested={k:[] for k in ['CB','CA','CpB','CpA']}
    for _ in range(2000):
        ix=np.concatenate([groups[g] for g in rng.integers(0,len(groups),len(groups))]);u,inv=np.unique(ix,return_inverse=True);choice=np.array([rng.integers(0,p['nok'][i]) for i in u]);vals=sd[u,choice][inv]
        for name,i,j in [('CB',2,1),('CA',2,0),('CpB',3,1),('CpA',3,0)]:nested[name].append(np.nanmedian(vals[:,i]-vals[:,j]))
    result['nested_intervals']={k:np.quantile(v,[.025,.5,.975]).tolist() for k,v in nested.items()}
    np.savez_compressed(ROOT/'data/results_v5.npz',A=A,B=B,C=C,Cp=Cp,exponents=e,Tgrid=T,admit=admit,scored=scored,window=window,paired=paired,bipolar_fraction=frac,rollover=roll,r_probability=classes,doi=doi,family=family)
    def clean(v):
        if isinstance(v,dict):return {k:clean(x) for k,x in v.items()}
        if isinstance(v,list):return [clean(x) for x in v]
        if isinstance(v,(float,np.floating)) and not np.isfinite(v):return None
        if isinstance(v,np.integer):return int(v)
        return v
    result=clean(result)
    (ROOT/'data/manuscript_numbers.json').write_text(json.dumps(result,indent=2,allow_nan=False));print(json.dumps(result,indent=2))

if __name__=='__main__':
    with warnings.catch_warnings():warnings.simplefilter('ignore',RuntimeWarning);main()
