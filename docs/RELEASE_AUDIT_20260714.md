# Public release audit - 14 July 2026

## Source and history

- Source audited: `jiangjyjy/OpenSAGE`, commit `f46d2d26914408c1624810820f01ac665558b630`.
- The current file tree contained no directly usable secret, but the old Git history contained four credential-shaped real tokens in removed files.
- This release uses a new clean history and does not import the old commits. The source-account owner must still revoke/rotate those historical credentials; migration cannot revoke them.

## Blocking output repair

The old `result/Maternal Health.pdf` had SHA-256 `197c23835bc0e4d3c67cf71bebffe8dc80de6869e9b1d614984a1d31c29164cc` and its body was Marburg. It is retained without content edits as `outputs/opensage/Marburg.pdf`.

The restored Maternal Health file has SHA-256 `03c3b6e26d1c4dcd5dacf68c2ed34712fc455cc3a5fad3c1b5aa748cc20a1fb9`. That hash matched all of the following independent retained locations:

- the explicit `D06-方案06_OpenSAGE_Maternal_Health_修正源文件.pdf`;
- the second-round blinded package `D06_Maternal_Health/D06-方案06.pdf`;
- the second-round original-generation package `D06_Maternal_Health/D06-方案06.pdf`;
- a separate retained transfer copy.

After repair, the release contains 56 OpenSAGE PDFs and 70 baseline PDFs. `analysis/validate_release.py` checks counts, hashes, topic identity, workbook consistency, prompt counts, and credential patterns.

## Preserved study artifacts

- Locked prompt contamination is disclosed rather than silently removed.
- Hepatitis remains a Hepatitis draft with an embedded `Hypertension.md` print header.
- Pneumonia remains the scored draft with defensive abortion-care wording.
- Locked T001 spelling errors are retained in the data table and cross-walked to normalized public filenames in the manifest.

## Removed non-study/internal material

- Header-derived `Disease_Health Condition.md`.
- Personal/internal `disease.xlsx` and its run-status column/metadata.
- Unrelated Euro 2024 notebook outputs.
- Misleading upstream author metadata and unsafe baseline credential placeholder.

## Remaining limitations

- Old-source credential revocation requires action by the owner of the affected service accounts.
- Rating-level reliability statistics cannot be independently recomputed from the public release boundary.
- Dynamic web retrieval and proprietary endpoint behavior cannot be replayed exactly.
- Evaluated drafts retain generation-time text/metadata defects because post-score cosmetic rewriting would break auditability.
