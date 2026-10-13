"""Scientific summary figures from finished diagnostics, without inferred claims."""
import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    ap=argparse.ArgumentParser();ap.add_argument('run',type=Path);a=ap.parse_args()
    manifest=json.loads((a.run/'manifest.json').read_text());names=manifest['variants']
    paths=[a.run/n/'test_diagnostics.json' for n in names]
    if not all(p.exists() for p in paths):raise RuntimeError('Independent tests are not complete')
    labels=[n.replace('mobility','independent bands').replace('_',' + ') for n in names]
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':200})
    dest=a.run/'figures';dest.mkdir(exist_ok=True)
    fig,axes=plt.subplots(2,1,figsize=(8,7.6),layout='constrained')
    for ax,kind,title in zip(axes,['test','narrow_upturn'],['Independent same-model tests','Shared narrow-gap lattice-upturn stress']):
        ds=[json.loads((a.run/n/(kind+'_diagnostics.json')).read_text()) for n in names]
        for offset,key,color,label in [(-.17,'lattice','#286b8c','Lattice'),(.17,'bipolar','#b76a36','Bipolar')]:
            values=[100*d['scored']['channels'][key]['coverage'] if d['scored']['n'] else np.nan for d in ds]
            ax.barh(np.arange(len(names))+offset,values,height=.32,color=color,label=label)
        ax.axvline(95,color='black',ls='--',lw=1,label='Nominal 95%')
        ax.set(yticks=np.arange(len(names)),yticklabels=labels,xlim=(0,100),xlabel='Pointwise coverage on scored curves (%)',title=title)
        ax.invert_yaxis()
    handles,legend_labels=axes[0].get_legend_handles_labels()
    fig.legend(handles,legend_labels,loc='outside lower center',ncol=3,fontsize=9)
    fig.savefig(dest/'coverage.png');fig.savefig(dest/'coverage.pdf');plt.close(fig)
    comparison=json.loads((a.run/'comparison.json').read_text())
    fig,ax=plt.subplots(figsize=(8,4.6),layout='constrained')
    allnames=['baseline']+names
    for i,n in enumerate(allnames):
        v=comparison['models'][n]['all_model_common']['C_B']
        if any(x is None for x in v):continue
        ax.hlines(i,v[1],v[2],color='#286b8c')
        ax.plot(v[0],i,'o',color='#286b8c')
    ax.axvline(0,color='black',lw=.8)
    ax.set(yticks=np.arange(len(allnames)),yticklabels=['v5 baseline']+labels,
           xlabel='Median per-curve lattice slope shift C minus B',
           title=f"400–750 K, same {comparison['all_model_common_n']} curves across all models\n95% paper-clustered bootstrap intervals")
    ax.invert_yaxis();fig.savefig(dest/'common_population.png');fig.savefig(dest/'common_population.pdf');plt.close(fig)
    print(dest)


if __name__=='__main__':main()
