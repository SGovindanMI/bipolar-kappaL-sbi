"""Verify release checksums and numerical/schema invariants without retraining."""
import hashlib,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def main():
 manifest=ROOT/'SHA256SUMS';checked=0;amend=json.loads((ROOT/'docs/FINAL_REVISION_AMENDMENTS.json').read_text())
 for line in manifest.read_text().splitlines():
  if not line.strip():continue
  digest,name=line.split(None,1);name=name.lstrip('*');path=ROOT/name
  if not path.is_file():raise AssertionError(f'Missing {name}')
  h=hashlib.sha256()
  with path.open('rb') as fh:
   for b in iter(lambda:fh.read(1024*1024),b''):h.update(b)
  if h.hexdigest()!=digest:
   change=amend.get(name,{})
   assert change.get('original_sha256')==digest and change.get('revised_sha256')==h.hexdigest(),f'Undocumented checksum difference: {name}'
  checked+=1
 a=np.load(ROOT/'data/real_analysis_set.npz');p=np.load(ROOT/'data/inference_v5.npz');r=np.load(ROOT/'data/results_v5.npz');v=json.loads((ROOT/'data/manuscript_numbers.json').read_text())
 assert a['x'].shape==(v['n'],50);assert len(np.unique(a['doi']))==v['papers']
 assert p['theta'].shape==(v['n'],128,10)
 finite=np.isfinite(p['theta']).all(2);np.testing.assert_array_equal(finite.sum(1),p['nok'])
 np.testing.assert_array_equal(p['scored'],p['nok']>=64)
 np.testing.assert_array_equal(p['admit'],p['scored']&(p['explained']>=.75))
 assert int(p['admit'].sum())==v['admitted'];assert int(r['paired'].sum())==v['paired']
 try:from .prior import in_box
 except ImportError:from prior import in_box
 # Float32 archival rounding can move a boundary by a few ulps. Inference is
 # checked in float64 before archival; released samples should remain very close.
 th=p['theta'][finite].astype(float);c=3.1-.5*(th[:,0]-17)
 assert np.all(th[:,3]>=c-1.8-2e-6) and np.all(th[:,3]<=c+1.2+2e-6)
 ratio=p['model_bipfrac_draws'];assert np.nanmin(ratio)>=0 and np.nanmax(ratio)<=1
 assert np.all(np.isfinite(r['exponents'][r['paired']]))
 print(f'PASS: {checked} file hashes; observations, draws, masks, counts and physical fraction bounds.')
if __name__=='__main__':main()
