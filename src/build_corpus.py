"""Rebuild the analysis corpus from the public Starrydata export.

This script documents and reproduces the path from the raw Starrydata CSV to the
13,256-curve analysis set used in the paper. Historical counts below are legacy
documentation, not a newly verified source-selection history. For the exhaustive
current export audit, use combined/audit_starrydata.py and read
docs/STARRYDATA_AUDIT.md. Reconstruction fails on ambiguous paper/sample joins.

    python src/build_corpus.py --csv path/to/starrydata_curves.csv

The export is not redistributed here. Download it yourself from
https://starrydata.nims.go.jp/ (Download / API page), choosing the
ThermoelectricMaterials project curve export.

----------------------------------------------------------------------------
Provenance chain (counts from the snapshot used in the paper, which contains
records created up to 2026-07-15):

    155,638   digitised curves in the export
    122,573   a transport property plotted against temperature in kelvin
     45,389   samples, after grouping and keeping one curve per property
     17,821   samples carrying S, kappa and either sigma or rho
     13,922   whose analysis window spans >= 200 K
     13,853   finite throughout, with positive sigma and kappa
     13,796   whose window ends at or below 1250 K
     13,389   after the remaining plausibility checks of the original pipeline (NOTE)
     13,357   after removing 32 curves with |S| > 3,000 uV/K (unit errors)
     13,256   after restricting to curves beginning at or below 500 K
              -> 2,754 papers

The analysis window of a sample runs from the start of the three curves' common
temperature range -- or from 300 K, if that range begins below it -- to the end of
the common range. The 300 K floor and the 1250 K ceiling were recovered from the
released arrays: window endpoints reproduce to better than 1e-4 K under this rule,
and no released curve ends above 1250 K.

NOTE on the 13,796 -> 13,389 step. The original pipeline applied a further
plausibility filter inside a helper module (`ppc.real_features`) whose source is no
longer present in the project. The 407 samples it removes are mostly very low
conductivity materials (median sigma 616 S/m against 69,000 S/m among those kept),
but the exact rule is not recoverable. The *result* of that step is preserved exactly:
`data/analysis_set_sids.csv` lists the Starrydata sample_id of every curve in
the analysis set. This script therefore reconstructs the corpus by selecting
those sample_ids and rebuilding features from a CSV. The prior sampled numerical
agreement did not establish paper identity: the 2026-10-09 exhaustive audit found
mixed-paper inputs. See docs/STARRYDATA_AUDIT.md. Downstream computation is reproducible from the frozen arrays, subject to
floating-point and device variation; the one lost step is a sample-selection filter whose output is
released rather than recomputed.
----------------------------------------------------------------------------
"""
import argparse, json, os, pickle, hashlib
from pathlib import Path
from collections import defaultdict

import numpy as np

NG = 16                      # points on the resampled temperature grid
MIN_SPAN = 200.0             # K of common range required across the three properties
T_FLOOR = 300.0              # analysis windows do not start below room temperature
T_CEIL = 1250.0              # nor end above this
S_MAX_UV = 3000.0            # |S| above this is a unit error in the source data
TLO_MAX = 500.0              # simulator window (paper, Section 2.3)

PROP = {'Seebeck coefficient': 'S', 'Electrical conductivity': 'sig',
        'Electrical resistivity': 'rho', 'Thermal conductivity': 'kap',
        'ZT': 'zt', 'Lattice thermal conductivity': 'kL'}
EXPECTED_UNITS={'S':'V*K^(-1)','sig':'ohm^(-1)*m^(-1)','rho':'ohm*m',
                'kap':'W*m^(-1)*K^(-1)','zt':'-','kL':'W*m^(-1)*K^(-1)'}


def build_cache(csv_path, cache_path='curves.pkl'):
    """Group the Starrydata export into {sample_id: {property: (T, y)}}."""
    import pandas as pd
    # Cache is tied to CSV content and parser version, never just its filename.
    digest=hashlib.sha256()
    with open(csv_path,'rb') as fh:
        for block in iter(lambda:fh.read(1024*1024),b''):digest.update(block)
    key={'csv_sha256':digest.hexdigest(),'parser_version':4}
    manifest=Path(str(cache_path)+'.json')
    if Path(cache_path).exists() and manifest.exists() and json.loads(manifest.read_text())==key:
        with open(cache_path,'rb') as fh:return pickle.load(fh)
    c = pd.read_csv(csv_path)
    # Affected 2026 exports reused integer IDs across unrelated source papers.
    # This legacy API returns integer-keyed dictionaries, so it MUST fail closed.
    validate_identity(c)
    print('  %7d digitised curves in the export' % len(c))
    cT = c[(c['prop_x'].isin(['Temperature', 'T'])) & (c['unit_x'] == 'K')]
    cT = cT[cT['prop_y'].isin(PROP)]
    print('  %7d a transport property against temperature in K' % len(cT))

    D, meta = defaultdict(dict), {}
    for r in cT.itertuples():
        try:
            x = np.array(json.loads(r.x), float)
            y = np.array(json.loads(r.y), float)
        except Exception:
            continue
        if len(x) != len(y) or len(x) < 5:
            continue
        k = PROP[r.prop_y]
        if not hasattr(r,'unit_y') or r.unit_y!=EXPECTED_UNITS[k]:
            raise ValueError(f'Unexpected or missing unit for {r.prop_y}; explicit conversion is required.')
        if k in D[r.sample_id]:          # keep the first curve for each property
            continue
        i = np.argsort(x)
        D[r.sample_id][k] = (x[i], y[i])
        meta[r.sample_id] = (r.DOI, r.composition)
    print('  %7d samples after grouping' % len(D))
    with open(cache_path,'wb') as fh:pickle.dump((dict(D),meta),fh)
    manifest.write_text(json.dumps(key,indent=2))
    return dict(D), meta


def validate_identity(c):
    paper = 'SID' if 'SID' in c.columns else 'DOI'
    if (c.groupby('sample_id')[paper].nunique(dropna=False) > 1).any():
        raise ValueError('Ambiguous sample_id across papers. Use (SID, sample_id) joins; see docs/STARRYDATA_AUDIT.md.')


def validate_selected(d, actual_doi, expected_doi, lo, hi):
    if str(actual_doi).strip().lower() != str(expected_doi).strip().lower():
        raise ValueError('Source DOI differs from frozen corpus attribution; do not silently rebuild.')
    for k in ['S','kap','sig' if 'sig' in d else 'rho']:
        if k not in d:raise ValueError('Required transport channel is missing.')
        t,y=d[k]
        if not (np.isfinite(t).all() and np.isfinite(y).all()):
            raise ValueError('Nonfinite raw transport curve.')
        if np.any(np.diff(t)<=0):
            raise ValueError('Duplicate raw temperatures require review before rebuilding.')
        if t[0]>lo+1e-4 or t[-1]<hi-1e-4:
            raise ValueError('Frozen window extends outside raw measurement coverage.')


def features(d, lo=None, hi=None):
    """50-vector: log10 sigma, S in uV/K, ln kappa on 16 points, then Thi/1000, Tlo/1000."""
    keys = ['S', 'kap', 'sig' if 'sig' in d else 'rho']
    if lo is None:
        lo = max(d[k][0][0] for k in keys)
        hi = min(d[k][0][-1] for k in keys)
    T = np.linspace(lo, hi, NG)
    S = np.interp(T, *d['S']) * 1e6                        # V/K -> uV/K
    kap = np.interp(T, *d['kap'])
    if 'sig' in d:
        sig = np.interp(T, *d['sig'])                      # S/m
    else:
        with np.errstate(all='ignore'):
            sig = 1.0 / np.interp(T, *d['rho'])            # ohm m -> S/m
    with np.errstate(all='ignore'):
        x = np.concatenate([np.log10(sig), S, np.log(kap),
                            [T[-1] / 1000.0, T[0] / 1000.0]])
    return x, lo, hi, sig, kap, S


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', required=True, help='Starrydata curve export CSV')
    ap.add_argument('--sids', default=str(Path(__file__).resolve().parents[1]/'data/analysis_set_sids.csv'),
                    help='released sample_id list defining the corpus')
    ap.add_argument('--out', default='real_analysis_set_rebuilt.npz')
    a = ap.parse_args()

    print('reading the Starrydata export')
    D, meta = build_cache(a.csv)

    # --- the filters that are fully reproducible from the CSV ---
    triple = {s: d for s, d in D.items()
              if ('sig' in d or 'rho' in d) and 'S' in d and 'kap' in d}
    print('  %7d samples with S, kappa and sigma or rho' % len(triple))

    spans = {}
    for s, d in triple.items():
        keys = ['S', 'kap', 'sig' if 'sig' in d else 'rho']
        lo = max(max(d[k][0][0] for k in keys), T_FLOOR)
        hi = min(d[k][0][-1] for k in keys)
        if hi - lo >= MIN_SPAN:
            spans[s] = (lo, hi)
    print('  %7d with an analysis window of >= %.0f K' % (len(spans), MIN_SPAN))

    valid = {}
    for s, (lo, hi) in spans.items():
        x, lo, hi, sig, kap, S = features(D[s], lo, hi)
        if not np.all(np.isfinite(x)):
            continue
        if np.any(sig <= 0) or np.any(kap <= 0):
            continue
        valid[s] = (x, lo, hi, S)
    print('  %7d finite with positive sigma and kappa' % len(valid))
    valid = {s: v for s, v in valid.items() if v[2] <= T_CEIL}
    print('  %7d with the window ending at or below %.0f K' % (len(valid), T_CEIL))

    # --- the released corpus definition (see NOTE in the module docstring) ---
    import csv as _csv
    want, dois, wins = [], {}, {}
    with open(a.sids) as fh:
        for row in _csv.DictReader(fh):
            sid_ = int(row['sample_id'])
            want.append(sid_)
            dois[sid_] = row['doi']
            wins[sid_] = (float(row['T_lo_K']), float(row['T_hi_K']))
    print('  %7d sample_ids in the released analysis set' % len(want))

    missing = [s for s in want if s not in D]
    if missing:
        print('  WARNING: %d released sample_ids are absent from this export.' % len(missing))
        print('           Your snapshot differs from the one used in the paper;')
        print('           Starrydata grows and is re-curated over time.')

    # rebuild on the recorded window so the output matches the released arrays exactly
    keep, rows, Slist = [], [], []
    for s in want:
        if s not in D:
            continue
        lo, hi = wins[s]
        validate_selected(D[s],meta[s][0],dois[s],lo,hi)
        x, lo, hi, sig, kap, S = features(D[s], lo, hi)
        if not np.all(np.isfinite(x)):
            continue
        keep.append(s); rows.append(x); Slist.append(S)
    X = np.array(rows)
    Tlo = np.array([wins[s][0] for s in keep])
    Thi = np.array([wins[s][1] for s in keep])
    sid = np.array(keep)
    doi = np.array([dois[s] for s in keep])

    # sanity: the two filters the paper states explicitly
    worst_S = np.array([np.abs(v).max() for v in Slist])
    assert worst_S.max() <= S_MAX_UV, 'a unit-error curve survived'
    assert Tlo.max() <= TLO_MAX + 1e-9, 'a curve starts above the simulator window'

    np.savez_compressed(a.out, x=X, Tlo=Tlo, Thi=Thi, sid=sid, doi=doi)
    print('\nwrote %s: %d curves, %d papers' % (a.out, len(X), len(np.unique(doi))))
    print('max |S| among retained curves: %.0f uV/K  (unit-error threshold %.0f)'
          % (worst_S.max(), S_MAX_UV))


if __name__ == '__main__':
    main()
