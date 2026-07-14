#!/usr/bin/env python3
"""Populate the prospective prompt template from an explicit clean CSV."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_TEMPLATE = ROOT / "prompts/current_template/prompt_template.md"
REQUIRED_COLUMNS = {
    "disease",
    "guideline_title",
    "guideline_date",
    "evidence_cutoff",
    "scope",
}


def safe_filename(value: str) -> str:
    """Return a portable filename without changing the prompt content."""
    value = re.sub(r'[<>:"/\\|?*]+', "_", value).strip(" .")
    return value[:120] or "untitled"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate prospective OpenSAGE prompts from a clean CSV."
    )
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacement of existing generated files.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    template = args.template.read_text(encoding="utf-8")
    with args.input_csv.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    if not rows:
        raise SystemExit("Input CSV has no data rows.")
    missing = REQUIRED_COLUMNS - set(rows[0])
    if missing:
        raise SystemExit(f"Missing required columns: {', '.join(sorted(missing))}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    replacements = {
        "[DISEASE]": "disease",
        "[GUIDELINE_TITLE]": "guideline_title",
        "[GUIDELINE_DATE]": "guideline_date",
        "[EVIDENCE_CUTOFF]": "evidence_cutoff",
        "[SCOPE]": "scope",
    }
    written = 0
    for index, row in enumerate(rows, start=2):
        if not row["disease"].strip():
            raise SystemExit(f"Row {index}: disease is blank.")
        content = template
        for placeholder, column in replacements.items():
            value = row[column].strip()
            if not value:
                raise SystemExit(f"Row {index}: {column} is blank.")
            content = content.replace(placeholder, value)
        destination = args.output_dir / f"{safe_filename(row['disease'])}.md"
        if destination.exists() and not args.overwrite:
            raise SystemExit(f"Refusing to overwrite {destination}; use --overwrite.")
        destination.write_text(content, encoding="utf-8")
        written += 1
    print(f"Generated {written} prospective prompt files in {args.output_dir}")


if __name__ == "__main__":
    main()
