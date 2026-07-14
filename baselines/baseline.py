#!/usr/bin/env python3
"""Run direct-generation prompts through an OpenAI-compatible endpoint.

This generic runner supports prospective checks. It cannot guarantee exact replay of
the proprietary April 2026 model versions represented by the locked PDF outputs.
"""

from __future__ import annotations

import argparse
import logging
import os
import time
from pathlib import Path

from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI, RateLimitError


LOGGER = logging.getLogger("opensage.baseline")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Batch direct-generation runner")
    parser.add_argument("input_dir", type=Path, help="Directory containing Markdown prompts")
    parser.add_argument("output_dir", type=Path, help="Directory for Markdown responses")
    parser.add_argument("--model", default=os.getenv("BASELINE_MODEL"))
    parser.add_argument("--base-url", default=os.getenv("OPENAI_BASE_URL"))
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY")
    parser.add_argument("--system-prompt", default="")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--max-retries", type=int, default=3)
    return parser.parse_args()


def call_model(client: OpenAI, *, model: str, prompt: str, system_prompt: str, max_retries: int) -> str:
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    delay = 2.0
    last_error: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.0,
                stream=False,
            )
            text = response.choices[0].message.content or ""
            if not text.strip():
                raise RuntimeError("Endpoint returned an empty response")
            return text
        except (RateLimitError, APITimeoutError, APIConnectionError) as exc:
            last_error = exc
        except APIStatusError as exc:
            if exc.status_code < 500:
                raise
            last_error = exc
        if attempt < max_retries:
            LOGGER.warning("Request failed; retrying in %.1f seconds", delay)
            time.sleep(delay)
            delay *= 2
    assert last_error is not None
    raise last_error


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    api_key = os.getenv(args.api_key_env)
    if not api_key:
        raise SystemExit(f"Credential environment variable {args.api_key_env!r} is not set")
    if not args.model:
        raise SystemExit("Set --model or BASELINE_MODEL")
    if not args.input_dir.is_dir():
        raise SystemExit(f"Input directory does not exist: {args.input_dir}")

    client = OpenAI(api_key=api_key, base_url=args.base_url or None, timeout=1200, max_retries=0)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    prompts = sorted(args.input_dir.glob("*.md"))
    if not prompts:
        raise SystemExit(f"No Markdown prompts found in {args.input_dir}")

    for index, source in enumerate(prompts, start=1):
        destination = args.output_dir / source.name
        if destination.exists() and not args.overwrite:
            LOGGER.info("[%d/%d] skip %s", index, len(prompts), source.name)
            continue
        LOGGER.info("[%d/%d] generate %s", index, len(prompts), source.name)
        result = call_model(
            client,
            model=args.model,
            prompt=source.read_text(encoding="utf-8"),
            system_prompt=args.system_prompt,
            max_retries=args.max_retries,
        )
        destination.write_text(result + ("" if result.endswith("\n") else "\n"), encoding="utf-8")


if __name__ == "__main__":
    main()
