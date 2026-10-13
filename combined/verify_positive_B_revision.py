"""Verify the sensitivity addition and exact preservation of author content."""
from pathlib import Path
from lxml import etree as E
import json,zipfile
import numpy as np

HERE=Path(__file__).resolve().parent
N={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
data=json.loads((HERE/'positive_B_sensitivity.json').read_text())
mask=np.load(HERE/'positive_B_masks.npz')
assert int(mask['common'].sum())==1507
assert int(mask['common_reference_B_nonpositive'].sum())==1361
assert np.all(~mask['common_reference_B_nonpositive'] | mask['common'])
def txt(e):return ''.join(e.xpath('.//w:t/text()',namespaces=N))
def fmt(v):return f'{v[0]:.3f} [{v[1]:.3f}, {v[2]:.3f}]'.replace('-', '−')
report={}
for key,src,dst in [('main','manuscript_zotero.docx','combined_manuscript.docx'),('supp','supplement_zotero.docx','combined_supplementary_information.docx')]:
    with zipfile.ZipFile(HERE/'manuscript_sources'/src) as a,zipfile.ZipFile(HERE/'manuscript'/dst) as b:
        assert a.namelist()==b.namelist()
        assert all(a.read(n)==b.read(n) for n in a.namelist() if n!='word/document.xml')
        x=E.fromstring(a.read('word/document.xml'));y=E.fromstring(b.read('word/document.xml'))
        assert x.xpath('//w:instrText/text()',namespaces=N)==y.xpath('//w:instrText/text()',namespaces=N)
        body=x.find('w:body',N);w='{'+N['w']+'}'
        while len(body)>1 and body[-2].tag==w+'p' and all(c.tag==w+'pPr' for c in body[-2]): body.remove(body[-2])
        original=[E.tostring(e,method='c14n') for e in body]
        current=[E.tostring(e,method='c14n') for e in y.find('w:body',N)]
        i=0
        for element in current:
            if i<len(original) and element==original[i]:i+=1
        assert i==len(original),'Original body content modified'
        text=txt(y)
        assert '\u00e2\u02c6' not in text and '\ufffd' not in text
        if key=='main':
            for term in ['431 of 4,248','3,817','−0.137','−0.153 to −0.125','1,361','−0.090 to −0.544','Supplementary Table 34']:assert term in text,term
        else:
            body=y.find('w:body',N);tables=list(body.findall('w:tbl',N))[-2:]
            # New tables precede computational details; identify by their headers.
            tables=[t for t in body.findall('w:tbl',N) if 'Positive B, n (%)' in txt(t) or 'Fixed subset (n = 1,361)' in txt(t)]
            assert len(tables)==2
            for t in tables:assert len(t.findall('w:tr',N))==7
            for i,(model,v) in enumerate(data['models'].items(),1):
                assert mask[model+'_native_B_nonpositive'].sum()==v['native']['B_nonpositive_n']
                ar=tables[0].findall('w:tr',N)[i];br=tables[1].findall('w:tr',N)[i]
                assert fmt(v['native']['CB_all']) in txt(ar)
                assert fmt(v['native']['CB_B_nonpositive']) in txt(ar)
                assert fmt(v['six_model_common']['CB_all']) in txt(br)
                assert fmt(v['common_reference_B_nonpositive']['CB']) in txt(br)
        report[key]={'original_content_preserved':True,'citation_fields_preserved':True,'sensitivity_text_checked':True}
report['masks']={'common':1507,'fixed_subset':1361,'native_masks_checked':6}
(HERE/'positive_B_revision_verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
