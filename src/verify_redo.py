"""Check saved posterior schemas and reconstruct channels from retained draws."""
import argparse
import json
from pathlib import Path
import warnings
import numpy as np
from .relaxed import Spec, forward, channel_array, sha256


def verify(path):
    p=np.load(path);meta=json.loads(str(p['metadata']));spec=Spec.from_metadata(meta['spec'])
    th=p['theta'];finite=np.isfinite(th).all(-1)
    np.testing.assert_array_equal(finite.sum(1),p['nok'])
    np.testing.assert_array_equal(p['scored'],p['nok']>=64)
    np.testing.assert_array_equal(p['admit'],p['scored']&(p['explained']>=.75))
    assert th.shape[-1]==spec.dim
    assert p['quantiles'].shape[2]==8
    ff=p['final_fractions'][finite]
    assert np.all(np.isfinite(ff))
    assert np.all((ff>=0)&(ff<=1+1e-6))
    assert np.all(ff.sum(1)<=1+1e-6)
    reconstructed=0
    for i in np.flatnonzero(p['scored'])[:6]:
        count=int(p['nok'][i]);T=np.broadcast_to(p['Tgrid'][i],(count,16))
        o=forward(th[i,:count],T,spec,p['ptype'][i,:count]);ch=channel_array(o,T)
        q=np.quantile(ch,[.025,.5,.975],axis=0)
        # Draw parameters are saved as float32 after float64 physical evaluation.
        # Seebeck is in uV/K; an absolute tolerance covers nearly zero medians.
        for j in range(8):
            np.testing.assert_allclose(q[:,j],p['quantiles'][i,:,j],rtol=2e-4,atol=.001 if j==1 else 1e-8)
        ffnew=np.stack([o[k][:,-1]/o['kappa'][:,-1] for k in ('kappa_L','kappa_bip','kappa_extra')],axis=-1)
        np.testing.assert_allclose(ffnew,p['final_fractions'][i,:count],rtol=2e-4,atol=1e-7)
        reconstructed+=1
    return dict(file=str(path),curves=len(th),scored=int(p['scored'].sum()),reconstructed_curves=reconstructed)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('run',type=Path);a=ap.parse_args()
    report=a.run/'archive_verification.json'
    previous={r['file']:r for r in json.loads(report.read_text())} if report.exists() else {}
    root=Path(__file__).resolve().parent
    code={p.name:sha256(p) for p in [Path(__file__),root/'relaxed.py',root/'temodel.py']}
    rows=[]
    for p in sorted(a.run.glob('*/*_inference.npz')):
        provenance={'archive_sha256':sha256(p),'verification_source_hashes':code}
        old=previous.get(str(p),{})
        if old.get('provenance')==provenance:row=old
        else:row=verify(p);row['provenance']=provenance
        rows.append(row)
        report.write_text(json.dumps(rows,indent=2))
    print(json.dumps(rows,indent=2))


if __name__=='__main__':main()
