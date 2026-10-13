"""Split the working tree into a GitHub code repository and a data deposit.

Run from the repository root:

    python tools/package_release.py            # dry run: size report and checksum check
    python tools/package_release.py --write    # copy files / build the zip under work/release

GitHub tree  (work/release/github/bipolar-kappaL-sbi/)
    source, tests, notebooks, docs, combined/ (manuscript, figures, numbers, scripts),
    checkpoints (*.pt, < 1 MB each), small JSON/Markdown/CSV summaries and the
    narrow-gap fixtures (experiments/fixtures/*.npz, 16 MB, needed to rebuild the
    manuscript numbers without the data deposit). Every file must be below --max-github-mb (default 50 MB;
    GitHub rejects files above 100 MB and warns above 50 MB).

Data deposit (work/release/data/bipolar-kappaL-sbi-data.zip, e.g. for Zenodo)
    every *.npz array (inference outputs, test and stress sets, frozen corpus),
    with paths preserved so that unzipping into a clone restores the full tree.
    Training sets (train.npz, about 1.5 GB in total) are regenerated from their
    recorded seeds and are excluded unless --include-training is given.

Excluded everywhere: caches, rendered page images, superseded exploratory runs
(v6_pilot, v6_production, v6_expanded) and console logs of interrupted stages.
A manifest with SHA-256 checksums is written for both parts. Before packaging, every
file listed in the frozen v5 manifest SHA256SUMS that is present must match it, and
every non-array file it lists must be present; the release is refused otherwise.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXCLUDE = [
    "*/__pycache__/*", "*.pyc", "*.log", ".git/*", "*/.ipynb_checkpoints/*", "work/*", "dist/*",
    "runs/mpl-cache/*", "runs/v6_pilot/*", "runs/v6_production/*", "runs/v6_expanded/*",
    "runs/*_console.log", "runs/v6_main/rendered/*", "runs/v6_main/publication/rendered/*",
    "runs/v6_main/cache_equivalence_check/*", "combined/node_modules/*", "combined/manuscript/rendered/*", ".pytest_cache/*", "*.zip", "~$*", "*/~$*",
]
DATA_PATTERNS = ["*.npz"]
# small arrays needed by combined/build_combined_numbers.py stay with the code
GITHUB_KEEP = ["experiments/fixtures/*.npz", "runs/v6_main/publication/family_comparison_masks.npz"]
TRAINING = ["*/train.npz"]


def match(rel: str, pats) -> bool:
    return any(fnmatch.fnmatch(rel, p) for p in pats)


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--out", type=Path, default=ROOT / "work" / "release")
    ap.add_argument("--write", action="store_true", help="copy files and build the zip (default: report only)")
    ap.add_argument("--include-training", action="store_true")
    ap.add_argument("--max-github-mb", type=float, default=50.0)
    a = ap.parse_args()
    root = a.root.resolve()

    code, data, skipped = [], [], []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if match(rel, EXCLUDE):
            skipped.append(rel)
        elif match(rel, TRAINING) and not a.include_training:
            skipped.append(rel)
        elif match(rel, DATA_PATTERNS) and not match(rel, GITHUB_KEEP):
            data.append(rel)
        else:
            code.append(rel)

    size = lambda rels: sum((root / r).stat().st_size for r in rels)
    too_big = [r for r in code if (root / r).stat().st_size > a.max_github_mb * 1e6]
    print(f"GitHub tree : {len(code):5d} files, {size(code) / 1e6:9.1f} MB")
    print(f"Data deposit: {len(data):5d} files, {size(data) / 1e6:9.1f} MB")
    print(f"Excluded    : {len(skipped):5d} files, {size(skipped) / 1e6:9.1f} MB")
    for r in too_big:
        print(f"  ERROR {r} is {(root / r).stat().st_size / 1e6:.1f} MB, above the GitHub limit; add it to DATA_PATTERNS")
    bad_sums = []
    amendment_path = root / 'docs/FINAL_REVISION_AMENDMENTS.json'
    amendments = json.loads(amendment_path.read_text()) if amendment_path.exists() else {}
    sums = root / "SHA256SUMS"
    if sums.exists():
        for line in sums.read_text().splitlines():
            if not line.strip():
                continue
            digest, name = line.split(None, 1)
            name = name.strip().lstrip("*")
            p = root / name
            if not p.is_file():
                if not name.endswith(".npz"):
                    bad_sums.append(f"{name} missing")
            elif sha(p) != digest:
                change = amendments.get(name,{})
                if change.get('original_sha256') != digest or change.get('revised_sha256') != sha(p):
                    bad_sums.append(f"{name} differs from SHA256SUMS without a matching documented amendment")
    for b in bad_sums:
        print(f"  ERROR {b}")
    required = ["combined/combined_numbers.json", "combined/manuscript/combined_manuscript.docx", "README.md", ".github/README.md", "CITATION.cff"]
    missing = [r for r in required if r not in code]
    for r in missing:
        print(f"  ERROR required file missing: {r}")
    if too_big or missing or bad_sums:
        return 1
    if not a.write:
        print("dry run: add --write to build work/release/")
        return 0

    gh = a.out / "github" / root.name
    if gh.exists():
        raise FileExistsError('Choose a fresh --out directory; existing release trees are preserved')
    for r in code:
        dst = gh / r
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / r, dst)
    (a.out / "data").mkdir(parents=True, exist_ok=True)
    zpath = a.out / "data" / f"{root.name}-data.zip"
    with zipfile.ZipFile(zpath, "w", compression=zipfile.ZIP_STORED, allowZip64=True) as z:
        for r in data:
            z.write(root / r, r)
    manifest = {
        "github": {r: sha(root / r) for r in code},
        "data": {r: sha(root / r) for r in data},
        "excluded": skipped,
        "training_included": a.include_training,
    }
    (a.out / "RELEASE_MANIFEST.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    shutil.copy2(a.out / "RELEASE_MANIFEST.json", gh / "RELEASE_MANIFEST.json")
    github_zip=a.out / f'{root.name}-github.zip'
    with zipfile.ZipFile(github_zip,'w',compression=zipfile.ZIP_DEFLATED,allowZip64=True) as z:
        for p in sorted(gh.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(gh.parent).as_posix())
    for archive in [zpath,github_zip]:
        with zipfile.ZipFile(archive) as z:
            if z.testzip() is not None:raise RuntimeError(f'CRC failure: {archive}')
    print(f'wrote {github_zip}; both ZIP integrity checks passed')
    print(f"wrote {gh}")
    print(f"wrote {zpath} ({zpath.stat().st_size / 1e6:.1f} MB)")
    print(f"wrote {a.out / 'RELEASE_MANIFEST.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
