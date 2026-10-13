import json
from types import SimpleNamespace
import numpy as np
import pandas as pd
import pytest
from src.build_corpus import validate_identity,validate_selected,build_cache
from combined.audit_starrydata import points,compare

def test_cross_paper_integer_collision_rejected():
    with pytest.raises(ValueError,match='Ambiguous'):
        validate_identity(pd.DataFrame({'sample_id':[1,1],'SID':[10,20]}))

def test_repeated_curves_same_paper_allowed():
    validate_identity(pd.DataFrame({'sample_id':[1,1],'SID':[10,10]}))

def test_wrong_attribution_and_extrapolation_rejected():
    d={k:(np.array([300.,600.]),np.array([1.,2.])) for k in ['S','sig','kap']}
    with pytest.raises(ValueError,match='DOI'):validate_selected(d,'10/a','10/b',300,600)
    with pytest.raises(ValueError,match='coverage'):validate_selected(d,'10/a','10/a',300,700)

def test_duplicate_points_distinguished_from_multivalued_temperature():
    r=SimpleNamespace(x=json.dumps([1,2,3,4,4,5]),y=json.dumps([1,2,3,4,4,5]))
    p,err=points(r);assert err is None and len(p[0])==5
    r.y=json.dumps([1,2,3,4,9,5]);assert points(r)[1]=='conflicting_duplicate_temperature'

def test_near_zero_endpoint_rounding_is_not_a_large_physical_error():
    error,threshold=compare('Electrical conductivity',np.array([2e-6,100.]),np.array([2e-12,100.]))
    assert error<threshold
    error,threshold=compare('Electrical conductivity',np.array([2.,100.]),np.array([2e-12,100.]))
    assert error>threshold

def test_unconverted_units_rejected(tmp_path):
    row={'prop_x':'Temperature','unit_x':'K','prop_y':'Thermal conductivity','unit_y':'W/cm/K',
         'sample_id':1,'SID':1,'DOI':'10/a','composition':'X','x':json.dumps([300,400,500,600,700]),'y':json.dumps([1,2,3,4,5])}
    path=tmp_path/'curves.csv';pd.DataFrame([row]).to_csv(path,index=False)
    with pytest.raises(ValueError,match='unit'):build_cache(path,tmp_path/'cache.pkl')
