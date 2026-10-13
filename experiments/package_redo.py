"""Package the corrected release plus v6 results, excluding regenerable training arrays."""
from pathlib import Path
import hashlib,json,zipfile,argparse

ap=argparse.ArgumentParser();ap.add_argument('--publication',action='store_true');args=ap.parse_args()

root=Path(__file__).resolve().parents[1];run=root/'runs/v6_main'
assert json.loads((run/'postprocessing_status.json').read_text())['status']=='complete'
assert (run/'manuscript_v6_research.docx').exists()
assert (run/'document_qa.json').exists()
dest=root.parent/'deliverables';dest.mkdir(exist_ok=True)
if args.publication:
    assert (run/'publication/publication_qa.json').exists()
    assert (run/'publication/publication_verification.json').exists()
    dest=dest/'publication';dest.mkdir(exist_ok=True)
archive=dest/('bipolar-kappaL-sbi-publication.zip' if args.publication else 'bipolar-kappaL-sbi-v6-research.zip')
selected=[]
for p in root.rglob('*'):
    if not p.is_file():continue
    rel=p.relative_to(root)
    if any(s in {'.git','__pycache__','.pytest_cache'} for s in rel.parts):continue
    if rel.parts[0]=='runs':
        if len(rel.parts)<3 or rel.parts[1]!='v6_main':continue
        if p.name=='train.npz':continue
        if 'cache_equivalence_check' in rel.parts and p.suffix!='.json':continue
        if 'rendered' in rel.parts:continue
    if rel.parts[0]=='experiments' and p.name.startswith('layout_check'):continue
    selected.append((p,rel))
hashes={}
with zipfile.ZipFile(archive,'w',allowZip64=True) as z:
    for p,rel in sorted(selected):
        h=hashlib.sha256()
        info=zipfile.ZipInfo('bipolar-kappaL-sbi/'+rel.as_posix())
        info.compress_type=zipfile.ZIP_STORED if p.suffix.lower() in {'.npz','.pt','.png','.pdf','.docx','.zip'} else zipfile.ZIP_DEFLATED
        with p.open('rb') as src,z.open(info,'w',force_zip64=True) as dst:
            for chunk in iter(lambda:src.read(1024*1024),b''):h.update(chunk);dst.write(chunk)
        hashes[rel.as_posix()]=h.hexdigest()
    z.writestr('bipolar-kappaL-sbi/PACKAGE_CONTENTS.json',json.dumps({'sha256':hashes,'omitted':'Five regenerable v6 train.npz arrays, superseded/pilot runs, and internal layout-check artifacts. All main inference and test arrays are included.','reproduction':'Use REDO_README.md and a fresh output directory to regenerate training and inference.'},indent=2))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
record={'archive':str(archive),'bytes':archive.stat().st_size,'files':len(selected),'crc_check':'passed'}
(dest/'package_verification.json').write_text(json.dumps(record,indent=2))
print(json.dumps(record,indent=2))
