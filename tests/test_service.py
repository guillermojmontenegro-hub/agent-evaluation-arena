from pathlib import Path

import pytest

from agent_arena.models import Budget, Candidate, EvaluationRequest, Suite, Task
from agent_arena.service import ArenaService
from agent_arena.store import RunStore


@pytest.fixture
def evaluation_request() -> EvaluationRequest:
    return EvaluationRequest(
        suite=Suite(
            id="core",
            version="1.2.0",
            tasks=[
                Task(id="math", prompt="What is 6 * 7?", expected="42"),
                Task(id="capital", prompt="Capital of Argentina?", expected="Buenos Aires"),
            ],
        ),
        candidates=[
            Candidate(
                id="atlas",
                model="fixture",
                model_version="1",
                prompt_version="1",
                answers={"math": "42", "capital": "Buenos Aires"},
            ),
            Candidate(
                id="nova",
                model="fixture",
                model_version="1",
                prompt_version="1",
                answers={"math": "41", "capital": "Buenos Aires"},
            ),
        ],
        budget=Budget(max_steps=10, max_tokens=1000, timeout_seconds=30),
        seed=7,
    )


def test_evaluation_persists_versioned_replayable_runs(tmp_path: Path, evaluation_request: EvaluationRequest) -> None:
    service = ArenaService(RunStore(tmp_path))
    result = service.evaluate(evaluation_request)

    assert len(result.run_ids) == 2
    run = service.get_run(result.run_ids[0])
    assert run is not None
    assert run.suite_version == "1.2.0"
    assert run.runner_version
    assert run.seed == 7
    assert run.budget_fingerprint == "steps=10;tokens=1000;timeout=30"
    assert [event.sequence for event in run.traces["math"]] == [0, 1, 2]


def test_leaderboard_has_confidence_interval_and_filters_budget(
    tmp_path: Path, evaluation_request: EvaluationRequest
) -> None:
    service = ArenaService(RunStore(tmp_path))
    service.evaluate(evaluation_request)
    snapshot = service.leaderboard("core", "1.2.0", evaluation_request.budget.fingerprint)

    assert [entry.candidate_id for entry in snapshot.entries] == ["atlas", "nova"]
    assert snapshot.entries[0].success_rate == 1
    assert 0 < snapshot.entries[0].confidence_low < snapshot.entries[0].confidence_high <= 1
    assert service.leaderboard("core", "1.2.0", "different-budget").entries == []
