"""Family comparisons on identical cases, with the unpublished project reference."""
import json,csv
from pathlib import Path
import numpy as np
from .relaxed_analysis import estimates,save_json
from .analysis_stats import cluster_interval
from .relaxed import sha256

ROOT=Path(__file__).resolve().parents[1];RUN=ROOT/'runs/v6_main';OUT=RUN/'publication'
NAMES=['baseline','mobility','extra','spline','mobility_extra','mobility_spline']
def main():
    OUT.mkdir(exist_ok=True)
    with np.load(ROOT/'data/real_analysis_set.npz',allow_pickle=True) as z:
        source={k:z[k] for k in z.files}
    family=source['family'].astype(str);doi=source['doi'].astype(str)
    rows={};common=np.ones(len(family),bool);paths={}
    for n in NAMES:
        path=ROOT/'data/inference_v5.npz' if n=='baseline' else RUN/n/'real_inference.npz'
        with np.load(path) as p:
            _,e=estimates(source,p);m=p['admit']&np.isfinite(e).all(1)
        rows[n]=(e,m);common &=m;paths[n]={'file':str(path.relative_to(ROOT)),'sha256':sha256(path)}
        print(n,int(m.sum()),flush=True)
    assert common.any()
    results={'reference_status':'Unpublished earlier implementation within the same project; internal identifier v5',
             'selection':'Admission and all five finite positive-endpoint 400–750 K estimates in every model',
             'bootstrap':{'resamples':2000,'seed':2024,'unit':'source paper','interval':'percentile 95%'},
             'all_common_n':int(common.sum()),'all_common_papers':len(np.unique(doi[common])),
             'family_assignment':'Inherited frozen real_analysis_set.npz labels, not newly audited; other is a heterogeneous residual group',
             'threshold':80,'families':{},'native_baseline':{},'provenance':paths}
    results['provenance']['source']={'sha256':sha256(ROOT/'data/real_analysis_set.npz')}
    results['provenance']['script']={'sha256':sha256(Path(__file__))}
    base=rows['baseline'][0];base_shift=base[:,2]-base[:,1];flat=[]
    for f in np.unique(family):
        m=common&(family==f);count=int(m.sum());entry={'n':count,'papers':len(np.unique(doi[m])),'reported':count>=80,'models':{}}
        if count>=80:
            for n in NAMES:
                e=rows[n][0];shift=e[:,2]-e[:,1]
                d={'C_B':cluster_interval(shift,doi,m),'paired_change_from_reference':cluster_interval(shift-base_shift,doi,m)}
                entry['models'][n]=d
                for quantity,v in d.items():flat.append({'family':f,'model':n,'curves':count,'papers':entry['papers'],'quantity':quantity,'median':v[0],'lower':v[1],'upper':v[2]})
        results['families'][f]=entry
        bm=rows['baseline'][1]&(family==f)
        if bm.sum()>=80:
            results['native_baseline'][f]={'n':int(bm.sum()),'papers':len(np.unique(doi[bm])),
                'C_B':cluster_interval(base_shift,doi,bm),'C_A':cluster_interval(base[:,2]-base[:,0],doi,bm),'Cprime_all_A':cluster_interval(base[:,4]-base[:,0],doi,bm)}
    np.savez_compressed(OUT/'family_comparison_masks.npz',common=common,family=family,paper=doi,**{n+'_selected':rows[n][1] for n in NAMES},**{n+'_C_B':rows[n][0][:,2]-rows[n][0][:,1] for n in NAMES})
    save_json(OUT/'family_comparison.json',results)
    with (OUT/'family_source_data.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)
    print(json.dumps({f:{k:v for k,v in d.items() if k!='models'} for f,d in results['families'].items()},indent=2))
if __name__=='__main__':main()
