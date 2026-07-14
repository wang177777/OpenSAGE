"""Generate release manifests and enforce the public-release quality gate."""

from __future__ import annotations

import argparse
import csv
import hashlib
import logging
import re
from pathlib import Path

from openpyxl import load_workbook
from pypdf import PdfReader

logging.getLogger("pypdf").setLevel(logging.ERROR)


ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "data/publication_tables"
MANIFESTS = ROOT / "data/manifests"
OPEN_OUTPUTS = ROOT / "outputs/opensage"
BASELINE_OUTPUTS = ROOT / "outputs/direct_generation"
LOCKED_PROMPTS = ROOT / "prompts/locked_experimental"

EXPECTED_MATERNAL_SHA256 = "03c3b6e26d1c4dcd5dacf68c2ed34712fc455cc3a5fad3c1b5aa748cc20a1fb9"
EXPECTED_MARBURG_SHA256 = "197c23835bc0e4d3c67cf71bebffe8dc80de6869e9b1d614984a1d31c29164cc"
LOCKED_ARTIFACT = "Meaningful youth engagement in a WHO guideline development process"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the OpenSAGE public release")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if regenerated manifests differ from committed manifests.",
    )
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compact(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def pdf_facts(path: Path, expected_topic: str) -> tuple[int, str, str]:
    reader = PdfReader(path)
    text = "\n".join((page.extract_text() or "") for page in reader.pages[:3])
    raw_title = (reader.metadata or {}).get("/Title", "")
    title = "" if raw_title is None or raw_title.__class__.__name__ == "NullObject" else str(raw_title)
    topic_aliases = {
        "STI": ["sexually transmitted infections", "sti"],
        "Taeniasis/Cysticercosis": ["taeniosis/cysticercosis", "taeniasis/cysticercosis"],
        "Injury": ["injury", "injuries"],
        "Newborn/Neonatal Health": ["newborn/neonatal health", "newborn neonatal health"],
    }
    candidates = topic_aliases.get(expected_topic, [expected_topic])
    body = compact(text)
    status = "pass" if any(compact(candidate) in body for candidate in candidates) else "fail"
    return len(reader.pages), title, status


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str], check: bool) -> None:
    lines: list[str] = []
    import io

    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    content = buffer.getvalue()
    if check:
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            raise AssertionError(f"Committed manifest is stale: {path.relative_to(ROOT)}")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def normalized_disease_map() -> dict[str, str]:
    rows = read_csv(TABLES / "S10_Anchor_Audit.csv")
    return {row["Locked_Dataset_Disease_Label"]: row["Disease"] for row in rows}


def opensage_filename(public_disease: str, locked_disease: str) -> str:
    exceptions = {
        "STI": "Sexually Transmitted Infections (STI).pdf",
        "Taeniasis/Cysticercosis": "Taeniosis_Cysticercosis.pdf",
    }
    if public_disease in exceptions:
        return exceptions[public_disease]
    return public_disease.replace("/", "_") + ".pdf"


def generate_opensage_manifest(check: bool) -> set[Path]:
    t001 = read_csv(TABLES / "T001_56_Disease_List.csv")
    normalized = normalized_disease_map()
    known_notes = {
        "Maternal Health": "Restored formal D06-方案06 file; verified against independent retained copies.",
        "Marburg": "Formerly mislabeled Maternal Health.pdf; scored Marburg body preserved without metadata rewrite.",
        "Hepatitis": "Hepatitis body retained; embedded print header says Hypertension.md.",
        "Pneumonia": "Scored body retained with defensive wording caused by the locked prompt artifact.",
    }
    rows: list[dict[str, object]] = []
    files: set[Path] = set()
    for source in t001:
        locked = source["Disease"]
        public = normalized.get(locked, locked)
        filename = opensage_filename(public, locked)
        path = OPEN_OUTPUTS / filename
        if not path.is_file():
            raise AssertionError(f"Missing OpenSAGE output: {path.relative_to(ROOT)}")
        pages, title, topic_status = pdf_facts(path, public)
        if topic_status != "pass":
            raise AssertionError(f"Topic check failed: {path.relative_to(ROOT)} -> {public}")
        files.add(path)
        rows.append(
            {
                "output_id": source["Output ID"],
                "phase": source["Phase"],
                "disease_id": source["Disease ID"],
                "locked_disease_label": locked,
                "public_disease": public,
                "blinded_output_id": source["Blinded output ID"],
                "score_definition": (
                    "R1 formal rerating" if source["Phase"] == "Stage 1" else "R2 locked adjudication-adjusted"
                ),
                "human_updated_DGQC": source["Human-updated DGQC"],
                "expert_confirmed_CD": source["Expert-confirmed CD"],
                "usable_draft": source["Usable draft"],
                "file_path": path.relative_to(ROOT).as_posix(),
                "sha256": sha256(path),
                "pages": pages,
                "pdf_title_metadata": title,
                "topic_check": topic_status,
                "known_note": known_notes.get(public, ""),
            }
        )
    actual = set(OPEN_OUTPUTS.glob("*.pdf"))
    if len(rows) != 56 or actual != files:
        raise AssertionError(f"OpenSAGE mapping is not exactly 56/56 (mapped={len(files)}, actual={len(actual)})")
    hashes = {row["public_disease"]: row["sha256"] for row in rows}
    if hashes["Maternal Health"] != EXPECTED_MATERNAL_SHA256:
        raise AssertionError("Maternal Health SHA-256 no longer matches the formal D06-方案06 source")
    if hashes["Marburg"] != EXPECTED_MARBURG_SHA256:
        raise AssertionError("Marburg SHA-256 no longer matches the preserved scored artifact")
    fieldnames = list(rows[0])
    write_csv(MANIFESTS / "opensage_outputs.csv", rows, fieldnames, check)
    return files


def generate_baseline_manifest(check: bool) -> set[Path]:
    t002 = read_csv(TABLES / "T002_Matched_80.csv")
    rows: list[dict[str, object]] = []
    files: set[Path] = set()
    for source in t002:
        if source["Model group"] != "baseline":
            continue
        path = BASELINE_OUTPUTS / f"{source['Model']}_Baseline" / f"{source['Disease']}.pdf"
        if not path.is_file():
            raise AssertionError(f"Missing baseline output: {path.relative_to(ROOT)}")
        pages, title, topic_status = pdf_facts(path, source["Disease"])
        if topic_status != "pass":
            raise AssertionError(f"Topic check failed: {path.relative_to(ROOT)} -> {source['Disease']}")
        files.add(path)
        rows.append(
            {
                "output_id": source["Output ID"],
                "disease": source["Disease"],
                "model": source["Model"],
                "blinded_output_id": source["Blinded output ID"],
                "score_definition": "R2 locked adjudication-adjusted",
                "human_updated_DGQC": source["Human-updated DGQC"],
                "raw_mean_DGQC": source["Raw mean DGQC"],
                "expert_confirmed_CD": source["Expert-confirmed CD"],
                "usable_draft": source["Usable draft"],
                "file_path": path.relative_to(ROOT).as_posix(),
                "sha256": sha256(path),
                "pages": pages,
                "pdf_title_metadata": title,
                "topic_check": topic_status,
            }
        )
    actual = set(BASELINE_OUTPUTS.glob("*_Baseline/*.pdf"))
    if len(rows) != 70 or actual != files:
        raise AssertionError(f"Baseline mapping is not exactly 70/70 (mapped={len(files)}, actual={len(actual)})")
    write_csv(MANIFESTS / "baseline_outputs.csv", rows, list(rows[0]), check)
    return files


def generate_prompt_manifest(check: bool) -> set[Path]:
    prompt_files = set(LOCKED_PROMPTS.glob("*.md"))
    if len(prompt_files) != 56:
        raise AssertionError(f"Expected 56 locked prompts, found {len(prompt_files)}")
    if (LOCKED_PROMPTS / "Disease_Health Condition.md").exists():
        raise AssertionError("Header-derived pseudo-disease prompt is present")
    rows = []
    for path in sorted(prompt_files):
        text = path.read_text(encoding="utf-8")
        if LOCKED_ARTIFACT not in text:
            raise AssertionError(f"Locked artifact unexpectedly changed in {path.name}")
        rows.append(
            {
                "disease_filename": path.stem,
                "file_path": path.relative_to(ROOT).as_posix(),
                "sha256": sha256(path),
                "locked_artifact_preserved": "yes",
            }
        )
    write_csv(MANIFESTS / "prompt_manifest.csv", rows, list(rows[0]), check)
    return prompt_files


def validate_workbooks() -> None:
    expected = {
        "Supplementary_Data_1.xlsx": {"T001_56_Disease_List": 57, "T002_Matched_80": 81, "S02": 4},
        "Supplementary_Data_2.xlsx": {"S12A": 4, "S12B": 4},
    }
    for filename, sheets in expected.items():
        path = ROOT / "data/supplementary" / filename
        workbook = load_workbook(path, data_only=True)
        if workbook.properties.lastModifiedBy:
            raise AssertionError(f"Workbook exposes lastModifiedBy: {filename}")
        for sheet, rows in sheets.items():
            if sheet not in workbook.sheetnames or workbook[sheet].max_row != rows:
                raise AssertionError(f"Unexpected workbook sheet/row count: {filename}:{sheet}")
        for sheet in workbook.worksheets:
            for row in sheet.iter_rows():
                for cell in row:
                    if cell.comment is not None:
                        raise AssertionError(f"Workbook comment remains: {filename}:{sheet.title}!{cell.coordinate}")


def secret_and_path_scan() -> None:
    patterns = {
        "OpenAI-style key": re.compile(rb"\bsk-[A-Za-z0-9_-]{16,}\b"),
        "Tavily key": re.compile(rb"\btvly-[A-Za-z0-9_-]{16,}\b"),
        "LangSmith key": re.compile(rb"\blsv2_[A-Za-z0-9_-]{16,}\b"),
        "GitHub token": re.compile(rb"\b(?:ghp|github_pat)_[A-Za-z0-9_]{16,}\b"),
        "Private key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        "Local user path": re.compile(rb"(?:/Users/|[A-Za-z]:\\\\Users\\\\)"),
    }
    binary_suffixes = {".pdf", ".xlsx", ".png", ".tiff", ".woff", ".woff2"}
    for path in ROOT.rglob("*"):
        if (
            not path.is_file()
            or any(part in {".git", "__pycache__", "node_modules", ".venv", "generated"} for part in path.parts)
            or path.suffix.lower() in binary_suffixes
        ):
            continue
        if path.resolve() == Path(__file__).resolve():
            continue  # This file necessarily contains the detection patterns themselves.
        data = path.read_bytes()
        for name, pattern in patterns.items():
            if pattern.search(data):
                raise AssertionError(f"{name} detected in {path.relative_to(ROOT)}")


def release_hashes(check: bool) -> None:
    excluded = {
        MANIFESTS / "release_sha256.csv",
        ROOT / "results/reproduced_summary.json",
    }
    rows = []
    for path in sorted(ROOT.rglob("*")):
        if (
            not path.is_file()
            or any(part in {".git", "__pycache__", "node_modules", ".venv"} for part in path.parts)
            or path in excluded
        ):
            continue
        if "generated" in path.parts or path.name == ".DS_Store":
            continue
        rows.append({"file_path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)})
    write_csv(MANIFESTS / "release_sha256.csv", rows, ["file_path", "sha256"], check)


def main() -> None:
    args = parse_args()
    MANIFESTS.mkdir(parents=True, exist_ok=True)
    generate_opensage_manifest(args.check)
    generate_baseline_manifest(args.check)
    generate_prompt_manifest(args.check)
    validate_workbooks()
    secret_and_path_scan()
    release_hashes(args.check)
    print("PASS - 56 OpenSAGE outputs, 70 baselines, 56 locked prompts")
    print("PASS - Maternal/Marburg provenance hashes and topic checks")
    print("PASS - workbooks, manifests, credential patterns, and local paths")


if __name__ == "__main__":
    main()
