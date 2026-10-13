"""Retrieve the dated official exports used by the source audit, verifying hashes."""
import hashlib,json,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'work/starrydata_audit';OUT.mkdir(parents=True,exist_ok=True)
spec=json.loads((ROOT/'combined/starrydata_audit/source_provenance.json').read_text(encoding='utf-8'))
for row in spec['files']:
    dest=OUT/row['local_name']
    if dest.exists() and hashlib.sha256(dest.read_bytes()).hexdigest()==row['sha256']:continue
    data=urllib.request.urlopen(row['url'],timeout=120).read()
    if hashlib.sha256(data).hexdigest()!=row['sha256']:raise ValueError('Upstream content changed: '+row['url'])
    dest.write_bytes(data)
    print(dest.name)
