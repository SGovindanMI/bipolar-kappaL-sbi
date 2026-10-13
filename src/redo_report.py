"""Build a transparent status/results report from completed v6 stage artifacts."""
import argparse
import json
from pathlib import Path


def number(value,digits=3):
    return 'unavailable' if value is None else f'{value:.{digits}f}'


def main():
    p=argparse.ArgumentParser();p.add_argument('run',type=Path);a=p.parse_args()
    manifest=json.loads((a.run/'manifest.json').read_text())
    state=json.loads((a.run/'status.json').read_text())
    lines=['# Extended transport model rerun', '',
           f"Run mode: **{manifest['mode']}**. Computational status: **{state['status']}**.", '',
           'These are conditional model comparisons. A completed run does not establish identifiability or calibrated uncertainty.', '',
           '## Independent same-model synthetic tests', '',
           '| Model | Test curves | Scored | Admitted | Lattice coverage | Bipolar coverage | Lattice median absolute relative error |',
           '|---|---:|---:|---:|---:|---:|---:|']
    for variant in manifest['variants']:
        path=a.run/variant/'test_diagnostics.json'
        if not path.exists():
            lines.append(f'| {variant} | pending | | | | | |');continue
        d=json.loads(path.read_text());sc=d['scored'];ad=d['admitted'];ch=sc.get('channels',{})
        lines.append(f"| {variant} | {d['n']} | {sc['n']} | {ad['n']} | {number(100*ch['lattice']['coverage'],1) if ch else 'unavailable'}% | {number(100*ch['bipolar']['coverage'],1) if ch else 'unavailable'}% | {number(ch['lattice']['median_absolute_relative_error']) if ch else 'unavailable'} |")
    lines += ['', 'Coverage is nominal 95% pointwise coverage conditional on scored curves. Relative errors exclude truth values at or below 1e-12 and report the included point count in the detailed JSON.', '',
              '## Shared narrow-gap lattice-upturn stress test', '',
              '| Model | Scored | Admitted | Lattice coverage | Bipolar coverage | Median fixed-window lattice slope error | Four-estimate subset n |',
              '|---|---:|---:|---:|---:|---:|---:|']
    for variant in manifest['variants']:
        path=a.run/variant/'narrow_upturn_diagnostics.json'
        if not path.exists():
            lines.append(f'| {variant} | pending | | | | | |');continue
        d=json.loads(path.read_text());sc=d['scored'];ad=d['admitted'];ch=sc.get('channels',{});sl=ad.get('slope',{}).get('original_four',{})
        lines.append(f"| {variant} | {sc['n']} | {ad['n']} | {number(100*ch['lattice']['coverage'],1) if ch else 'unavailable'}% | {number(100*ch['bipolar']['coverage'],1) if ch else 'unavailable'}% | {number(sl.get('median_error'))} | {sl.get('n',0)} |")
    lines += ['', '## Frozen experimental corpus', '',
              '| Model | Admitted | Native paired | Baseline-common paired | Native C-minus-B shift | Common C-minus-B shift |',
              '|---|---:|---:|---:|---:|---:|']
    for variant in manifest['variants']:
        path=a.run/variant/'real_summary.json'
        if not path.exists():
            lines.append(f'| {variant} | pending | | | | |');continue
        d=json.loads(path.read_text());n=d['native'];c=d['common_baseline']
        lines.append(f"| {variant} | {d['admitted']} | {n['n']} | {c['n']} | {number(n['shifts']['C_B'][0])} | {number(c['shifts']['C_B'][0])} |")
    lines += ['', 'Native populations can change with the model and endpoint masks. The common subset additionally requires baseline admission and finite baseline estimates. Detailed JSON includes paper-clustered intervals and a nested interval; these do not include physical-model uncertainty.', '',
              '## Interpretation requirements', '',
              '- Review undercoverage and unscored cases before interpreting experimental posterior intervals.',
              '- Compare native and common populations; do not attribute selection-induced changes solely to physical decomposition.',
              '- Keep the extra rising channel distinct from lattice heat.',
              '- Treat flexible-lattice results as sensitive to knot placement and node priors until those alternatives are tested.',
              '- Retain external-validation and non-parabolic-band limitations.',
              '- Pilot results cannot replace production manuscript results.', '']
    (a.run/'RESULTS.md').write_text('\n'.join(lines),encoding='utf-8')
    print(a.run/'RESULTS.md')


if __name__=='__main__':main()
