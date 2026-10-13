"""Version 6 research variants. The released v5 modules and results stay intact.

The extra channel is not labelled lattice. The positive PCHIP lattice has no
monotonicity constraint. Independent band parameters are inferred in mobility
variants. Priors are explicit research choices, not established physical bounds.
"""
from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import time
import numpy as np
from scipy.interpolate import PchipInterpolator
from . import temodel as tm, prior as base

VERSION = '6.0.1-research'
VARIANTS = ('baseline', 'mobility', 'extra', 'mobility_extra', 'spline', 'mobility_spline')
KNOTS = np.array([285., 400., 550., 750., 1000., 1250.])
CHANNELS = ['sigma', 'S_uVK', 'kappa', 'kappa_L', 'kappa_bip', 'Luni', 'kappa_e', 'kappa_extra']
TRUTH_CHANNELS = ['kappa_L', 'kappa_bip', 'Luni', 'kappa', 'kappa_extra']


@dataclass(frozen=True)
class Spec:
    name: str
    lattice_min: float = .001
    lattice_max: float = 100.

    def __post_init__(self):
        if self.name not in VARIANTS:
            raise ValueError(self.name)
        if not 0 < self.lattice_min < self.lattice_max:
            raise ValueError('Invalid lattice prior support')

    @classmethod
    def from_metadata(cls, metadata):
        """Rehydrate support from its checkpoint, including the initial v6 pilot."""
        name=metadata['variant']
        limits=metadata.get('spline_limits')
        if limits is None and 'spline' in name:
            j=metadata['names'].index('log10kL_285')
            limits=[10.**metadata['lower'][j],10.**metadata['upper'][j]]
        spec=cls(name,*(limits or [.001,100.]))
        if spec.names != metadata['names']:
            raise ValueError('Checkpoint parameter names do not match supported schema')
        return spec

    @property
    def independent(self):
        return self.name.startswith('mobility')

    @property
    def spline(self):
        return 'spline' in self.name

    @property
    def extra(self):
        return 'extra' in self.name

    @property
    def names(self):
        names = list(base.NAMES)
        if self.spline:
            names = [n for n in names if n not in ('log10A', 'w', 'kmin')]
            names += [f'log10kL_{int(t)}' for t in KNOTS]
        if self.independent:
            names += ['log10mobility_ratio', 'p_mu_min', 'r_min']
        if self.extra:
            names += ['B_extra']
        return names

    @property
    def dim(self):
        return len(self.names)

    def bounds(self):
        lookup = {n: (lo, hi) for n, lo, hi in zip(base.NAMES, base.LOW, base.HIGH)}
        lookup.update({f'log10kL_{int(t)}': (np.log10(self.lattice_min), np.log10(self.lattice_max)) for t in KNOTS})
        lookup.update(log10mobility_ratio=(-1., 1.), p_mu_min=(-3.5, 2.),
                      r_min=(-1., 2.), B_extra=(0., .05))
        return np.array([lookup[n] for n in self.names]).T

    def metadata(self):
        lo, hi = self.bounds()
        return dict(version=VERSION, variant=self.name, names=self.names,
                    lower=[None if np.isnan(v) else float(v) for v in lo],
                    upper=[None if np.isnan(v) else float(v) for v in hi],
                    conditional_mu='3.1 - 0.5*(log10N_net-17) + Uniform(-1.8,1.2)',
                    spline_knots=KNOTS.tolist() if self.spline else None,
                    spline_limits=[self.lattice_min,self.lattice_max] if self.spline else None,
                    spline='PCHIP(log10(kL)) versus log(T), independent uniform node priors' if self.spline else None,
                    extra='B_extra*(T/300)^3, separate from lattice' if self.extra else None,
                    noise=base.NOISE, zT_max=base.ZT_MAX)


def in_box(theta, spec):
    th = np.asarray(theta, float)
    if th.shape[-1] not in (spec.dim, spec.dim+1):
        raise ValueError('Parameter dimension does not match variant')
    v = th[..., :spec.dim]
    lo, hi = spec.bounds()
    ok = np.isfinite(th).all(-1)
    for j, name in enumerate(spec.names):
        a, b = lo[j], hi[j]
        if name == 'log10mu300':
            c = 3.1-.5*(v[..., 0]-17.)
            a, b = c-1.8, c+1.2
        ok &= (v[..., j] >= a) & (v[..., j] <= b)
    if th.shape[-1] == spec.dim+1:
        ok &= (th[..., -1] == 0) | (th[..., -1] == 1)
    return ok


def sample_box(n, rng, spec):
    original, loT, hiT = base.sample_box(n, rng)
    values = {name: original[:, j] for j, name in enumerate(base.NAMES)}
    low, high = spec.bounds()
    for j, name in enumerate(spec.names):
        if name not in values:
            values[name] = rng.uniform(low[j], high[j], n)
    th = np.column_stack([values[n] for n in spec.names] + [original[:, 10]])
    return th, loT, hiT


def positive_lattice(nodes, T):
    """Vectorised row-wise PCHIP; exponentiating guarantees positivity."""
    T = np.asarray(T, float)
    if np.any((T < KNOTS[0]-1e-8) | (T > KNOTS[-1]+1e-8)):
        raise ValueError('Spline evaluation outside declared temperature support')
    logt, knots = np.log(T), np.log(KNOTS)
    curve = PchipInterpolator(knots, np.asarray(nodes), axis=1, extrapolate=False)
    ix = np.clip(np.searchsorted(knots, logt, side='right')-1, 0, len(knots)-2)
    row = np.arange(len(nodes))[:, None]
    dx = logt-knots[ix]
    c = curve.c
    y = ((c[0, ix, row]*dx+c[1, ix, row])*dx+c[2, ix, row])*dx+c[3, ix, row]
    return 10.**y


def forward(theta, T, spec, ptype=None):
    th = np.atleast_2d(np.asarray(theta, float))
    if th.shape[1] not in (spec.dim, spec.dim+1):
        raise ValueError('Parameter dimension does not match variant')
    if ptype is None:
        if th.shape[1] != spec.dim+1:
            raise ValueError('Explicit carrier sign is required')
        ptype = th[:, -1] > .5
    T = np.broadcast_to(np.asarray(T, float), (len(th), np.asarray(T).shape[-1]))
    v = {n: th[:, j, None] for j, n in enumerate(spec.names)}
    o = tm.forward(T, 10**v['log10N_net'], 10**v['log10m_maj'], 10**v['log10m_min'],
                   10**v['log10mu300'], v['p_mu'], 10**v['log10Eg'],
                   10**v.get('log10A', np.zeros((len(th), 1))), v.get('w', 1.),
                   r=v['r'], ptype=np.asarray(ptype)[:, None], kmin=v.get('kmin', 0.))
    if spec.independent:
        ep, en = o['eta_p'], o['eta_n']
        sp = tm.QE*o['p']*tm.mobility(ep, T, 10**v['log10mu300'], v['p_mu'], v['r'])
        sn = tm.QE*o['n']*tm.mobility(en, T, 10**(v['log10mu300']+v['log10mobility_ratio']),
                                    v['p_mu_min'], v['r_min'])
        _, Sp, Lp = tm.band(ep, v['r'])
        _, Sn, Ln = tm.band(en, v['r_min'])
        sig = sp+sn
        o['sigma'] = sig
        o['S'] = np.where(np.asarray(ptype)[:, None], 1., -1.)*(sp*Sp-sn*Sn)/sig
        o['kappa_e'] = (Lp*sp+Ln*sn)*T
        o['kappa_bip'] = sp*sn/sig*(Sp+Sn)**2*T
    if spec.spline:
        nodes = th[:, [spec.names.index(f'log10kL_{int(t)}') for t in KNOTS]]
        o['kappa_L'] = positive_lattice(nodes, T)
    o['kappa_extra'] = v.get('B_extra', 0.)*(T/300.)**3
    o['kappa'] = o['kappa_e']+o['kappa_bip']+o['kappa_L']+o['kappa_extra']
    o['zT'] = o['S']**2*o['sigma']*T/o['kappa']
    if not all(np.isfinite(o[k]).all() for k in ('sigma','S','kappa','zT')):
        raise ArithmeticError('Nonfinite relaxed forward result')
    return o


def channel_array(o, T):
    return np.stack([o['sigma'], o['S']*1e6, o['kappa'], o['kappa_L'], o['kappa_bip'],
                     o['kappa_e']/(o['sigma']*T), o['kappa_e'], o['kappa_extra']], axis=1)


def generate(n, seed, path, spec, batch=4096, narrow=False):
    rng = np.random.default_rng(seed)
    xs, ts, truths = [], [], []
    got = attempts = rejected = 0
    t0 = time.time()
    while got < n:
        th, lo, hi = sample_box(batch, rng, spec)
        if narrow:
            th[:, spec.names.index('log10Eg')] = rng.uniform(-1., np.log10(.5), batch)
        ng = rng.integers(8, 21, batch)
        x = np.empty((batch, 50)); truth = np.empty((batch, 5, 16)); ok = np.zeros(batch, bool)
        for count in range(8, 21):
            ids = np.flatnonzero(ng == count)
            if not len(ids):
                continue
            T = np.linspace(lo[ids], hi[ids], count, axis=1)
            o = forward(th[ids], T, spec)
            noisy = [o[k]*np.exp(rng.normal(0, base.NOISE, o[k].shape)) for k in ('sigma','S','kappa')]
            x[ids, :16] = np.log10(base.interpolate_uniform(noisy[0]))
            x[ids, 16:32] = base.interpolate_uniform(noisy[1])*1e6
            x[ids, 32:48] = np.log(base.interpolate_uniform(noisy[2]))
            x[ids, 48], x[ids, 49] = hi[ids]/1000, lo[ids]/1000
            Tg = np.linspace(lo[ids], hi[ids], 16, axis=1)
            t = forward(th[ids], Tg, spec)
            ok[ids] = np.max(t['zT'], axis=1) <= base.ZT_MAX
            truth[ids] = np.stack([t['kappa_L'],t['kappa_bip'],t['kappa_e']/(t['sigma']*Tg),t['kappa'],t['kappa_extra']],axis=1)
        if not np.isfinite(x).all():
            raise ArithmeticError('Nonfinite observation')
        take = min(n-got, int(ok.sum()))
        xs.append(x[ok][:take]); ts.append(th[ok][:take]); truths.append(truth[ok][:take])
        got += take; attempts += batch; rejected += int((~ok).sum())
        if got % 50000 < batch or got == n:
            print(f'{spec.name}: generated {got}/{n}, {time.time()-t0:.1f}s', flush=True)
    meta = dict(spec=spec.metadata(), seed=seed, n=n, attempts=attempts, rejected_zT=rejected,
                narrow=narrow, seconds=time.time()-t0, truth_channels=TRUTH_CHANNELS)
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, theta=np.concatenate(ts).astype('f4'), x=np.concatenate(xs).astype('f4'),
                        truth=np.concatenate(truths).astype('f4'), metadata=np.array(json.dumps(meta)))
    path.with_suffix('.json').write_text(json.dumps(meta, indent=2))
    return meta


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()
