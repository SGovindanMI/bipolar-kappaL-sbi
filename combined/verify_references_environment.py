"""Check citation numbering, bibliography consistency and recorded run environment."""
import json,re
from pathlib import Path
from docx import Document
ROOT=Path(__file__).resolve().parents[1]
r=json.loads((ROOT/'combined/reference_registry.json').read_text(encoding='utf-8'))
refs={v['number']:v['text'] for v in r['references'].values()}
assert set(refs)==set(range(1,23))
for name,heading in [('combined_manuscript','References'),('combined_supplementary_information','References cited in Supplementary Information')]:
    d=Document(ROOT/f'combined/manuscript/{name}.docx');p=d.paragraphs
    cut=next(i for i,x in enumerate(p) if x.text==heading)
    body='\n'.join(x.text for x in p[:cut]);assert '[@' not in body
    cited=[int(n) for m in re.finditer(r'\[(\d+(?:,\d+)*)\]',body) for n in m.group(1).split(',')]
    bib={}
    for x in p[cut+1:]:
        m=re.match(r'^\[(\d+)\]\s+(.*)',x.text)
        if m:bib[int(m.group(1))]=m.group(2)
    assert set(cited)==set(bib)
    assert all(refs[n]==text for n,text in bib.items())
    if name=='combined_manuscript':assert list(dict.fromkeys(cited))==list(range(1,23))
    print(f'{name}: {len(bib)} references, all cited; bibliography matches registry.')
e=json.loads((ROOT/'data/computational_environment.json').read_text())
for model in ['mobility','extra','spline','mobility_extra','mobility_spline']:
    assert e['extended']==json.loads((ROOT/f'runs/v6_main/{model}/manifest.json').read_text())['environment']
v=json.loads((ROOT/'data/posterior_v5.json').read_text())
assert e['reference_recorded']=={k:v[k] for k in ['device','torch']}
print('PASS: environment matches five archived manifests and reference-training metadata.')
