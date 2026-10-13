"""Full-precision Gaussian conditional approximation and reproducible training."""
import os
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import argparse,json,time,random
from pathlib import Path
import numpy as np
import torch
from torch import nn
ROOT=Path(__file__).resolve().parents[1]
class Posterior(nn.Module):
    def __init__(self):
        super().__init__(); layers=[]; ni=50
        for _ in range(3):layers.extend([nn.Linear(ni,256),nn.SiLU()]);ni=256
        self.body=nn.Sequential(*layers);self.mu=nn.Linear(256,10);self.dg=nn.Linear(256,10);self.off=nn.Linear(256,45);self.logit=nn.Linear(256,1)
        for h in (self.mu,self.dg,self.off):nn.init.zeros_(h.weight);nn.init.zeros_(h.bias)
        self.register_buffer('ir',torch.tril_indices(10,10,-1)[0]);self.register_buffer('ic',torch.tril_indices(10,10,-1)[1])
    def forward(self,x):
        h=self.body(x);mu=self.mu(h);dg=self.dg(h).clamp(-3,6);off=self.off(h)
        A=torch.diag_embed(dg.exp());A[:,self.ir,self.ic]=off
        return mu,A,dg,self.logit(h).squeeze(-1)
    def loss(self,x,y,s):
        mu,A,dg,logit=self(x);v=torch.bmm(A.transpose(1,2),(y-mu).unsqueeze(-1)).squeeze(-1)
        return (.5*(v*v).sum(-1)-dg.sum(-1)+5*np.log(2*np.pi)+nn.functional.binary_cross_entropy_with_logits(logit,s,reduction='none')).mean()

def train(path,out,epochs=900,seed=0):
    random.seed(seed);np.random.seed(seed);torch.manual_seed(seed);torch.set_num_threads(4)
    device='cuda' if torch.cuda.is_available() else 'cpu'
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    torch.use_deterministic_algorithms(True)
    z=np.load(path);x=z['x'];y=z['theta'];ix=np.random.default_rng(3).permutation(len(x));nv=min(12000,max(100,int(.02*len(x))));ti,vi=ix[nv:],ix[:nv]
    xm=x[ti].mean(0);xs=x[ti].std(0);ym=y[ti,:10].mean(0);ys=y[ti,:10].std(0)
    X=torch.tensor((x-xm)/xs,device=device);Y=torch.tensor((y[:,:10]-ym)/ys,device=device);S=torch.tensor(y[:,10],device=device)
    ti=torch.tensor(ti,device=device);vi=torch.tensor(vi,device=device);model=Posterior().to(device);opt=torch.optim.AdamW(model.parameters(),lr=.0015,weight_decay=1e-5);sched=torch.optim.lr_scheduler.ReduceLROnPlateau(opt,factor=.5,patience=6)
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);best=np.inf;stale=0;hist=[];t0=time.time()
    meta=dict(model_version='5.0.0',n_train=len(ti),n_validation=len(vi),seed=seed,split_seed=3,batch_size=1024,max_epochs=epochs,early_stopping_patience=50,device=device,torch=str(torch.__version__),source_metadata=json.loads(str(z['metadata'])),architecture='50-256-256-256; SiLU; full Gaussian precision and independent Bernoulli')
    print(meta,flush=True)
    for epoch in range(epochs):
        model.train();perm=ti[torch.randperm(len(ti),device=device)];total=0.
        for ids in perm.split(1024):
            opt.zero_grad(set_to_none=True);loss=model.loss(X[ids],Y[ids],S[ids]);loss.backward();nn.utils.clip_grad_norm_(model.parameters(),5.);opt.step();total+=float(loss.detach())*len(ids)
        model.eval()
        with torch.no_grad():vl=sum(float(model.loss(X[ids],Y[ids],S[ids]))*len(ids) for ids in vi.split(4096))/len(vi)
        sched.step(vl);hist.append(dict(epoch=epoch,train_nll=total/len(ti),val_nll=vl,lr=opt.param_groups[0]['lr'],seconds=time.time()-t0))
        if vl<best-1e-4:
            best=vl;stale=0;meta.update(best_epoch=epoch,best_validation_nll=best)
            torch.save(dict(state={k:v.detach().cpu() for k,v in model.state_dict().items()},xm=torch.tensor(xm),xs=torch.tensor(xs),ym=torch.tensor(ym),ys=torch.tensor(ys),metadata=meta.copy()),out)
        else:stale+=1
        if epoch%10==0:print(hist[-1],flush=True);out.with_suffix('.history.json').write_text(json.dumps(hist,indent=2))
        if stale>=50:break
    meta.update(epochs_completed=epoch+1,stop_reason='patience' if stale>=50 else 'epoch_cap',seconds=time.time()-t0)
    out.with_suffix('.json').write_text(json.dumps(meta,indent=2));out.with_suffix('.history.json').write_text(json.dumps(hist,indent=2));print(meta,flush=True)

def load(path=None,device='cpu'):
    c=torch.load(path or ROOT/'data/posterior_v5.pt',map_location=device,weights_only=True);m=Posterior().to(device);m.load_state_dict(c['state']);m.eval();return m,c

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,default=ROOT/'work/train_v5.npz');p.add_argument('--out',type=Path,default=ROOT/'data/posterior_v5.pt');p.add_argument('--epochs',type=int,default=900);a=p.parse_args();train(a.data,a.out,a.epochs)

