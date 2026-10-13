"""Recompute the corrected paper's principal stratifications for each v6 fit."""
import argparse
import json
import warnings
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
from .relaxed_analysis import estimates, save_json
from .analysis_stats import cluster_interval, finite_probability, interpolate
from .relaxed import sha256


def main():
    ap=argparse.ArgumentParser();ap.add_argument('run',type=Path);ap.add_argument('--bootstrap',type=int,default=2000);ap.add_argument('--models',nargs='+');a=ap.parse_args()
    root=Path(__file__).resolve().parents[1]
    manifest=json.loads((a.run/'manifest.json').read_text())
    source=np.load(root/'data/real_analysis_set.npz',allow_pickle=True)
    doi=source['doi'].astype(str);family=source['family'].astype(str);x=source['x'].astype(float)
    for variant in (a.models or manifest['variants']):
        provenance={'inference_sha256':sha256(a.run/variant/'real_inference.npz'),
                    'source_sha256':sha256(root/'data/real_analysis_set.npz'),
                    'script_sha256':sha256(Path(__file__)),
                    'analysis_sha256':sha256(root/'src/relaxed_analysis.py'),'bootstrap_resamples':a.bootstrap}
        report=a.run/variant/'supplementary_analysis.json'
        if report.exists() and json.loads(report.read_text()).get('provenance')==provenance:
            print(variant,'verified cached supplement',flush=True);continue
        dest=a.run/variant;p=np.load(dest/'real_inference.npz');meta=json.loads(str(p['metadata']))
        curves,e=estimates(source,p);T=p['Tgrid'];q=p['quantiles'];ad=p['admit'];sc=p['scored']
        pair=ad&np.isfinite(e).all(1)
        fraction=interpolate(T,q[:,1,4],750)/interpolate(T,np.exp(x[:,32:48]),750)
        S=abs(x[:,16:32]);peak=S.argmax(1)
        rollover=np.where((peak>0)&(peak<15),(S.max(1)-S[:,-1])/np.maximum(S.max(1),1e-12),-1.)
        def group(mask):
            m=mask&np.isfinite(e).all(1)
            d=dict(n=int(m.sum()),papers=len(np.unique(doi[m])))
            for key,i,j in [('C_B',2,1),('C_A',2,0),('Cprime_bip_A',3,0),('Cprime_all_A',4,0)]:
                d[key]=cluster_interval(e[:,i]-e[:,j],doi,m,a.bootstrap)
            d['rho_bipolar_share_vs_C_B']=float(spearmanr(fraction[m],e[m,2]-e[m,1]).statistic) if m.sum()>2 else None
            return d
        result={'variant':variant,'provenance':provenance,'selection':'native all-five positive endpoints at 400 and 750 K',
                'strata':{label:group(pair&m) for label,m in [('below_2',fraction<.02),('2_to_10',(fraction>=.02)&(fraction<.1)),('10_to_100',(fraction>=.1)&(fraction<=1)),('above_100',fraction>1)]},
                'families':{f:group(pair&(family==f)) for f in np.unique(family) if (pair&(family==f)).sum()>=80},
                'rollover':{label:group(pair&m) for label,m in [('none',rollover<0),('below_5',(rollover>=0)&(rollover<.05)),('5_to_15',(rollover>=.05)&(rollover<.15)),('above_15',rollover>=.15)]},
                'screen_thresholds':{str(t):group(sc&(p['explained']>=t)) for t in [0,.3,.4,.5,.6,.7,.75,.8,.85,.9,.95]}}
        result['negative_conventional_remainder']={name:dict(n=int((m&(curves[0].min(1)<0)).sum()),denominator=int(m.sum())) for name,m in [('all',np.ones(len(ad),bool)),('admitted',ad),('excluded',sc&~ad),('unscored',~sc)]}
        result['effective_scattering']={}
        for name in ['r','r_min']:
            if name not in meta['spec']['names']:continue
            j=meta['spec']['names'].index(name);prob=finite_probability(p['theta'][:,:,j])
            result['effective_scattering'][name]={'P_r_below_half_gt_0p8':int((ad&(prob>.8)).sum()),
                'P_r_below_half_lt_0p2':int((ad&(prob<.2)).sum()),'ambiguous':int((ad&(prob>=.2)&(prob<=.8)).sum()),
                'denominator':int(ad.sum()),'interpretation':'Effective parameter classification, not independently identified microscopic scattering'}
        save_json(dest/'supplementary_analysis.json',result)
        print(variant,'supplement complete',flush=True)


if __name__=='__main__':
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',RuntimeWarning);main()
