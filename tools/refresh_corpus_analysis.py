"""Recompute all empirical summaries from the corrected observations and retained draws.

No training or posterior inference is performed. The data deposit and frozen
checkpoints remain the inputs. Run from the repository root.
"""
import argparse,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.relaxed_analysis import corpus

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--skip-reference',action='store_true');ap.add_argument('--summaries-only',action='store_true');a=ap.parse_args()
    log=ROOT/'work/analysis_refresh';log.mkdir(parents=True,exist_ok=True)
    def run(name,args):
        print(name,flush=True)
        with (log/(name+'.log')).open('w',encoding='utf-8') as f:subprocess.run([sys.executable,*args],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True)
    if not a.skip_reference:run('reference',['-m','src.analyse'])
    for v in ['mobility','extra','spline','mobility_extra','mobility_spline']:
        print('Refreshing '+v,flush=True)
        corpus(ROOT/'data/real_analysis_set.npz',ROOT/f'runs/v6_main/{v}/real_inference.npz',ROOT/'data/inference_v5.npz',ROOT/f'runs/v6_main/{v}/real_summary.json')
    if a.summaries_only:return
    for name,args in [('comparison',['-m','src.redo_compare','runs/v6_main']),('supplement',['-m','src.redo_supplement','runs/v6_main']),('families',['-m','src.publication_families']),('numbers',['combined/build_combined_numbers.py']),('components',['combined/component_comparison.py']),('figures',['combined/make_combined_figures.py'])]:run(name,args)
    print('All empirical analyses refreshed.',flush=True)
if __name__=='__main__':main()
