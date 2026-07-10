from __future__ import annotations

import re
from collections.abc import Callable

from .models import Grade, Task

GRADER_VERSION = "1.0.0"


def _normalize(value: str) -> str:
    return " ".join(value.casefold().strip().split())


def exact_match(task: Task, output: str) -> Grade:
    passed = _normalize(output) == _normalize(task.expected)
    return Grade(
        grader="exact_match",
        grader_version=GRADER_VERSION,
        score=float(passed),
        passed=passed,
        explanation="normalized output matches expected value" if passed else "normalized output differs",
    )


def contains(task: Task, output: str) -> Grade:
    passed = _normalize(task.expected) in _normalize(output)
    return Grade(
        grader="contains",
        grader_version=GRADER_VERSION,
        score=float(passed),
        passed=passed,
        explanation="expected value is present" if passed else "expected value is absent",
    )


def regex(task: Task, output: str) -> Grade:
    passed = re.search(task.expected, output, flags=re.IGNORECASE) is not None
    return Grade(
        grader="regex",
        grader_version=GRADER_VERSION,
        score=float(passed),
        passed=passed,
        explanation="output matches regex" if passed else "output does not match regex",
    )


GRADERS: dict[str, Callable[[Task, str], Grade]] = {
    "exact_match": exact_match,
    "contains": contains,
    "regex": regex,
}


def grade(task: Task, output: str) -> Grade:
    try:
        grader = GRADERS[task.grader]
    except KeyError as exc:
        raise ValueError(f"unknown deterministic grader: {task.grader}") from exc
    return grader(task, output)
