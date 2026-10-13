"""Corrected SPB transport model, version 5. Float64 and checked neutrality."""
from pathlib import Path
import os
import numpy as np
from scipy.special import gamma, roots_legendre

MODEL_VERSION='5.0.0'
KB_E=KB_EV=8.617333262e-5
ME,HPL,KBJ,QE=9.1093837015e-31,6.62607015e-34,1.380649e-23,1.602176634e-19
_JG=np.linspace(-.5,4.5,501)
_ETA=np.linspace(-20.,50.,2801)
_DJ=_JG[1]-_JG[0]
_CACHE=Path(os.environ.get('BIPOLAR_CACHE',str(Path(__file__).resolve().parents[1]/'data')))/'fermi_v5.npz'
_TAB=None

def _table():
    global _TAB
    if _TAB is not None:return _TAB
    if _CACHE.exists():
        with np.load(_CACHE,allow_pickle=False) as d:
            if np.array_equal(d['jg'],_JG) and np.array_equal(d['eta'],_ETA):
                _TAB=d['tab'];return _TAB
    # E=u^4 regularises the endpoint for every supported integral order.
    z,wz=roots_legendre(512)
    u=(z+1.)*140.**.25/2.;wu=wz*140.**.25/2.
    power=4.*u[None,:]**(4.*_JG[:,None]+3.)*wu
    occ=1./(1.+np.exp(np.clip(u[:,None]**4-_ETA[None,:],-700.,700.)))
    _TAB=np.log(power@occ)
    _CACHE.parent.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(_CACHE,tab=_TAB,jg=_JG,eta=_ETA)
    return _TAB

def F(j,eta):
    """Unnormalised Fermi integral, broadcasting orders and arguments.

    Cubic interpolation in order and linear interpolation in eta, in log space;
    Boltzmann-series and Sommerfeld tails avoid out-of-grid clamping.
    """
    j,eta=np.broadcast_arrays(np.asarray(j,float),np.asarray(eta,float))
    if np.any((j<-.5)|(j>4.5)) or not np.all(np.isfinite(eta)) or not np.all(np.isfinite(j)):
        raise ValueError('F requires finite eta and -0.5 <= j <= 4.5')
    shape=eta.shape;jf,ef=j.ravel(),eta.ravel();ans=np.empty_like(ef)
    low,high=ef < -20.,ef > 50.;mid=~(low|high)
    if np.any(low):
        a,b=jf[low],ef[low];z=np.exp(b)
        ans[low]=gamma(a+1.)*z*(1.-z/2.**(a+1.)+z*z/3.**(a+1.))
    if np.any(high):
        a,b=jf[high],ef[high]
        v=b**(a+1.)/(a+1.)+np.pi**2/6.*a*b**(a-1.)
        v+=7*np.pi**4/360.*a*(a-1.)*(a-2.)*b**(a-3.)
        v+=31*np.pi**6/15120.*a*(a-1.)*(a-2.)*(a-3.)*(a-4.)*b**(a-5.)
        ans[high]=v
    if np.any(mid):
        a,b=jf[mid],ef[mid];tab=_table();q=(a-_JG[0])/_DJ
        if np.all(a == a[0]) and abs(q[0]-round(q[0])) < 1e-8:
            ans[mid]=np.exp(np.interp(b,_ETA,tab[int(round(q[0]))]))
            return ans.reshape(shape)
        base=np.clip(np.floor(q).astype(int)-1,0,len(_JG)-4);t=q-base
        h=np.clip(np.searchsorted(_ETA,b,side='right')-1,0,len(_ETA)-2)
        w=(b-_ETA[h])/(_ETA[h+1]-_ETA[h]);val=np.zeros_like(a)
        coeff=[-(t-1)*(t-2)*(t-3)/6.,t*(t-2)*(t-3)/2.,-t*(t-1)*(t-3)/2.,t*(t-1)*(t-2)/6.]
        for k in range(4):val+=coeff[k]*(tab[base+k,h]*(1-w)+tab[base+k,h+1]*w)
        ans[mid]=np.exp(val)
    return ans.reshape(shape)

def Nc(T,m):
    return 2.*(2.*np.pi*np.asarray(m,float)*ME*KBJ*np.asarray(T,float)/HPL**2)**1.5

def dens(eta,T,m):return Nc(T,m)*2./np.sqrt(np.pi)*F(.5,eta)

def solve_eta(T,N_net,m_maj,m_min,Eg):
    T,N_net,m_maj,m_min,Eg=np.broadcast_arrays(*[np.asarray(v,float) for v in (T,N_net,m_maj,m_min,Eg)])
    if np.any(T<=0) or np.any(N_net<=0) or np.any(m_maj<=0) or np.any(m_min<=0) or np.any(Eg<0):
        raise ValueError('T, N_net and masses must be positive; Eg must be nonnegative')
    g=Eg/(KB_EV*T)
    def net(eta):return dens(eta,T,m_maj)-dens(-eta-g,T,m_min)
    lo,hi=np.full(T.shape,-40.),np.full(T.shape,40.)
    for _ in range(12):
        left,right=net(lo)>N_net,net(hi)<N_net
        if not (np.any(left) or np.any(right)):break
        lo=np.where(left,lo*2.,lo);hi=np.where(right,hi*2.,hi)
    else:raise ArithmeticError('Could not bracket charge neutrality')
    for _ in range(60):
        mid=(lo+hi)/2.;left=net(mid)<N_net
        lo=np.where(left,mid,lo);hi=np.where(left,hi,mid)
    eta=(lo+hi)/2.;p,n=dens(eta,T,m_maj),dens(-eta-g,T,m_min)
    tol=1e-8*N_net+32*np.finfo(float).eps*(p+n)
    if np.any(np.abs(p-n-N_net)>tol):raise ArithmeticError('Charge-neutrality residual exceeds tolerance')
    return eta,-eta-g

def band(eta,r=-.5):
    eta,r=np.broadcast_arrays(np.asarray(eta,float),np.asarray(r,float))
    a,b,c=F(r+.5,eta),F(r+1.5,eta),F(r+2.5,eta)
    den=np.maximum((r+1.5)*a,1e-300);m1=(r+2.5)*b/den
    S=KB_E*(m1-eta);L=KB_E**2*((r+3.5)*c/den-m1*m1)
    low=eta < -20.
    S=np.where(low,KB_E*(r+2.5-eta),S);L=np.where(low,KB_E**2*(r+2.5),L)
    if np.any(L<=0) or not np.all(np.isfinite(L)):raise ArithmeticError('Nonpositive or nonfinite band Lorenz number')
    return den,S,L

def mobility(eta,T,mu300,p_mu,r=-.5):
    eta,T,mu300,p_mu,r=np.broadcast_arrays(*[np.asarray(v,float) for v in (eta,T,mu300,p_mu,r)])
    shape=F(r+.5,eta)/np.maximum(F(.5,eta),1e-300)*gamma(1.5)/gamma(r+1.5)
    shape=np.where(eta < -20.,1.,shape)
    return mu300*1e-4*(T/300.)**p_mu*shape

def forward(T,N_net,m_maj,m_min,mu300,p_mu,Eg,A,w,r=-.5,ptype=True,kmin=0.,minority_mobility_ratio=1.):
    """Complete model. N in cm^-3; masses in m_e; mu300 in cm2/V/s.

    The optional lattice floor is included in kappa_L, total kappa and zT.
    Minority mobility ratio differs from unity only in explicit stress tests.
    """
    T,N_net,m_maj,m_min,mu300,p_mu,Eg,A,w,r,kmin,ratio=np.broadcast_arrays(*[
        np.asarray(v,float) for v in (T,N_net,m_maj,m_min,mu300,p_mu,Eg,A,w,r,kmin,minority_mobility_ratio)])
    if np.any(A<=0) or np.any(kmin<0) or np.any(mu300<=0) or np.any(ratio<=0):
        raise ValueError('Amplitude/mobilities must be positive and kmin nonnegative')
    ep,en=solve_eta(T,N_net*1e6,m_maj,m_min,Eg)
    p,n=dens(ep,T,m_maj),dens(en,T,m_min)
    sp=QE*p*mobility(ep,T,mu300,p_mu,r);sn=QE*n*mobility(en,T,mu300,p_mu,r)*ratio;sig=sp+sn
    _,Sp,Lp=band(ep,r);_,Sn,Ln=band(en,r);sgn=np.where(np.asarray(ptype),1.,-1.)
    S=sgn*(sp*Sp-sn*Sn)/sig;ke=(Lp*sp+Ln*sn)*T;kb=(sp*sn/sig)*(Sp+Sn)**2*T
    kl=kmin+A*(300./T)**w;kap=ke+kb+kl
    return dict(T=T,sigma=sig,S=S,kappa=kap,kappa_e=ke,kappa_bip=kb,kappa_L=kl,p=p,n=n,eta_p=ep,eta_n=en,zT=S*S*sig*T/kap)

def forward_theta(theta,T,ptype=None,**kwargs):
    """Batch wrapper: theta (n,10 or 11), T (n,g) or (g,)."""
    th=np.atleast_2d(np.asarray(theta,float))
    if th.shape[1] not in (10,11):raise ValueError('Expected ten continuous parameters plus optional sign')
    if ptype is None:ptype=th[:,10]>.5 if th.shape[1]==11 else np.ones(len(th),bool)
    pp=np.asarray(ptype).reshape(-1,1);v=[th[:,k,None] for k in range(10)]
    return forward(np.asarray(T,float),10**v[0],10**v[1],10**v[2],10**v[3],v[4],10**v[5],10**v[6],v[7],r=v[8],ptype=pp,kmin=v[9],**kwargs)

def L_kim(S):return (1.5+np.exp(-np.abs(np.asarray(S,float))*1e6/116.))*1e-8
