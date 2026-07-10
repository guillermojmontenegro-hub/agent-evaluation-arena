from __future__ import annotations

import random
from collections import defaultdict
from datetime import datetime, timezone
from uuid import UUID

from .graders import grade
from .models import (
    Candidate,
    EvaluationRequest,
    EvaluationResult,
    LeaderboardEntry,
    LeaderboardSnapshot,
    Run,
    RunStatus,
    TraceEvent,
)
from .stats import wilson_interval
from .store import RunStore

RUNNER_VERSION = "local-answer-runner@1.0.0"


class ArenaService:
    def __init__(self, store: RunStore) -> None:
        self.store = store

    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        run_ids = [self._run_candidate(request, candidate).id for candidate in request.candidates]
        return EvaluationResult(run_ids=run_ids)

    def _run_candidate(self, request: EvaluationRequest, candidate: Candidate) -> Run:
        rng = random.Random(f"{request.seed}:{candidate.id}")
        traces = {}
        grades = {}
        total_tokens = 0
        total_latency = 0.0

        for task in request.suite.tasks:
            output = candidate.answers.get(task.id, "")
            input_tokens = max(1, len(task.prompt.split()))
            output_tokens = len(output.split())
            latency = round(18 + rng.random() * 42 + output_tokens * 1.8, 2)
            total_tokens += input_tokens + output_tokens
            total_latency += latency
            traces[task.id] = [
                TraceEvent(sequence=0, kind="task.started", payload={"prompt": task.prompt}),
                TraceEvent(
                    sequence=1,
                    kind="candidate.output",
                    payload={"output": output, "input_tokens": input_tokens, "output_tokens": output_tokens},
                ),
                TraceEvent(sequence=2, kind="task.completed", payload={"latency_ms": latency}),
            ]
            grades[task.id] = grade(task, output)

        cost = round(total_tokens * 0.000002, 6)
        completed_at = datetime.now(timezone.utc)
        run = Run(
            suite_id=request.suite.id,
            suite_version=request.suite.version,
            candidate_id=candidate.id,
            candidate_config={
                "model": candidate.model,
                "model_version": candidate.model_version,
                "prompt_version": candidate.prompt_version,
            },
            runner_version=RUNNER_VERSION,
            budget=request.budget,
            budget_fingerprint=request.budget.fingerprint,
            seed=request.seed,
            completed_at=completed_at,
            status=RunStatus.completed,
            traces=traces,
            grades=grades,
            tokens=total_tokens,
            cost_usd=cost,
            latency_ms=round(total_latency, 2),
        )
        self.store.save(run)
        return run

    def get_run(self, run_id: UUID) -> Run | None:
        return self.store.get(run_id)

    def leaderboard(self, suite_id: str, suite_version: str, budget_fingerprint: str) -> LeaderboardSnapshot:
        compatible = [
            run
            for run in self.store.list()
            if run.suite_id == suite_id
            and run.suite_version == suite_version
            and run.budget_fingerprint == budget_fingerprint
        ]
        grouped: dict[str, list[Run]] = defaultdict(list)
        for run in compatible:
            grouped[run.candidate_id].append(run)

        entries = []
        for candidate_id, runs in grouped.items():
            grades = [item for run in runs for item in run.grades.values()]
            successes = sum(item.passed for item in grades)
            low, high = wilson_interval(successes, len(grades))
            entries.append(
                LeaderboardEntry(
                    candidate_id=candidate_id,
                    runs=len(runs),
                    successes=successes,
                    success_rate=successes / len(grades) if grades else 0,
                    confidence_low=low,
                    confidence_high=high,
                    avg_cost_usd=sum(run.cost_usd for run in runs) / len(runs),
                    avg_latency_ms=sum(run.latency_ms for run in runs) / len(runs),
                    avg_tokens=sum(run.tokens for run in runs) / len(runs),
                )
            )
        entries.sort(key=lambda entry: (-entry.success_rate, entry.avg_cost_usd, entry.avg_latency_ms))
        return LeaderboardSnapshot(
            suite_id=suite_id,
            suite_version=suite_version,
            budget_fingerprint=budget_fingerprint,
            entries=entries,
        )
