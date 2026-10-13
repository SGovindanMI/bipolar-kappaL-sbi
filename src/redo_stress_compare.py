"""Compare every estimator on identical shared known-truth populations."""
import argparse
import json
from pathlib import Path
import numpy as np
from .relaxed_analysis import estimates, save_json
from .analysis_stats import window_slope
from .relaxed import sha256


def main():
    ap=argparse.ArgumentParser();ap.add_argument('run',type=Path);a=ap.parse_args()
    root=Path(__file__).resolve().parents[1]
    names=['baseline']+json.loads((a.run/'manifest.json').read_text())['variants']
    sets={'narrow_upturn':('experiments/fixtures/upturn_narrow_v5.npz','experiments/fixtures/upturn_narrow_v5_inference.npz'),
          'narrow_control':('experiments/fixtures/control_narrow_v5.npz','experiments/fixtures/control_narrow_v5_inference.npz'),
          'mobility_low':('data/stress_mobility_low.npz','data/stress_mobility_low_inference.npz'),
          'mobility_high':('data/stress_mobility_high.npz','data/stress_mobility_high_inference.npz'),
          'wide_upturn':('data/stress_lattice_upturn.npz','data/stress_lattice_upturn_inference.npz')}
    output={}
    for case,(src,base) in sets.items():
        source=np.load(root/src);truth=source['truth'];n=len(truth)
        rows={};common_scored=np.ones(n,bool);common_slope=np.ones(n,bool)
        for name in names:
            path=root/base if name=='baseline' else a.run/name/(case+'_inference.npz')
            with np.load(path) as p:
                _,e=estimates(source,p);t=window_slope(p['Tgrid'],truth[:,0])
                m=p['admit']&np.isfinite(e[:,:4]).all(1)&np.isfinite(t)
                common_scored &= p['scored'];common_slope &= m
                rows[name]={'q':p['quantiles'].copy(),'slope_error':e[:,2]-t,'native_mask':m,'sha256':sha256(path)}
        result={'source_sha256':sha256(root/src),'n':n,'common_scored_n':int(common_scored.sum()),
                'common_slope_n':int(common_slope.sum()),'slope_selection':'admitted, spans 400-750 K, original four finite estimates in every model',
                'models':{}}
        for name,row in rows.items():
            q=row['q'];d={'inference_sha256':row['sha256'],'channels':{}}
            for label,j,k in [('lattice',0,3),('bipolar',1,4),('total',3,2)]:
                y=truth[common_scored,j];v=q[common_scored,:,k]
                d['channels'][label]={'coverage':float(((y>=v[:,0])&(y<=v[:,2])).mean()),
                    'median_absolute_error':float(np.median(abs(v[:,1]-y))),
                    'median_interval_width':float(np.median(v[:,2]-v[:,0]))}
            for label,m in [('native',row['native_mask']),('common',common_slope)]:
                err=row['slope_error'][m]
                d[label+'_slope']={'n':int(m.sum()),'median_error':float(np.median(err)) if len(err) else None,
                    'median_absolute_error':float(np.median(abs(err))) if len(err) else None}
            result['models'][name]=d
        output[case]=result
    save_json(a.run/'stress_comparison.json',output)
    print(a.run/'stress_comparison.json')


if __name__=='__main__':main()
