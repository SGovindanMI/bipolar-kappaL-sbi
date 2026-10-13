"""Selection-controlled comparisons against v5 and across all completed models."""
import argparse
from pathlib import Path
import json
import numpy as np
from .relaxed_analysis import estimates, save_json
from .analysis_stats import cluster_interval


def main():
    ap=argparse.ArgumentParser();ap.add_argument('run',type=Path);ap.add_argument('--bootstrap',type=int,default=2000);a=ap.parse_args()
    root=Path(__file__).resolve().parents[1];manifest=json.loads((a.run/'manifest.json').read_text())
    source=np.load(root/'data/real_analysis_set.npz',allow_pickle=True);doi=source['doi'].astype(str)
    names=['baseline']+manifest['variants'];paths=[root/'data/inference_v5.npz']+[a.run/n/'real_inference.npz' for n in names[1:]]
    if not all(p.exists() for p in paths):
        raise RuntimeError('All requested real-inference files must exist before an all-model comparison')
    rows={};all_common=np.ones(len(doi),bool)
    for name,path in zip(names,paths):
        with np.load(path) as p:
            _,e=estimates(source,p);mask=p['admit']&np.isfinite(e).all(1)
            rows[name]=(e,mask);all_common &= mask
    output={'all_model_common_n':int(all_common.sum()),'all_model_common_papers':len(np.unique(doi[all_common])),
            'selection':'Admission and all five finite estimates in every model; fifth duplicates fourth for models without extra heat',
            'models':{}}
    base,base_mask=rows['baseline']
    for name,(e,native) in rows.items():
        d={}
        for label,m in [('native',native),('baseline_common',native&base_mask),('all_model_common',all_common)]:
            d[label]={'n':int(m.sum()),'papers':len(np.unique(doi[m])),
                      'C_B':cluster_interval(e[:,2]-e[:,1],doi,m,a.bootstrap),
                      'baseline_C_B_same_mask':cluster_interval(base[:,2]-base[:,1],doi,m&base_mask,a.bootstrap),
                      'paired_change_C_B':cluster_interval((e[:,2]-e[:,1])-(base[:,2]-base[:,1]),doi,m&base_mask,a.bootstrap),
                      'C_A':cluster_interval(e[:,2]-e[:,0],doi,m,a.bootstrap),
                      'Cprime_all_A':cluster_interval(e[:,4]-e[:,0],doi,m,a.bootstrap)}
        output['models'][name]=d
    save_json(a.run/'comparison.json',output)
    print(json.dumps(output,indent=2))


if __name__=='__main__':main()
