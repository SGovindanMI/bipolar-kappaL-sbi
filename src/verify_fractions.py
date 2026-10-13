"""Check matched-draw fractions and reconstruct the cross-model predictions."""
import argparse,json
from pathlib import Path
import numpy as np
from .verify_redo import verify
from .relaxed import sha256


def main():
    ap=argparse.ArgumentParser();ap.add_argument('run',type=Path);a=ap.parse_args()
    rows=[];cross=[]
    paths=sorted(a.run.glob('*/*_inference.npz'))+sorted((a.run/'cross_model').glob('*.npz'))
    for path in paths:
        with np.load(path) as p:
            T=p['Tgrid'];nok=p['nok'];ff=p['fractions750']
            span=(T[:,0]<=400)&(T[:,-1]>=750)
            valid=span[:,None]&(np.arange(ff.shape[1])[None,:]<nok[:,None])
            np.testing.assert_array_equal(np.isfinite(ff).all(-1),valid)
            f=ff[valid]
            assert np.all((f>=0)&(f<=1+1e-6))
            assert np.all(f.sum(-1)<=1+1e-6)
            np.testing.assert_allclose(ff[:,:,1],p['model_bipfrac_draws'],equal_nan=True,rtol=1e-6,atol=1e-8)
            np.testing.assert_allclose(p['bipfrac_draws'],p['model_bipfrac_draws']*p['model_total_ratio_draws'],equal_nan=True,rtol=3e-6,atol=1e-7)
            rows.append({'file':str(path),'sha256':sha256(path),'finite_matched_draws_at_750K':int(valid.sum()),'bounds_and_ratio_identity':'passed'})
        if path.parent.name=='cross_model':cross.append(verify(path))
    (a.run/'fraction_verification.json').write_text(json.dumps(rows,indent=2))
    (a.run/'cross_archive_verification.json').write_text(json.dumps(cross,indent=2))
    print('Verified fraction identities:',len(rows),'archives; reconstructed cross-model archives:',len(cross))


if __name__=='__main__':main()
