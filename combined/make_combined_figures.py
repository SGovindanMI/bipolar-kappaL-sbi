"""Figures for the combined manuscript (reference analysis + extended-model robustness).

Run from the repository root after build_combined_numbers.py:

    python combined/make_combined_figures.py

Figures 1-4 are redrawn from the corrected v5 arrays (data/results_v5.npz,
data/inference_v5.npz, data/manuscript_numbers.json) with the same content as the
v5 figures. Figures 5-6 are new and read only combined/combined_numbers.json.
Supplementary Figure 1 is copied from runs/v6_main/publication outputs when present.
Every figure is written as 600 dpi PNG and TIFF plus vector PDF and SVG.
"""
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "combined/figures"
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "work/matplotlib"))
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#898781", "#e1e0d9"
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#7a5bc9"]  # categorical, fixed order
SEQ3 = ["#86b6ef", "#3987e5", "#0d366b"]
SEQ4 = ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]
MM = 1 / 25.4
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Liberation Sans", "DejaVu Sans"],
    "font.size": 7.5, "axes.titlesize": 8, "axes.labelsize": 7.5, "legend.fontsize": 6.8,
    "xtick.labelsize": 7, "ytick.labelsize": 7,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": INK2, "axes.linewidth": 0.6, "xtick.color": INK2, "ytick.color": INK2,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6, "axes.labelcolor": INK, "text.color": INK,
    "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.titlepad": 6,
    "savefig.dpi": 600, "pdf.fonttype": 42, "svg.fonttype": "none", "legend.frameon": False,
})
ORDER = ["baseline", "mobility", "extra", "spline", "mobility_extra", "mobility_spline"]


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf", "svg"):
        fig.savefig(OUT / f"{name}.{ext}", bbox_inches="tight")
    fig.savefig(OUT / f"{name}.tiff", bbox_inches="tight", pil_kwargs={"compression": "tiff_lzw"})
    plt.close(fig)


def errbar_x(ax, y, tri, **kw):
    m, lo, hi = tri
    ax.errorbar(m, y, xerr=[[m - lo], [hi - m]], fmt=kw.pop("fmt", "o"), ms=kw.pop("ms", 4), elinewidth=1.1, capsize=0, **kw)


def zero_line(ax, axis="x"):
    (ax.axvline if axis == "x" else ax.axhline)(0, color=MUTED, lw=0.7, ls="--", zorder=0)


def grid(ax, axis="x"):
    ax.grid(axis=axis, color=GRID, lw=0.5)
    ax.set_axisbelow(True)


# ---------------------------------------------------------------------------------
# Figures 1-4: reference analysis
# ---------------------------------------------------------------------------------
def reference_figures():
    r = np.load(ROOT / "data/results_v5.npz")
    p = np.load(ROOT / "data/inference_v5.npz")
    v = json.loads((ROOT / "data/manuscript_numbers.json").read_text())
    ad, sc, pair, e, fr = r["admit"], r["scored"], r["paired"], r["exponents"], r["bipolar_fraction"]
    shift = e[:, 2] - e[:, 1]

    # Figure 1
    fig, axs = plt.subplots(1, 2, figsize=(180 * MM, 66 * MM), layout="constrained")
    ax = axs[0]
    ax.hist(p["explained"][sc], bins=np.linspace(0, 1, 25), color=CAT[0], edgecolor="white", linewidth=0.5)
    ax.axvline(0.75, color=INK, ls="--", lw=0.8)
    ax.text(0.735, ax.get_ylim()[1] * 0.95, "screen 0.75", ha="right", va="top", fontsize=6.8, color=INK2)
    ax.set(xlabel="Observed-point containment in latent 95% band", ylabel="Scored curves", title="a   Fit screen")
    grid(ax, "y")
    ax = axs[1]
    names = list(v["temperature_admission"])
    c = np.array([v["temperature_admission"][k]["ci"] for k in names])
    xs = np.arange(len(names))
    ax.bar(xs, c[:, 0], color=CAT[0], width=0.62)
    ax.errorbar(xs, c[:, 0], yerr=[c[:, 0] - c[:, 1], c[:, 2] - c[:, 0]], fmt="none", ecolor=INK, elinewidth=0.9, capsize=2)
    for i, k in enumerate(names):
        ax.text(i, 0.03, f"n = {v['temperature_admission'][k]['n']:,}", ha="center", color="white", fontsize=6.5)
    ax.set_xticks(xs, [n.replace("-", "–") for n in names])
    ax.set(xlabel="Measurement ceiling (K)", ylabel="Admitted fraction of scored curves", ylim=(0, 1), title="b   Admission by temperature window")
    grid(ax, "y")
    save(fig, "figure1_fit_screen")

    # Figure 2
    fig = plt.figure(figsize=(180 * MM, 128 * MM), layout="constrained")
    gs = fig.add_gridspec(2, 2)
    a0, a1, a2 = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, :])
    a0.scatter(fr[pair], shift[pair], color=CAT[0], s=3, alpha=0.35, lw=0, rasterized=True)
    a0.set_xscale("symlog", linthresh=0.01)
    zero_line(a0, "y")
    a0.set(xlabel="Inferred bipolar / measured total at 750 K", ylabel="Slope shift C − B", title="a   Bipolar association")
    a1.scatter(e[pair, 3] - e[pair, 1], shift[pair], s=3, alpha=0.3, color=CAT[0], lw=0, rasterized=True)
    zero_line(a1, "y"); zero_line(a1, "x")
    a1.set(xlabel="Additive shift C′ − B", ylabel="Model-lattice shift C − B", title="b   Distinct estimands")
    labels = ["A  Kim subtraction", "B  posterior Lorenz", "C  model lattice", "C′  additive bipolar removal"]
    for i, (lab, col) in enumerate(zip(labels, CAT)):
        a2.hist(e[pair, i], bins=np.linspace(-2, 1, 46), histtype="step", color=col, lw=1.2, density=True, label=lab)
    a2.legend(loc="upper left")
    a2.set(xlabel="Finite-window log slope, 400–750 K", ylabel="Density", title="c   Four lattice estimates (paired set)")
    grid(a2, "y")
    save(fig, "figure2_estimates")

    # Figure 3
    fig, axs = plt.subplots(1, 2, figsize=(180 * MM, 78 * MM), layout="constrained", gridspec_kw={"width_ratios": [1.15, 1]})
    fam = v["families"]
    names = sorted(fam, key=lambda k: fam[k]["CB"][0])
    for i, k in enumerate(names):
        errbar_x(axs[0], i, fam[k]["CB"], color=CAT[0])
    axs[0].set_yticks(range(len(names)), [f"{k} ({fam[k]['n']})" for k in names])
    axs[0].invert_yaxis()
    zero_line(axs[0]); grid(axs[0])
    axs[0].set(xlabel="Median slope shift C − B", title="a   Within-family shifts")
    ro = v["rollover"]
    keys = ["none", "below_5", "5_to_15", "above_15"]
    for i, k in enumerate(keys):
        m, lo, hi = ro[k]["CB"]
        axs[1].errorbar(i, m, yerr=[[m - lo], [hi - m]], fmt="o", ms=4.5, color=SEQ4[i], elinewidth=1.1)
    axs[1].set_xticks(range(4), [f"None\n{ro['none']['n']:,}", f"<5%\n{ro['below_5']['n']:,}", f"5–15%\n{ro['5_to_15']['n']:,}", f"≥15%\n{ro['above_15']['n']:,}"])
    zero_line(axs[1], "y"); grid(axs[1], "y")
    axs[1].set(xlabel="Measured Seebeck rollover (curves)", ylabel="Median slope shift C − B", title="b   Measurement-derived strata")
    save(fig, "figure3_families_rollover")

    # Figure 4
    fig, axs = plt.subplots(1, 2, figsize=(180 * MM, 66 * MM), layout="constrained")
    prob = r["r_probability"]
    med = np.full(len(ad), np.nan)
    med[ad] = np.nanmedian(p["theta"][ad, :, 8], axis=1)
    masks = [prob > 0.8, prob < 0.2, (prob >= 0.2) & (prob <= 0.8)]
    labs = ["Phonon-like", "Impurity-like", "Ambiguous"]
    axs[0].hist([med[ad & m] for m in masks], bins=np.linspace(-1, 2, 40), stacked=True, color=CAT[:3], label=labs, edgecolor="white", linewidth=0.3)
    axs[0].axvline(-0.5, color=INK, ls="--", lw=0.7)
    axs[0].axvline(1.5, color=INK, ls=":", lw=0.7)
    axs[0].legend(loc="upper right")
    axs[0].set(xlabel="Posterior median effective r", ylabel="Admitted curves", title="a   Effective exponent by class")
    grid(axs[0], "y")
    c = np.array([v["classes"][k]["ci"] for k in ["phonon_like", "impurity_like", "ambiguous"]])
    axs[1].bar(labs, c[:, 0], color=CAT[:3], width=0.6)
    axs[1].errorbar(labs, c[:, 0], yerr=[c[:, 0] - c[:, 1], c[:, 2] - c[:, 0]], fmt="none", ecolor=INK, elinewidth=0.9, capsize=2)
    axs[1].set(ylabel="Fraction of admitted curves", ylim=(0, 1), title="b   Class fractions")
    grid(axs[1], "y")
    save(fig, "figure4_scattering")


# ---------------------------------------------------------------------------------
# Figure 6: corpus robustness across six models
# ---------------------------------------------------------------------------------
def figure5(N):
    S = N["short"]
    ys = np.arange(len(ORDER))
    fig, axs = plt.subplots(1, 3, figsize=(180 * MM, 92 * MM), layout="constrained", sharey=True)
    ax = axs[0]
    for j, (key, lab, col, mk) in enumerate([("CB", "C − B", CAT[0], "o"), ("CA", "C − A", CAT[1], "s")]):
        for i, m in enumerate(ORDER):
            errbar_x(ax, i + (j - 0.5) * 0.28, N["corpus"][m]["all_model_common"][key], color=col, fmt=mk, ms=3.8)
    ax.legend(handles=[Line2D([], [], color=CAT[0], marker="o", lw=0, ms=4, label="C − B"),
                       Line2D([], [], color=CAT[1], marker="s", lw=0, ms=4, label="C − A")],
              title="Estimate pair", title_fontsize=6.8, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2)
    n = N["all_model_common"]
    ax.set(xlabel="Median slope shift", title=f"a   Common set ({n['n']:,} curves)")
    ax.set_xlim(-0.85, 0.05)
    zero_line(ax); grid(ax)

    ax = axs[1]
    keys = ["below_2", "2_to_10", "10_to_100"]
    labs = ["<2%", "2–10%", "10–100%"]
    for j, k in enumerate(keys):
        for i, m in enumerate(ORDER):
            errbar_x(ax, i + (j - 1) * 0.24, N["strata"][m][k]["CB"], color=SEQ3[j], ms=3.6)
    ax.legend(handles=[Line2D([], [], color=SEQ3[j], marker="o", lw=0, ms=4, label=labs[j]) for j in range(3)],
              title="Inferred bipolar share at 750 K", title_fontsize=6.8, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3, columnspacing=0.8, handletextpad=0.2)
    ax.set(xlabel="Median slope shift C − B", title="b   By inferred bipolar share")
    zero_line(ax); grid(ax)

    ax = axs[2]
    keys = ["none", "below_5", "5_to_15", "above_15"]
    labs = ["None", "<5%", "5–15%", "≥15%"]
    for j, k in enumerate(keys):
        for i, m in enumerate(ORDER):
            errbar_x(ax, i + (j - 1.5) * 0.19, N["rollover"][m][k]["CB"], color=SEQ4[j], ms=3.4)
    ax.legend(handles=[Line2D([], [], color=SEQ4[j], marker="o", lw=0, ms=4, label=labs[j]) for j in range(4)],
              title="Measured Seebeck rollover", title_fontsize=6.8, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=4, columnspacing=0.6, handletextpad=0.1)
    ax.set(xlabel="Median slope shift C − B", title="c   By measured rollover")
    zero_line(ax); grid(ax)
    axs[0].set_yticks(ys, [S[m] for m in ORDER])
    axs[0].invert_yaxis()
    for ax in axs[1:]:
        ax.tick_params(axis="y", length=0)
    save(fig, "figure6_model_robustness")


# ---------------------------------------------------------------------------------
# Figure 5: synthetic accuracy, width and transfer
# ---------------------------------------------------------------------------------
def figure6(N):
    S = N["short"]
    st = N["stress_common"]["narrow_upturn"]
    ys = np.arange(len(ORDER))
    fig, axs = plt.subplots(1, 4, figsize=(180 * MM, 70 * MM), layout="constrained", sharey=True,
                            gridspec_kw={"width_ratios": [1, 1, 1, 1.15]})
    cov = [st["models"][m]["lattice_coverage"] * 100 for m in ORDER]
    wid = [st["models"][m]["lattice_width"] for m in ORDER]
    err = [st["models"][m]["common_slope"]["median_absolute_error"] for m in ORDER]
    for ax, vals, xl, ttl in [(axs[0], cov, "Lattice coverage (%)", "a   Coverage"),
                              (axs[1], wid, "Median width (W m$^{-1}$ K$^{-1}$)", "b   Interval width"),
                              (axs[2], err, "Median |slope error|", "c   Slope error")]:
        ax.barh(ys, vals, color=CAT[0], height=0.62)
        ax.set(xlabel=xl, title=ttl)
        grid(ax)
    axs[0].axvline(95, color=INK, ls="--", lw=0.7)
    axs[0].set_xlim(0, 100)
    axs[1].set_xscale("log")
    axs[1].set_xlim(0.3, 20)
    for i, w in enumerate(wid):
        axs[1].text(w * 1.08, i, f"{w:.2f}" if w < 2 else f"{w:.1f}", va="center", fontsize=6.3, color=INK2)
    tx = {(t["inference"], t["truth"]): t for t in N["transfer"]}
    for j, (truth, lab) in enumerate([("mobility_extra", "Independent + rising truth"), ("mobility_spline", "Independent + flexible truth")]):
        vals = [tx[(m, truth)]["lattice_coverage"] * 100 for m in ORDER]
        axs[3].barh(ys + (j - 0.5) * 0.36, vals, height=0.34, color=CAT[j], label=lab)
    axs[3].axvline(95, color=INK, ls="--", lw=0.7)
    axs[3].set(xlabel="Lattice coverage (%)", title="d   Transfer", xlim=(0, 100))
    axs[3].legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=1)
    grid(axs[3])
    axs[0].set_yticks(ys, [S[m] for m in ORDER])
    axs[0].invert_yaxis()
    for ax in axs[1:]:
        ax.tick_params(axis="y", length=0)
    save(fig, "figure5_synthetic_tests")


def supplementary():
    src = ROOT / "runs/v6_main/publication"
    for ext in ("png", "pdf", "svg", "tiff"):
        for cand in (src / "figures" / f"figure1_network.{ext}", src / f"figure1_network.{ext}"):
            if cand.exists():
                shutil.copy2(cand, OUT / f"supplementary_figure1_network.{ext}")
                break


def main():
    N = json.loads((ROOT / "combined/combined_numbers.json").read_text())
    if (ROOT / "data/results_v5.npz").exists() and (ROOT / "data/inference_v5.npz").exists():
        reference_figures()
    else:
        print("data/results_v5.npz or inference_v5.npz missing: Figures 1-4 skipped")
    figure5(N)
    figure6(N)
    family_common(N)
    supplementary()
    print("figures written to", OUT.relative_to(ROOT))


def family_common(N):
    groups=[(f,d) for f,d in N['family_common']['families'].items() if d['reported']]
    # The heterogeneous residual group follows all named families.
    groups.sort(key=lambda x:(x[0]=='other',x[0]))
    fig,ax=plt.subplots(figsize=(7.1,4.2),layout='constrained')
    colors=['#333333','#0072B2','#D55E00','#009E73','#CC79A7','#E69F00']
    markers=['o','s','^','D','v','P']
    for j,m in enumerate(ORDER):
        for i,(family,d) in enumerate(groups):
            v=d['models'][m]['C_B'];y=i+(j-2.5)*.115
            ax.hlines(y,v[1],v[2],color=colors[j],lw=.8)
            ax.plot(v[0],y,marker=markers[j],ms=3,color=colors[j],ls='none',label=N['short'][m] if i==0 else None)
    ax.set(yticks=range(len(groups)),yticklabels=[f"{f} ({d['n']} curves, {d['papers']} papers)" for f,d in groups],xlabel='Median per-curve C − B log-slope shift')
    ax.invert_yaxis();ax.axvline(0,color='black',ls='--',lw=.7)
    fig.legend(loc='outside lower center',ncol=3,fontsize=6.8,frameon=False)
    save(fig,'figure7_common_families')


if __name__ == "__main__":
    main()
