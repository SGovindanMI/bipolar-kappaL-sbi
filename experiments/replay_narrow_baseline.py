"""Replay the externally supplied narrow-gap baseline with the corrected checkpoint."""
from pathlib import Path
import json,numpy as np
from src.inference import infer
from src.relaxed import sha256

root=Path(__file__).resolve().parents[1];out=root/'runs/v6_main/baseline_replay';out.mkdir(exist_ok=True)
rows=[]
for name,seed in [('upturn',3007),('control',3008)]:
    source=root/'experiments/fixtures'/f'{name}_narrow_v5.npz'
    archived=source.with_name(source.stem+'_inference.npz');target=out/(name+'.npz')
    infer(source,target,seed=seed,checkpoint=root/'data/posterior_v5.pt')
    a=np.load(archived);b=np.load(target);fields={}
    for key in ['theta','quantiles','nok','scored','admit','explained','slope_draws']:
        av,bv=a[key],b[key]
        fields[key]={'exact_equal':bool(np.array_equal(av,bv,equal_nan=True)),
                     'close_rtol_1e4_atol_1e6':bool(np.allclose(av,bv,rtol=1e-4,atol=1e-6,equal_nan=True))}
    rows.append({'case':name,'seed':seed,'source_sha256':sha256(source),'checkpoint_sha256':sha256(root/'data/posterior_v5.pt'),
                 'archived_sha256':sha256(archived),'replay_sha256':sha256(target),'fields':fields,
                 'archived_scored':int(a['scored'].sum()),'replay_scored':int(b['scored'].sum()),
                 'archived_admitted':int(a['admit'].sum()),'replay_admitted':int(b['admit'].sum())})
(out/'verification.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
