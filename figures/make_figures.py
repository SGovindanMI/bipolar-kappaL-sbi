"""Publication figures generated exclusively from corrected version 5 arrays."""
from pathlib import Path
import json,os,numpy as np
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'work/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':220})
COL=['#3d627e','#be6c43','#527e61','#79618e']

def main():
    r=np.load(ROOT/'data/results_v5.npz');p=np.load(ROOT/'data/inference_v5.npz');v=json.loads((ROOT/'data/manuscript_numbers.json').read_text());ad=r['admit'];sc=r['scored'];pair=r['paired'];e=r['exponents'];fr=r['bipolar_fraction'];shift=e[:,2]-e[:,1]
    def save(fig,n):
        fig.savefig(ROOT/f'figures/fig{n}.png',bbox_inches='tight');fig.savefig(ROOT/f'figures/fig{n}.pdf',bbox_inches='tight');plt.close(fig)
    fig,axs=plt.subplots(1,2,figsize=(7,3.3),layout='constrained')
    axs[0].hist(p['explained'][sc],bins=np.linspace(0,1,25),color=COL[0]);axs[0].axvline(.75,color=COL[1],ls='--',label='Screen threshold 0.75');axs[0].legend(frameon=False,loc='upper left',fontsize=8);axs[0].set(xlabel='Observed-point containment\nin latent band',ylabel='Scored curves',title='a  Fit screen')
    names=list(v['temperature_admission']);vals=[v['temperature_admission'][k] for k in names];c=np.array([x['ci'] for x in vals]);axs[1].bar(names,c[:,0],color=COL[0]);axs[1].errorbar(names,c[:,0],yerr=[c[:,0]-c[:,1],c[:,2]-c[:,0]],fmt='none',color='black',capsize=3)
    for i,x in enumerate(vals):axs[1].text(i,.025,f"n={x['n']}",ha='center',color='white',fontsize=8)
    axs[1].set(xlabel='Measurement ceiling bin (K)',ylabel='Admitted fraction of scored curves',ylim=(0,1),title='b  Screen by temperature window');save(fig,1)
    fig=plt.figure(figsize=(7,6.4),layout='constrained');gs=fig.add_gridspec(2,2);axs=[fig.add_subplot(gs[0,0]),fig.add_subplot(gs[0,1]),fig.add_subplot(gs[1,:])]
    colors=p['explained'][pair];im=axs[0].scatter(fr[pair],shift[pair],color=COL[0],s=5,alpha=.5,rasterized=True);axs[0].set_xscale('symlog',linthresh=.01);axs[0].axhline(0,color='gray',lw=.8);axs[0].set(xlabel='Inferred bipolar / measured total\nat 750 K',ylabel='Slope shift C − B',title='a  Bipolar association')
    axs[1].scatter(e[pair,3]-e[pair,1],shift[pair],s=5,alpha=.3,color=COL[0],rasterized=True);axs[1].set(xlabel='Additive shift C′ − B',ylabel='Model lattice shift C − B',title='b  Distinct estimands');axs[1].axhline(0,color='gray',lw=.8);axs[1].axvline(0,color='gray',lw=.8)
    axs[2].hist([e[pair,i] for i in [0,1,2,3]],bins=np.linspace(-2,1,46),histtype='step',label=['A Kim','B posterior L','C model lattice','C′ additive'],color=COL,density=True);axs[2].legend(frameon=False,fontsize=8);axs[2].set(xlabel='Finite-window log slope over 400–750 K',ylabel='Density',title='c  Lattice estimates');save(fig,2)
    fig,axs=plt.subplots(1,2,figsize=(7,4.4),layout='constrained');families=v['families'];names=list(families);c=np.array([families[k]['CB'] for k in names]);ys=np.arange(len(names));axs[0].errorbar(c[:,0],ys,xerr=[c[:,0]-c[:,1],c[:,2]-c[:,0]],fmt='o',color=COL[0],capsize=3);axs[0].set_yticks(ys,names);axs[0].axvline(0,color='gray',ls='--');axs[0].set(xlabel='Slope shift C − B',title='a  Within-family associations')
    names=list(v['rollover']);c=np.array([v['rollover'][k]['CB'] for k in names]);axs[1].errorbar(np.arange(4),c[:,0],yerr=[c[:,0]-c[:,1],c[:,2]-c[:,0]],fmt='o',color=COL[1],capsize=4);axs[1].set_xticks(np.arange(4),['None','<5%','5–15%','≥15%']);axs[1].axhline(0,color='gray',ls='--');axs[1].set(xlabel='Measured Seebeck rollover',ylabel='Slope shift C − B',title='b  Measurement-derived stratification');save(fig,3)
    fig,axs=plt.subplots(1,2,figsize=(7,3.3),layout='constrained');prob=r['r_probability'];med=np.full(len(ad),np.nan);med[ad]=np.nanmedian(p['theta'][ad,:,8],axis=1);masks=[prob>.8,prob<.2,(prob>=.2)&(prob<=.8)];labels=['Phonon-like','Impurity-like','Ambiguous'];axs[0].hist([med[ad&m] for m in masks],bins=np.linspace(-1,2,40),stacked=True,color=COL[:3],label=labels);axs[0].axvline(-.5,color='black',ls='--',lw=.8);axs[0].axvline(1.5,color='black',ls=':',lw=.8);axs[0].legend(frameon=False,fontsize=8);axs[0].set(xlabel='Posterior median effective r',ylabel='Admitted curves',title='a  Conditional exponent classes')
    c=np.array([v['classes'][k]['ci'] for k in ['phonon_like','impurity_like','ambiguous']]);axs[1].bar(labels,c[:,0],color=COL[:3]);axs[1].errorbar(labels,c[:,0],yerr=[c[:,0]-c[:,1],c[:,2]-c[:,0]],fmt='none',color='black',capsize=3);axs[1].set(ylabel='Fraction of admitted curves',ylim=(0,1),title='b  Paper-clustered intervals');save(fig,4)
if __name__=='__main__':main()
