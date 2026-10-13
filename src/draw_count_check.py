"""Finite-draw sensitivity on independent synthetic test cases."""
import json,numpy as np,torch
from pathlib import Path
try:from .inference import sample;from .posterior import load,ROOT
except ImportError:from inference import sample;from posterior import load,ROOT

def main():
 torch.set_num_threads(4);z=np.load(ROOT/'data/test_v5.npz');rng=np.random.default_rng(4001);ids=rng.choice(len(z['x']),512,replace=False);m,c=load();pred=[];truth=[];nfull=0
 for st in range(0,512,32):
  ix=ids[st:st+32];th,sg,ch,n,at,box=sample(z['x'][ix],m,c,rng,256,8192);keep=n==256;nfull+=int(keep.sum());pred.append(ch[keep]);truth.append(z['truth'][ix][keep])
 ch=np.concatenate(pred);truth=np.concatenate(truth);result={'seed':4001,'requested':512,'complete_256':nfull,'note':'Nested prefixes of the same retained draws, restricted to test cases yielding all 256; this is a Monte Carlo check, not proof of posterior calibration.'}
 channels=[3,4,5,2]
 for n in [64,128,256]:
  q=np.quantile(ch[:,:n,channels,:],[.025,.5,.975],axis=1);cv=((truth>=q[0])&(truth<=q[2])).mean((0,2));ref=np.median(ch[:,:,channels,:],axis=1)
  result[str(n)]={'pointwise_95_coverage':dict(zip(['kappa_L','kappa_bip','L_uni','kappa_total'],cv.tolist())),'median_absolute_difference_from_256':dict(zip(['kappa_L','kappa_bip','L_uni','kappa_total'],np.median(np.abs(q[1]-ref),axis=(0,2)).tolist()))}
 (ROOT/'data/draw_count_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
