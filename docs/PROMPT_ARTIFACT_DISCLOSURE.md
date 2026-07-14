# Locked prompt artifact disclosure

The study-time prompt template contained three non-generalizable fixed instructions:

1. identify a title beginning “Meaningful youth engagement in a WHO guideline development process: case study of WHO … guideline”;
2. treat 29 April 2026 as a fixed latest-update date;
3. synthesize exactly five WHO guidelines for every disease.

The first instruction came from the abortion-care tracking/template context. Its disease placeholder was not correctly populated in the shared fixed line, although a separate disease-specific guideline title was inserted later in each prompt. Text extraction confirms that related wording propagated into many OpenSAGE and baseline outputs. Pneumonia, for example, contains defensive text explaining that the abortion-care case study is not a pneumonia guideline.

This artifact was present for every matched system within a disease, but equal exposure does not make it harmless: systems may respond differently to conflicting instructions. It may have affected anchor identification, content allocation, and baseline performance. The workflow-versus-direct-generation comparison should therefore be interpreted as the effect under the actual locked prompts, not under an ideal generic prompt.

For research integrity, the 56 experimental prompt files and scored PDFs remain unchanged. The corrected prospective template is stored separately in `prompts/current_template/` and is explicitly not represented as the historical experimental condition.
