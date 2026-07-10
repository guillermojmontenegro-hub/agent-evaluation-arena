from __future__ import annotations

from math import sqrt


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval, robust for small samples and extreme proportions."""
    if total == 0:
        return (0.0, 0.0)
    proportion = successes / total
    denominator = 1 + z**2 / total
    centre = proportion + z**2 / (2 * total)
    margin = z * sqrt((proportion * (1 - proportion) + z**2 / (4 * total)) / total)
    return ((centre - margin) / denominator, (centre + margin) / denominator)
