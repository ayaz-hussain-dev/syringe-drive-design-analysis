"""Regenerate the study charts from the published CSV records."""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, StrMethodFormatter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/figures"
COLOURS = {"baseline": "#395b78", "revised": "#168273"}


def load_csv(name):
    with (ROOT / "analysis" / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def style(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#dfe5e9", linewidth=0.7, zorder=0)
    ax.tick_params(colors="#414c57")
    ax.set_axisbelow(True)


def save(fig, stem):
    fig.savefig(OUT / (stem + ".png"), dpi=190, facecolor="white")
    fig.savefig(OUT / (stem + ".pdf"), facecolor="white")
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 10,
        "axes.labelcolor": "#243847", "axes.titleweight": "bold",
        "axes.titlesize": 12, "figure.titlesize": 16,
        "axes.labelsize": 10, "legend.fontsize": 9,
        "savefig.bbox": "tight",
    })
    rows = load_csv("fea_results.csv")
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.7), layout="constrained")
    fig.suptitle("Mesh refinement: displacement and reported peak stress", x=0.01, ha="left", fontweight="bold")
    for design in ["baseline", "revised"]:
        group = [r for r in rows if r["design"] == design]
        x = [int(r["mesh_nodes"]) / 1000 for r in group]
        u = [float(r["maximum_total_deformation_mm"]) * 1000 for r in group]
        s = [float(r["maximum_averaged_von_mises_MPa"]) for r in group]
        for ax, values in zip(axes, [u, s]):
            ax.plot(x, values, "-o", color=COLOURS[design], linewidth=2, markersize=5, label=design.title())
            for xx, yy, r in zip(x, values, group):
                offset = (0, 8) if design == "baseline" else (0, -15)
                ax.annotate(r["nominal_element_size_mm"] + " mm", (xx, yy),
                            xytext=offset, textcoords="offset points", ha="center", fontsize=8,
                            color=COLOURS[design])
    axes[0].set(title="Maximum total deformation", xlabel="Mesh nodes (thousands)", ylabel="Deformation (µm)")
    axes[0].set_ylim(1.784, 1.799)
    axes[0].yaxis.set_major_formatter(StrMethodFormatter("{x:.3f}"))
    axes[1].set(title="Global averaged von Mises maximum", xlabel="Mesh nodes (thousands)", ylabel="Stress (MPa)")
    axes[1].set_ylim(.118, .132)
    for ax in axes:
        style(ax)
        ax.legend(frameon=False, loc="upper left")
        ax.xaxis.set_major_locator(MaxNLocator(5))
    fig.get_layout_engine().set(rect=(0, .05, 1, .86))
    fig.text(.01, .01, "Point labels give nominal element size. Lines connect independently remeshed cases; stress peaks may change location.",
             fontsize=8, color="#53626e")
    save(fig, "mesh_sensitivity")

    comp = load_csv("design_comparison.csv")
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.6), layout="constrained")
    fig.suptitle("Base-frame comparison", x=.01, ha="left", fontweight="bold")
    labels = ["Baseline\n3 mm mesh", "Revised\n2 mm mesh"]
    colours = [COLOURS[r["design"]] for r in comp]
    values = [
        [float(r["solid_model_mass_kg"]) * 1000 for r in comp],
        [float(r["selected_max_deformation_mm"]) * 1000 for r in comp],
    ]
    for ax, vals, label, unit, ymax, digits in zip(
            axes, values, ["Solid-model base mass", "Maximum total deformation"],
            ["Mass (g)", "Deformation (µm)"], [440, 2.1], [2, 4]):
        bars = ax.bar(labels, vals, color=colours, width=.54, zorder=3)
        ax.bar_label(bars, labels=[f"{v:.{digits}f}" for v in vals], padding=6, fontsize=11, fontweight="bold")
        ax.set(title=label, ylabel=unit, ylim=(0, ymax))
        style(ax)
    fig.get_layout_engine().set(rect=(0, .07, 1, .85))
    fig.text(.01, .02, "Same 5.835 N load and study material. Mass: −4.26% (16.19 g). Selected deformation: +0.44%.",
             fontsize=9, color="#344d5f")
    save(fig, "base_comparison")
    print("Saved charts to", OUT)


if __name__ == "__main__":
    main()
