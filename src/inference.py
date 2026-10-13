"""Prior-restricted sampling and matched-draw transport predictions.

Credible rank relabelling is deliberately not applied to these draws. Coverage
is assessed empirically on a separate test set. Bands describe latent curves.
"""
import argparse,json,time,warnings
from pathlib import Path
import numpy as np
import torch
try:
    from .posterior import load,ROOT
    from .prior import in_box,ZT_MAX
    from . import temodel as tm
except ImportError:
    from posterior import load,ROOT
    from prior import in_box,ZT_MAX
    import temodel as tm


def sample(x,model,checkpoint,rng,draws=128,budget=8192):
    x=np.asarray(x);n=len(x);T=np.linspace(x[:,49]*1000,x[:,48]*1000,16,axis=1)
    with torch.no_grad():
        xt=torch.tensor(x,dtype=torch.float32);mu,A,dg,logit=model((xt-checkpoint['xm'])/checkpoint['xs'])
    mu=mu.numpy();inv=np.linalg.inv(A.numpy().transpose(0,2,1));prob=torch.sigmoid(logit).numpy();ym=checkpoint['ym'].numpy();ys=checkpoint['ys'].numpy()
    th=np.full((n,draws,10),np.nan);sign=np.zeros((n,draws),bool);counts=np.zeros(n,int);attempted=np.zeros(n,int);box_hits=np.zeros(n,int)
    channels=np.full((n,draws,7,16),np.nan)
    for start in range(0,budget,256):
        active=np.flatnonzero(counts<draws)
        if not len(active):break
        K=min(256,budget-start);eps=rng.standard_normal((len(active),K,10));candidates=(mu[active,None,:]+np.einsum('nij,nkj->nki',inv[active],eps))*ys+ym
        signs=rng.random((len(active),K))<prob[active,None];ok=in_box(candidates);attempted[active]+=K;box_hits[active]+=ok.sum(1)
        # Evaluate only the first still-needed box proposals; discarded extras are
        # exchangeable and do not bias the retained conditional distribution.
        owners=[];cs=[];ss=[]
        for j,i in enumerate(active):
            ids=np.flatnonzero(ok[j])[:draws-counts[i]]
            if len(ids):owners.extend([i]*len(ids));cs.append(candidates[j,ids]);ss.append(signs[j,ids])
        if not owners:continue
        owners=np.array(owners);cand=np.concatenate(cs);sgn=np.concatenate(ss);o=tm.forward_theta(cand,T[owners],sgn);valid=np.max(o['zT'],axis=1)<=ZT_MAX
        L=o['kappa_e']/(o['sigma']*T[owners]);arr=np.stack([o['sigma'],o['S']*1e6,o['kappa'],o['kappa_L'],o['kappa_bip'],L,o['kappa_e']],axis=1)
        for i in np.unique(owners):
            take=np.flatnonzero((owners==i)&valid);a=counts[i];b=a+len(take)
            th[i,a:b]=cand[take];sign[i,a:b]=sgn[take];channels[i,a:b]=arr[take];counts[i]=b
    return th,sign,channels,counts,attempted,box_hits


def infer(source,out,seed=3001,draws=128,budget=8192,batch=32,checkpoint=None):
    torch.set_num_threads(4);z=np.load(source,allow_pickle=True);x=z['x'];model,c=load(checkpoint);rng=np.random.default_rng(seed);N=len(x)
    theta=np.full((N,draws,10),np.nan,np.float32);ptype=np.zeros((N,draws),bool);nok=np.zeros(N,int);attempted=np.zeros(N,int);box_hits=np.zeros(N,int)
    q=np.full((N,3,7,16),np.nan);coverage=np.full(N,np.nan);slope_draws=np.full((N,draws,4),np.nan,np.float32);bipfrac_draws=np.full((N,draws),np.nan,np.float32);model_bipfrac_draws=bipfrac_draws.copy();model_total_ratio_draws=bipfrac_draws.copy()
    T=np.linspace(x[:,49]*1000,x[:,48]*1000,16,axis=1);sig=10.**x[:,:16];kap=np.exp(x[:,32:48]);A=kap-tm.L_kim(x[:,16:32]*1e-6)*sig*T;t0=time.time()
    parameter_cover=np.zeros((N,10),bool)
    for start in range(0,N,batch):
        stop=min(start+batch,N);th,sg,ch,num,att,box=sample(x[start:stop],model,c,rng,draws,budget)
        theta[start:stop]=th;ptype[start:stop]=sg;nok[start:stop]=num;attempted[start:stop]=att;box_hits[start:stop]=box
        with warnings.catch_warnings():
            warnings.simplefilter('ignore',RuntimeWarning);qq=np.nanquantile(ch,[.025,.5,.975],axis=1).transpose(1,0,2,3);tq=np.nanquantile(th,[.025,.975],axis=1)
        q[start:stop]=qq
        obs=np.stack([sig[start:stop],x[start:stop,16:32],kap[start:stop]],axis=1)
        coverage[start:stop]=((obs>=qq[:,0,:3])&(obs<=qq[:,2,:3])).mean((1,2))
        if 'theta' in z:parameter_cover[start:stop]=(z['theta'][start:stop,:10]>=tq[0])&(z['theta'][start:stop,:10]<=tq[1])
        for k,i in enumerate(range(start,stop)):
            if T[i,0]>400 or T[i,-1]<750:continue
            B=kap[i,None,:]-ch[k,:,5]*sig[i,None,:]*T[i,None,:];Cp=B-ch[k,:,4];C=ch[k,:,3]
            for h,curves in enumerate([np.broadcast_to(A[i],B.shape),B,C,Cp]):
                lo=np.array([np.interp(400,T[i],v) for v in curves]);hi=np.array([np.interp(750,T[i],v) for v in curves]);valid=(lo>0)&(hi>0)&np.isfinite(lo)&np.isfinite(hi)
                slope_draws[i,valid,h]=np.log(hi[valid]/lo[valid])/np.log(750/400)
            bip750=np.array([np.interp(750,T[i],v) for v in ch[k,:,4]]);total750=np.array([np.interp(750,T[i],v) for v in ch[k,:,2]])
            bipfrac_draws[i]=bip750/np.interp(750,T[i],kap[i]);model_bipfrac_draws[i]=bip750/total750;model_total_ratio_draws[i]=total750/np.interp(750,T[i],kap[i])
        if start%(batch*10)==0:print(f'{Path(out).name}: {stop}/{N}, {time.time()-t0:.0f}s',flush=True)
    min_draws=min(64,draws);scored=nok>=min_draws;admit=scored&(coverage>=.75)
    meta=dict(model_version=tm.MODEL_VERSION,seed=seed,draws=draws,budget=budget,batch=batch,min_draws=min_draws,admission_threshold=.75,bands='latent 2.5 and 97.5 percentiles, no observation noise',prior_restriction='conditional parameter box and peak zT <=3.5 on 16-point observation window',seconds=time.time()-t0)
    np.savez_compressed(out,theta=theta,ptype=ptype,nok=nok,attempted=attempted,box_hits=box_hits,quantiles=q,explained=coverage,scored=scored,admit=admit,Tgrid=T,slope_draws=slope_draws,bipfrac_draws=bipfrac_draws,model_bipfrac_draws=model_bipfrac_draws,model_total_ratio_draws=model_total_ratio_draws,parameter_cover=parameter_cover,metadata=np.array(json.dumps(meta)))
    Path(out).with_suffix('.json').write_text(json.dumps(meta,indent=2));print(dict(n=N,scored=int(scored.sum()),admitted=int(admit.sum()),seconds=meta['seconds']),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=ROOT/'data/real_analysis_set.npz');p.add_argument('--out',type=Path,default=ROOT/'data/inference_v5.npz');p.add_argument('--seed',type=int,default=3001);p.add_argument('--draws',type=int,default=128);p.add_argument('--budget',type=int,default=8192);p.add_argument('--batch',type=int,default=32);a=p.parse_args();infer(a.source,a.out,a.seed,a.draws,a.budget,a.batch)
