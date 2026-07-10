from pathlib import Path

from fastapi.testclient import TestClient

from agent_arena.api import app
from agent_arena.service import ArenaService
from agent_arena.store import RunStore


def test_health() -> None:
    assert TestClient(app).get("/health").json() == {"status": "ok"}


def test_evaluation_replay_and_leaderboard(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("agent_arena.api.service", ArenaService(RunStore(tmp_path)))
    client = TestClient(app)
    payload = {
        "suite": {
            "id": "smoke",
            "version": "1",
            "tasks": [{"id": "t1", "prompt": "Say yes", "expected": "yes"}],
        },
        "candidates": [
            {"id": "a", "model": "fixture", "model_version": "1", "prompt_version": "1", "answers": {"t1": "yes"}},
            {"id": "b", "model": "fixture", "model_version": "1", "prompt_version": "1", "answers": {"t1": "no"}},
        ],
        "budget": {"max_steps": 3, "max_tokens": 100, "timeout_seconds": 5},
        "seed": 42,
    }
    response = client.post("/v1/evaluations", json=payload)
    assert response.status_code == 201
    run_id = response.json()["run_ids"][0]
    assert client.get(f"/v1/runs/{run_id}").status_code == 200
    assert client.get(f"/v1/runs/{run_id}/replay").json()["t1"][1]["kind"] == "candidate.output"

    leaderboard = client.get(
        "/v1/leaderboard",
        params={"suite_id": "smoke", "suite_version": "1", "budget": "steps=3;tokens=100;timeout=5"},
    )
    assert [entry["candidate_id"] for entry in leaderboard.json()["entries"]] == ["a", "b"]
