"""Collect every number quoted in the combined manuscript into one JSON file.

Run from the repository root:

    python combined/build_combined_numbers.py

Inputs (all already in the release):
  data/manuscript_numbers.json                 corrected v5 reference analysis
  runs/v6_main/comparison.json                 native / common corpus comparisons
  runs/v6_main/<variant>/supplementary_analysis.json
  runs/v6_main/<variant>/real_summary.json
  runs/v6_main/<variant>/posterior.json
  runs/v6_main/stress_comparison.json
  runs/v6_main/cross_model/summary.json
  runs/v6_main/<variant>/*_diagnostics.json     exact same-model and native narrow-gap metrics
  experiments/fixtures/*_narrow_v5*.npz        archived reference-model stress inference

Output: combined/combined_numbers.json

Nothing here re-runs inference. The script only reads archived outputs, so the
manuscript numbers can be regenerated and diffed after any change upstream.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
VARIANTS = ["mobility", "extra", "spline", "mobility_extra", "mobility_spline"]
MODELS = ["baseline"] + VARIANTS
LABELS = {
    "baseline": "Reference (shared bands, monotone lattice)",
    "mobility": "Independent bands",
    "extra": "Rising channel",
    "spline": "Flexible lattice",
    "mobility_extra": "Independent bands + rising channel",
    "mobility_spline": "Independent bands + flexible lattice",
}
SHORT = {
    "baseline": "Reference",
    "mobility": "Independent bands",
    "extra": "Rising channel",
    "spline": "Flexible lattice",
    "mobility_extra": "Independent + rising",
    "mobility_spline": "Independent + flexible",
}
DIM = {"baseline": 10, "mobility": 13, "extra": 11, "spline": 13, "mobility_extra": 14, "mobility_spline": 16}


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tri(x):
    """[median, lo, hi] -> list of floats (None-safe)."""
    return None if x is None else [None if v is None else float(v) for v in x]


def group(d: dict) -> dict:
    return {
        "n": d["n"],
        "papers": d["papers"],
        "CB": tri(d.get("C_B")),
        "CA": tri(d.get("C_A")),
    }


def baseline_group(d: dict) -> dict:
    return {"n": d["n"], "papers": d["papers"], "CB": tri(d.get("CB")), "CA": tri(d.get("CA"))}


def parse_md_table(text: str, header_start: str) -> list[list[str]]:
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("| " + header_start):
            rows = []
            for row in lines[i + 2:]:
                if not row.startswith("|"):
                    break
                rows.append([c.strip() for c in row.strip("|").split("|")])
            return rows
    raise KeyError(header_start)


def pct(s: str) -> float:
    return float(s.rstrip("%")) / 100.0


def control_upturn(root: Path) -> dict:
    """Recompute the decreasing-lattice control: apparent Kim-subtraction upturns."""
    src = np.load(root / "experiments/fixtures/control_narrow_v5.npz")
    inf = np.load(root / "experiments/fixtures/control_narrow_v5_inference.npz")
    x = src["x"].astype(np.float64)
    truth = src["truth"].astype(np.float64)  # channels: lattice, bipolar, electronic, total
    sigma = 10.0 ** x[:, 0:16]
    S = x[:, 16:32]
    kappa = np.exp(x[:, 32:48])
    T = inf["Tgrid"].astype(np.float64)
    L = (1.5 + np.exp(-np.abs(S) / 116.0)) * 1e-8
    A = kappa - L * sigma * T  # sigma in S/m, kappa in W/m/K
    up = A[:, 15] > A[:, 8]
    adm = inf["admit"].astype(bool)
    lat_up = truth[:, 0, 15] > truth[:, 0, 8]
    bipfrac_hi = truth[:, 1, 15] / truth[:, 3, 15]
    return {
        "admitted": int(adm.sum()),
        "apparent_upturn_admitted": int((up & adm).sum()),
        "true_lattice_upturn_admitted": int((lat_up & adm).sum()),
        "median_true_bipolar_fraction_at_Thi_upturn": float(np.median(bipfrac_hi[up & adm])),
        "median_true_bipolar_fraction_at_Thi_other": float(np.median(bipfrac_hi[~up & adm])),
        "definition": "Kim subtraction A from archived features; upturn means A at grid index 15 exceeds index 8",
    }


def upturn_reference_native(root: Path, replay: dict) -> dict:
    inf = np.load(root / "experiments/fixtures/upturn_narrow_v5_inference.npz")
    ver = [v for v in replay if v["case"] == "upturn"][0]
    return {"scored": int(inf["scored"].sum()), "admitted": int(inf["admit"].sum()), "archived_scored": ver["archived_scored"]}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args()
    root = a.root.resolve()
    run = root / "runs/v6_main"
    out = a.out or root / "combined/combined_numbers.json"

    v5 = load(root / "data/manuscript_numbers.json")
    comp = load(run / "comparison.json")
    stress = load(run / "stress_comparison.json")
    cross = load(run / "cross_model/summary.json")
    results_md = (run / "RESULTS.md").read_text(encoding="utf-8")
    replay_ver = load(run / "baseline_replay/verification.json")
    replay_met = load(run / "baseline_replay/metric_comparison.json")

    N = {"labels": LABELS, "short": SHORT, "dimension": DIM, "models": MODELS}

    # ---- reference (v5) analysis, copied verbatim -------------------------------
    N["v5"] = v5

    # ---- real-corpus selection counts per model ---------------------------------
    sel = {"baseline": {"n": v5["n"], "scored": v5["scored"], "admitted": v5["admitted"]}}
    for v in VARIANTS:
        r = load(run / v / "real_summary.json")
        sel[v] = {"n": r["n"], "scored": r["scored"], "admitted": r["admitted"]}
    N["selection"] = sel

    # ---- corpus comparisons (native / baseline-common / all-model-common) -------
    N["all_model_common"] = {"n": comp["all_model_common_n"], "papers": comp["all_model_common_papers"], "selection": comp["selection"]}
    cc = {}
    for m in MODELS:
        d = comp["models"][m]
        cc[m] = {}
        for pop in ("native", "baseline_common", "all_model_common"):
            p = d[pop]
            cc[m][pop] = {
                "n": p["n"], "papers": p["papers"],
                "CB": tri(p["C_B"]), "CA": tri(p["C_A"]),
                "paired_change_CB": tri(p["paired_change_C_B"]),
                "baseline_CB_same_mask": tri(p["baseline_C_B_same_mask"]),
                "Cprime_all_A": tri(p["Cprime_all_A"]),
            }
    N["corpus"] = cc

    # ---- stratified analyses per model (native populations) --------------------
    strata, roll, fam, thr, neg, scat = {}, {}, {}, {}, {}, {}
    strata["baseline"] = {k: baseline_group(v5["strata"][k]) for k in v5["strata"]}
    roll["baseline"] = {k: baseline_group(v5["rollover"][k]) for k in v5["rollover"]}
    fam["baseline"] = {k: baseline_group(v5["families"][k]) for k in v5["families"]}
    thr["baseline"] = {k: baseline_group(v5["thresholds"][k]) for k in v5["thresholds"]}
    neg["baseline"] = v5["negative_A"]
    for v in VARIANTS:
        s = load(run / v / "supplementary_analysis.json")
        strata[v] = {k: group(x) for k, x in s["strata"].items()}
        roll[v] = {k: group(x) for k, x in s["rollover"].items()}
        fam[v] = {k: group(x) for k, x in s["families"].items()}
        thr[v] = {k: group(x) for k, x in s["screen_thresholds"].items()}
        neg[v] = s["negative_conventional_remainder"]
        scat[v] = s["effective_scattering"]
    N.update(strata=strata, rollover=roll, families=fam, thresholds=thr, negative_A=neg, effective_scattering=scat)

    # derived: ratio of top to bottom bipolar stratum shift, per model
    N["strata_ratio_top_bottom"] = {m: strata[m]["10_to_100"]["CB"][0] / strata[m]["below_2"]["CB"][0] for m in MODELS}
    N["threshold_range_CB"] = {m: [min(x["CB"][0] for x in thr[m].values()), max(x["CB"][0] for x in thr[m].values())] for m in MODELS}

    # ---- training records --------------------------------------------------------
    tr = {}
    for v in VARIANTS:
        p = load(run / v / "posterior.json")
        tr[v] = {k: p[k] for k in ("seed", "epochs_completed", "best_epoch", "stop_reason", "best_validation_nll", "n_train", "n_validation", "dimension")}
        tr[v]["selected_epoch_one_based"] = p["best_epoch"] + 1  # posterior.json stores a zero-based index
    N["training"] = tr

    # ---- synthetic tests ---------------------------------------------------------
    same = {}
    for v in VARIANTS:
        d = load(run / v / "test_diagnostics.json")
        ch = d["scored"]["channels"]
        same[v] = {"n": d["n"], "scored": d["scored"]["n"], "admitted": d["admitted"]["n"],
                   "lattice_coverage": ch["lattice"]["coverage"], "bipolar_coverage": ch["bipolar"]["coverage"],
                   "lattice_median_abs_rel_error": ch["lattice"]["median_absolute_relative_error"]}
    N["same_model_test"] = same
    narrow = {}
    for v in VARIANTS:
        d = load(run / v / "narrow_upturn_diagnostics.json")
        ch = d["scored"]["channels"]; sl = d["admitted"]["slope"]["original_four"]
        narrow[v] = {"scored": d["scored"]["n"], "admitted": d["admitted"]["n"], "lattice_coverage": ch["lattice"]["coverage"],
                     "bipolar_coverage": ch["bipolar"]["coverage"], "median_slope_error": sl["median_error"], "slope_n": sl["n"]}
    up_met = [x for x in replay_met if x["case"] == "upturn"][0]["archived"]
    ref_counts = upturn_reference_native(root, replay_ver)
    narrow["baseline"] = {"scored": ref_counts["scored"], "admitted": ref_counts["admitted"],
                          "lattice_coverage": up_met["coverage"]["lattice"], "bipolar_coverage": up_met["coverage"]["bipolar"],
                          "median_slope_error": up_met["median_slope_error"], "slope_n": up_met["slope_n"]}
    N["narrow_upturn_native"] = narrow

    st = {}
    for case, d in stress.items():
        st[case] = {"n": d["n"], "common_scored_n": d["common_scored_n"], "common_slope_n": d["common_slope_n"], "models": {}}
        for m, md in d["models"].items():
            st[case]["models"][m] = {
                "lattice_coverage": md["channels"]["lattice"]["coverage"],
                "bipolar_coverage": md["channels"]["bipolar"]["coverage"],
                "total_coverage": md["channels"]["total"]["coverage"],
                "lattice_width": md["channels"]["lattice"]["median_interval_width"],
                "lattice_mae": md["channels"]["lattice"]["median_absolute_error"],
                "native_slope": md["native_slope"],
                "common_slope": md["common_slope"],
            }
    N["stress_common"] = st

    tx = []
    for e in cross:
        tx.append({
            "inference": e["inference"]["spec"]["variant"],
            "truth": e["source"]["spec"]["variant"],
            "n": e["n"],
            "scored": e["scored"]["n"],
            "admitted": e["admitted"]["n"],
            "lattice_coverage": e["scored"]["channels"]["lattice"]["coverage"],
            "bipolar_coverage": e["scored"]["channels"]["bipolar"]["coverage"],
            "total_coverage": e["scored"]["channels"].get("total", {}).get("coverage"),
            "seed": e["inference"]["seed"],
        })
    N["transfer"] = tx

    N["control_narrow"] = control_upturn(root)
    N["family_common"] = load(run / "publication/family_comparison.json")
    reference_training = load(root / "data/posterior_v5.json")
    N["reference_training"] = {**reference_training, "selected_epoch_one_based": reference_training["best_epoch"] + 1}

    # ---- provenance of every input ----------------------------------------------
    inputs = [root / "data/manuscript_numbers.json", run / "comparison.json", run / "stress_comparison.json",
              run / "cross_model/summary.json", run / "RESULTS.md", run / "baseline_replay/verification.json",
              run / "baseline_replay/metric_comparison.json"]
    for v in VARIANTS:
        inputs += [run / v / "supplementary_analysis.json", run / v / "real_summary.json", run / v / "posterior.json"]
        inputs += [run / v / "test_diagnostics.json", run / v / "narrow_upturn_diagnostics.json"]
    inputs += sorted((root / "experiments/fixtures").glob("*narrow_v5*.npz"))
    inputs += [run / "publication/family_comparison.json", root / "data/posterior_v5.json"]
    N["provenance"] = {str(p.relative_to(root)).replace("\\", "/"): sha(p) for p in inputs}

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(N, indent=1, sort_keys=False), encoding="utf-8")
    print(f"wrote {out}  ({len(N['provenance'])} inputs hashed)")
    c = N["control_narrow"]
    print(f"control: {c['apparent_upturn_admitted']}/{c['admitted']} admitted curves with apparent upturn")


if __name__ == "__main__":
    main()
