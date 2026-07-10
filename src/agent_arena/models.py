from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Task(BaseModel):
    id: str = Field(min_length=1, pattern=r"^[a-zA-Z0-9._-]+$")
    prompt: str = Field(min_length=1)
    expected: str
    grader: str = "exact_match"
    metadata: dict[str, Any] = Field(default_factory=dict)


class Suite(BaseModel):
    id: str = Field(min_length=1, pattern=r"^[a-zA-Z0-9._-]+$")
    version: str = Field(min_length=1)
    tasks: list[Task] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_task_ids(self) -> Suite:
        ids = [task.id for task in self.tasks]
        if len(ids) != len(set(ids)):
            raise ValueError("task ids must be unique")
        return self


class Candidate(BaseModel):
    id: str = Field(min_length=1, pattern=r"^[a-zA-Z0-9._-]+$")
    model: str = Field(min_length=1)
    model_version: str = Field(min_length=1)
    prompt_version: str = Field(min_length=1)
    answers: dict[str, str] = Field(default_factory=dict)


class Budget(BaseModel):
    max_steps: int = Field(default=20, ge=1, le=200)
    max_tokens: int = Field(default=8_000, ge=1)
    timeout_seconds: float = Field(default=120, gt=0, le=3600)

    @property
    def fingerprint(self) -> str:
        return f"steps={self.max_steps};tokens={self.max_tokens};timeout={self.timeout_seconds:g}"


class TraceEvent(BaseModel):
    sequence: int = Field(ge=0)
    kind: str
    timestamp: datetime = Field(default_factory=utc_now)
    payload: dict[str, Any] = Field(default_factory=dict)


class Grade(BaseModel):
    grader: str
    grader_version: str
    score: float = Field(ge=0, le=1)
    passed: bool
    explanation: str


class RunStatus(StrEnum):
    completed = "completed"
    failed = "failed"


class Run(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    suite_id: str
    suite_version: str
    candidate_id: str
    candidate_config: dict[str, str]
    runner_version: str
    budget: Budget
    budget_fingerprint: str
    seed: int
    started_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime | None = None
    status: RunStatus
    traces: dict[str, list[TraceEvent]]
    grades: dict[str, Grade]
    tokens: int = Field(ge=0)
    cost_usd: float = Field(ge=0)
    latency_ms: float = Field(ge=0)


class EvaluationRequest(BaseModel):
    suite: Suite
    candidates: list[Candidate] = Field(min_length=2)
    budget: Budget = Field(default_factory=Budget)
    seed: int = 42

    @model_validator(mode="after")
    def unique_candidate_ids(self) -> EvaluationRequest:
        ids = [candidate.id for candidate in self.candidates]
        if len(ids) != len(set(ids)):
            raise ValueError("candidate ids must be unique")
        return self


class EvaluationResult(BaseModel):
    evaluation_id: UUID = Field(default_factory=uuid4)
    run_ids: list[UUID]
    status: str = "completed"


class LeaderboardEntry(BaseModel):
    candidate_id: str
    runs: int
    successes: int
    success_rate: float
    confidence_low: float
    confidence_high: float
    avg_cost_usd: float
    avg_latency_ms: float
    avg_tokens: float


class LeaderboardSnapshot(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=utc_now)
    suite_id: str
    suite_version: str
    budget_fingerprint: str
    entries: list[LeaderboardEntry]
