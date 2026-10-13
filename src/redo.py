"""Reproducible v6 experiment matrix, isolated from all v5 release artifacts.

Pilot output is a software/feasibility check only. Production is a fresh full
training and held-out evaluation for each variant; it does not guarantee that
the scientific limitations have been resolved.
"""
import argparse
import json
import platform
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import time
import numpy as np
import scipy
import torch
from .relaxed import Spec, VERSION, generate, sha256
from .relaxed_posterior import train
from .relaxed_inference import infer
from .relaxed_analysis import diagnostics, corpus, save_json

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_VARIANTS=['mobility','extra','spline','mobility_extra','mobility_spline']


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mode',choices=['pilot','production'],default='pilot')
    ap.add_argument('--variants',nargs='+',default=DEFAULT_VARIANTS)
    ap.add_argument('--out',type=Path)
    ap.add_argument('--resume',action='store_true')
    ap.add_argument('--real',action='store_true',help='Also run the experimental models on the frozen real corpus')
    ap.add_argument('--jobs',type=int,default=1,help='Independent model workers; use 2 to overlap GPU training and CPU inference')
    ap.add_argument('--worker',action='store_true',help=argparse.SUPPRESS)
    args=ap.parse_args()
    specs=[Spec(n) for n in args.variants]
    out=args.out or ROOT/'runs'/('v6_'+args.mode)
    out.mkdir(parents=True,exist_ok=True)
    settings=dict(version=VERSION,mode=args.mode,variants=args.variants,real=args.real,
                  simulations=600000 if args.mode=='production' else 12000,
                  epochs=900 if args.mode=='production' else 40,
                  test_n=6000 if args.mode=='production' else 128,
                  narrow_n=1000 if args.mode=='production' else 128,
                  source_hashes={p.name:sha256(p) for p in (ROOT/'src').glob('relaxed*.py')},
                  driver_hash=sha256(Path(__file__)),base_solver_sha256=sha256(ROOT/'src/temodel.py'),
                  frozen_corpus_sha256=sha256(ROOT/'data/real_analysis_set.npz'),
                  fixtures_sha256={p.name:sha256(p) for p in (ROOT/'experiments/fixtures').glob('*.npz')},
                  environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,
                                   torch=str(torch.__version__),cuda=torch.version.cuda,
                                   gpu=torch.cuda.get_device_name(0) if torch.cuda.is_available() else None))
    control=out/specs[0].name if args.worker else out
    control.mkdir(parents=True,exist_ok=True)
    manifest=control/'manifest.json';status_path=control/'status.json'
    if manifest.exists():
        if not args.resume:raise RuntimeError('Run already exists; use --resume or a new output directory')
        if json.loads(manifest.read_text())!=settings:raise RuntimeError('Resume configuration/code differs from manifest; use a new directory')
    else:save_json(manifest,settings)
    state=json.loads(status_path.read_text()) if status_path.exists() else dict(completed=[],started=time.time())

    if args.jobs > 1 and not args.worker:
        state.update(status='running',active='parallel model workers',workers=args.jobs)
        save_json(status_path,state)
        def worker(spec):
            command=[sys.executable,'-m','src.redo','--mode',args.mode,'--out',str(out.resolve()),'--variants',spec.name,'--worker']
            if args.real:command.append('--real')
            if args.resume:command.append('--resume')
            with (out/(spec.name+'.log')).open('a' if args.resume else 'w') as log:
                subprocess.run(command,check=True,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
            return spec.name
        try:
            with ThreadPoolExecutor(max_workers=args.jobs) as pool:
                futures=[pool.submit(worker,spec) for spec in specs]
                for future in as_completed(futures):
                    name=future.result();state['completed'].append(name);save_json(status_path,state)
                    print('COMPLETED MODEL '+name,flush=True)
        except BaseException as exc:
            state.update(status='failed',error=repr(exc));save_json(status_path,state);raise
        state.update(status='complete',active=None,finished=time.time(),scientific_status='Exploratory; review diagnostics before manuscript claims')
        save_json(status_path,state)
        return

    def stage(key,fn):
        if key in state['completed']:return
        state.update(active=key,status='running');save_json(status_path,state)
        print(f'STAGE {key}',flush=True)
        try:fn()
        except Exception as exc:
            state.update(status='failed',error=repr(exc));save_json(status_path,state);raise
        state['completed'].append(key);save_json(status_path,state)

    for index,spec in enumerate(specs):
        dest=out/spec.name;dest.mkdir(exist_ok=True)
        training=dest/'train.npz';test=dest/'test.npz';narrow=dest/'narrow.npz';checkpoint=dest/'posterior.pt'
        seed=6100+DEFAULT_VARIANTS.index(spec.name)*10
        stage(spec.name+'/generate_train',lambda:generate(settings['simulations'],seed,training,spec))
        stage(spec.name+'/train',lambda:train(training,checkpoint,settings['epochs'],seed=seed+1))
        stage(spec.name+'/generate_test',lambda:generate(settings['test_n'],seed+2,test,spec))
        stage(spec.name+'/generate_narrow',lambda:generate(settings['narrow_n'],seed+3,narrow,spec,narrow=True))
        # Model-consistent tests and shared, fixed misspecification controls.
        sources={'test':test,'narrow':narrow}
        if args.mode=='production':
            sources.update(base_test=ROOT/'data/test_v5.npz',
                           mobility_low=ROOT/'data/stress_mobility_low.npz',
                           mobility_high=ROOT/'data/stress_mobility_high.npz',
                           wide_upturn=ROOT/'data/stress_lattice_upturn.npz',
                           narrow_upturn=ROOT/'experiments/fixtures/upturn_narrow_v5.npz',
                           narrow_control=ROOT/'experiments/fixtures/control_narrow_v5.npz')
        for label,source in sources.items():
            target=dest/(label+'_inference.npz')
            stage(spec.name+'/infer_'+label,lambda source=source,target=target:infer(source,target,seed=seed+4,checkpoint=checkpoint))
            stage(spec.name+'/diagnose_'+label,lambda source=source,target=target,label=label:diagnostics(source,target,dest/(label+'_diagnostics.json')))
        if args.real:
            target=dest/'real_inference.npz'
            stage(spec.name+'/infer_real',lambda:infer(ROOT/'data/real_analysis_set.npz',target,seed=seed+5,checkpoint=checkpoint))
            stage(spec.name+'/analyse_real',lambda:corpus(ROOT/'data/real_analysis_set.npz',target,ROOT/'data/inference_v5.npz',dest/'real_summary.json'))
    state.update(status='complete',active=None,finished=time.time(),scientific_status='Exploratory; review coverage, identifiability and prior sensitivity before manuscript claims')
    save_json(status_path,state)
    print(json.dumps(state,indent=2),flush=True)


if __name__=='__main__':
    main()
