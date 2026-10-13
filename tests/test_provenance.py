"""A changed raw export must never silently reuse a stale parsed cache."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
import numpy as np
from src.build_corpus import build_cache

def test_cache_is_keyed_by_source_content(tmp_path):
    source=tmp_path/'curves.csv';cache=tmp_path/'curves.pkl'
    row={'prop_x':'Temperature','unit_x':'K','unit_y':'W*m^(-1)*K^(-1)','prop_y':'Thermal conductivity','sample_id':1,'x':json.dumps([300,400,500,600,700]),'y':json.dumps([1,2,3,4,5]),'DOI':'10.1000/example','composition':'test'}
    pd.DataFrame([row]).to_csv(source,index=False)
    a,_=build_cache(source,cache)
    row['y']=json.dumps([2,3,4,5,6]);pd.DataFrame([row]).to_csv(source,index=False)
    b,_=build_cache(source,cache)
    np.testing.assert_allclose(b[1]['kap'][1]-a[1]['kap'][1],1.)
