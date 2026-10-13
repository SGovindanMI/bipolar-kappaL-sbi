"""Regression checks for posterior geometry and sampler support."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import torch
from src.posterior import Posterior
from src.inference import sample
from src.prior import in_box

def test_precision_sampling_matches_covariance():
    rng=np.random.default_rng(123);A=np.tril(rng.normal(size=(10,10))*.1)+np.eye(10)*2
    eps=rng.normal(size=(60000,10));draw=eps@np.linalg.inv(A.T).T
    np.testing.assert_allclose(np.cov(draw,rowvar=False),np.linalg.inv(A@A.T),atol=.006,rtol=.06)

def test_sampler_retains_valid_matched_channels():
    m=Posterior();m.eval()
    # Deliberately concentrated physical synthetic Gaussian, independent of the
    # trained checkpoint, to exercise sampler constraints and channel matching.
    with torch.no_grad():m.dg.bias.fill_(2.)
    center=np.array([19.,-.2,-.3,2.,-1.,-.5,.3,1.,-.5,.2],np.float32)
    c={'xm':torch.zeros(50),'xs':torch.ones(50),'ym':torch.tensor(center),'ys':torch.full((10,),.01)}
    x=np.zeros((3,50),np.float32);x[:,48]=.8;x[:,49]=.3
    th,sign,ch,n,att,box=sample(x,m,c,np.random.default_rng(7),16,512)
    assert np.all(n==16);assert in_box(th).all()
    np.testing.assert_allclose(ch[:,:,2],ch[:,:,3]+ch[:,:,4]+ch[:,:,6],rtol=1e-12)
    T=np.linspace(300,800,16);zt=(ch[:,:,1]*1e-6)**2*ch[:,:,0]*T/ch[:,:,2]
    assert np.max(zt)<=3.5
