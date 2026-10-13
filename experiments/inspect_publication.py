"""Render page contact sheets and audit the embedded image resolution."""
from pathlib import Path
import json,zipfile,io
from PIL import Image,ImageOps,ImageDraw
from lxml import etree
import pypdfium2 as pdfium
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'runs/v6_main/publication';QA=OUT/'rendered';QA.mkdir(exist_ok=True)
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
record={}
for stem in ['manuscript_publication','supplementary_information']:
    pdf=pdfium.PdfDocument(str(OUT/(stem+'.pdf')));reader=PdfReader(OUT/(stem+'.pdf'));pages=[]
    for i,page in enumerate(pdf):
        im=page.render(scale=1.4).to_pil().convert('RGB');im.save(QA/f'{stem}_{i+1:02}.png');pages.append(im)
    for start in range(0,len(pages),6):
        canvas=Image.new('RGB',(1200,1800),'#dddddd');draw=ImageDraw.Draw(canvas)
        for j,im in enumerate(pages[start:start+6]):
            thumb=ImageOps.contain(im,(590,565));x=(j%2)*600;y=(j//2)*600;canvas.paste(thumb,(x,y+25));draw.text((x+10,y+5),f'{stem} — page {start+j+1}',fill='black')
        canvas.save(QA/f'{stem}_contact_{start//6+1}.png')
    with zipfile.ZipFile(OUT/(stem+'.docx')) as z:
        xml=etree.fromstring(z.read('word/document.xml'));rels=etree.fromstring(z.read('word/_rels/document.xml.rels'));rd={r.get('Id'):r.get('Target') for r in rels};images=[]
        for shape in xml.xpath('//wp:inline',namespaces=ns):
            ext=shape.find('wp:extent',ns);rid=shape.find('.//a:blip',ns).get('{'+ns['r']+'}embed');target=rd[rid];im=Image.open(io.BytesIO(z.read('word/'+target)))
            dpi=im.width/(int(ext.get('cx'))/914400);assert dpi>=600
            images.append({'pixels':im.size,'embedded_width_inches':int(ext.get('cx'))/914400,'effective_dpi':dpi})
        record[stem]={'pages':len(pages),'figures':images,'native_equations':len(xml.xpath('//m:oMath',namespaces=ns)),'tables':len(xml.xpath('//w:tbl',namespaces=ns)),'words_pdf':sum(len(p.extract_text().split()) for p in reader.pages)}
    (QA/(stem+'_pages.txt')).write_text('\n\n'.join(f'PAGE {i+1}\n{p.extract_text()}' for i,p in enumerate(reader.pages)),encoding='utf-8')
(OUT/'publication_qa.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
