"""Shared statistics; finite draws and papers in the reported subset only."""
import numpy as np

def finite_probability(values,threshold=.5):
    a=np.asarray(values);n=np.isfinite(a).sum(axis=-1)
    return np.divide(((a<threshold)&np.isfinite(a)).sum(axis=-1),n,out=np.full(n.shape,np.nan),where=n>0)

def cluster_interval(values,papers,keep=None,n_boot=2000,seed=2024):
    values=np.asarray(values,float);papers=np.asarray(papers);valid=np.isfinite(values)
    if keep is not None:valid &= np.asarray(keep,bool)
    v=values[valid];p=papers[valid]
    if not len(v):return [float('nan')]*3
    names,inv=np.unique(p,return_inverse=True);groups=[np.flatnonzero(inv==i) for i in range(len(names))]
    rng=np.random.default_rng(seed);boots=np.empty(n_boot)
    for b in range(n_boot):
        ix=np.concatenate([groups[g] for g in rng.integers(0,len(groups),len(groups))]);boots[b]=np.median(v[ix])
    return [float(np.median(v)),*np.quantile(boots,[.025,.975]).tolist()]

def interpolate(T,y,t):
    T=np.asarray(T);y=np.asarray(y);return np.array([np.interp(t,tx,yy) for tx,yy in zip(T,y)])

def window_slope(T,y,lo=400.,hi=750.):
    a,b=interpolate(T,y,lo),interpolate(T,y,hi)
    ok=(a>0)&(b>0)&(T[:,0]<=lo)&(T[:,-1]>=hi)
    out=np.full(len(y),np.nan);out[ok]=np.log(b[ok]/a[ok])/np.log(hi/lo);return out
