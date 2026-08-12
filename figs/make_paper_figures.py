#!/usr/bin/env python
"""
Regenerate every analysis figure in the TCSVT manuscript, in English and with
paper-facing terminology.

The figures shipped in docs/reports/ carry Chinese axis labels and internal
jargon (m14 / m15 / beta / skip_phase17), so they cannot be used directly.  This
script rebuilds them from the same raw evaluation outputs.

Usage
-----
    /home/avlab/anaconda3/envs/infinity-clean/bin/python figs/make_paper_figures.py

Inputs (all under REPO/outputs/outputs_loop_exp/):
    pie_edit_rewrite_minimal_m14_h<h>_cum0_N2/_eval/per_case.csv      14 arms
    pie_edit_rewrite_minimal_m14_h<h>_cum0_N2_noBeta/_eval/...         3 arms
    pie_edit_rewrite_minimal_m14_h0.6_{cum0_N0,l0.5}/_eval/...         composition
    pie_attn_analysis/attn_stats.csv                                   attention stats

Outputs: imgs/fig_*.png  (300 dpi)

Recipe for every run: minimal rewrite + cum0 + N2, seed 1, PIE-Bench 700 cases.
Arms with kappa_max = 0 (tau == h) are referred to as "fixed threshold".
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EXP = os.path.join(REPO, "outputs", "outputs_loop_exp")
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "imgs"))
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 8,
    "axes.titlesize": 8.5,
    "axes.labelsize": 8,
    "legend.fontsize": 7,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linewidth": 0.5,
    "figure.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02,
})

# IEEE single-column is 3.5 in, double-column 7.16 in.
COL, COL2 = 3.45, 7.1

C_MAIN, C_ALT, C_ACC, C_GREY = "#3B5BA5", "#E8871A", "#B3283B", "#7A7A7A"

ARMS = [0.48, 0.50, 0.52, 0.54, 0.56, 0.58, 0.60,
        0.62, 0.64, 0.65, 0.66, 0.68, 0.70, 0.75]

CATS = ["0_random_140", "1_change_object_80", "2_add_object_80",
        "3_delete_object_80", "4_change_attribute_content_40",
        "5_change_attribute_pose_40", "6_change_attribute_color_40",
        "7_change_attribute_material_40", "8_change_background_80",
        "9_change_style_80"]
CAT_SHORT = ["Random", "Replace", "Add", "Delete", "Content",
             "Pose", "Color", "Material", "Backgr.", "Style"]
DEV = CATS[1:]                    # nine concrete categories, n = 560
HOLDOUT = CATS[0]                 # 0_random, n = 140

M = {"ir": "image_reward", "ssim": "ssim_unedit_part", "psnr": "psnr_unedit_part",
     "lpips": "lpips_unedit_part", "sd": "structure_distance", "hps": "hps_v2"}


# --------------------------------------------------------------------------- #
# loading
# --------------------------------------------------------------------------- #
def arm_dir(h, suffix=""):
    """Result directories are inconsistently named (h0.5 but h0.70), so try both."""
    for s in (f"{h:g}", f"{h:.2f}"):
        d = os.path.join(EXP, f"pie_edit_rewrite_minimal_m14_h{s}_cum0_N2{suffix}")
        if os.path.isdir(os.path.join(d, "_eval")):
            return d
    return os.path.join(EXP,
                        f"pie_edit_rewrite_minimal_m14_h{h:g}_cum0_N2{suffix}")


def load_per_case(path):
    df = pd.read_csv(os.path.join(path, "_eval", "per_case.csv"))
    df["key"] = df["category"] + "/" + df["case_id"].astype(str)
    return df.set_index("key")


def load_arms(suffix="", hs=None):
    out = {}
    for h in (hs or ARMS):
        d = arm_dir(h, suffix)
        if os.path.isdir(os.path.join(d, "_eval")):
            out[h] = load_per_case(d)
    return out


def load_attn():
    df = pd.read_csv(os.path.join(EXP, "pie_attn_analysis", "attn_stats.csv"))
    df = df[df["scale_idx"] == df["scale_idx"].max()].copy()   # last scale, 64x64
    # min-max normalization is affine, so std of the normalized map is
    # std / (max - min); this is the sigma used by the adaptive term.
    df["sigma_norm"] = df["std"] / (df["attn_max"] - df["attn_min"])
    df["key"] = df["category"] + "/" + df["case_id"].astype(str)
    return df.set_index("key")


def overall(df, m):
    return df[M[m]].mean()


def cat_mean(df, cat, m):
    return df[df["category"] == cat][M[m]].mean()


# --------------------------------------------------------------------------- #
# F1: what the coefficient of variation actually measures
# --------------------------------------------------------------------------- #
def fig_cv_decomposition(attn):
    fig, axes = plt.subplots(1, 3, figsize=(COL2, 2.05))
    panels = [("cv", r"$c_k=\sigma_k/\mu_k$", None),
              ("std", r"$\sigma_k$", 1e-3),
              ("mean", r"$\mu_k$", 1e-3)]
    for ax, (col, lab, scale) in zip(axes, panels):
        data = [attn[attn["category"] == c][col].values for c in CATS]
        if scale:
            data = [d / scale for d in data]
        parts = ax.violinplot(data, showextrema=False, widths=0.85)
        for pc in parts["bodies"]:
            pc.set_facecolor(C_MAIN); pc.set_alpha(0.55); pc.set_edgecolor("none")
        med = [np.median(d) for d in data]
        ax.scatter(range(1, 11), med, s=7, color="white", zorder=3,
                   edgecolor=C_ACC, linewidth=0.7)
        ax.set_xticks(range(1, 11))
        ax.set_xticklabels(CAT_SHORT, rotation=55, ha="right")
        ax.set_ylabel(lab + (r"  ($\times 10^{-3}$)" if scale else ""))
        lo, hi = min(med), max(med)
        ax.set_title(f"median spread  {hi/lo:.1f}$\\times$", pad=3)
    axes[0].set_title("median spread  " +
                      f"{max([np.median(attn[attn['category']==c]['cv']) for c in CATS])/min([np.median(attn[attn['category']==c]['cv']) for c in CATS]):.1f}$\\times$",
                      pad=3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig_cv_decomposition.png"))
    plt.close(fig)


# --------------------------------------------------------------------------- #
# F2: the fixed-threshold frontier
# --------------------------------------------------------------------------- #
def fig_frontier_h(arms):
    fig, ax = plt.subplots(figsize=(COL, 2.5))
    hs = sorted(arms)
    x = [overall(arms[h], "psnr") for h in hs]
    y = [overall(arms[h], "ir") for h in hs]
    ax.plot(x, y, "-o", color=C_MAIN, ms=3.5, lw=1.2)
    for h, xi, yi in zip(hs, x, y):
        if h in (0.48, 0.52, 0.56, 0.60, 0.65, 0.70, 0.75):
            ax.annotate(f"$h$={h:g}", (xi, yi), textcoords="offset points",
                        xytext=(4, 5), fontsize=6.5, color=C_GREY)
    ax.set_xlabel("PSNR on unedited region (dB)   $\\rightarrow$ preservation")
    ax.set_ylabel("ImageReward   $\\rightarrow$ edit quality")
    ax.set_title("Sweeping the base level $h$ ($\\kappa_{\\max}=0$)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig_frontier_h.png"))
    plt.close(fig)


# --------------------------------------------------------------------------- #
# offline simulation of the adaptive threshold
# --------------------------------------------------------------------------- #
METRICS = ("ir", "ssim", "lpips", "psnr", "sd", "hps")


class Sim:
    """Dense (arm x case x metric) tensor so the grid search is pure numpy."""

    def __init__(self, arms, attn, keys):
        self.keys = np.asarray(keys)
        self.h = np.array(sorted(arms))
        self.S = np.stack([[arms[hh].loc[self.keys, M[m]].values.astype(float)
                            for m in METRICS] for hh in self.h])   # (A, M, C)
        self.cv = attn.loc[self.keys, "cv"].values.astype(float)
        self.sn = attn.loc[self.keys, "sigma_norm"].values.astype(float)
        # The unedited-region metrics (SSIM / PSNR / LPIPS) are undefined for the
        # cases whose ground-truth mask leaves no unedited region, so they carry
        # NaN for every arm.  Average per metric rather than dropping the case,
        # otherwise ImageReward -- which is defined everywhere -- is computed on
        # a different and smaller population than the benchmark reports.
        miss = ~np.isfinite(self.S[0]).all(axis=0)
        if miss.any():
            print(f"  {miss.sum()}/{len(self.keys)} cases have no unedited region; "
                  f"preservation metrics are averaged over the remainder")
        bad = ~np.isfinite(self.cv) | ~np.isfinite(self.sn)
        if bad.any():
            self.keys, self.S = self.keys[~bad], self.S[:, :, ~bad]
            self.cv, self.sn = self.cv[~bad], self.sn[~bad]
        self.cat = np.array([k.split("/")[0] for k in self.keys])

    def subset(self, mask):
        s = object.__new__(Sim)
        s.keys, s.S = self.keys[mask], self.S[:, :, mask]
        s.cv, s.sn, s.cat = self.cv[mask], self.sn[mask], self.cat[mask]
        s.h = self.h
        return s

    def run(self, h, cv_max, k_max, cv_min=0.0):
        frac = np.clip((self.cv - cv_min) / max(cv_max - cv_min, 1e-9), 0, 1)
        tau = h + k_max * frac * self.sn
        idx = np.abs(tau[:, None] - self.h[None, :]).argmin(axis=1)
        picked = self.S[idx, :, np.arange(self.S.shape[2])]      # (C, M)
        return dict(zip(METRICS, np.nanmean(picked, axis=0)))

    def fixed(self, m):
        return np.nanmean(self.S[:, METRICS.index(m), :], axis=1)  # (A,)


def grid_search(sim, h=0.50):
    # Stage 1: the search range is defined by the dev-set CV distribution, not
    # chosen by hand.  Below P70 more than half the cases are clamped at
    # kappa_max and the mapping stops discriminating; above P99 essentially
    # nothing is clamped and it degenerates to a linear ramp.
    # (P70 is 0.148 on the dev set; it is rounded up to the 0.025 grid step.)
    step = 0.025
    p70 = np.ceil(np.percentile(sim.cv, 70) / step) * step
    cvs = np.round(p70 + np.arange(18) * step, 4)
    kms = np.round(np.arange(20) * 0.05, 4)
    recs = [{**sim.run(h, cv, km), "cv_max": cv, "k_max": km}
            for cv in cvs for km in kms]
    return pd.DataFrame(recs), cvs, kms


def add_utility(grid, sim):
    """u = nIR + nSSIM, min-max normalized over grid configs and fixed arms."""
    def norm(col, anchor):
        ref = np.concatenate([grid[col].values, anchor])
        return (grid[col].values - ref.min()) / (ref.max() - ref.min())
    grid = grid.copy()
    grid["u"] = norm("ir", sim.fixed("ir")) + norm("ssim", sim.fixed("ssim"))
    return grid


# --------------------------------------------------------------------------- #
# F3: the adaptive term pushes the frontier outward
# --------------------------------------------------------------------------- #
def fig_adaptive_frontier(sim, grid):
    fixed = {m: sim.fixed(m) for m in ("ir", "ssim", "lpips")}
    paper = sim.run(0.50, 0.20, 0.60)
    cons = sim.run(0.50, 0.15, 0.55)
    ironly = sim.run(0.50, 0.125, 0.05)

    def gain(xm, x, y, invert):
        """IR minus the fixed-threshold frontier interpolated at the same x."""
        xs, ys = fixed[xm], fixed["ir"]
        o = np.argsort(xs)
        return y - np.interp(x, xs[o], ys[o])

    fig, axes = plt.subplots(1, 3, figsize=(COL2, 2.35),
                             gridspec_kw={"width_ratios": [1.05, 1, 1]})

    # (a) the frontier, for context
    ax = axes[0]
    ax.scatter(grid["ssim"], grid["ir"], s=3, color=C_MAIN, alpha=0.25,
               edgecolor="none", label="adaptive (360 configs)")
    ax.plot(fixed["ssim"], fixed["ir"], "-o", color=C_GREY, ms=2.6, lw=1.0,
            label="fixed threshold ($\\kappa_{\\max}{=}0$)")
    ax.scatter([ironly["ssim"]], [ironly["ir"]], marker="^", s=26, color="k",
               zorder=5, label="edit-only obj. (degenerate)")
    ax.set_xlabel("SSIM on unedited region")
    ax.set_ylabel("ImageReward")
    ax.set_title("(a) both families", pad=3)
    ax.legend(loc="lower left", handlelength=1.2, framealpha=0.9)

    # (b), (c) the gain over the interpolated frontier -- this is the claim
    for ax, xm, xlab, inv, pt in [
            (axes[1], "ssim", "SSIM on unedited region", False, "(b)"),
            (axes[2], "lpips", "LPIPS on unedited region", True, "(c)")]:
        g = gain(xm, grid[xm].values, grid["ir"].values, inv)
        ax.axhline(0, color=C_GREY, lw=1.0)
        ax.scatter(grid[xm], g, s=3.2, color=C_MAIN, alpha=0.3, edgecolor="none")
        for cfg, mk, col, lab, s in [(paper, "D", C_ACC, "ours", 34),
                                     (cons, "*", C_ALT, "consensus", 85)]:
            gv = gain(xm, np.array([cfg[xm]]), np.array([cfg["ir"]]), inv)[0]
            ax.scatter([cfg[xm]], [gv], marker=mk, s=s, color=col, zorder=5,
                       edgecolor="k", linewidth=0.3, label=f"{lab}  ${gv:+.3f}$")
        ax.set_xlabel(xlab)
        ax.set_title(f"{pt} gain over the frontier", pad=3)
        ax.set_ylim(min(g.min(), -0.005) - 0.002, max(g.max(), 0.04) + 0.016)
        ax.legend(loc="lower right", handlelength=1.0, framealpha=0.9)
        if inv:
            ax.invert_xaxis()
    axes[1].set_ylabel("$\\Delta$ ImageReward", labelpad=1)

    fig.suptitle("Dev set ($n=560$).  The adaptive threshold buys edit quality "
                 "that no fixed threshold reaches at the same preservation.", y=1.04)
    fig.tight_layout(w_pad=1.4)
    fig.savefig(os.path.join(OUT, "fig_adaptive_frontier.png"))
    plt.close(fig)
    return paper, cons, fixed


# --------------------------------------------------------------------------- #
# F4: how the parameters were obtained
# --------------------------------------------------------------------------- #
def fig_protocol(sim, grid, cvs, kms):
    dev_cv = sim.cv
    p70, p99 = np.percentile(dev_cv, [70, 99])

    fig, axes = plt.subplots(1, 2, figsize=(COL2, 2.5))

    ax = axes[0]
    ax.hist(dev_cv, bins=60, range=(0, 0.7), color=C_MAIN, alpha=0.75)
    ax.axvspan(p70, p99, color=C_ALT, alpha=0.16)
    for v, lab in [(p70, "$P_{70}$"), (p99, "$P_{99}$")]:
        ax.axvline(v, color=C_ALT, ls="--", lw=1.0)
        ax.annotate(lab, (v, ax.get_ylim()[1] * 0.93), fontsize=6.5,
                    color=C_ALT, ha="left" if lab.endswith("70}$") else "right",
                    xytext=(3 if lab.endswith("70}$") else -3, 0),
                    textcoords="offset points")
    ax.set_xlabel("coefficient of variation $c_k$ (last scale)")
    ax.set_ylabel("cases")
    ax.set_title("Stage 1: search range for $c_{\\max}$", pad=3)

    ax = axes[1]
    U = grid.pivot(index="k_max", columns="cv_max", values="u").values
    im = ax.imshow(U, origin="lower", aspect="auto", cmap="Blues",
                   extent=[cvs[0] - 0.0125, cvs[-1] + 0.0125,
                           kms[0] - 0.025, kms[-1] + 0.025])
    ax.contour(cvs, kms, U, levels=[U.max() - 0.05], colors="k",
               linestyles="--", linewidths=0.9)
    # leave-one-category-out optima: search on eight categories, hold out the ninth
    fold = []
    for held in DEV:
        sub = sim.subset(sim.cat != held)
        g, _, _ = grid_search(sub)
        g = add_utility(g, sub)
        r = g.loc[g["u"].idxmax()]
        fold.append((r["cv_max"], r["k_max"]))
    fold = np.array(fold)
    jit = np.random.default_rng(1).normal(0, 0.0035, fold.shape)
    ax.scatter(fold[:, 0] + jit[:, 0], fold[:, 1] + jit[:, 1] * 2, s=16,
               color=C_ALT, edgecolor="k", linewidth=0.3, zorder=4,
               label="LOCO fold optima (9, jittered)")
    ax.scatter([np.median(fold[:, 0])], [np.median(fold[:, 1])], marker="s",
               s=44, facecolor="none", edgecolor="k", linewidth=1.0, zorder=5,
               label="fold consensus")
    ax.scatter([0.20], [0.60], marker="D", s=34, color=C_ACC, zorder=5,
               label="ours $(0.20,0.60)$")
    ax.set_xlabel("$c_{\\max}$")
    ax.set_ylabel("$\\kappa_{\\max}$")
    ax.set_title("Stages 2--3: utility $u=\\mathrm{nIR}+\\mathrm{nSSIM}$", pad=3)
    ax.legend(loc="lower right", framealpha=0.9, handlelength=1.2)
    ax.grid(False)
    fig.colorbar(im, ax=ax, fraction=0.045, pad=0.02, label="$u$")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig_protocol.png"))
    plt.close(fig)
    return np.median(fold, axis=0), (U >= U.max() - 0.05).mean()


# --------------------------------------------------------------------------- #
# F5 / F6: the Phase 2 ablation
# --------------------------------------------------------------------------- #
def fig_beta(arms, nob):
    fig, ax = plt.subplots(figsize=(COL, 2.5))
    for src, lab, col, mk in [(arms, "full pipeline", C_MAIN, "o"),
                              (nob, "without Phase 2", C_ALT, "s")]:
        hs = sorted(src)
        x = [overall(src[h], "psnr") for h in hs]
        y = [overall(src[h], "ir") for h in hs]
        ax.plot(x, y, "--" + mk, color=col, ms=4, lw=1.2, label=lab)
        for h, xi, yi in zip(hs, x, y):
            ax.annotate(f"{h:g}", (xi, yi), textcoords="offset points",
                        xytext=(3, 4), fontsize=6, color=col)
    ax.set_xlabel("PSNR on unedited region (dB)   $\\rightarrow$ preservation")
    ax.set_ylabel("ImageReward   $\\rightarrow$ edit quality")
    ax.set_title("The two frontiers do not intersect")
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig_beta_frontier.png"))
    plt.close(fig)


def fig_beta_category(arms, nob, h=0.52):
    d = [cat_mean(nob[h], c, "ir") - cat_mean(arms[h], c, "ir") for c in CATS]
    order = np.argsort(d)
    fig, ax = plt.subplots(figsize=(COL, 2.4))
    cols = [C_MAIN if CATS[i] != "3_delete_object_80" else C_ALT for i in order]
    ax.barh(range(10), [d[i] for i in order], color=cols, height=0.68)
    ax.axvspan(-0.11, 0.11, color=C_GREY, alpha=0.22, lw=0)
    ax.set_yticks(range(10))
    ax.set_yticklabels([CAT_SHORT[i] for i in order])
    ax.set_xlabel("$\\Delta$ ImageReward  (without Phase 2 $-$ full)")
    ax.set_title(f"Per-category effect at $h={h:g}$")
    ax.annotate("run-to-run noise", (0, 9.6), fontsize=6, color=C_GREY,
                ha="center", va="bottom")
    ax.annotate("no target growth needed", (d[3], 0), textcoords="offset points",
                xytext=(8, 0), fontsize=6, color=C_ALT, va="center")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig_beta_category.png"))
    plt.close(fig)


# --------------------------------------------------------------------------- #
# F7: composition rule
# --------------------------------------------------------------------------- #
def fig_anchoring():
    variants = [
        ("cumulative prob.,\nno explicit $N$", os.path.join(EXP, "pie_edit_rewrite_minimal_m14_h0.6_l0.5")),
        ("binary,\nno explicit $N$", os.path.join(EXP, "pie_edit_rewrite_minimal_m14_h0.6_cum0_N0")),
        ("binary $+$\nexplicit $N{=}2$", arm_dir(0.60)),
    ]
    dfs = [load_per_case(p) for _, p in variants]
    fig, axes = plt.subplots(1, 3, figsize=(COL2, 2.0))
    for ax, m, lab, better in [(axes[0], "psnr", "PSNR (dB)", "higher"),
                               (axes[1], "lpips", "LPIPS", "lower"),
                               (axes[2], "ir", "ImageReward", "higher")]:
        v = [overall(d, m) for d in dfs]
        cols = [C_GREY, C_GREY, C_MAIN]
        ax.bar(range(3), v, color=cols, width=0.6)
        for i, vi in enumerate(v):
            ax.annotate(f"{vi:.3f}" if m != "psnr" else f"{vi:.2f}",
                        (i, vi), textcoords="offset points", xytext=(0, 2),
                        ha="center", fontsize=6.5)
        ax.set_xticks(range(3))
        ax.set_xticklabels([n for n, _ in variants], fontsize=6.2)
        ax.set_title(f"{lab}  ({better} better)", pad=3)
        ax.set_ylim(0, max(v) * 1.18)
    fig.suptitle("Composition rule and coarse anchoring, all at $h=0.60$", y=1.03)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig_anchoring.png"))
    plt.close(fig)


# --------------------------------------------------------------------------- #
# F8: the per-case optimum is not predictable
# --------------------------------------------------------------------------- #
def fig_besth_vs_cv(sim_all):
    ir = sim_all.S[:, METRICS.index("ir"), :]        # (A, C)
    best = sim_all.h[ir.argmax(axis=0)]
    cv = sim_all.cv

    fig, ax = plt.subplots(figsize=(COL, 2.4))
    rng = np.random.default_rng(0)
    ax.scatter(cv, best + rng.normal(0, 0.004, len(best)), s=3.2, alpha=0.3,
               color=C_MAIN, edgecolor="none")
    q = np.quantile(cv, np.linspace(0, 1, 9))
    xm, ym = [], []
    for lo, hi in zip(q[:-1], q[1:]):
        s = (cv >= lo) & (cv < hi)
        if s.sum() > 5:
            xm.append(cv[s].mean()); ym.append(np.median(best[s]))
    ax.plot(xm, ym, "-o", color=C_ACC, ms=3.5, lw=1.3, label="binned median")
    r = np.corrcoef(cv, best)[0, 1]
    ax.annotate(f"Pearson $\\rho={r:+.2f}$", (0.97, 0.06), xycoords="axes fraction",
                ha="right", fontsize=7, color=C_GREY)
    ax.set_xlabel("coefficient of variation $c_k$")
    ax.set_ylabel("per-case optimal $h$")
    ax.set_title("The per-case optimum spans the whole range at every $c_k$")
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig_besth_vs_cv.png"))
    plt.close(fig)


# --------------------------------------------------------------------------- #
# F9: qualitative effect of Phase 2
# --------------------------------------------------------------------------- #
def fig_beta_qualitative(h=0.52):
    from PIL import Image
    cases = [("2_add_object_80", "221000000008", "add object"),
             ("9_change_style_80", "922000000001", "style transfer")]
    full, nob = arm_dir(h), arm_dir(h, "_noBeta")
    fig, axes = plt.subplots(2, 3, figsize=(COL2 * 0.72, 4.3))
    for r, (cat, cid, tag) in enumerate(cases):
        paths = [os.path.join(full, cat, cid, "source.jpg"),
                 os.path.join(full, cat, cid, "target.jpg"),
                 os.path.join(nob, cat, cid, "target.jpg")]
        for c, (p, t) in enumerate(zip(paths, ["source", "full pipeline",
                                               "without Phase 2"])):
            ax = axes[r, c]
            if os.path.exists(p):
                ax.imshow(Image.open(p))
            ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
            for sp in ax.spines.values():
                sp.set_linewidth(0.4)
            if r == 0:
                ax.set_title(t, pad=3)
            if c == 0:
                ax.set_ylabel(tag, fontsize=7.5)
    fig.tight_layout(pad=0.3)
    fig.savefig(os.path.join(OUT, "fig_beta_qualitative.png"))
    plt.close(fig)


# --------------------------------------------------------------------------- #
def main():
    print("loading ...")
    arms = load_arms()
    nob = load_arms("_noBeta", hs=[0.52, 0.54, 0.60])
    attn = load_attn()
    keys = sorted(set(attn.index) & set(arms[0.52].index))
    dev_keys = [k for k in keys if not k.startswith(HOLDOUT + "/")]
    print(f"  {len(arms)} fixed arms, {len(nob)} ablated arms, "
          f"{len(keys)} cases ({len(dev_keys)} dev)")

    sim_all = Sim(arms, attn, keys)
    sim_dev = sim_all.subset(sim_all.cat != HOLDOUT)

    print("F1 cv decomposition");   fig_cv_decomposition(attn)
    print("F2 fixed frontier");     fig_frontier_h(arms)

    print("grid search (360 configs) ...")
    grid, cvs, kms = grid_search(sim_dev)
    grid = add_utility(grid, sim_dev)

    print("F3 adaptive frontier")
    paper, cons, _ = fig_adaptive_frontier(sim_dev, grid)
    print("F4 protocol (+ 9 leave-one-category-out searches)")
    consensus, flat = fig_protocol(sim_dev, grid, cvs, kms)

    print("F5 phase-2 frontier");   fig_beta(arms, nob)
    print("F6 phase-2 categories"); fig_beta_category(arms, nob)
    print("F7 anchoring");          fig_anchoring()
    # F8 (best-h vs CV) removed together with Sec. V-G: the per-case-oracle /
    # threshold-predictability analysis is out of scope for this paper.
    print("F9 phase-2 qualitative"); fig_beta_qualitative()

    best = grid.loc[grid["u"].idxmax()]
    print("\n--- numbers to cross-check against the manuscript ---")
    print(f"grid optimum      (c_max, k_max) = ({best['cv_max']:.3f}, {best['k_max']:.2f})"
          f"   u = {best['u']:.3f}")
    print(f"LOCO consensus    (c_max, k_max) = ({consensus[0]:.3f}, {consensus[1]:.2f})")
    print(f"flat region (u >= max-0.05)      = {flat*100:.0f}% of the grid")
    print(f"ours   (0.20,0.60): IR {paper['ir']:.3f}  SSIM {paper['ssim']:.3f}  "
          f"LPIPS {paper['lpips']:.4f}  PSNR {paper['psnr']:.2f}")
    print(f"cons.  (0.15,0.55): IR {cons['ir']:.3f}  SSIM {cons['ssim']:.3f}  "
          f"LPIPS {cons['lpips']:.4f}  PSNR {cons['psnr']:.2f}")
    print(f"\nwrote figures to {OUT}")


if __name__ == "__main__":
    main()
