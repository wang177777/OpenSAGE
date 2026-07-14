# Data dictionary

## Public supplementary files

- `data/supplementary/Supplementary_Data_1.xlsx`: README/CRediT, output tables T001-T002, Tables S01-S10, DGQC template, data dictionary, anchor audit, and terminology crosswalk.
- `data/supplementary/Supplementary_Data_2.xlsx`: Tables S11-S14, including analysis-set definitions and corrected S12B raw domain summaries.
- `data/supplementary/Supplementary_Data_3_Figure_S1_Source.csv`: long-format source for Supplementary Figure S1.
- `data/publication_tables/*.csv`: one CSV export per released table for machine-readable checks.

## Core output-level fields

| Field | Definition |
|---|---|
| `Output ID` | Unique locked output identifier. |
| `Phase` | Stage 1 formal rerating or Stage 2 matched comparison. |
| `Disease` | Disease label in the locked table; historical spelling is retained in T001. |
| `Blinded output ID` | Identifier shown in the blinded review package. |
| `Model` | Locked system label merged after scoring. |
| `Human-updated DGQC` | Main continuous endpoint; termed adjudication-adjusted DGQC in the manuscript. |
| `Raw mean DGQC` | Mean of original raw expert scores for the Stage 2 output. |
| `Expert-confirmed CD` | Strict dual-adjudicator-confirmed defect status. |
| `Usable draft` | Study-defined expert-review eligibility: adjusted DGQC ≥70 with no strict confirmed defect. |

T001 retains locked spellings such as `Marbug`, `Measle`, and `Yello Fever`. S10 supplies normalized public disease names. The manifests preserve both fields so normalization is auditable rather than silently changing the locked dataset.

## Raw domain files

S12B and Supplementary Data 3 contain mean D1-D7 values for the full OpenSAGE set and Stage 1/Stage 2 subsets. They use the mixed raw-domain definition: formal-rerating raw domains for Stage 1 plus original raw ratings for Stage 2. They do not contain reviewer-level records.

## Manifests

- `opensage_outputs.csv`: 56 output IDs, locked/public disease labels, PDF paths, hashes, page counts, topic checks, and known provenance notes.
- `baseline_outputs.csv`: 70 matched baseline output IDs, model labels, PDF paths, hashes, and topic checks.
- `prompt_manifest.csv`: 56 locked prompt files and hashes.
- `release_sha256.csv`: hashes of released data, documents, prompts, outputs, and submitted figures.

## Controlled fields not released

Reviewer IDs, rating-level D1-D7 scores, rating-level critical-defect flags, free-text comments, expert identity mappings, pre-unblinding mapping keys, and confidential adjudication workbooks are not public. Their variable definitions remain in `data/publication_tables/Data_Dictionary.csv`; the definitions do not imply release of the source records.

## Missing values and numeric formatting

Empty cells are represented as empty CSV fields. Public tables use display precision appropriate to the manuscript; some output-level scores are rounded to two decimals. Scripts use the released values and compare rounded publication results where appropriate.
