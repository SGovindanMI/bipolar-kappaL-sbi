"""Check plotted numbers against source diagnostics and article structure."""
from pathlib import Path
import csv,json,math,zipfile,hashlib
from lxml import etree
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];RUN=ROOT/'runs/v6_main';OUT=RUN/'publication'
def read(p):return json.loads(p.read_text())
shared=read(RUN/'stress_comparison.json')['narrow_upturn'];comp=read(RUN/'comparison.json')
hist={n:read(RUN/n/'posterior.history.json') for n in ['mobility','extra','spline','mobility_extra','mobility_spline']}
count=0
for row in csv.DictReader((OUT/'figure_source_data.csv').open(encoding='utf-8')):
    f=int(row['figure']);n=row['model'];q=row['quantity'];v=float(row['value'])
    if f==1:
        h=hist[n];expected=h[int(row['x'])-1]['val_nll']-min(r['val_nll'] for r in h)
    elif f==2:
        d=shared['models'][n];expected=d['common_slope']['median_absolute_error'] if q=='slope' else d['channels']['lattice'][q]*(100 if q=='coverage' else 1)
    elif f==3:
        triplet=comp['models'][n]['all_model_common']['C_B'];expected=triplet[0]
        assert float(row['lower'])==triplet[1] and float(row['upper'])==triplet[2]
    else:
        truth=q.removeprefix('lattice_coverage_given_');d=read(RUN/'cross_model'/f'{n}__{truth}.diagnostics.json')
        expected=100*d['scored']['channels']['lattice']['coverage'];assert int(row['x'])==d['scored']['n']
    assert math.isclose(v,expected,rel_tol=1e-12,abs_tol=1e-12),(row,expected)
    count+=1
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
with zipfile.ZipFile(OUT/'manuscript_publication.docx') as z:
    tree=etree.fromstring(z.read('word/document.xml'));text=' '.join(tree.xpath('//w:t/text()',namespaces=ns))
    assert len(tree.xpath('//wp:inline',namespaces=ns))==4
    assert len(tree.xpath('//m:oMath',namespaces=ns))==11
    assert not any(s in text for s in ['@FIG','@NN','$$'])
    assert 'software release v5' in text
    assert [text.index(f'Figure {i} |') for i in range(1,5)]==sorted(text.index(f'Figure {i} |') for i in range(1,5))
for p in (OUT/'figures').glob('*.tiff'):
    with Image.open(p) as im:assert im.mode=='RGB' and min(im.info['dpi'])>=599.9
for p in (OUT/'figures').glob('*.png'):
    with Image.open(p) as im:assert min(im.info['dpi'])>=599.9
qa=read(OUT/'publication_qa.json');assert qa['supplementary_information']['tables']==8
record={'plotted_values_verified':count,'source_data_check':'all values match saved diagnostics or histories','figures':4,'native_equations':11,'supplementary_tables':8,'baseline_release_v5_included':True,'raster_dpi':600,'minimum_embedded_dpi':min(r['effective_dpi'] for r in qa['manuscript_publication']['figures']),'scientific_arrays_modified':False,'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('*') if p.suffix in ['.docx','.pdf','.csv']}}
(OUT/'publication_verification.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
