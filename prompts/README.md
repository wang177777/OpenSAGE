# Prompt sets

## `locked_experimental/`

These 56 files preserve the disease-specific prompt content used for the reported experiment. Their text has not been silently corrected. In particular, every prompt contains a fixed instruction referring to a “Meaningful youth engagement … case study” title, a hard-coded 29 April 2026 date, and a requirement to synthesize exactly five WHO guidelines. The placeholder in that fixed title was not correctly populated outside the disease-specific anchor line.

The artifact originated from the abortion-care tracking row/template and is visible in many evaluated outputs. It may have affected anchor identification and direct-generation performance. The evaluated PDFs and locked prompts are retained for auditability, not recommended for prospective clinical research use.

`Disease_Health Condition.md` from the old repository was an Excel header mistakenly treated as a record. It was excluded because it was never one of the 56 study diseases.

## `current_template/`

The prospective template removes the contaminated fixed title, fixed date, and arbitrary five-guideline requirement. It requires an explicit anchor, cutoff, and scope; it also clarifies that GRADE-like labels are provisional drafting aids. This template was **not** used to generate or score the reported study outputs.

Use `generate_prompts.py` to populate the prospective template from a clean CSV. Do not overwrite `locked_experimental/`.
