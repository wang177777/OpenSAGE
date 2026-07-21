# Public release notes - 21 July 2026, final terminology release

## Release scope

This release aligns the machine-readable sources for Supplementary Tables S3 and S7 with the tables reported in the Supplementary Information.

- `data/publication_tables/S03.csv` contains the T002-derived leave-one-disease-out results for the pooled direct-generation comparison.
- `data/publication_tables/S07.csv` contains the seven direct-comparator contrasts used for the Holm family. The pooled comparison remains reported in Supplementary Table S1.
- `data/supplementary/Supplementary_Data_1.xlsx` contains the same S3 and S7 values as the Supplementary Information and CSV exports.
- `analysis/reproduce_core_results.py` verifies the S3 and S7 means and exact sign-flip P values from T002, the S7 Holm adjustment, and the reported BCa interval records.
- The public validation environment uses Pillow 12.3.0.
- Final DGQC score is the single continuous endpoint throughout the manuscript-facing tables, documentation, and machine-readable files.
- Senior adjudicators determine only the critical-defect endpoint and do not modify final DGQC scores.
- Figure 3 uses the same-model-label title consistently in the figure, caption, and source code.

The primary pooled comparison, direct GPT-5.5 comparison, reliability results, figures, and conclusions are unchanged.
