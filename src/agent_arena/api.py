from __future__ import annotations

import os
from pathlib import Path
from uuid import UUID

from fastapi import FastAPI, HTTPException, Query

from .models import EvaluationRequest, EvaluationResult, LeaderboardSnapshot, Run
from .service import ArenaService
from .store import RunStore

app = FastAPI(
    title="Agent Evaluation Arena",
    version="0.1.0",
    description="Reproducible, budget-aware evaluation for AI systems.",
)
service = ArenaService(RunStore(Path(os.getenv("ARENA_RUNS_DIR", "runs"))))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/evaluations", response_model=EvaluationResult, status_code=201)
def create_evaluation(request: EvaluationRequest) -> EvaluationResult:
    try:
        return service.evaluate(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/v1/runs/{run_id}", response_model=Run)
def get_run(run_id: UUID) -> Run:
    run = service.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    return run


@app.get("/v1/runs/{run_id}/replay", response_model=dict[str, list])
def replay_run(run_id: UUID) -> dict[str, list]:
    run = service.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    return {task_id: [event.model_dump(mode="json") for event in events] for task_id, events in run.traces.items()}


@app.get("/v1/leaderboard", response_model=LeaderboardSnapshot)
def leaderboard(
    suite_id: str = Query(min_length=1),
    suite_version: str = Query(min_length=1),
    budget: str = Query(min_length=1, description="Exact budget fingerprint from the run"),
) -> LeaderboardSnapshot:
    return service.leaderboard(suite_id, suite_version, budget)
