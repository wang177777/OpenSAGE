"""Recompute public DGQC results and cross-file consistency checks."""

from __future__ import annotations

import csv
import itertools
import json
import statistics
from collections import defaultdict
from pathlib import Path

from dgqc_scoring import dgqc_score


ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "data/publication_tables"


def read_csv(name: str) -> list[dict[str, str]]:
    with (TABLES / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def close(actual: float, expected: float, tolerance: float = 0.015) -> None:
    if abs(actual - expected) > tolerance:
        raise AssertionError(f"{actual} differs from {expected} by more than {tolerance}")


def exact_sign_flip_p(differences: list[float]) -> float:
    """Two-sided exact paired sign-flip P value using the absolute mean statistic."""
    observed = abs(statistics.mean(differences))
    extreme = 0
    total = 2 ** len(differences)
    for signs in itertools.product((-1.0, 1.0), repeat=len(differences)):
        statistic = abs(statistics.mean(s * d for s, d in zip(signs, differences)))
        if statistic >= observed - 1e-12:
            extreme += 1
    return extreme / total


def parse_fraction(value: str) -> tuple[int, int]:
    numerator, denominator = value.split("/", maxsplit=1)
    return int(numerator), int(denominator)


t001 = read_csv("T001_56_Disease_List.csv")
t002 = read_csv("T002_Matched_80.csv")
s01 = read_csv("S01.csv")
s02 = read_csv("S02.csv")
s12a = read_csv("S12A.csv")
s12b = read_csv("S12B.csv")
s13 = read_csv("S13.csv")

if len(t001) != 56 or len(t002) != 80:
    raise AssertionError("T001/T002 output counts are not 56/80")


def summarize(rows: list[dict[str, str]]) -> dict[str, float | int]:
    values = [float(row["Final DGQC score"]) for row in rows]
    return {
        "n": len(rows),
        "mean": statistics.mean(values),
        "median_from_rounded_public_values": statistics.median(values),
        "expert_confirmed_cd": sum(row["Expert-confirmed CD"] == "yes" for row in rows),
        "usable": sum(row["Usable draft"] == "yes" for row in rows),
    }


full = summarize(t001)
r1 = summarize([row for row in t001 if row["Phase"] == "Stage 1"])
r2 = summarize([row for row in t001 if row["Phase"] == "Stage 2"])

close(float(full["mean"]), 72.63)
close(float(r1["mean"]), 72.82)
close(float(r2["mean"]), 71.78)
assert (full["usable"], full["expert_confirmed_cd"]) == (43, 8)
assert (r1["usable"], r1["expert_confirmed_cd"]) == (35, 8)
assert (r2["usable"], r2["expert_confirmed_cd"]) == (8, 0)

reported_sets = {row["Set"]: row for row in s12a}
for name, derived in [
    ("OpenSAGE full 56", full),
    ("Stage 1 OpenSAGE 46", r1),
    ("Stage 2 OpenSAGE 10", r2),
]:
    row = reported_sets[name]
    assert int(row["n"]) == derived["n"]
    close(float(row["Mean DGQC"]), float(derived["mean"]))
    assert parse_fraction(row["Expert-confirmed CD"])[0] == derived["expert_confirmed_cd"]
    assert parse_fraction(row["Usable draft"])[0] == derived["usable"]

by_disease: dict[str, list[dict[str, str]]] = defaultdict(list)
for row in t002:
    by_disease[row["Disease"]].append(row)
if set(map(len, by_disease.values())) != {8}:
    raise AssertionError("Every Stage 2 disease must have eight system rows")


def paired_differences(score_field: str, comparator: str) -> list[float]:
    values = []
    for disease in sorted(by_disease):
        rows = by_disease[disease]
        opensage = float(next(row for row in rows if row["Model"] == "OpenSAGE")[score_field])
        if comparator == "pooled":
            baseline = statistics.mean(
                float(row[score_field]) for row in rows if row["Model group"] == "baseline"
            )
        else:
            baseline = float(next(row for row in rows if row["Model"] == comparator)[score_field])
        values.append(opensage - baseline)
    return values


comparisons = {
    "final_gpt55": paired_differences("Final DGQC score", "GPT-5.5"),
    "final_pooled": paired_differences("Final DGQC score", "pooled"),
    "reviewer_mean_gpt55": paired_differences("Reviewer-mean DGQC", "GPT-5.5"),
    "reviewer_mean_pooled": paired_differences("Reviewer-mean DGQC", "pooled"),
}
expected_means = {
    "final_gpt55": 19.54,
    "final_pooled": 42.54,
    "reviewer_mean_gpt55": 15.86,
    "reviewer_mean_pooled": 38.89,
}
for key, differences in comparisons.items():
    close(statistics.mean(differences), expected_means[key])
    close(exact_sign_flip_p(differences), 0.00195, tolerance=0.00001)

s01_by_contrast = {row["Contrast"]: row for row in s01}
contrast_keys = {
    "final_gpt55": "Final DGQC score: OpenSAGE vs direct GPT-5.5",
    "final_pooled": "Final DGQC score: OpenSAGE vs pooled direct-generation comparator",
    "reviewer_mean_gpt55": "Reviewer-mean DGQC: OpenSAGE vs direct GPT-5.5",
    "reviewer_mean_pooled": "Reviewer-mean DGQC: OpenSAGE vs pooled direct-generation comparator",
}
for key, contrast in contrast_keys.items():
    row = s01_by_contrast[contrast]
    close(float(row["Mean difference"]), statistics.mean(comparisons[key]))
    close(float(row["Exact paired permutation P"]), exact_sign_flip_p(comparisons[key]), 0.00001)

model_rows = {row["Model"]: row for row in s13}
for model, row in model_rows.items():
    model_scores = [
        float(item["Final DGQC score"]) for item in t002 if item["Model"] == model
    ]
    assert len(model_scores) == int(row["n"]) == 10
    close(statistics.mean(model_scores), float(row["Mean DGQC"]))

figure_s1_path = ROOT / "data/supplementary/Supplementary_Data_3_Figure_S1_Source.csv"
with figure_s1_path.open(encoding="utf-8-sig", newline="") as handle:
    figure_s1 = list(csv.DictReader(handle))
domain_lookup = {(row["Set"], row["Domain"]): float(row["Mean score"]) for row in figure_s1}
for row in s12b:
    profile = {domain: float(row[f"{domain} raw mean"]) for domain in [f"D{i}" for i in range(1, 8)]}
    if not 0.0 <= dgqc_score(profile) <= 100.0:
        raise AssertionError(f"Invalid DGQC profile for {row['Set']}")
    for domain in [f"D{i}" for i in range(1, 8)]:
        close(float(row[f"{domain} raw mean"]), domain_lookup[(row["Set"], domain)], 0.0051)

expected_reconstructed_means = {
    "OpenSAGE full 56": 72.56,
    "Stage 1 OpenSAGE 46": 72.82,
    "Stage 2 OpenSAGE 10": 71.37,
}
for row in s12b:
    profile = {domain: float(row[f"{domain} raw mean"]) for domain in [f"D{i}" for i in range(1, 8)]}
    close(dgqc_score(profile), expected_reconstructed_means[row["Set"]], tolerance=0.06)

stage2_profile = next(row for row in s12b if row["Set"] == "Stage 2 OpenSAGE 10")
stage2_profile_score = dgqc_score(
    {domain: float(stage2_profile[f"{domain} raw mean"]) for domain in [f"D{i}" for i in range(1, 8)]}
)
stage2_reviewer_mean = statistics.mean(
    float(row["Reviewer-mean DGQC"]) for row in t002 if row["Model"] == "OpenSAGE"
)
close(stage2_profile_score, stage2_reviewer_mean, tolerance=0.05)

reliability = {row["Analysis set"]: row for row in s02}
assert reliability["All 126 outputs"]["ICC(2,k) (bootstrap 95% CI)"] == "0.992 (0.990 to 0.993)"
assert reliability["All 126 outputs"]["Gwet AC1 (bootstrap 95% CI)"] == "0.824 (0.768 to 0.876)"

result = {
    "analysis_definition": {
        "rating_round": "one blinded expert-rating round with twelve expert reviewers",
        "primary_continuous_endpoint": "final DGQC score for all 126 outputs",
        "secondary_score_summary": "reviewer-mean DGQC and raw D1-D7 domain summaries from the same rating round",
    },
    "opensage": {"full": full, "stage1": r1, "stage2": r2},
    "matched_comparisons": {
        key: {
            "mean_difference": statistics.mean(values),
            "exact_two_sided_sign_flip_p": exact_sign_flip_p(values),
        }
        for key, values in comparisons.items()
    },
    "reliability_table_validation": {
        "all_output_icc": reliability["All 126 outputs"]["ICC(2,k) (bootstrap 95% CI)"],
        "all_output_gwet_ac1": reliability["All 126 outputs"]["Gwet AC1 (bootstrap 95% CI)"],
        "note": "Published reliability estimates validated across the released tables.",
    },
}

destination = ROOT / "results/reproduced_summary.json"
destination.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2, ensure_ascii=False))
print(f"PASS - wrote {destination.relative_to(ROOT)}")
