"""Read-only claim-specific audit of archived arrays; no training or inference."""
import json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.relaxed_analysis import estimates
from src.analysis_stats import cluster_interval, window_slope, interpolate

N = json.loads((ROOT/'combined/combined_numbers.json').read_text())
RUN = ROOT/'runs/v6_main'
checks = []
def check(name, actual, expected, atol=1e-10):
    assert np.allclose(actual, expected, atol=atol, rtol=1e-9, equal_nan=True), (name, actual, expected)
    checks.append(name)

source = np.load(ROOT/'data/real_analysis_set.npz', allow_pickle=True)
papers = source['doi'].astype(str)
rows = {}
for model in N['models']:
    path = ROOT/'data/inference_v5.npz' if model == 'baseline' else RUN/model/'real_inference.npz'
    with np.load(path) as p:
        curves, e = estimates(source, p)
        admit, scored = p['admit'], p['scored']
        mask = admit & np.isfinite(e).all(1)
        rows[model] = (e, mask)
        q=p['quantiles']; T=p['Tgrid']; x=source['x'].astype(float)
        frac=interpolate(T,q[:,1,4],750)/interpolate(T,np.exp(x[:,32:48]),750)
        ab=abs(x[:,16:32]); peak=ab.argmax(1)
        roll=np.where((peak>0)&(peak<15),(ab.max(1)-ab[:,-1])/np.maximum(ab.max(1),1e-12),-1.)
        strata={'below_2':frac<.02,'2_to_10':(frac>=.02)&(frac<.1),'10_to_100':(frac>=.1)&(frac<=1),'above_100':frac>1}
        rollover={'none':roll<0,'below_5':(roll>=0)&(roll<.05),'5_to_15':(roll>=.05)&(roll<.15),'above_15':roll>=.15}
        families={k:source['family'].astype(str)==k for k in N['families'][model]}
        for category, groups in [('strata',strata),('rollover',rollover),('families',families)]:
            for label,g in groups.items():
                m=mask&g; record=N[category][model][label]
                check(model+' '+category+' '+label+' counts',[m.sum(),len(np.unique(papers[m]))],[record['n'],record['papers']])
                if m.any():check(model+' '+category+' '+label+' median',np.median(e[m,2]-e[m,1]),record['CB'][0],atol=2e-6)
        for threshold,record in N['thresholds'][model].items():
            m=scored&(p['explained']>=float(threshold))&np.isfinite(e).all(1)
            check(model+' threshold '+threshold+' count',m.sum(),record['n'])
            check(model+' threshold '+threshold+' median',np.median(e[m,2]-e[m,1]),record['CB'][0],atol=2e-6)
        check(model+' scored/admitted/native', [scored.sum(), admit.sum(), mask.sum()],
              [N['selection'][model]['scored'], N['selection'][model]['admitted'], N['corpus'][model]['native']['n']])
        negative = np.min(curves[0], axis=1) < 0
        for label, m in [('all', np.ones(len(admit), bool)), ('admitted', admit), ('excluded', scored & ~admit), ('unscored', ~scored)]:
            record = N['negative_A'][model][label]
            check(model+' negative A '+label, [(negative&m).sum(), m.sum()], [record['n'], record['denominator']])
        print('Checked corpus arrays:',model,flush=True)

common = np.logical_and.reduce([v[1] for v in rows.values()])
check('Common curves and papers', [common.sum(), len(np.unique(papers[common]))], [N['all_model_common']['n'],N['all_model_common']['papers']])
base = rows['baseline'][0]
for model, (e, native) in rows.items():
    for pop, mask in [('native', native), ('baseline_common',native&rows['baseline'][1]), ('all_model_common',common)]:
        record = N['corpus'][model][pop]
        check(model+' '+pop+' C-B interval', cluster_interval(e[:,2]-e[:,1],papers,mask), record['CB'])
        check(model+' '+pop+' C-A interval', cluster_interval(e[:,2]-e[:,0],papers,mask), record['CA'])
    if model != 'baseline':
        check(model+' common paired change',cluster_interval(e[:,2]-e[:,1]-base[:,2]+base[:,1],papers,common),N['corpus'][model]['all_model_common']['paired_change_CB'])
    print('Checked paper bootstrap:',model,flush=True)

for label,i,j in [('BA',1,0),('CB',2,1),('CA',2,0),('CpB',3,1),('CpA',3,0)]:
    check('Reference shift '+label,cluster_interval(base[:,i]-base[:,j],papers,rows['baseline'][1]),N['v5']['shifts'][label],atol=2e-6)

sets = {'narrow_upturn':('experiments/fixtures/upturn_narrow_v5.npz','experiments/fixtures/upturn_narrow_v5_inference.npz'),
        'narrow_control':('experiments/fixtures/control_narrow_v5.npz','experiments/fixtures/control_narrow_v5_inference.npz'),
        'mobility_low':('data/stress_mobility_low.npz','data/stress_mobility_low_inference.npz'),
        'mobility_high':('data/stress_mobility_high.npz','data/stress_mobility_high_inference.npz'),
        'wide_upturn':('data/stress_lattice_upturn.npz','data/stress_lattice_upturn_inference.npz')}
for case,(src,bp) in sets.items():
    z = np.load(ROOT/src); truth=z['truth']; rr={}
    for model in N['models']:
        with np.load(ROOT/bp if model=='baseline' else RUN/model/(case+'_inference.npz')) as p:
            _,e=estimates(z,p); true_slope=window_slope(p['Tgrid'],truth[:,0])
            rr[model]=(p['quantiles'],p['scored'],p['admit']&np.isfinite(e[:,:4]).all(1)&np.isfinite(true_slope),e[:,2]-true_slope)
    scored=np.logical_and.reduce([v[1] for v in rr.values()]); slope=np.logical_and.reduce([v[2] for v in rr.values()])
    expected=N['stress_common'][case]
    check(case+' common denominators',[scored.sum(),slope.sum()],[expected['common_scored_n'],expected['common_slope_n']])
    for model,(q,_,_,err) in rr.items():
        record=expected['models'][model]
        for label,j,k in [('lattice',0,3),('bipolar',1,4),('total',3,2)]:
            y=truth[scored,j]; v=q[scored,:,k]
            check(case+' '+model+' '+label+' coverage',((y>=v[:,0])&(y<=v[:,2])).mean(),record[label+'_coverage'])
        check(case+' '+model+' width',np.median(q[scored,2,3]-q[scored,0,3]),record['lattice_width'])
        check(case+' '+model+' slope error',[np.median(err[slope]),np.median(abs(err[slope]))],[record['common_slope']['median_error'],record['common_slope']['median_absolute_error']])
    print('Checked stress arrays:',case,flush=True)

for model in N['models'][1:]:
    z=np.load(RUN/model/'test.npz'); p=np.load(RUN/model/'test_inference.npz'); t=z['truth'];q=p['quantiles'];s=p['scored']
    record=N['same_model_test'][model]
    check(model+' same-model counts',[len(s),s.sum(),p['admit'].sum()],[record['n'],record['scored'],record['admitted']])
    for name,j,k in [('lattice',0,3),('bipolar',1,4)]:
        check(model+' same-model '+name,((t[s,j]>=q[s,0,k])&(t[s,j]<=q[s,2,k])).mean(),record[name+'_coverage'])
    p.close();z.close()

for record in N['transfer']:
    model,truthmodel=record['inference'],record['truth']
    with np.load(RUN/truthmodel/'narrow.npz') as z, np.load(RUN/'cross_model'/f'{model}__{truthmodel}.npz') as p:
        t=z['truth'];q=p['quantiles'];s=p['scored']
        check(model+' transfer '+truthmodel+' counts',[len(s),s.sum(),p['admit'].sum()],[record['n'],record['scored'],record['admitted']])
        for name,j,k in [('lattice',0,3),('bipolar',1,4),('total',3,2)]:
            check(model+' transfer '+truthmodel+' '+name,((t[s,j]>=q[s,0,k])&(t[s,j]<=q[s,2,k])).mean(),record[name+'_coverage'])

out={'status':'passed','checks':len(checks),'scope':checks,'not_checked':['raw Starrydata reconstruction and lost historical filter','independent experimental heat-channel truth','retraining seed robustness','all posterior joint or simultaneous calibration']}
(ROOT/'combined/SCIENTIFIC_AUDIT.json').write_text(json.dumps(out,indent=2))
print('PASS:',len(checks),'claim-specific numerical checks')
