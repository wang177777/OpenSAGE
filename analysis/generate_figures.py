"""Generate data-aligned audit figures from the 14 July 2026 public tables.

The submitted artwork is retained under figures/submission. These generated plots
provide transparent data-to-figure checks and are not claimed to be pixel-identical.
"""

from __future__ import annotations

import csv
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "data/publication_tables"
OUT = ROOT / "figures/generated"
BLUE = "#2166AC"
ORANGE = "#D6604D"
GRAY = "#6B7280"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def save(fig: plt.Figure, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{name}.png", dpi=300, bbox_inches="tight")
    fig.savefig(OUT / f"{name}.svg", bbox_inches="tight")
    plt.close(fig)


plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.facecolor": "white",
    }
)

t001 = read_csv(TABLES / "T001_56_Disease_List.csv")
t002 = read_csv(TABLES / "T002_Matched_80.csv")

# Figure 1: study flow.
fig, ax = plt.subplots(figsize=(8.2, 3.4))
ax.axis("off")
nodes = [
    (0.05, 0.58, "Stage 1\n46 OpenSAGE outputs"),
    (0.37, 0.72, "Stage 2\n10 OpenSAGE outputs"),
    (0.37, 0.30, "Stage 2\n70 direct-generation outputs"),
    (0.72, 0.72, "OpenSAGE analysis set\n56 outputs"),
    (0.72, 0.30, "Matched comparison\n80 outputs"),
]
for x, y, label in nodes:
    ax.text(
        x,
        y,
        label,
        transform=ax.transAxes,
        ha="left",
        va="center",
        bbox={"boxstyle": "round,pad=0.5", "facecolor": "#EEF4FA", "edgecolor": BLUE},
    )
for start, end in [((0.28, 0.58), (0.70, 0.72)), ((0.59, 0.72), (0.70, 0.72)), ((0.59, 0.30), (0.70, 0.30))]:
    ax.annotate("", xy=end, xytext=start, xycoords="axes fraction", arrowprops={"arrowstyle": "->", "color": GRAY})
ax.set_title("OpenSAGE/DGQC two-stage evaluation flow (126 outputs; 1,512 ratings)", loc="left", fontweight="bold")
save(fig, "Figure_1_flow_audit")

# Figure 2: OpenSAGE score distribution.
stage1 = [float(row["Human-updated DGQC"]) for row in t001 if row["Phase"] == "Stage 1"]
stage2 = [float(row["Human-updated DGQC"]) for row in t001 if row["Phase"] == "Stage 2"]
fig, ax = plt.subplots(figsize=(6.2, 4.3))
box = ax.boxplot([stage1, stage2], tick_labels=["Stage 1 (n=46)", "Stage 2 (n=10)"], patch_artist=True, widths=0.5)
for patch, color in zip(box["boxes"], [BLUE, ORANGE]):
    patch.set_facecolor(color)
    patch.set_alpha(0.25)
for index, values in enumerate([stage1, stage2], start=1):
    offsets = [((i % 7) - 3) * 0.012 for i in range(len(values))]
    ax.scatter([index + offset for offset in offsets], values, s=18, alpha=0.75, color=[BLUE, ORANGE][index - 1])
ax.axhline(70, color="#238B45", linestyle="--", linewidth=1, label="Expert-review eligibility score threshold")
ax.axhline(85, color=GRAY, linestyle=":", linewidth=1, label="High-quality score threshold")
ax.set_ylabel("Adjudication-adjusted DGQC")
ax.set_ylim(0, 100)
ax.set_title("OpenSAGE score distribution", loc="left", fontweight="bold")
ax.legend(frameon=False, fontsize=8, loc="lower right")
save(fig, "Figure_2_opensage_distribution_audit")

# Figure 3: same-foundation matched comparison.
by_disease: dict[str, list[dict[str, str]]] = defaultdict(list)
for row in t002:
    by_disease[row["Disease"]].append(row)
diseases = sorted(by_disease)
gpt = []
opensage = []
for disease in diseases:
    rows = by_disease[disease]
    gpt.append(float(next(row for row in rows if row["Model"] == "GPT-5.5")["Human-updated DGQC"]))
    opensage.append(float(next(row for row in rows if row["Model"] == "OpenSAGE")["Human-updated DGQC"]))
fig, ax = plt.subplots(figsize=(6.2, 4.6))
for i, disease in enumerate(diseases):
    ax.plot([0, 1], [gpt[i], opensage[i]], color="#B8C2CC", linewidth=1)
    ax.scatter([0, 1], [gpt[i], opensage[i]], color=[GRAY, BLUE], s=28)
ax.set_xticks([0, 1], ["Direct GPT-5.5", "OpenSAGE (GPT-5.5)"])
ax.set_xlim(-0.25, 1.25)
ax.set_ylim(0, 100)
ax.set_ylabel("Adjudication-adjusted DGQC")
ax.set_title(f"Matched same-foundation comparison\nMean paired difference: {statistics.mean(o-g for o,g in zip(opensage,gpt)):.2f}", loc="left", fontweight="bold")
save(fig, "Figure_3_same_foundation_audit")

# Figure 4: model summary and disease-level pooled differences.
models = []
for model in ["OpenSAGE", "GPT-5.5", "Claude-Opus-4.7", "Gemini-3.1-Pro", "GLM-5.1", "Deepseek-v4", "Qwen-3.6-Plus", "Doubao-2.0-Pro"]:
    scores = [float(row["Human-updated DGQC"]) for row in t002 if row["Model"] == model]
    models.append((model, statistics.mean(scores)))
pooled_differences = []
for disease in diseases:
    rows = by_disease[disease]
    current = float(next(row for row in rows if row["Model"] == "OpenSAGE")["Human-updated DGQC"])
    pooled = statistics.mean(float(row["Human-updated DGQC"]) for row in rows if row["Model group"] == "baseline")
    pooled_differences.append((disease, current - pooled))
fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), gridspec_kw={"width_ratios": [1, 1.15]})
labels = [item[0] for item in models][::-1]
means = [item[1] for item in models][::-1]
axes[0].barh(labels, means, color=[BLUE if label == "OpenSAGE" else GRAY for label in labels])
axes[0].set_xlim(0, 100)
axes[0].set_xlabel("Mean adjudication-adjusted DGQC")
axes[0].set_title("A. Model summaries", loc="left", fontweight="bold")
diff_labels = [item[0] for item in pooled_differences][::-1]
diff_values = [item[1] for item in pooled_differences][::-1]
axes[1].barh(diff_labels, diff_values, color=BLUE)
axes[1].axvline(0, color="black", linewidth=0.8)
axes[1].set_xlabel("OpenSAGE minus pooled baseline")
axes[1].set_title(f"B. Disease-level differences (mean {statistics.mean(diff_values):.2f})", loc="left", fontweight="bold")
fig.tight_layout()
save(fig, "Figure_4_matched_comparison_audit")

# Supplementary Figure S1: mixed-definition raw domain means.
s1 = read_csv(ROOT / "data/supplementary/Supplementary_Data_3_Figure_S1_Source.csv")
sets = ["OpenSAGE full 56", "Stage 1 OpenSAGE 46", "Stage 2 OpenSAGE 10"]
domains = [f"D{i}" for i in range(1, 8)]
lookup = {(row["Set"], row["Domain"]): float(row["Mean score"]) for row in s1}
fig, ax = plt.subplots(figsize=(7.2, 4.4))
for name, color, marker in zip(sets, [BLUE, GRAY, ORANGE], ["o", "s", "^"]):
    ax.plot(domains, [lookup[(name, domain)] for domain in domains], marker=marker, label=name, color=color)
ax.set_ylim(1, 7)
ax.set_ylabel("Mean raw domain score")
ax.set_title("Supplementary Figure S1: OpenSAGE raw domain profile", loc="left", fontweight="bold")
ax.legend(frameon=False, fontsize=8)
save(fig, "Supplementary_Figure_S1_raw_domains_audit")

print(f"PASS - generated 10 files under {OUT.relative_to(ROOT)}")
