"""Complete deterministic workflow; retraining is explicitly optional."""
import argparse,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(file,*args):subprocess.run([sys.executable,str(ROOT/file),*map(str,args)],check=True,cwd=ROOT)
def main():
 p=argparse.ArgumentParser();p.add_argument('--retrain',action='store_true');a=p.parse_args()
 if a.retrain:
  run('src/prior.py','--n',600000,'--seed',2001,'--out',ROOT/'work/train_v5.npz');run('src/posterior.py')
 for name,seed,n,stress in [('calibration_v5',2002,6000,None),('test_v5',2003,6000,None),('stress_lattice_upturn',2004,1000,'lattice_upturn'),('stress_mobility_low',2005,1000,'mobility_low'),('stress_mobility_high',2006,1000,'mobility_high')]:
  args=['--n',n,'--seed',seed,'--out',ROOT/f'data/{name}.npz']
  if stress:args+=['--stress',stress]
  run('src/prior.py',*args)
 for name,seed in [('test_v5',3002),('stress_lattice_upturn',3003),('stress_mobility_low',3004),('stress_mobility_high',3005)]:run('src/inference.py','--source',ROOT/f'data/{name}.npz','--out',ROOT/f'data/{name}_inference.npz','--seed',seed)
 run('src/validate.py');run('src/draw_count_check.py');run('src/inference.py');run('src/analyse.py');run('figures/make_figures.py')
if __name__=='__main__':main()
