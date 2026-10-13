"""Regression tests for physical limits and scientific aggregation."""
import sys
from pathlib import Path
import numpy as np
import pytest
from scipy.integrate import quad
from scipy.special import expit
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import temodel as tm
from prior import sample_box,in_box

def test_neutrality_high_doping_light_mass():
    T=np.array([285.,300.,750.,1250.])
    o=tm.forward(T,1e21,10**-1.3,.5,100.,-1.5,.3,2.,1.,kmin=.3)
    np.testing.assert_allclose((o['p']-o['n'])/1e27,1.,rtol=1e-10)
    assert o['eta_p'][0]>250.

def test_integral_against_independent_quadrature():
    for j in [-.5,-.473,.5,1.273,4.5]:
        for eta in [-100.,-19.987,-4.013,.013,12.137,49.99,50.01,80.,300.]:
            upper=max(140.,eta+70.)**.25
            ref=quad(lambda u:4*u**(4*j+3)*expit(eta-u**4),0,upper,epsabs=1e-60,epsrel=1e-10,limit=300)[0]
            assert abs(float(tm.F(j,eta))/ref-1.)<2e-5

def test_lorenz_limits_and_positive_lattice():
    for r in [-1.,-.497,.013,1.257,2.]:
        L=tm.band(np.array([-30.,300.]),r)[2]
        np.testing.assert_allclose(L[0],tm.KB_E**2*(r+2.5),rtol=1e-8)
        np.testing.assert_allclose(L[1],tm.KB_E**2*np.pi**2/3.,rtol=1e-3)

def test_float32_is_promoted_before_physical_constants():
    args=[1e19,.5,.5,400.,-1.5,.3,2.,1.]
    a=tm.forward(np.array([300.,750.]),*args,kmin=.3)
    b=tm.forward(np.array([300.,750.],np.float32),*[np.float32(v) for v in args],kmin=np.float32(.3))
    np.testing.assert_allclose(a['sigma'],b['sigma'],rtol=1e-6)
    np.testing.assert_allclose(b['kappa'],b['kappa_e']+b['kappa_bip']+b['kappa_L'])
    np.testing.assert_allclose(b['zT'],b['S']**2*b['sigma']*b['T']/b['kappa'])

def test_prior_corner_and_random_neutrality():
    th,lo,hi=sample_box(300,np.random.default_rng(45))
    assert in_box(th[:,:10]).all()
    o=tm.forward_theta(th,np.linspace(lo,hi,16,axis=1))
    residual=np.abs((o['p']-o['n'])/(10**th[:,0,None]*1e6)-1)
    assert residual.max()<1e-7
    assert np.all(o['kappa_L']>0)
    assert np.all(o['kappa_bip']>=0)
    assert np.all(o['kappa_bip']<=o['kappa'])
