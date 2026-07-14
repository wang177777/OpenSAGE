# OpenSAGE + DGQC

This repository is the audited public release for the OpenSAGE/DGQC study. It combines the runnable OpenSAGE reference implementation, the 56 evaluated OpenSAGE drafts, the 70 matched direct-generation drafts, the locked experimental prompts, the DGQC instrument, the 14 July 2026 public data tables, submitted figures, and reproducibility checks.

OpenSAGE drafts are research artifacts for expert review. They are **not clinical guidelines, clinical-release approvals, or patient-specific medical advice**. WHO did not participate in, endorse, or validate OpenSAGE or DGQC.

## What was repaired in this release

- Migrated the current source tree into a new one-commit history. The inaccessible source repository's old history is not carried forward because an audit found four API credentials in historical commits.
- Restored the evaluated output set to 56/56: the mislabeled `Maternal Health.pdf` was identified as Marburg, preserved as `Marburg.pdf`, and the formal `D06-方案06` Maternal Health file was restored after SHA-256 verification against three independent retained copies.
- Normalized public filenames while preserving locked dataset labels and PDF contents. The complete mapping and hashes are in `data/manifests/`.
- Separated the **locked experimental prompts** from a corrected prospective template. The locked prompts retain the study-time prompt artifact and must not be mistaken for the recommended current template.
- Added the corrected 14 July 2026 supplementary workbooks, CSV exports, figure source data, locked DGQC manual, analysis checks, data dictionary, release boundary, and audit record.
- Removed internal workbook status fields, personal workbook metadata, stale notebook outputs, hard-coded credential placeholders, and the incorrect upstream package-author declaration.

## Locked analysis definition

Two related but distinct definitions are intentionally used:

1. **Main continuous endpoint:** Stage 1 (R1) uses the formal rerating; Stage 2 (R2), including OpenSAGE and all baselines, uses the locked human-updated/adjudication-adjusted score.
2. **Raw domain summaries (Supplementary Table S12B and Supplementary Figure S1):** Stage 1 uses formal-rerating raw domain scores and Stage 2 uses the original R2 raw ratings.

The public repository does not silently rerate or replace R2. See `docs/METHODS_AND_REPRODUCIBILITY.md` and `docs/DATA_DICTIONARY.md`.

## Repository map

- `backend/`, `frontend/`: runnable reference application.
- `outputs/opensage/`: 56 evaluated OpenSAGE PDF drafts.
- `outputs/direct_generation/`: 70 evaluated direct-generation PDF drafts (7 systems × 10 diseases).
- `prompts/locked_experimental/`: 56 study-time prompts, preserved without content edits.
- `prompts/current_template/`: corrected template for prospective use; not used in the reported experiment.
- `data/supplementary/`: Supplementary Data 1-3 dated 14 July 2026.
- `data/publication_tables/`: CSV exports of Tables T001-T002 and S01-S14.
- `data/manifests/`: output/prompt mappings, hashes, and validation status.
- `analysis/`: public numerical checks, release validation, and figure-generation code.
- `figures/submission/`, `figures/supplementary/`: submitted figures and Supplementary Figure S1.
- `docs/`: DGQC instrument, methods, data dictionary, prompt disclosure, release boundary, and audit record.

## Reproduce and validate

Core numerical checks use only the Python standard library:

```bash
python analysis/reproduce_core_results.py
```

Install the validation/figure dependencies and run the full release gate:

```bash
python -m pip install -r analysis/requirements.txt
python analysis/validate_release.py --check
python analysis/generate_figures.py
```

The public aggregate/output-level files can reproduce descriptive results, matched comparisons, exact sign-flip P values, and figure inputs. They cannot independently recompute reviewer-level ICC/Gwet statistics because rating-level records and reviewer identifiers are controlled rather than public. The script therefore validates those reliability values across the released tables instead of claiming to recompute them.

## Application quick start

The application requires Python 3.11+, Node.js 20+, an OpenAI-compatible chat endpoint, and Tavily.

```bash
cp backend/.env.example backend/.env
# Add your own credentials to backend/.env; never commit that file.
cd backend && python -m pip install -e .
cd ../frontend && npm ci && npm run build
cd .. && make dev
```

Configuration details and reproducibility limits are documented in `backend/README.md`. The historical model labels and dynamic search indexes are not guaranteed to remain available, so exact retrieval replay is not claimed.

## Privacy and release boundary

Released files contain aggregate and output-level data. Rating-level expert records, reviewer identifiers, identity mappings, free-text comments, confidential mapping files, and credentials are not public because explicit public-disclosure authorization was not available. Controlled materials may be made available to editors and referees under appropriate confidentiality safeguards.

## Licences and citation

Original top-level code is released under Apache-2.0. The retained backend template component remains under its MIT licence; see `backend/LICENSE` and `THIRD_PARTY_NOTICES.md`. Curated data tables and documentation are released under CC BY 4.0 as described in `DATA_LICENSE.md`. Evaluated PDFs may contain third-party citations and names for which no additional rights are granted.

Citation metadata are in `CITATION.cff`.
