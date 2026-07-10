from agent_arena.graders import contains, exact_match, regex
from agent_arena.models import Task


def task(expected: str, grader: str) -> Task:
    return Task(id="t1", prompt="answer", expected=expected, grader=grader)


def test_exact_match_normalizes_case_and_whitespace() -> None:
    result = exact_match(task("Buenos Aires", "exact_match"), "  BUENOS   AIRES ")
    assert result.passed
    assert result.score == 1


def test_contains_finds_normalized_value() -> None:
    assert contains(task("42", "contains"), "The result is 42.").passed


def test_regex_is_case_insensitive() -> None:
    assert regex(task(r"arena-\d+", "regex"), "ARENA-42").passed
