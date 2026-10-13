"""Document structure, image resolution, cross-references and rendered-page QA."""
from pathlib import Path
import json,zipfile,io,re,hashlib
from lxml import etree
from PIL import Image,ImageOps,ImageDraw
from pypdf import PdfReader
import pypdfium2 as pdfium
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'combined/manuscript';QA=OUT/'rendered';QA.mkdir(exist_ok=True)
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math','a':'http://schemas.openxmlformats.org/drawingml/2006/main','wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
report={};texts={}
for stem in ['combined_manuscript','combined_supplementary_information']:
    path=OUT/(stem+'.docx')
    with zipfile.ZipFile(path) as z:
        tree=etree.fromstring(z.read('word/document.xml'));rels=etree.fromstring(z.read('word/_rels/document.xml.rels'));rd={r.get('Id'):r.get('Target') for r in rels}
        all_text=' '.join(tree.xpath('//w:t/text() | //m:t/text()',namespaces=NS))
        assert not any(marker in all_text for marker in ['\u00e2\u02c6','\u00e2\u20ac','\ufffd']), 'Corrupted Unicode in '+stem
        paragraphs=[''.join(p.xpath('.//w:t/text()',namespaces=NS)) for p in tree.xpath('//w:body/w:p',namespaces=NS)]
        text='\n'.join(paragraphs);texts[stem]=text
        (QA/(stem+'.txt')).write_text(text,encoding='utf-8');images=[]
        for shape in tree.xpath('//wp:inline',namespaces=NS):
            ext=shape.find('wp:extent',NS);rid=shape.find('.//a:blip',NS).get('{'+NS['r']+'}embed');im=Image.open(io.BytesIO(z.read('word/'+rd[rid])))
            dpi=im.width/(int(ext.get('cx'))/914400);assert dpi>=599,(stem,dpi)
            images.append({'pixels':im.size,'effective_dpi':dpi})
        record={'image_count':len(images),'images':images,'native_equations':len(tree.xpath('//m:oMath',namespaces=NS)),'tables':len(tree.xpath('//w:tbl',namespaces=NS)),'docx_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        assert len(images)==(7 if stem=='combined_manuscript' else 1), 'Missing figure in '+stem
    reader=PdfReader(OUT/(stem+'.pdf'));pdf=pdfium.PdfDocument(str(OUT/(stem+'.pdf')));pages=[]
    for i,page in enumerate(pdf):
        im=page.render(scale=1.25).to_pil().convert('RGB');im.save(QA/f'{stem}_{i+1:02}.png');pages.append(im)
    for start in range(0,len(pages),6):
        sheet=Image.new('RGB',(1200,1800),'#dddddd');draw=ImageDraw.Draw(sheet)
        for j,im in enumerate(pages[start:start+6]):
            x=j%2*600;y=j//2*600;sheet.paste(ImageOps.contain(im,(590,565)),(x,y+25));draw.text((x+12,y+5),f'{stem} page {start+j+1}',fill='black')
        sheet.save(QA/f'{stem}_contact_{start//6+1}.png')
    record.update(pages=len(pages),pdf_sha256=hashlib.sha256((OUT/(stem+'.pdf')).read_bytes()).hexdigest())
    report[stem]=record
    (QA/(stem+'_pdf.txt')).write_text('\n\n'.join(f'PAGE {i+1}\n{p.extract_text()}' for i,p in enumerate(reader.pages)),encoding='utf-8')
main=texts['combined_manuscript'];si=texts['combined_supplementary_information']
assert set(map(int,re.findall(r'^Table (\d+)\.',main,re.M)))=={1,2}
assert set(map(int,re.findall(r'^Supplementary Table (\d+)\.',si,re.M)))==set(range(1,35))
assert set(map(int,re.findall(r'^Figure (\d+)\.',main,re.M)))==set(range(1,8))
assert not re.search(r'(?<!Supplementary )\bTable (?:[3-9]|1[0-2])\b',main)
assert 'have not been published separately' not in main
assert 'Supplementary Information' in si
assert 'selecting epoch 890 (one-based; stored index 889)' in main
assert '§ST:' not in main+si
referenced=set()
for match in re.finditer(r'Supplementary Tables? (\d+)(?: and (\d+))?',main):
    referenced.update(int(v) for v in match.groups() if v)
assert referenced==set(range(1,35)), ('Supplementary tables missing a main-text reference',set(range(1,35))-referenced)
report['checks']={'all_table_and_figure_captions_present':True,'implementation_history_removed':True, 'separate_supplementary_information':True,'reference_selected_epoch_one_based':890,'main_display_items':9,'visual_review':'pending inspection of rendered pages'}
(OUT/'FINAL_DOCUMENT_QA.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
