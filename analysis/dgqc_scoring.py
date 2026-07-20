"""DGQC scoring utilities for seven reviewer-rated domains."""

from __future__ import annotations

from collections.abc import Mapping


DOMAIN_WEIGHTS: dict[str, float] = {
    "D1": 20.0,
    "D2": 20.0,
    "D3": 15.0,
    "D4": 20.0,
    "D5": 10.0,
    "D6": 5.0,
    "D7": 10.0,
}


def dgqc_score(domain_scores: Mapping[str, float]) -> float:
    """Convert D1-D7 ratings on the 1-7 scale to the 0-100 DGQC scale."""
    if set(domain_scores) != set(DOMAIN_WEIGHTS):
        missing = sorted(set(DOMAIN_WEIGHTS) - set(domain_scores))
        extra = sorted(set(domain_scores) - set(DOMAIN_WEIGHTS))
        raise ValueError(f"Expected D1-D7 exactly (missing={missing}, extra={extra})")

    total = 0.0
    for domain, weight in DOMAIN_WEIGHTS.items():
        value = float(domain_scores[domain])
        if not 1.0 <= value <= 7.0:
            raise ValueError(f"{domain} must be in [1, 7], received {value}")
        total += weight * (value - 1.0) / 6.0
    return total
