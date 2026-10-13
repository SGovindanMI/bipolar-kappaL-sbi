"""Physical regression and inference contracts for the new model family."""
import numpy as np
import pytest
import torch
from src import prior, temodel
from src.relaxed import Spec, VARIANTS, KNOTS, forward, sample_box, in_box, positive_lattice
from src.relaxed_posterior import Posterior


def base_inputs():
    th, lo, hi = prior.sample_box(12, np.random.default_rng(14))
    return th, np.linspace(lo, hi, 16, axis=1)


def test_baseline_regression():
    th, T = base_inputs()
    old, new = temodel.forward_theta(th, T), forward(th, T, Spec('baseline'))
    for name in ('sigma','S','kappa','kappa_L','kappa_bip','kappa_e','zT'):
        np.testing.assert_allclose(new[name], old[name], rtol=1e-13)


def test_independent_bands_nest_shared_model_and_ratio_stress():
    th, T = base_inputs(); spec = Spec('mobility')
    for ratio in (.1, 1., 10.):
        extended = np.column_stack([th[:,:10],np.full(len(th),np.log10(ratio)),th[:,4],th[:,8],th[:,10]])
        old = temodel.forward_theta(th,T,minority_mobility_ratio=ratio)
        new = forward(extended,T,spec)
        for name in ('sigma','S','kappa','kappa_bip','kappa_e'):
            np.testing.assert_allclose(new[name],old[name],rtol=2e-12,atol=1e-15)


def test_independent_temperature_and_scattering_act_on_minority():
    th=np.array([[18.,-.3,-.3,2.,-1.5,-1.,0.,1.,-.5,.2,0.,-1.5,-.5,1.]])
    T=np.array([[300.,500.,750.]])
    a=forward(th,T,Spec('mobility'))
    th[:,11]=.5
    b=forward(th,T,Spec('mobility'))
    np.testing.assert_allclose(a['sigma'][:,0],b['sigma'][:,0])
    assert b['sigma'][0,-1] > a['sigma'][0,-1]
    th[:,12]=1.
    c=forward(th,T,Spec('mobility'))
    assert not np.allclose(c['S'],b['S'])
    for name in ('p','n','eta_p','eta_n'):
        np.testing.assert_array_equal(a[name],c[name])


def test_positive_spline_can_rise_fall_and_turn_over():
    nodes=np.array([[0,1,0,-1,0,1],[1,.8,.6,.4,.2,0],[0,.2,.4,.6,.8,1]])
    T=np.broadcast_to(KNOTS,(3,6))
    np.testing.assert_allclose(positive_lattice(nodes,T),10.**nodes)
    grid=np.broadcast_to(np.linspace(285,1250,200),(3,200))
    y=positive_lattice(nodes,grid)
    assert np.all(y>0)
    assert np.all(np.diff(y[1])<0) and np.all(np.diff(y[2])>0)
    assert np.any(np.diff(y[0])<0) and np.any(np.diff(y[0])>0)


@pytest.mark.parametrize('name',VARIANTS)
def test_prior_heat_conservation_sign_and_output_dimensions(name):
    spec=Spec(name);th,lo,hi=sample_box(20,np.random.default_rng(7),spec)
    assert in_box(th,spec).all()
    T=np.linspace(lo,hi,16,axis=1);o=forward(th,T,spec)
    np.testing.assert_allclose(o['kappa'],o['kappa_L']+o['kappa_e']+o['kappa_bip']+o['kappa_extra'])
    np.testing.assert_allclose(o['zT'],o['S']**2*o['sigma']*T/o['kappa'])
    flipped=th.copy();flipped[:,-1]=1-flipped[:,-1]
    f=forward(flipped,T,spec)
    np.testing.assert_allclose(f['S'],-o['S'])
    np.testing.assert_allclose(f['kappa'],o['kappa'])
    model=Posterior(spec.dim)
    mu,A,dg,sign=model(torch.zeros(2,50))
    assert mu.shape==(2,spec.dim) and A.shape==(2,spec.dim,spec.dim)
    assert torch.isfinite(model.loss(torch.zeros(2,50),torch.zeros(2,spec.dim),torch.zeros(2)))


def test_extra_channel_separate_and_zero_nesting():
    th,T=base_inputs(); spec=Spec('extra')
    v=np.column_stack([th[:,:10],np.zeros(len(th)),th[:,10]])
    a=forward(v,T,spec);original=temodel.forward_theta(th,T)
    np.testing.assert_allclose(a['kappa'],original['kappa'])
    v[:,-2]=.02;b=forward(v,T,spec)
    np.testing.assert_allclose(b['kappa_L'],a['kappa_L'])
    np.testing.assert_allclose(b['kappa_bip'],a['kappa_bip'])
    np.testing.assert_allclose(b['kappa']-a['kappa'],.02*(T/300)**3,rtol=1e-10)


def test_checkpoint_prior_support_is_not_silently_changed():
    old=Spec('mobility_spline',.01,30.)
    metadata=old.metadata()
    metadata.pop('spline_limits')  # Initial checkpoint format.
    restored=Spec.from_metadata(metadata)
    np.testing.assert_allclose(restored.bounds(),old.bounds(),equal_nan=True)
    assert restored.lattice_max < Spec('mobility_spline').lattice_max
