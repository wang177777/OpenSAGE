# Methods and reproducibility notes

## Analysis sets

The locked two-stage study comprises 46 Stage 1 OpenSAGE outputs and 80 Stage 2 comparative outputs (10 diseases × OpenSAGE plus seven direct-generation systems), giving 56 OpenSAGE outputs and 126 outputs overall. Twelve clinicians provided 1,512 expert-output ratings. Rating-level records are controlled and are not included here.

## Locked mixed definition

The main continuous endpoint is the field called `human-updated DGQC` in the locked files and `adjudication-adjusted DGQC` in the manuscript.

- **Stage 1 (R1):** the 46 OpenSAGE observations use the formal rerating.
- **Stage 2 (R2):** the 10 OpenSAGE and 70 baseline observations retain the locked human-updated/adjudication-adjusted results.

For raw domain reporting in Supplementary Table S12B and Supplementary Figure S1, Stage 1 uses the formal-rerating raw domains while Stage 2 uses the **original R2 raw ratings**. This raw-domain source is not a replacement endpoint and is not used to overwrite the locked R2 continuous endpoint.

A dual-adjudicator-confirmed critical defect is the main safety endpoint. An expert-review eligible draft has an adjudication-adjusted DGQC score of at least 70 and no dual-adjudicator-confirmed critical defect. These are study categories for pre-panel review, not clinical-release categories.

## Publicly reproducible results

`analysis/reproduce_core_results.py` recomputes from the public T001/T002 output-level tables:

- the OpenSAGE full-set, Stage 1, and Stage 2 descriptive summaries;
- disease-level OpenSAGE-minus-pooled-baseline and OpenSAGE-minus-GPT-5.5 differences;
- the two-sided exact paired sign-flip permutation P values;
- the raw-score matched sensitivity differences;
- consistency of S01, S02, S12A, S12B, S13, and the Figure S1 source.

Bias-corrected and accelerated bootstrap intervals and reliability statistics are reported in the released tables. Reviewer-level ICC(2,k) and Gwet AC1 cannot be independently recomputed without the controlled rating records, so the public checks validate cross-file consistency and do not overstate independent reproduction.

## Reliability record

The 14 July 2026 release reports:

- Stage 1 OpenSAGE 46: ICC(2,k) 0.952 (95% CI 0.928-0.966); Gwet AC1 0.799 (0.712-0.874).
- Stage 2 comparative 80: ICC(2,k) 0.985 (0.979-0.989); Gwet AC1 0.898 (0.838-0.946).
- All 126 outputs: ICC(2,k) 0.992 (0.990-0.993); Gwet AC1 0.824 (0.768-0.876).

The source analysis used output-level bootstrap resampling with 2,000 replicates and seed `20260708`, retaining all 12 ratings for each sampled output.

## Prompt and retrieval limitations

All evaluated systems received the same disease-specific prompt content within each matched disease. The locked prompts contain the study-time fixed “Meaningful youth engagement … case study” artifact, a hard-coded 29 April 2026 date, and an exactly-five-guideline instruction. This is disclosed in `PROMPT_ARTIFACT_DISCLOSURE.md` and must be considered when interpreting anchor failures and between-system differences.

The workflow used dynamic proprietary model endpoints and Tavily/web indexes. Intermediate retrieval responses were not comprehensively archived, and exact historical replay is therefore not guaranteed. URL retention in the implementation does not imply canonical deduplication across every retrieval loop.

## Output integrity

Evaluated PDFs are preserved as scored research artifacts. Public filename normalization does not rewrite their text or metadata. Known embedded artifacts (including the Hepatitis source header and Pneumonia defensive wording) remain visible and are recorded in the output manifest/audit instead of being cosmetically regenerated.
