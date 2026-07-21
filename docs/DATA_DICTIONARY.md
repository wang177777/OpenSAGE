# Data dictionary

## Public supplementary files

- `data/supplementary/Supplementary_Data_1.xlsx`: README/CRediT, output tables T001-T002, Tables S01-S10, DGQC template, data dictionary, output identity/outcome metadata, and terminology crosswalk.
- `data/supplementary/Supplementary_Data_2.xlsx`: Tables S11-S14, including analysis-set definitions and S12B descriptive domain summaries.
- `data/supplementary/Supplementary_Data_3_Figure_S1_Source.csv`: long-format source for Supplementary Figure S1.
- `data/publication_tables/*.csv`: one CSV export per released table for machine-readable checks.

## Core output-level fields

| Field | Definition |
|---|---|
| `Output ID` | Unique study output identifier. |
| `Phase` | Stage 1 non-comparative OpenSAGE subset or Stage 2 matched comparison subset. |
| `Disease` | Disease label used consistently across the public tables and output filenames. |
| `Blinded output ID` | Identifier shown in the blinded review package. |
| `Model` | System label associated with the blinded output after scoring. |
| `Final DGQC score` | Primary continuous endpoint reported for every output. |
| `Expert-confirmed CD` | Expert-confirmed critical-defect status. |
| `Usable draft` | Study-defined expert-review eligibility: final DGQC score ≥70 with no expert-confirmed critical defect. |

S10 provides output identity, scope-classification, and reported DGQC outcome fields for the OpenSAGE set.

## Domain-summary files

S12B and Supplementary Data 3 contain mean D1-D7 values for the full OpenSAGE set and the Stage 1/Stage 2 subsets. All domain summaries derive from the same blinded expert-rating round.

Reviewer-level DGQC maps each 1-7 domain score to 0-100 and applies the Table S08 weights: `DGQC = Σ w_d × (D_d − 1) / 6`. The released D1-D7 means are descriptive component summaries and are not a separate continuous endpoint.

## Manifests

- `release_sha256.csv`: hashes of the files included in this public package.

## Controlled research fields

Historical generation inputs and evaluated document files, reviewer IDs, rating-level D1-D7 scores, rating-level critical-defect flags, free-text comments, expert identity mappings, pre-unblinding mapping keys, and expert-review workbooks remain outside the public package. Their variable definitions are listed in `data/publication_tables/Data_Dictionary.csv`.

## Missing values and numeric formatting

Empty cells are represented as empty CSV fields. Public tables use display precision appropriate to the manuscript; some output-level scores are rounded to two decimals. Scripts use the released values and compare rounded publication results where appropriate.
