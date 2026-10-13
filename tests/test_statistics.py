import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from src.analysis_stats import finite_probability,cluster_interval,window_slope

def test_missing_draws_not_negative_votes():
    np.testing.assert_allclose(finite_probability([[.1,.2,np.nan],[.8,np.nan,np.nan],[np.nan]*3]),[1.,0.,np.nan],equal_nan=True)

def test_bootstrap_subset_excludes_other_papers():
    a=cluster_interval([1.,2.,3.,100.],['a','a','b','c'],[True,True,True,False],200,17)
    b=cluster_interval([1.,2.,3.],['a','a','b'],n_boot=200,seed=17)
    assert a==b

def test_powerlaw_slope_and_no_clipping_of_negative_values():
    T=np.array([[400.,750.]]*3);y=np.array([T[0]**-.7,[-1.,2.],[1.,0.]])
    np.testing.assert_allclose(window_slope(T,y),[-.7,np.nan,np.nan],equal_nan=True)

