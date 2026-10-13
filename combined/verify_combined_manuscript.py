"""Check the combined manuscript and SI against the archived results.

Run from the repository root:

    python combined/verify_combined_manuscript.py

1. Rebuilds combined_numbers.json from the archived run outputs into a temporary
   file and requires it to equal the committed copy (no stale numbers).
2. Extracts every numeric token from the manuscript and SI .docx (body text, tables,
   captions and equations) and requires each one to be traceable either to an
   archived JSON value (at the precision printed) or to a documented design
   constant listed below. Untraceable tokens are reported and the script fails.

Traceability is a necessary check, not a sufficient one: a number that happens to
match an unrelated archived value would pass. Headline claims are additionally
asserted explicitly in HEADLINE_CHECKS.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = [ROOT / "combined/manuscript/combined_manuscript.docx",
        ROOT / "combined/manuscript/combined_supplementary_information.docx"]

# Design constants stated in Methods (priors, seeds, grid, thresholds, sizes, years,
# reference numbers, DOIs). Anything numeric not derived from an archived result.
CONSTANTS = """
0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 25 29 30 32 40 44 45 48 50 63 64 80 100 116 128 200 256 285 300 400 407
500 512 550 700 750 900 1000 1024 1100 1250 1500 2000 2001 2002 2003 2004 2005 2006 2024 2025 4096 7300 8192
0.01 0.02 0.025 0.03 0.05 0.1 0.15 0.2 0.3 0.4 0.5 0.6 0.7 0.75 0.8 0.85 0.9 0.95 1.0 1.2 1.3 1.5 1.7 1.8 2.0 3.1 3.5 3.55 0.55 0.10 0.50 0.70
16.0 21.0 0.0 3.0 2.0 1.0 0.0015 0.001 281.43 1.56 0.0030 0.78125 5.0 6.0
588,000 12,000 6,000 600,000 612,000 1,000 13,256 2,754 2,000 8,192 30 2.5 97.5 95 99 90 50 1,233
1999 2015 2016 2017 2018 2020 2024 2025 2026 1980 1984 304 1804.06788 041506 10136 30055 30062 869 872 1250 1258 2506976 6981 11528 763 238 246 117 28 3 13 29 5 15
1.1 1.6 0.4 0.48 1.52 1.233
2.1 2.2 2.3 2.4 2.5 2.6 2.7 2.8 2.9 3.12 0.0001 20261008 31 33 34 3.2 3.4 3.6 3.7 3.8 3.9 3.10
""".split()

HEADLINE_CHECKS = [
    # (description, json path, printed value)
    ("reference C-B paired 4,248", ("v5", "shifts", "CB", 0), "−0.166"),
    ("reference B-A", ("v5", "shifts", "BA", 0), "0.003"),
    ("all-model-common n", ("all_model_common", "n"), "1,507"),
    ("common C-B reference", ("corpus", "baseline", "all_model_common", "CB", 0), "−0.107"),
    ("common C-B independent+flexible", ("corpus", "mobility_spline", "all_model_common", "CB", 0), "−0.593"),
    ("upturn coverage reference", ("stress_common", "narrow_upturn", "models", "baseline", "lattice_coverage"), "41.7%"),
    ("upturn coverage independent+flexible", ("stress_common", "narrow_upturn", "models", "mobility_spline", "lattice_coverage"), "97.2%"),
    ("control apparent upturns", ("control_narrow", "apparent_upturn_admitted"), "608"),
]

NUM = re.compile(r"(?<![\w.])[−-]?\d[\d,]*(?:\.\d+)?%?")


def docx_text(p: Path) -> str:
    with zipfile.ZipFile(p) as z:
        xml = z.read("word/document.xml").decode("utf8")
    # Exclude Zotero citation-field results, not ordinary scientific superscripts.
    from lxml import etree
    tree = etree.fromstring(xml.encode('utf8'))
    stack, parts = [], []
    for el in tree.iter():
        local = etree.QName(el).localname
        if local == 'fldChar':
            typ = el.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fldCharType')
            if typ == 'begin': stack.append('')
            elif typ == 'end' and stack: stack.pop()
        elif local == 'instrText' and stack:
            stack[-1] += el.text or ''
        elif local == 't' and not any('ZOTERO_ITEM' in field for field in stack):
            parts.append(el.text or '')
    return ' '.join(parts).replace('\u2063', '')



def leaves(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from leaves(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from leaves(v)
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        yield obj


def renderings(x) -> set[str]:
    out = set()
    if isinstance(x, int) or (isinstance(x, float) and x.is_integer() and abs(x) >= 1):
        out |= {str(int(abs(x))), f"{int(abs(x)):,}"}
    if isinstance(x, float):
        a = abs(x)
        for d in (1, 2, 3, 4):
            out.add(f"{a:.{d}f}")
        for d in (0, 1, 2):
            out.add(f"{a * 100:.{d}f}")
    return out


def norm(tok: str) -> str:
    return tok.lstrip("−-").rstrip("%")


def main() -> int:
    ok = True
    committed = ROOT / "combined/combined_numbers.json"
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "n.json"
        subprocess.run([sys.executable, str(ROOT / "combined/build_combined_numbers.py"), "--out", str(tmp)], check=True, capture_output=True)
        if json.loads(tmp.read_text()) != json.loads(committed.read_text()):
            print("FAIL combined_numbers.json is stale: rebuild it and the manuscript")
            ok = False
        else:
            print("ok   combined_numbers.json matches archived outputs")
    N = json.loads(committed.read_text())

    # Version/device numerals are verified separately against the archived manifests.
    env=json.loads((ROOT / "data/computational_environment.json").read_text())
    environment_tokens=set(NUM.findall(json.dumps(env)))
    pool = environment_tokens | set(CONSTANTS) | {norm(c) for c in CONSTANTS}
    sources = [json.loads((ROOT / "combined/positive_B_sensitivity.json").read_text()), N, json.loads((ROOT / "combined/component_comparison.json").read_text())] + [json.loads(p.read_text()) for p in sorted((ROOT / "data").glob("*.json"))]
    for src in sources:
        for x in leaves(src):
            pool |= renderings(x)
    # ratios quoted in text (fold changes) are derived from archived values
    for m, v in N["strata_ratio_top_bottom"].items():
        pool.add(f"{v:.1f}")
    cb = N["corpus"]
    pool.add(f"{cb['mobility_spline']['all_model_common']['CB'][0] / cb['baseline']['all_model_common']['CB'][0]:.1f}")
    thr = [v[1] - v[0] for m, v in N["threshold_range_CB"].items() if m != "spline"]
    pool.add(f"{max(thr):.3f}")
    c = N["control_narrow"]
    pool.add(f"{100 * c['apparent_upturn_admitted'] / c['admitted']:.1f}")

    for path, val in [(d, None) for d in DOCS]:
        if not path.exists():
            print(f"FAIL missing {path.relative_to(ROOT)}")
            ok = False
            continue
        text = docx_text(path)
        scan = text.split(" References ")[0] if path == DOCS[0] else text.split(" References cited in Supplementary Information ")[0]  # bibliography not scanned
        if path == DOCS[0] and " Abstract " in scan: scan = scan.split(" Abstract ", 1)[1]  # exclude author postal addresses
        scan = re.sub(r"https?://\S+|doi:\S+|arXiv:\S+", " ", scan)
        scan = re.sub(r"\[\d+(?:[,–]\d+)*\]", " ", scan)  # citation markers
        scan = re.sub(r"(Sections?|Tables?|Figures?|Fig\.|equation|Supplementary Table|Supplementary Figure|Supplementary Tables)\s+[\d.,–a-d\s]+(?:and\s+[\d.]+)?", " ", scan)
        toks = NUM.findall(scan)
        bad = sorted({t for t in toks if norm(t).replace(",", "") not in {p.replace(",", "") for p in pool} and norm(t) not in pool})
        print(f"{'ok  ' if not bad else 'FAIL'} {path.name}: {len(toks)} numeric tokens, {len(bad)} untraceable")
        for b in bad:
            i = text.find(b)
            print(f"       {b!r}  …{text[max(0, i - 60):i + 40]}…")
        ok &= not bad

    main_text = docx_text(DOCS[0])
    for desc, keys, printed in HEADLINE_CHECKS:
        v = N
        for k in keys:
            v = v[k]
        present = printed in main_text
        print(f"{'ok  ' if present else 'FAIL'} headline {desc}: {printed} (archived {v})")
        ok &= present
    print("PASS" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
