"""Regenerate publication artwork and exact plotted source data; no model rerun."""
import json,csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'runs/v6_main'
OUT=RUN/'publication';FIG=OUT/'figures'
NAMES=['baseline','mobility','extra','spline','mobility_extra','mobility_spline']
LABELS=['Reference','Independent bands','Rising channel','Flexible lattice','Independent + rising','Independent + flexible']
def read(p):return json.loads(p.read_text())
def main():
    FIG.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'Arial','font.size':7,'axes.titlesize':7,'axes.labelsize':7,'xtick.labelsize':7,'ytick.labelsize':7,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none'})
    source=[]
    def save(fig,name):
        fig.savefig(FIG/(name+'.png'),dpi=600)
        fig.savefig(FIG/(name+'.pdf'))
        fig.savefig(FIG/(name+'.svg'))
        with Image.open(FIG/(name+'.png')) as im:im.convert('RGB').save(FIG/(name+'.tiff'),dpi=(600,600),compression='tiff_lzw')
        plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(7.1,2.8),layout='constrained',gridspec_kw={'width_ratios':[1,1.35]})
    ax=axes[0];ax.axis('off')
    boxes=[('50 standardised inputs',.88),('3 hidden layers: 256 SiLU units each',.64),('Mean + full precision + sign heads',.40),('128 accepted physical posterior draws',.16)]
    for text,y in boxes:ax.text(.5,y,text,ha='center',va='center',bbox={'boxstyle':'round,pad=.6','fc':'#e9f2f6','ec':'#0072B2'},transform=ax.transAxes)
    for y in [.81,.57,.33]:ax.annotate('',xy=(.5,y-.09),xytext=(.5,y),xycoords='axes fraction',arrowprops={'arrowstyle':'->'})
    ax.set_title('a  Amortised inference',loc='left',fontweight='bold',fontsize=8)
    ax=axes[1]
    colors=['#0072B2','#D55E00','#009E73','#CC79A7','#333333']
    for n,c in zip(NAMES[1:],colors):
        h=read(RUN/n/'posterior.history.json');v=np.array([r['val_nll'] for r in h]);e=np.arange(1,len(h)+1)
        ax.plot(e,v-v.min(),label=LABELS[NAMES.index(n)],color=c,lw=1)
        for ep,row in zip(e,h):source.append({'figure':1,'model':n,'quantity':'validation_nll_above_run_minimum','x':int(ep),'value':row['val_nll']-float(v.min()),'lower':'','upper':''})
    ax.set(xlabel='Epoch',ylabel='Validation NLL above run minimum',yscale='symlog',ylim=(0,None))
    ax.set_title('b  Optimisation histories',loc='left',fontweight='bold',fontsize=8);ax.legend(fontsize=6,frameon=False)
    save(fig,'figure1_network')
    shared=read(RUN/'stress_comparison.json')['narrow_upturn']['models']
    fig,axes=plt.subplots(1,3,figsize=(7.1,2.8),layout='constrained')
    for k,(quantity,title,xlabel) in enumerate([('coverage','a  Lattice coverage','Pointwise coverage (%)'),('median_interval_width','b  Interval width',r'Median width (W m$^{-1}$ K$^{-1}$)'),('slope','c  Slope error','Median absolute slope error')]):
        values=[]
        for n in NAMES:
            v=shared[n]['common_slope']['median_absolute_error'] if quantity=='slope' else shared[n]['channels']['lattice'][quantity]*(100 if quantity=='coverage' else 1)
            values.append(v);source.append({'figure':2,'model':n,'quantity':quantity,'x':'','value':v,'lower':'','upper':''})
        ax=axes[k];ax.barh(range(6),values,color='#0072B2');ax.set(yticks=range(6),yticklabels=LABELS if k==0 else ['']*6,xlabel=xlabel);ax.invert_yaxis();ax.set_title(title,loc='left',fontweight='bold',fontsize=8)
        if k==0:ax.axvline(95,color='black',ls='--',lw=.7);ax.set_xlim(0,102)
    save(fig,'figure2_tradeoff')
    comp=read(RUN/'comparison.json')
    fig,ax=plt.subplots(figsize=(7.1,2.6),layout='constrained')
    for i,n in enumerate(NAMES):
        v=comp['models'][n]['all_model_common']['C_B'];ax.hlines(i,v[1],v[2],color='#0072B2');ax.plot(v[0],i,'o',color='#0072B2',ms=4)
        source.append({'figure':3,'model':n,'quantity':'median_slope_shift_C_minus_B','x':'','value':v[0],'lower':v[1],'upper':v[2]})
    ax.set(yticks=range(6),yticklabels=LABELS,xlabel='Median per-curve slope shift, C minus B');ax.invert_yaxis();ax.axvline(0,color='black',lw=.7)
    save(fig,'figure3_corpus')
    fig,axes=plt.subplots(1,2,figsize=(7.1,2.8),layout='constrained')
    for ax,truth,title in zip(axes,['mobility_extra','mobility_spline'],['a  Rising-channel truth','b  Flexible-lattice truth']):
        vals=[];counts=[]
        for n in NAMES:
            d=read(RUN/'cross_model'/f'{n}__{truth}.diagnostics.json');v=100*d['scored']['channels']['lattice']['coverage'];vals.append(v);counts.append(d['scored']['n'])
            source.append({'figure':4,'model':n,'quantity':'lattice_coverage_given_'+truth,'x':d['scored']['n'],'value':v,'lower':'','upper':''})
        ax.barh(range(6),vals,color='#009E73');ax.set(yticks=range(6),yticklabels=[f'{l} (n={n})' for l,n in zip(LABELS,counts)],xlabel='Pointwise lattice coverage (%)',xlim=(0,102));ax.invert_yaxis();ax.axvline(95,color='black',ls='--',lw=.7);ax.set_title(title,loc='left',fontweight='bold',fontsize=8)
    save(fig,'figure4_transfer')
    with (OUT/'figure_source_data.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(source[0]));w.writeheader();w.writerows(source)
    metadata={p.name:{'pixels':Image.open(p).size,'dpi':Image.open(p).info.get('dpi')} for p in FIG.glob('*.png')}
    (OUT/'figure_metadata.json').write_text(json.dumps(metadata,indent=2))
    print(OUT)
if __name__=='__main__':main()
