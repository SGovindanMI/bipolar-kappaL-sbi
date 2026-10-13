"""Legacy sampled numerical check, NOT an exhaustive provenance certificate.

Use combined/audit_starrydata.py for paper/sample identity, units, ambiguous
temperatures, full-corpus comparisons and recorded source hashes. See
docs/STARRYDATA_AUDIT.md for demonstrated historical mixed-paper joins.

This does not trust any intermediate file. It reads the raw Starrydata CSV, rebuilds
the feature vectors from scratch, and compares them to the released arrays.

    python src/verify_provenance.py --csv path/to/starrydata_curves.csv

Checks performed:
  1. the export's schema matches the documented Starrydata curve export
  2. every DOI is structurally valid and the registrant mix is reported
  3. a random sample of curves is rebuilt from the CSV and compared to
     data/real_analysis_set.npz, element by element
  4. units are reported in physical terms so they can be eyeballed
"""
import argparse, json, pickle, re
from pathlib import Path
from collections import defaultdict

import numpy as np

NG = 16
EXPECTED_COLUMNS = {'SID', 'DOI', 'composition', 'sample_id', 'figure_id', 'figure_name',
                    'prop_x', 'prop_y', 'unit_x', 'unit_y', 'x', 'y',
                    'created_at', 'updated_at', 'project_names', 'comments'}
PROP = {'Seebeck coefficient': 'S', 'Electrical conductivity': 'sig',
        'Electrical resistivity': 'rho', 'Thermal conductivity': 'kap',
        'ZT': 'zt', 'Lattice thermal conductivity': 'kL'}


def main():
    import pandas as pd
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', required=True)
    ap.add_argument('--data', default=str(Path(__file__).resolve().parents[1]/'data/real_analysis_set.npz'))
    ap.add_argument('--n', type=int, default=300, help='curves to re-derive')
    a = ap.parse_args()

    c = pd.read_csv(a.csv)
    try:
        from .build_corpus import validate_identity
    except ImportError:
        from build_corpus import validate_identity
    validate_identity(c)
    source=np.load(a.data,allow_pickle=True)
    actual=c.groupby('sample_id').DOI.first().to_dict()
    mismatch=[int(s) for s,d in zip(source['sid'],source['doi'])
              if str(actual.get(s,'')).strip().lower()!=str(d).strip().lower()]
    if mismatch:
        raise ValueError(f'{len(mismatch)} frozen sample/paper pairs differ from this export; use the exhaustive audit.')
    print('LEGACY SAMPLED CHECK ONLY: does not establish exhaustive source provenance.')
    print('1. SCHEMA')
    cols = set(c.columns)
    print('   columns match the documented Starrydata export:', cols == EXPECTED_COLUMNS)
    if cols != EXPECTED_COLUMNS:
        print('   unexpected:', cols - EXPECTED_COLUMNS, ' missing:', EXPECTED_COLUMNS - cols)
    tagged = c.project_names.fillna('').str.contains('ThermoelectricMaterials').mean()
    print('   rows tagged ThermoelectricMaterials: %.1f%%' % (100 * tagged))
    tz = c.created_at.str.extract(r'\(([^)]*)\)')[0].value_counts()
    print('   record timestamps, timezone:', dict(tz.head(2)))
    d = pd.to_datetime(c.created_at.str.slice(4, 24), format='%b %d %Y %H:%M:%S', errors='coerce')
    print('   record dates: %s to %s' % (d.min().date(), d.max().date()))

    print('\n2. DOIs')
    dois = c.DOI.dropna().unique()
    bad = [x for x in dois if not re.match(r'^10\.\d{4,9}/\S+$', str(x))]
    print('   %d unique DOIs, %d structurally invalid' % (len(dois), len(bad)))
    pref = pd.Series([str(x).split('/')[0] for x in dois]).value_counts().head(6)
    print('   top registrants:', dict(pref))

    print('\n3. RE-DERIVATION FROM THE RAW CSV')
    cT = c[(c['prop_x'].isin(['Temperature', 'T'])) & (c['unit_x'] == 'K')]
    cT = cT[cT['prop_y'].isin(PROP)]
    D = defaultdict(dict)
    for r in cT.itertuples():
        try:
            x = np.array(json.loads(r.x), float); y = np.array(json.loads(r.y), float)
        except Exception:
            continue
        if len(x) != len(y) or len(x) < 5:
            continue
        k = PROP[r.prop_y]
        if k in D[r.sample_id]:
            continue
        i = np.argsort(x); D[r.sample_id][k] = (x[i], y[i])

    A = np.load(a.data, allow_pickle=True)
    X, sid, Tlo, Thi = A['x'], A['sid'], A['Tlo'], A['Thi']
    present = np.array([s in D for s in sid])
    print('   released sample_ids present in this export: %d / %d' % (present.sum(), len(sid)))

    rng = np.random.default_rng(3)
    pool = np.flatnonzero(present)
    if not len(pool):raise ValueError('No compatible sample identifiers in this export')
    idxs = rng.choice(pool, min(a.n, len(pool)), replace=False)
    absdiff = []
    for j in idxs:
        d = D[sid[j]]
        T = np.linspace(Tlo[j], Thi[j], NG)
        S = np.interp(T, *d['S']) * 1e6
        kap = np.interp(T, *d['kap'])
        with np.errstate(all='ignore'):
            sig = np.interp(T, *d['sig']) if 'sig' in d else 1.0 / np.interp(T, *d['rho'])
            got = np.concatenate([np.log10(sig), S, np.log(kap)])
        absdiff.append(np.nanmax(np.abs(got - X[j, :3 * NG])))
    absdiff = np.array(absdiff)
    big = (absdiff > 1e-3).sum()
    print('   %d curves re-derived from the CSV' % len(absdiff))
    print('   max absolute difference vs released features: median %.1e  worst %.1e'
          % (np.median(absdiff), absdiff.max()))
    print('   curves differing by more than 1e-3 in any feature: %d (%.2f%%)'
          % (big, 100 * big / len(absdiff)))
    print('''
   Expected behaviour. The released window endpoints are stored as float64 with float32-quantised
   endpoint values, so the 16-point grid cannot be reconstructed to better than about
   1e-5 K. For almost every curve that is irrelevant (median agreement ~1e-5),
   but a handful of curves have digitised points so closely spaced that a shift
   of 1e-5 K lands on the other side of a kink and changes one interpolated
   value by a few units. The original release reported 6 such curves in 13,256; this script
   does not assume that count for a new export.
   real_analysis_set.npz is the authoritative array; this script checks that it
   was derived from the public CSV, not that the CSV can regenerate it bitwise.''')
    verdict = 'PASS' if (np.median(absdiff) < 1e-3 and big <= 0.01 * len(absdiff)) else 'FAIL'
    print('   VERDICT:', verdict)
    if verdict!='PASS':raise AssertionError('Raw feature comparison failed')

    print('\n4. UNITS')
    S_all = X[:, NG:2 * NG]; sig_all = 10 ** X[:, :NG]; kap_all = np.exp(X[:, 2 * NG:3 * NG])
    print('   |S|    median %7.1f uV/K     max %7.1f' % (np.nanmedian(np.abs(S_all)), np.nanmax(np.abs(S_all))))
    print('   sigma  median %7.1e S/m      1st-99th %.1e to %.1e'
          % (np.nanmedian(sig_all), np.nanpercentile(sig_all, 1), np.nanpercentile(sig_all, 99)))
    print('   kappa  median %7.2f W/m/K    1st-99th %.2f to %.2f'
          % (np.nanmedian(kap_all), np.nanpercentile(kap_all, 1), np.nanpercentile(kap_all, 99)))


if __name__ == '__main__':
    main()
