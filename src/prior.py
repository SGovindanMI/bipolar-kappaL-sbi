"""Explicit prior, observation model and deterministic simulation datasets."""
import argparse,json,time,hashlib
from pathlib import Path
import numpy as np
try:from . import temodel as tm
except ImportError:import temodel as tm
ROOT=Path(__file__).resolve().parents[1]
NAMES=['log10N_net','log10m_maj','log10m_min','log10mu300','p_mu','log10Eg','log10A','w','r','kmin']
LOW=np.array([16.,-1.3,-1.7,np.nan,-3.5,-1.5,-1.,0.,-1.,0.])
HIGH=np.array([21.,.7,1.,np.nan,2.,.55,1.2,3.,2.,.7])
ZT_MAX=3.5;NOISE=.02;NG=16

def in_box(theta):
    th=np.asarray(theta,float)
    if th.ndim<1 or th.shape[-1] not in (10,11):raise ValueError('Expected 10 continuous parameters and optional binary sign')
    c=3.1-.5*(th[...,0]-17.)
    ok=np.isfinite(th).all(-1)
    if th.shape[-1]==11:ok &= (th[...,10]==0)|(th[...,10]==1)
    for k in range(10):
        lo,hi=(c-1.8,c+1.2) if k==3 else (LOW[k],HIGH[k])
        ok &= (th[...,k]>=lo)&(th[...,k]<=hi)
    return ok

def sample_box(n,rng):
    th=np.empty((n,11))
    for k in range(10):
        if k==3:
            c=3.1-.5*(th[:,0]-17.);th[:,k]=rng.uniform(c-1.8,c+1.2)
        else:th[:,k]=rng.uniform(LOW[k],HIGH[k],n)
    th[:,10]=rng.integers(0,2,n)
    lo=rng.uniform(285.,500.,n);hi=rng.uniform(500.,1250.,n)
    bad=hi-lo<200.
    while np.any(bad):
        lo[bad]=rng.uniform(285.,500.,bad.sum());hi[bad]=rng.uniform(500.,1250.,bad.sum());bad=hi-lo<200.
    return th,lo,hi

def interpolate_uniform(y,nout=16):
    p=np.linspace(0.,y.shape[1]-1,nout);i=np.minimum(p.astype(int),y.shape[1]-2);f=p-i
    return y[:,i]*(1-f)+y[:,i+1]*f

def simulate_batch(n,rng,stress=None):
    th,lo,hi=sample_box(n,rng);ng=rng.integers(8,21,n)
    if stress=='lattice_upturn':
        th[:,5]=rng.uniform(np.log10(1.5),.55,n)
        th[:,7]=-rng.uniform(.2,1.2,n)
    ratio=1. if stress not in ('mobility_low','mobility_high') else (.1 if stress=='mobility_low' else 10.)
    X=np.empty((n,50));truth=np.empty((n,4,16));accepted=np.zeros(n,bool)
    for count in range(8,21):
        sel=np.flatnonzero(ng==count)
        if not len(sel):continue
        T=np.linspace(lo[sel],hi[sel],count,axis=1)
        o=tm.forward_theta(th[sel],T,minority_mobility_ratio=ratio)
        # The zT support is evaluated on the same 16-point grid at training
        # and inference; the noisy measurements still use 8--20 points.
        sig=o['sigma']*np.exp(rng.normal(0,NOISE,o['sigma'].shape))
        S=o['S']*np.exp(rng.normal(0,NOISE,o['S'].shape))
        kap=o['kappa']*np.exp(rng.normal(0,NOISE,o['kappa'].shape))
        X[sel,:16]=np.log10(interpolate_uniform(sig));X[sel,16:32]=interpolate_uniform(S)*1e6;X[sel,32:48]=np.log(interpolate_uniform(kap))
        X[sel,48]=hi[sel]/1000.;X[sel,49]=lo[sel]/1000.
        Tg=np.linspace(lo[sel],hi[sel],16,axis=1)
        true=tm.forward_theta(th[sel],Tg,minority_mobility_ratio=ratio)
        accepted[sel]=np.max(true['zT'],axis=1)<=ZT_MAX
        truth[sel]=np.stack([true['kappa_L'],true['kappa_bip'],true['kappa_e']/(true['sigma']*Tg),true['kappa']],axis=1)
    if not np.isfinite(X).all():raise ArithmeticError('Nonfinite simulated feature')
    return th[accepted],X[accepted],truth[accepted],int((~accepted).sum())

def generate(n,seed,path,batch=4096,stress=None):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(seed);ts=[];xs=[];ys=[];got=0;rejected=0;attempted=0;all_accepted=0;t0=time.time()
    while got<n:
        th,x,y,nrej=simulate_batch(batch,rng,stress);attempted+=batch;all_accepted+=len(th);take=min(n-got,len(th));ts.append(th[:take]);xs.append(x[:take]);ys.append(y[:take]);got+=take;rejected+=nrej
        if got%50000<batch or got==n:print(f'{path.name}: {got}/{n}; {time.time()-t0:.0f}s',flush=True)
    theta=np.concatenate(ts).astype(np.float32);x=np.concatenate(xs).astype(np.float32);truth=np.concatenate(ys).astype(np.float32)
    meta=dict(model_version=tm.MODEL_VERSION,n=n,seed=seed,batch=batch,stress=stress,noise=NOISE,rejected_zT=rejected,attempted=attempted,generated_accepted=all_accepted,stored=n,seconds=time.time()-t0)
    np.savez_compressed(path,theta=theta,x=x,truth=truth,metadata=np.array(json.dumps(meta)))
    path.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
    return meta

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--n',type=int,default=600000);ap.add_argument('--seed',type=int,default=2001);ap.add_argument('--batch',type=int,default=4096);ap.add_argument('--out',type=Path,default=ROOT/'work/train_v5.npz');ap.add_argument('--stress',choices=['lattice_upturn','mobility_low','mobility_high']);a=ap.parse_args();print(generate(a.n,a.seed,a.out,a.batch,a.stress))
