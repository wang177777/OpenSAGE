"""Generate the submitted data figures from the public release tables.

Figure 1 is a study-design diagram retained as submitted vector artwork. This
script rebuilds Figures 2-4 and Supplementary Figure S1 from the released CSV
files and writes the journal-ready files under ``figures/submission`` together
with PNG/SVG verification copies under ``figures/generated``.
"""

from __future__ import annotations

import csv
import statistics
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "data/publication_tables"
SUPPLEMENTARY = ROOT / "data/supplementary"
GENERATED = ROOT / "figures/generated"
SUBMISSION = ROOT / "figures/submission"
SUPPLEMENTARY_FIGURES = ROOT / "figures/supplementary"

BLUE = "#2166AC"
ORANGE = "#D6604D"
GREEN = "#238B45"
GRAY = "#6B7280"
RED = "#B2182B"
LIGHT_GRAY = "#B8C2CC"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize_svg(path: Path) -> None:
    """Remove generator-only trailing spaces while preserving SVG content."""
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(line.rstrip() for line in lines) + "\n", encoding="utf-8")


def save_submission_figure(fig: plt.Figure, stem: str) -> None:
    """Save matching verification and journal-upload versions of a data figure."""
    GENERATED.mkdir(parents=True, exist_ok=True)
    SUBMISSION.mkdir(parents=True, exist_ok=True)
    fig.savefig(GENERATED / f"{stem}.png", dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(GENERATED / f"{stem}.svg", bbox_inches="tight", facecolor="white")
    tiff = SUBMISSION / f"{stem}.tiff"
    fig.savefig(tiff, dpi=600, bbox_inches="tight", facecolor="white", pil_kwargs={"compression": "tiff_lzw"})
    plt.close(fig)

    # Journal artwork is stored as flattened RGB LZW TIFF at 600 dpi.
    temporary = tiff.with_suffix(".rgb.tiff")
    with Image.open(tiff) as image:
        rgba = image.convert("RGBA")
        white = Image.new("RGB", rgba.size, "white")
        white.paste(rgba, mask=rgba.getchannel("A"))
        white.save(temporary, format="TIFF", compression="tiff_lzw", dpi=(600, 600))
    temporary.replace(tiff)


def generate_figure_2(t001: list[dict[str, str]]) -> None:
    ordered = sorted(t001, key=lambda row: float(row["Final DGQC score"]))
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    for index, row in enumerate(ordered, start=1):
        color = BLUE if row["Phase"] == "Stage 1" else ORANGE
        confirmed_defect = row["Expert-confirmed CD"] == "yes"
        ax.scatter(
            index,
            float(row["Final DGQC score"]),
            s=28,
            color="white" if confirmed_defect else color,
            edgecolor=color,
            linewidth=1.1,
            zorder=3,
        )
    ax.axhline(70, color=GREEN, linestyle="--", linewidth=1.1)
    ax.axhline(85, color=GRAY, linestyle=":", linewidth=1.1)
    ax.set_xlim(0, 57)
    ax.set_ylim(45, 90)
    ax.set_xlabel("OpenSAGE outputs ordered by final DGQC score")
    ax.set_ylabel("Final DGQC score")
    ax.set_title("OpenSAGE final DGQC score distribution", loc="left", fontweight="bold")
    legend = [
        Line2D([0], [0], marker="o", linestyle="none", markerfacecolor=BLUE, markeredgecolor=BLUE, label="Stage 1"),
        Line2D([0], [0], marker="o", linestyle="none", markerfacecolor=ORANGE, markeredgecolor=ORANGE, label="Stage 2"),
        Line2D([0], [0], marker="o", linestyle="none", markerfacecolor="white", markeredgecolor=GRAY, label="Expert-confirmed critical defect"),
        Line2D([0], [0], color=GREEN, linestyle="--", label="Expert-review eligibility score threshold (70)"),
        Line2D([0], [0], color=GRAY, linestyle=":", label="High-quality score threshold (85)"),
    ]
    ax.legend(
        handles=legend,
        frameon=True,
        facecolor="white",
        framealpha=1.0,
        edgecolor="none",
        fontsize=7.4,
        loc="upper left",
        ncol=2,
        handlelength=2.2,
        columnspacing=1.2,
    )
    fig.tight_layout()
    save_submission_figure(fig, "Figure_2")


def generate_figure_3(t002: list[dict[str, str]]) -> None:
    paired: list[tuple[str, float, float]] = []
    for disease in sorted({row["Disease"] for row in t002}):
        rows = [row for row in t002 if row["Disease"] == disease]
        direct = float(next(row for row in rows if row["Model"] == "GPT-5.5")["Final DGQC score"])
        workflow = float(next(row for row in rows if row["Model"] == "OpenSAGE")["Final DGQC score"])
        paired.append((disease, direct, workflow))
    paired.sort(key=lambda item: item[2] - item[1])

    fig, ax = plt.subplots(figsize=(7.4, 5.1))
    y = list(range(len(paired)))
    for yi, (_, direct, workflow) in zip(y, paired):
        ax.plot([direct, workflow], [yi, yi], color=LIGHT_GRAY, linewidth=1.4, zorder=1)
    ax.scatter([item[1] for item in paired], y, color=GRAY, s=32, label="Direct GPT-5.5", zorder=2)
    ax.scatter([item[2] for item in paired], y, color=BLUE, s=32, label="OpenSAGE workflow", zorder=2)
    ax.set_yticks(y, [item[0] for item in paired])
    ax.set_xlim(0, 100)
    ax.set_xlabel("Final DGQC score")
    mean_difference = statistics.mean(workflow - direct for _, direct, workflow in paired)
    ax.set_title(
        f"Matched same-model-label comparison\nMean paired difference: {mean_difference:.2f} points",
        loc="left",
        fontweight="bold",
    )
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    fig.tight_layout()
    save_submission_figure(fig, "Figure_3")


def generate_figure_4(s14: list[dict[str, str]]) -> None:
    open_row = next(row for row in s14 if row["Group"] == "OpenSAGE full set")
    base_row = next(row for row in s14 if row["Group"] == "Baseline comparative outputs")
    domains = ["CD1", "CD2", "CD3", "CD4", "CD5", "CD6"]
    y = list(range(len(domains)))
    open_counts = [int(open_row[key]) for key in domains]
    base_counts = [int(base_row[key]) for key in domains]
    open_values = [100 * count / 56 for count in open_counts]
    base_values = [100 * count / 70 for count in base_counts]

    fig, ax = plt.subplots(figsize=(7.0, 4.6))
    for yi, left, right in zip(y, open_values, base_values):
        ax.plot([left, right], [yi, yi], color="#CBD5E1", linewidth=2, zorder=1)
    ax.scatter(open_values, y, color=BLUE, s=42, label="OpenSAGE (n = 56)", zorder=2)
    ax.scatter(base_values, y, color=RED, marker="s", s=40, label="Direct-generation comparators (n = 70)", zorder=2)
    for yi, value, count in zip(y, open_values, open_counts):
        ax.text(value + 1.3, yi - 0.12, f"{count}/56", fontsize=7, color=BLUE)
    for yi, value, count in zip(y, base_values, base_counts):
        ax.text(value + 1.3, yi + 0.17, f"{count}/70", fontsize=7, color=RED)
    ax.set_yticks(y, domains)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("Outputs with expert-confirmed critical-defect subtype (%)")
    ax.set_title("Expert-confirmed critical-defect classifications", loc="left", fontweight="bold")
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    fig.tight_layout()
    save_submission_figure(fig, "Figure_4")


def generate_supplementary_figure_s1() -> None:
    rows = read_csv(SUPPLEMENTARY / "Supplementary_Data_3_Figure_S1_Source.csv")
    sets = ["OpenSAGE full 56", "Stage 1 OpenSAGE 46", "Stage 2 OpenSAGE 10"]
    domains = [f"D{i}" for i in range(1, 8)]
    lookup = {(row["Set"], row["Domain"]): float(row["Mean score"]) for row in rows}

    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    for name, color, marker in zip(sets, [BLUE, GRAY, ORANGE], ["o", "s", "^"]):
        ax.plot(domains, [lookup[(name, domain)] for domain in domains], marker=marker, color=color, label=name)
    ax.set_ylim(1, 7)
    ax.set_ylabel("Mean D1-D7 rating")
    ax.set_xlabel("DGQC domain")
    ax.set_title("OpenSAGE mean domain profile from the common expert-rating round", loc="left", fontweight="bold")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()

    SUPPLEMENTARY_FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(SUPPLEMENTARY_FIGURES / "Supplementary_Figure_S1.png", dpi=300, bbox_inches="tight", facecolor="white")
    svg_path = SUPPLEMENTARY_FIGURES / "Supplementary_Figure_S1.svg"
    fig.savefig(
        svg_path,
        bbox_inches="tight",
        facecolor="white",
        metadata={"Creator": "OpenSAGE public figure generator", "Date": "2026-07-21"},
    )
    normalize_svg(svg_path)
    fixed_time = datetime(2026, 7, 21, tzinfo=timezone.utc)
    fig.savefig(
        SUPPLEMENTARY_FIGURES / "Supplementary_Figure_S1.pdf",
        bbox_inches="tight",
        facecolor="white",
        metadata={
            "Title": "Supplementary Figure S1: OpenSAGE mean domain profile",
            "Author": "OpenSAGE study group",
            "Creator": "OpenSAGE public figure generator",
            "CreationDate": fixed_time,
            "ModDate": fixed_time,
        },
    )
    tiff = SUPPLEMENTARY_FIGURES / "Supplementary_Figure_S1_600dpi_LZW.tiff"
    fig.savefig(tiff, dpi=600, bbox_inches="tight", facecolor="white", pil_kwargs={"compression": "tiff_lzw"})
    plt.close(fig)
    temporary = tiff.with_suffix(".rgb.tiff")
    with Image.open(tiff) as image:
        rgba = image.convert("RGBA")
        white = Image.new("RGB", rgba.size, "white")
        white.paste(rgba, mask=rgba.getchannel("A"))
        white.save(temporary, format="TIFF", compression="tiff_lzw", dpi=(600, 600))
    temporary.replace(tiff)


def main() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.facecolor": "white",
            "svg.hashsalt": "OpenSAGE-20260720",
        }
    )
    t001 = read_csv(TABLES / "T001_56_Disease_List.csv")
    t002 = read_csv(TABLES / "T002_Matched_80.csv")
    generate_figure_2(t001)
    generate_figure_3(t002)
    generate_figure_4(read_csv(TABLES / "S14.csv"))
    generate_supplementary_figure_s1()
    print("PASS - rebuilt submitted Figures 2-4 and Supplementary Figure S1 from public CSV files")


if __name__ == "__main__":
    main()
