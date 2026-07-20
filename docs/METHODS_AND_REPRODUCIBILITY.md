# Methods and reproducibility notes

## Analysis sets

The two-stage study comprises 46 Stage 1 OpenSAGE outputs and 80 Stage 2 comparative outputs (10 diseases × OpenSAGE plus seven direct-generation systems), giving 56 OpenSAGE outputs and 126 outputs overall. Twelve expert reviewers provided 1,512 blinded expert-output ratings in one expert-rating round.

## Scoring and endpoints

The primary continuous endpoint is the final DGQC score reported for every output. Stage 1 and Stage 2 are analysis subsets within the same expert-rating round:

- **Stage 1:** 46 non-comparative OpenSAGE outputs.
- **Stage 2:** 10 OpenSAGE and 70 direct-generation outputs across ten matched diseases.

The reviewer-mean DGQC sensitivity endpoint and the raw D1-D7 domain summaries in Supplementary Table S12B and Supplementary Figure S1 are derived from that same rating round. The R1/R2 prefixes in output identifiers denote study phases, not separate reviewer cohorts or rating rounds.

Each reviewer-level DGQC score maps the seven 1-7 domain ratings to a 0-100 scale using the weights reported in Table S08: `DGQC = Σ w_d × (D_d − 1) / 6`, where the domain weights sum to 100. The public implementation is provided in `analysis/dgqc_scoring.py`.

An expert-confirmed critical defect is the main safety endpoint. An expert-review eligible draft has a final DGQC score of at least 70 and no expert-confirmed critical defect.

## Publicly reproducible results

`analysis/reproduce_core_results.py` recomputes from the public T001/T002 output-level tables:

- the OpenSAGE full-set, Stage 1, and Stage 2 descriptive summaries;
- disease-level OpenSAGE-minus-pooled-baseline and OpenSAGE-minus-GPT-5.5 differences;
- the two-sided exact paired sign-flip permutation P values;
- the reviewer-mean matched sensitivity differences;
- consistency of S01, S02, S12A, S12B, S13, and the Figure S1 source.

Bias-corrected and accelerated bootstrap intervals and reliability statistics are reported in the released tables. The public checks reproduce output-level analyses and validate the published reliability estimates across files; reviewer-level ICC(2,k) and Gwet AC1 are estimated from the controlled rating-level dataset.

## Reliability record

The 20 July 2026 release reports:

- Stage 1 OpenSAGE 46: ICC(2,k) 0.952 (95% CI 0.928-0.966); Gwet AC1 0.799 (0.712-0.874).
- Stage 2 comparative 80: ICC(2,k) 0.985 (0.979-0.989); Gwet AC1 0.898 (0.838-0.946).
- All 126 outputs: ICC(2,k) 0.992 (0.990-0.993); Gwet AC1 0.824 (0.768-0.876).

The source analysis used output-level bootstrap resampling with 2,000 replicates and seed `20260708`, retaining all 12 ratings for each sampled output.

## Workflow comparison

The matched analysis compares the complete OpenSAGE workflow with direct-generation conditions under the evaluated study design. Retrieval, reflection, source retention, computational resources, and tool access form part of the workflow condition. The released application supports configured OpenAI-compatible endpoints and Tavily/web retrieval, while the public analysis tables reproduce the reported output-level summaries and comparisons.

## Public analysis record

The public record includes aggregate and output-level analysis tables, figure sources, and release-file hashes. Historical generation inputs and evaluated document files are outside this public package.
