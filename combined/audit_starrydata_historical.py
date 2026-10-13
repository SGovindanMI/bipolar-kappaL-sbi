"""Diagnose legacy single-ID joins in a separate, non-original archival snapshot."""
import json,hashlib
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'work/starrydata_audit';OUT=ROOT/'combined/starrydata_audit'
h=pd.read_csv(P/'historical_20260715_curves.csv.gz',keep_default_na=False)
with np.load(ROOT/'data/real_analysis_set.npz',allow_pickle=True) as z:f={k:z[k] for k in z.files}
props={'Seebeck coefficient':'S','Electrical conductivity':'sig','Electrical resistivity':'rho','Thermal conductivity':'kap','ZT':'zt','Lattice thermal conductivity':'kL'}
D=defaultdict(dict);M={}
for r in h.itertuples():
    if r.prop_x not in ['Temperature','T'] or r.unit_x!='K' or r.prop_y not in props:continue
    try:t=np.array(json.loads(r.x),float);y=np.array(json.loads(r.y),float)
    except (ValueError,TypeError):continue
    if len(t)!=len(y) or len(t)<5:continue
    k=props[r.prop_y]
    if k in D[r.sample_id]:continue
    o=np.argsort(t);D[r.sample_id][k]=(t[o],y[o],r.DOI,r.SID,r.figure_id);M[r.sample_id]=r.DOI
out=[]
for i,s in enumerate(f['sid']):
    d=D[s];ks=['S','sig' if 'sig' in d else 'rho','kap']
    rd={'frozen_row':i,'sample_id':int(s),'recorded_doi':str(f['doi'][i]),'historical_last_metadata_doi':M.get(s),'source_dois':json.dumps({k:d[k][2] for k in ks if k in d})}
    rd['mixed_papers']=len(set(d[k][3] for k in ks if k in d))>1
    if all(k in d for k in ks):
        T=np.linspace(f['Tlo'][i],f['Thi'][i],16);v=[np.interp(T,*d[k][:2]) for k in ks]
        if ks[1]=='rho':v[1]=1/v[1]
        with np.errstate(all='ignore'):xx=np.r_[np.log10(v[1]),v[0]*1e6,np.log(v[2])]
        rd['max_feature_difference']=float(np.max(abs(xx-f['x'][i,:48])))
    out.append(rd)
r=pd.DataFrame(out);r.to_csv(OUT/'historical_join_audit.csv',index=False)
m=json.loads((P/'data-20260715_manifest.json').read_text(encoding='utf-8'))
digest=hashlib.sha256((P/'historical_20260715_curves.csv.gz').read_bytes()).hexdigest()
assert digest==m['projects']['ThermoelectricMaterials']['curves']['sha256']
summary={'release_tag':'data-20260715','manifest_db_snapshot':m['db_snapshot'],'sha256':digest,'rows':len(h),'caveat':'This is not established as the original snapshot; counts differ from legacy documentation.',
 'sample_ids_crossing_papers':int((h.groupby('sample_id').SID.nunique()>1).sum()),'legacy_join_mixed_transport_papers':int(r.mixed_papers.sum()),
 'legacy_join_max_feature_difference_le_0_001':int((r.max_feature_difference<=.001).sum()),
 'last_metadata_doi_matches_recorded':int((r.recorded_doi.str.lower()==r.historical_last_metadata_doi.str.lower()).sum())}
(OUT/'historical_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
