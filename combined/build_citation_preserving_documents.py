"""Insert the sensitivity addition into frozen author-edited Zotero templates.

Only word/document.xml changes; no original paragraph, citation, bibliography,
equation, image, relationship, or field is rebuilt. Run this instead of the
legacy JS document pipeline for the current author-edited release.
"""
from pathlib import Path
from copy import deepcopy
from lxml import etree as E
import json, zipfile, hashlib

ROOT=Path(__file__).resolve().parents[1]
HERE=Path(__file__).resolve().parent
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
W='{'+NS['w']+'}'
DATA=json.loads((HERE/'positive_B_sensitivity.json').read_text())
NAMES=['Reference','Independent bands','Rising channel','Flexible lattice','Independent + rising','Independent + flexible']

def paragraph(text,bold=False,page=False,size=22):
    p=E.Element(W+'p');pr=E.SubElement(p,W+'pPr')
    E.SubElement(pr,W+'spacing',{W+'after':'120',W+'line':'276',W+'lineRule':'auto'})
    if page:E.SubElement(pr,W+'pageBreakBefore')
    if bold:E.SubElement(pr,W+'keepNext')
    r=E.SubElement(p,W+'r');rp=E.SubElement(r,W+'rPr')
    E.SubElement(rp,W+'rFonts',{W+'ascii':'Times New Roman',W+'hAnsi':'Times New Roman'})
    E.SubElement(rp,W+'sz',{W+'val':str(size)})
    if bold:E.SubElement(rp,W+'b')
    t=E.SubElement(r,W+'t');t.text=text
    return p

def table(rows,widths):
    tbl=E.Element(W+'tbl');pr=E.SubElement(tbl,W+'tblPr')
    E.SubElement(pr,W+'tblW',{W+'w':str(sum(widths)),W+'type':'dxa'})
    E.SubElement(pr,W+'tblLayout',{W+'type':'fixed'})
    borders=E.SubElement(pr,W+'tblBorders')
    for edge in ['top','left','bottom','right','insideH','insideV']:
        E.SubElement(borders,W+edge,{W+'val':'single',W+'sz':'4',W+'color':'D9D9D9'})
    margin=E.SubElement(pr,W+'tblCellMar')
    for edge in ['top','left','bottom','right']:E.SubElement(margin,W+edge,{W+'w':'80',W+'type':'dxa'})
    grid=E.SubElement(tbl,W+'tblGrid')
    for width in widths:E.SubElement(grid,W+'gridCol',{W+'w':str(width)})
    for i,row in enumerate(rows):
        tr=E.SubElement(tbl,W+'tr');trpr=E.SubElement(tr,W+'trPr');E.SubElement(trpr,W+'cantSplit')
        if i==0:E.SubElement(trpr,W+'tblHeader')
        for text,width in zip(row,widths):
            tc=E.SubElement(tr,W+'tc');cp=E.SubElement(tc,W+'tcPr')
            E.SubElement(cp,W+'tcW',{W+'w':str(width),W+'type':'dxa'})
            E.SubElement(cp,W+'vAlign',{W+'val':'center'})
            if i==0:E.SubElement(cp,W+'shd',{W+'fill':'E7E6E6'})
            tc.append(paragraph(str(text),bold=i==0,size=20))
    return tbl

def fmt(v):return f'{v[0]:.3f} [{v[1]:.3f}, {v[2]:.3f}]'.replace('-', '−')

def additions(kind):
    if kind=='main':
        p=paragraph('Excluding curves with a rising unipolar-subtraction estimate reduced, but did not eliminate, the slope shift. In the reference paired population, 431 of 4,248 curves (10.1%) had a positive B slope. Among the remaining 3,817 curves, the median C − B shift was −0.137 (95% paper-clustered bootstrap interval −0.153 to −0.125), compared with −0.166 in the full paired population. Restricting the six-model common population to the same 1,361 curves with non-positive reference B slopes retained negative median shifts for all six models, ranging from −0.090 to −0.544 (Supplementary Table 34). This descriptive sensitivity check shows that the negative shift is not confined to rising-B curves; it does not establish a unique bipolar attribution or remove model and prior dependence.')
        return [p]
    rows=[['Model','Native n','Positive B, n (%)','Kept n','C − B, all','C − B, B ≤ 0']]
    for name,r in zip(NAMES,DATA['models'].values()):
        v=r['native'];rows.append([name,f"{v['n']:,}",f"{v['positive_B_count']:,} ({100*v['positive_B_fraction']:.1f})",f"{v['B_nonpositive_n']:,}",fmt(v['CB_all']),fmt(v['CB_B_nonpositive'])])
    fixed=[['Model','Common set (n = 1,507)','Fixed subset (n = 1,361)']]
    for name,r in zip(NAMES,DATA['models'].values()):fixed.append([name,fmt(r['six_model_common']['CB_all']),fmt(r['common_reference_B_nonpositive']['CB'])])
    return [paragraph('Supplementary Table 34. Sensitivity to exclusion of rising-B curves.',True,True),
        paragraph('A. Native paired populations. Positive B denotes a strictly positive 400–750 K log-slope of the unipolar-subtraction estimate. Each model uses its own B slope for exclusion; the resulting populations therefore differ. Values are median per-curve C − B slope differences [95% paper-clustered bootstrap intervals].'),
        table(rows,[1700,850,1150,900,2200,2200]),
        paragraph('All native populations retain the original admission and finite-endpoint requirements. B ≤ 0 includes flat B curves. Intervals use 2,000 source-paper cluster resamples with seed 2024, recalculated within each reported subset. They are descriptive and unadjusted for multiple comparisons.'),
        paragraph('Supplementary Table 34 (continued).',True,True),
        paragraph('B. Identical-population comparison. Starting from the 1,507-curve six-model common population, remove the 146 curves with positive reference-model B slopes. The resulting 1,361-curve subset is identical across all six models; each model retains its own B and C estimates. The restriction does not require each extended model’s B slope to be non-positive.'),
        table(fixed,[2500,3250,3250]),
        paragraph('The negative median shift persists after exclusion of rising reference-B curves. This check addresses the positive-B tail, not all consequences of lattice restrictions, selection or prior assumptions. It is not a unipolar synthetic null test. These results were recomputed from the archived posterior outputs without retraining or new inference.')]

def text(p):return ''.join(p.xpath('.//w:t/text()',namespaces=NS))
def canon(e):return E.tostring(e,method='c14n')

report={}
for kind,source,dest in [('main','manuscript_zotero.docx','combined_manuscript.docx'),('supp','supplement_zotero.docx','combined_supplementary_information.docx')]:
    src=HERE/'manuscript_sources'/source;dst=HERE/'manuscript'/dest
    with zipfile.ZipFile(src) as z:
        raw=z.read('word/document.xml');tree=E.fromstring(raw);body=tree.find('w:body',NS)
        removed_blank_paragraphs=0
        while len(body)>1 and body[-2].tag==W+'p' and all(c.tag==W+'pPr' for c in body[-2]):
            body.remove(body[-2]); removed_blank_paragraphs+=1
        original=[canon(e) for e in body]
        anchor=next(p for p in body if text(p).startswith('3.7 Effective scattering') if kind=='main') if kind=='main' else next(p for p in body if text(p)=='Supplementary computational details')
        for element in additions(kind):
            if kind=='main':
                style_source=next(p for p in body if text(p).startswith('Non-positive endpoints'))
                element.remove(element.find('w:pPr',NS))
                if style_source.find('w:pPr',NS) is not None: element.insert(0,deepcopy(style_source.find('w:pPr',NS)))
            body.insert(body.index(anchor),element)
        unchanged=[canon(e) for e in body if canon(e) in original]
        assert unchanged==original,'Existing content changed'
        instructions=tree.xpath('//w:instrText/text()',namespaces=NS)
        before=E.fromstring(raw).xpath('//w:instrText/text()',namespaces=NS)
        assert instructions==before
        payload=E.tostring(tree,xml_declaration=True,encoding='UTF-8',standalone=True)
        with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED) as target:
            for entry in z.infolist():target.writestr(entry,payload if entry.filename=='word/document.xml' else z.read(entry.filename))
    with zipfile.ZipFile(src) as a,zipfile.ZipFile(dst) as b:
        changed=[n for n in a.namelist() if a.read(n)!=b.read(n)]
        assert changed==['word/document.xml']
    report[kind]={'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'removed_trailing_empty_paragraphs':removed_blank_paragraphs,'unchanged_original_body_elements':len(original),'unchanged_field_instruction_fragments':len(before),'zotero_field_instruction_fragments':sum('ZOTERO' in s for s in before),'changed_package_parts':changed}
(HERE/'citation_preservation_check.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
