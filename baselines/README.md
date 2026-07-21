# Direct-generation systems

The reported matched analysis comprises seven direct-generation systems across ten diseases. Their model labels, blinded output identifiers, final DGQC scores, and expert-confirmed critical-defect status are reported in `data/publication_tables/T002_Matched_80.csv`.

`baseline.py` runs a user-supplied directory of Markdown task files against an OpenAI-compatible endpoint selected with `--model` (or `BASELINE_MODEL`). Endpoint credentials are supplied through an environment variable and are never stored in the repository.

Install the runner dependency in the active Python environment:

```bash
python -m pip install -r baselines/requirements.txt
```

Example:

```bash
python baselines/baseline.py /path/to/task_files outputs/new_run \
  --model MODEL_IDENTIFIER
```

This runner is a reference utility for prospective executions with user-supplied task files and current service endpoints.
