"""Readable tables for the released family and sensitivity calculations."""
import argparse,json
from pathlib import Path


def value(v):
    if any(x is None for x in v):return 'not estimable'
    return f'{v[0]:.3f} [{v[1]:.3f}, {v[2]:.3f}]'


def main():
    ap=argparse.ArgumentParser();ap.add_argument('run',type=Path);a=ap.parse_args()
    m=json.loads((a.run/'manifest.json').read_text())
    lines=['# Supplementary corpus comparisons','',
        'All shifts are medians of per-curve slope differences over 400–750 K. Brackets give 95% paper-clustered intervals. Selections require all five positive-endpoint estimates and admission, except the explicitly varied containment threshold. Family tables retain groups with at least 80 selected curves. The comparisons are descriptive and do not establish experimental channel truth.','']
    for name in m['variants']:
        d=json.loads((a.run/name/'supplementary_analysis.json').read_text());lines += [f'## {name}','']
        for key,title in [('families','Material families'),('strata','Inferred bipolar-share strata'),('rollover','Seebeck rollover'),('screen_thresholds','Containment threshold')]:
            lines += [f'### {title}','','| Group | Curves | Papers | C minus B | C minus A | Cprime_all minus A |','|---|---:|---:|---:|---:|---:|']
            for label,g in d[key].items():
                lines.append(f"| {label} | {g['n']} | {g['papers']} | {value(g['C_B'])} | {value(g['C_A'])} | {value(g['Cprime_all_A'])} |")
            lines.append('')
        lines+=['Negative conventional remainder at any point in the observed window:','', '| Population | Negative curves | Denominator |','|---|---:|---:|']
        for label,g in d['negative_conventional_remainder'].items():lines.append(f"| {label} | {g['n']} | {g['denominator']} |")
        lines.append('')
    lines+=['Bipolar strata use the median inferred bipolar heat divided by observed total heat at 750 K. Labels below_2, 2_to_10 and 10_to_100 refer to percentages. Rollover labels refer to the percentage decrease in absolute Seebeck coefficient after an interior maximum; none means no interior maximum. These ratios are distinct from the separately saved matched-draw model fractions.','']
    (a.run/'SUPPLEMENTARY_RESULTS.md').write_text('\n'.join(lines),encoding='utf-8')
    print(a.run/'SUPPLEMENTARY_RESULTS.md')


if __name__=='__main__':main()
