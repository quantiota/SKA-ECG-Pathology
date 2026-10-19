#!/usr/bin/env python3
"""Entropy figure of one run, as in SKA-ECG-Heart-Rate-Variability (ecg-ska-engine/plot_results.py),
read from the run CSV instead of the database.

Two panels on the step index (one step per wave, five per cycle), coloured by transition:
    H(k)                       the entropy
    P = exp(-|dH / H|)         the transition probability

Usage
    python plot_entropy.py results                     # every results/<record>/ska_<record>_runs.csv
    python plot_entropy.py results ptb104 ptb049_s0173 # some records
        -> results/<record>/figures/ska_<record>_cdot_cos_scale25.png
Requires: numpy, pandas, matplotlib
"""
import pathlib
import sys

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

INK, MUTE, GRID, BG = "#1f1f1d", "#6b6a63", "#e6e5df", "#fcfcfb"
C = dict(zip("PQRST", ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]))
TR = ["P-Q", "Q-R", "R-S", "S-T", "T-P"]
CT = {t: C[t[-1]] for t in TR}


def style(a):
    a.set_facecolor(BG); a.grid(color=GRID, lw=.6); a.set_axisbelow(True)
    a.tick_params(colors=MUTE, labelsize=8)
    for s in ("top", "right"):
        a.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        a.spines[s].set_color(GRID)


def plot(folder, inp="cdot_cos"):
    rec = folder.name
    d = pd.read_csv(folder / f"ska_{rec}_runs.csv", usecols=["input", "scale", "transition", "event_index", "entropy"])
    d = d[d.input == inp]
    for scale, r in d.groupby("scale"):
        r = r.sort_values("event_index")
        tr = r.transition.values
        H = r.entropy.values.astype(float)
        k = np.arange(1, H.size + 1)
        P = np.full(H.size, np.nan)
        P[1:] = np.exp(-np.abs(np.diff(H) / H[1:]))
        fig, ax = plt.subplots(2, 1, figsize=(15, 9), sharex=True, facecolor=BG, gridspec_kw={"hspace": 0.12})
        for t in TR:
            m = tr == t
            ax[0].plot(k[m], H[m], ".", color=CT[t], ms=3, label=t.replace("-", "→"))
            ax[1].plot(k[m], P[m], ".", color=CT[t], ms=3)
        ax[0].axhline(0, color=MUTE, lw=.7, ls=(0, (3, 3)))
        ax[0].set_ylabel("H", color=MUTE); ax[1].set_ylabel("P = exp(−|ΔH/H|)", color=MUTE)
        ax[1].set_xlabel("step = wave index (5 per cycle)", color=MUTE)
        for A in ax:
            style(A)
        ax[0].legend(ncol=5, frameon=False, loc="lower right", bbox_to_anchor=(1, 1.0), markerscale=3, labelcolor=INK)
        fig.suptitle(f"SKA on the ECG wave stream — record {rec}, input {inp}, scale {scale:g}, "
                     f"{H.size:,} waves ({H.size // 5:,} cycles)", x=0.04, ha="left", color=INK, fontsize=13)
        out = folder / "figures" / f"ska_{rec}_{inp}_scale{scale:g}.png"
        out.parent.mkdir(exist_ok=True)
        fig.savefig(out, dpi=140, bbox_inches="tight", facecolor=BG)
        plt.close(fig)
        print(f"wrote {out}")


def main():
    results = pathlib.Path(sys.argv[1])
    names = sys.argv[2:] or sorted(p.name for p in results.iterdir() if (p / f"ska_{p.name}_runs.csv").exists())
    for n in names:
        plot(results / n)


if __name__ == "__main__":
    main()
