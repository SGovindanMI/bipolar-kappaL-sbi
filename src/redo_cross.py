"""Evaluate all estimators on the same two extended-model truth datasets."""
import argparse
import json
from pathlib import Path
import torch
from .relaxed import Spec, sha256
from .relaxed_inference import infer
from .relaxed_analysis import diagnostics, save_json


def main():
    ap=argparse.ArgumentParser();ap.add_argument('run',type=Path);ap.add_argument('--models',nargs='+');a=ap.parse_args()
    root=Path(__file__).resolve().parents[1];manifest=json.loads((a.run/'manifest.json').read_text())
    sources={n:a.run/n/'narrow.npz' for n in ['mobility_extra','mobility_spline']}
    if not all(p.exists() for p in sources.values()):raise RuntimeError('Extended-model truth sets are not ready')
    dest=a.run/'cross_model';dest.mkdir(exist_ok=True)
    # Wrap identical v5 weights with the dimension/schema fields required by v6.
    # This is a metadata adapter; no weight or normalisation tensor is changed.
    old=root/'data/posterior_v5.pt';adapted=dest/'baseline_metadata_adapter.pt'
    original=torch.load(old,map_location='cpu',weights_only=True)
    original['metadata']=dict(original['metadata'],dimension=10,spec=Spec('baseline').metadata(),
                              original_checkpoint_sha256=sha256(old),adapter='Metadata only; frozen v5 tensors')
    if not adapted.exists():torch.save(original,adapted)
    checkpoint={'baseline':adapted,**{n:a.run/n/'posterior.pt' for n in manifest['variants']}}
    if a.models:checkpoint={n:checkpoint[n] for n in a.models}
    rows=[]
    for name,ckpt in checkpoint.items():
        for truth,source in sources.items():
            target=dest/(name+'__'+truth+'.npz');report=target.with_suffix('.diagnostics.json')
            if not target.exists():infer(source,target,seed=7300,checkpoint=ckpt)
            rows.append(diagnostics(source,target,report))
    save_json(dest/'summary.json',rows)


if __name__=='__main__':main()
