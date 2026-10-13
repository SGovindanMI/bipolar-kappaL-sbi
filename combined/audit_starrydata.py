"""Exhaustive, non-mutating audit against a locally pinned official export.

Run: python combined/audit_starrydata.py --export work/starrydata_audit
Does not replace the frozen corpus or infer parameters. Only exact canonical
property labels and units are used for numerical checks. Inventory retains all labels.
"""
import argparse, hashlib, json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
UNITS = {'Seebeck coefficient':'V*K^(-1)', 'Electrical conductivity':'ohm^(-1)*m^(-1)',
         'Electrical resistivity':'ohm*m', 'Thermal conductivity':'W*m^(-1)*K^(-1)',
         'Power factor':'W*m^(-1)*K^(-2)', 'ZT':'-'}

def doi(s):
    return str(s).strip().lower().removeprefix('https://doi.org/').removeprefix('http://dx.doi.org/')

def points(r):
    """Reject ambiguous duplicate temperatures; never extrapolate in checks."""
    try:
        t, y = np.asarray(json.loads(r.x),float), np.asarray(json.loads(r.y),float)
        if t.ndim != 1 or y.shape != t.shape or len(t)<5: return None, 'short_or_shape'
        if not (np.isfinite(t).all() and np.isfinite(y).all()): return None, 'nonfinite'
        ix=np.argsort(t);t,y=t[ix],y[ix]
        # Repeated identical digitized points add no information and are safe to collapse.
        xy=np.unique(np.column_stack([t,y]),axis=0);t,y=xy[:,0],xy[:,1]
        if np.any(np.diff(t)<=0): return None, 'conflicting_duplicate_temperature'
        return (t,y), None
    except (ValueError,TypeError): return None, 'parse'

def compare(prop, pred, target):
    if prop=='Seebeck coefficient': return float(np.max(np.abs(pred-target))), 1.0
    if np.any(target<=0) or np.any(pred<=0): return float('inf'), .01
    # A 1e-3 S/m absolute allowance handles endpoint rounding near zero sigma.
    scale=np.maximum(target,.1) if prop=='Electrical conductivity' else target
    return float(np.max(np.abs(pred-target)/scale)), .01

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--export',type=Path,required=True)
    ap.add_argument('--out',type=Path,default=ROOT/'work/current_source_audit');a=ap.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((a.export/'manifest.json').read_text(encoding='utf-8'))
    hashes={};tables={}
    for kind, spec in manifest['projects']['ThermoelectricMaterials'].items():
        if kind not in ['curves','samples','papers']:continue
        f=a.export/spec['filename'];h=hashlib.sha256(f.read_bytes()).hexdigest()
        assert h==spec['sha256'],(kind,'checksum')
        tables[kind]=pd.read_csv(f,keep_default_na=False)
        assert len(tables[kind])==spec['rows'],(kind,'row count')
        hashes[f.name]=h
    c=tables['curves'];s=tables['samples'];f=np.load(ROOT/'data/real_analysis_set.npz',allow_pickle=True)
    x=f['x'].astype(float);ids=f['sid'].astype(int);ds=list(map(doi,f['doi']));keys=list(zip(ds,ids));keyset=set(keys)
    c['doi_norm']=c.DOI.map(doi);s['doi_norm']=s.DOI.map(doi)
    c['in_corpus']=[k in keyset for k in zip(c.doi_norm,c.sample_id)]
    sc=pd.read_csv(ROOT/'data/analysis_set_sids.csv')
    assert np.array_equal(sc.sample_id.to_numpy(),ids)
    assert list(map(doi,sc.doi))==ds
    assert np.isfinite(x).all()
    assert c.groupby(['doi_norm','sample_id']).SID.nunique().max()==1
    export_keys=set(zip(c.doi_norm,c.sample_id))
    groups=defaultdict(lambda:defaultdict(list));reject=Counter();reasons=defaultdict(lambda:defaultdict(set))
    for r in c[c.in_corpus & c.prop_x.isin(['Temperature','T']) & (c.unit_x=='K')].itertuples():
        if r.prop_y in UNITS and r.unit_y==UNITS[r.prop_y]:
            p,err=points(r)
            if err:
                reject[err]+=1;reasons[(r.doi_norm,int(r.sample_id))][r.prop_y].add(err)
            else:groups[(r.doi_norm,int(r.sample_id))][r.prop_y].append((p,int(r.Index),int(r.SID),int(r.figure_id)))
    rows=[];anc=[]
    for i,key in enumerate(keys):
        g=groups[key];T=np.linspace(float(f['Tlo'][i]),float(f['Thi'][i]),16)
        targets={'Seebeck coefficient':x[i,16:32], 'Electrical conductivity':10**x[i,:16], 'Thermal conductivity':np.exp(x[i,32:48])}
        rr={'frozen_row':i,'doi':key[0],'sample_id':key[1],'family':str(f['family'][i])}
        statuses=[];issues=set()
        if key not in export_keys:issues.add('paper_sample_identity_mismatch')
        for prop,tar in targets.items():
            used=prop if prop!='Electrical conductivity' or g[prop] else 'Electrical resistivity'
            cand=g[used];matches=[];covers=[];errs=[]
            for (t,y),j,sid,fig in cand:
                covered=t[0]<=T[0]+1e-4 and t[-1]>=T[-1]-1e-4
                v=np.interp(T,t,y)
                if used=='Electrical resistivity':v=np.divide(1.,v,out=np.full_like(v,np.nan),where=v!=0)
                if prop=='Seebeck coefficient':v=v*1e6
                er,thr=compare(prop,v,tar);errs.append(er);covers.append(covered);matches.append(covered and np.isfinite(er) and er<=thr)
            ok=any(matches);statuses.append(ok)
            if not ok and key in export_keys:
                issues.update(reasons[key][used])
                if prop=='Electrical conductivity':
                    issues.update(reasons[key]['Electrical conductivity'])
                    issues.update(reasons[key]['Electrical resistivity'])
                if not cand:issues.add('no_usable_'+used)
                elif not any(covers):issues.add('insufficient_temperature_coverage')
                else:issues.add('numerical_mismatch_of_usable_candidates')
            short={'Seebeck coefficient':'S','Electrical conductivity':'sigma','Thermal conductivity':'kappa'}[prop]
            rr.update({short+'_candidates':len(cand),short+'_first_max_error':errs[0] if errs else None,
                       short+'_best_max_error':min((e for e,cv in zip(errs,covers) if cv),default=None),
                       short+'_matching_candidates':sum(matches),short+'_covered_candidates':sum(covers),
                       short+'_first_matches':bool(matches and matches[0])})
        rr['verified_within_tolerance']=all(statuses);rr['first_curves_match']=all(rr[z+'_first_matches'] for z in ['S','sigma','kappa']);rr['review_reasons']=';'.join(sorted(issues));rows.append(rr)
        for prop in ['Power factor','ZT']:
            expected=(x[i,16:32]*1e-6)**2*10**x[i,:16]
            if prop=='ZT':expected=expected*T/np.exp(x[i,32:48])
            for (t,y),j,sid,fig in g[prop]:
                mask=(T>=t[0])&(T<=t[-1])&(expected>1e-20)
                if mask.sum()<5:continue
                v=np.interp(T[mask],t,y);e=expected[mask]
                # Symmetric relative difference avoids division by a near-zero reported value.
                rel=2*np.abs(v-e)/(np.abs(v)+np.abs(e))
                anc.append({'frozen_row':i,'doi':key[0],'sample_id':key[1],'SID':sid,'export_row':j,'figure_id':fig,'property':prop,'points_compared':int(mask.sum()),'median_symmetric_relative_difference':float(np.median(rel)),'max_symmetric_relative_difference':float(rel.max())})
    r=pd.DataFrame(rows);r.to_csv(a.out/'per_sample_audit.csv',index=False)
    ac=pd.DataFrame(anc);ac.to_csv(a.out/'derived_property_consistency.csv',index=False)
    common=set(pd.read_csv(ROOT/'combined/component_source_data.csv').frozen_row.unique())
    verified=set(r.loc[r.verified_within_tolerance,'frozen_row']);admit=set(np.flatnonzero(np.load(ROOT/'data/inference_v5.npz')['admit']))
    population={'frozen':set(range(len(ids))),'reference_admitted':admit,'six_model_common':common,'verified_inputs':verified}
    keyrow={k:i for i,k in enumerate(keys)}
    c['frozen_row']=[keyrow.get(k,-1) for k in zip(c.doi_norm,c.sample_id)]
    inventory=[]
    for (prop,unit),g in c.groupby(['prop_y','unit_y'],dropna=False):
        d={'property':prop,'unit':unit,'export_curves':len(g),'export_samples':len(g[['SID','sample_id']].drop_duplicates())}
        for label,pop in population.items():
            d[label+'_samples']=len(set(g.frozen_row)&pop)
            d[label+'_temperature_K_samples']=len(set(g.loc[g.prop_x.isin(['Temperature','T'])&(g.unit_x=='K'),'frozen_row'])&pop)
        inventory.append(d)
    inv=pd.DataFrame(inventory).sort_values('export_curves',ascending=False);inv.to_csv(a.out/'property_inventory.csv',index=False)
    columns=['SID','DOI','sample_id','figure_id','prop_x','prop_y','unit_x','unit_y','frozen_row','created_at','updated_at']
    c.loc[c.in_corpus,columns].to_csv(a.out/'matched_curve_manifest.csv',index=False)
    metadata=Counter();matchedmeta=[]
    for row in s.itertuples():
        k=(row.doi_norm,int(row.sample_id))
        if k not in keyset:continue
        try:info=json.loads(row.sample_info)
        except (ValueError,TypeError):continue
        fields={name:val for name,val in info.items() if val and (not isinstance(val,dict) or any(str(v).strip() for v in val.values() if v is not None))}
        for name in fields:metadata[name]+=1
        matchedmeta.append({'frozen_row':keyrow[k],'SID':int(row.SID),'sample_id':int(row.sample_id),'doi':row.doi_norm,'sample_name':row.sample_name,'composition':row.composition,'fields':fields})
    (a.out/'matched_sample_metadata.json').write_text(json.dumps(matchedmeta,indent=2,ensure_ascii=False),encoding='utf-8')
    summary={'db_snapshot':manifest['db_snapshot'],'source_hashes':hashes,'corpus_sha256':hashlib.sha256((ROOT/'data/real_analysis_set.npz').read_bytes()).hexdigest(),
     'export_counts':{k:len(v) for k,v in tables.items()},'frozen_samples':len(ids),'frozen_papers':len(set(ds)),
     'duplicate_frozen_keys':len(keys)-len(keyset),'duplicate_feature_rows':len(x)-len(np.unique(x,axis=0)),
     'sample_ids_crossing_papers_in_current_export':int((c.groupby('sample_id').SID.nunique()>1).sum()),
     'frozen_keys_missing_current_export':len(keyset-set(zip(c.doi_norm,c.sample_id))),
     'thresholds':{'sigma_kappa_max_relative':.01,'sigma_absolute_floor_S_per_m':.001,'S_max_absolute_uV_per_K':1.,'endpoint_rounding_K':1e-4},
     'rejected_canonical_rows':dict(reject),'verified_inputs':int(r.verified_within_tolerance.sum()),'first_curves_match':int(r.first_curves_match.sum()),
     'population':{name:{'n':len(p),'verified':len(p&verified),'unverified':len(p-verified)} for name,p in population.items()},
     'metadata_field_nonempty_sample_counts':dict(metadata),'derived_consistency':{}}
    for prop in ['Power factor','ZT']:
        z=ac[ac.property==prop];best=z.groupby('frozen_row').median_symmetric_relative_difference.min()
        summary['derived_consistency'][prop]={'curves':len(z),'samples':len(best),'best_curve_median_difference_median':float(best.median()),'all_candidates_median_difference_gt_20pct_samples':int((best>.2).sum()),'note':'20% is a descriptive flag, not an exclusion or error diagnosis; best candidate minimizes difference.'}
    (a.out/'audit_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
