# OpenSAGE + DGQC

This repository provides the research software, public analysis data, and reproducibility resources accompanying the OpenSAGE/DGQC study. It includes the runnable OpenSAGE reference implementation, the DGQC instrument, public data tables, submitted figures, and reproducibility checks.

OpenSAGE drafts are study outputs intended for expert review. The study was conducted independently of WHO.

## Repository scope

- A versioned public repository containing the reference application, public analysis data, figures, and documentation.
- Output-level analysis tables for the 56-output OpenSAGE set and 70-output direct-generation comparison set.
- Supplementary workbooks, CSV exports, Figure S1 source data, the DGQC manual, analysis checks, and a public data dictionary.
- Reproducibility scripts for the released descriptive summaries, matched comparisons, exact sign-flip tests, submitted data figures, release hashes, and cross-file consistency checks.

## Evaluation and analysis definitions

The study comprises 1,512 blinded ratings from twelve expert reviewers in one expert-rating round. Stage 1 and Stage 2 identify analysis subsets rather than separate rating rounds:

1. **Primary continuous endpoint:** the final DGQC score is reported for all 126 outputs.
2. **Reviewer-mean and raw-domain summaries:** the reviewer-mean DGQC sensitivity endpoint and D1-D7 domain summaries are derived from the same expert-rating round.

See `docs/METHODS_AND_REPRODUCIBILITY.md` and `docs/DATA_DICTIONARY.md` for the analysis sets and field definitions.

## Repository map

- `backend/`, `frontend/`: runnable reference application.
- `data/supplementary/`: Supplementary Data 1-3 for the 20 July 2026 public release.
- `data/publication_tables/`: CSV exports of Tables T001-T002 and S01-S14.
- `data/manifests/`: release-file hashes.
- `analysis/`: public numerical checks, release validation, and submitted data-figure generation code.
- `figures/submission/`, `figures/supplementary/`: submitted figures and Supplementary Figure S1.
- `docs/`: DGQC instrument, methods, data dictionary, public-release boundaries, and release notes.

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

The public aggregate and output-level files reproduce the descriptive results, matched comparisons, exact sign-flip P values, DGQC weighting, and submitted data figures. Reliability estimates are cross-checked across the released tables; reviewer-level re-estimation uses the controlled rating-level dataset.

## Application quick start

The application requires Python 3.11+, Node.js 20+, an OpenAI-compatible chat endpoint, and Tavily.

```bash
cp backend/.env.example backend/.env
# Add your own credentials to backend/.env; never commit that file.
cd backend && python -m pip install -e .
cd ../frontend && npm ci && npm run build
cd .. && make dev
```

Configuration details are documented in `backend/README.md`. The released application is a reference implementation, and the public analysis tables reproduce the reported numerical analyses.

## Privacy and release boundary

Released files contain aggregate and output-level analysis data. Historical generation inputs and evaluated document files, rating-level expert records, reviewer identifiers, identity mappings, free-text comments, and confidential mapping files are not part of this public package. Controlled research materials may be made available to editors and referees under appropriate confidentiality safeguards.

## Licences and citation

Original top-level code is released under Apache-2.0. The retained backend template component remains under its MIT licence; see `backend/LICENSE` and `THIRD_PARTY_NOTICES.md`. Curated data tables and documentation are released under CC BY 4.0 as described in `DATA_LICENSE.md`.

Citation metadata are in `CITATION.cff`.
