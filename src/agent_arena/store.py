from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from uuid import UUID

from .models import Run


class RunStore:
    """Append-only JSON store: inspectable, replayable, and safe to replace later."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self._lock = Lock()

    def save(self, run: Run) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        target = self.root / f"{run.id}.json"
        temporary = target.with_suffix(".tmp")
        with self._lock:
            temporary.write_text(run.model_dump_json(indent=2), encoding="utf-8")
            temporary.replace(target)

    def get(self, run_id: UUID) -> Run | None:
        target = self.root / f"{run_id}.json"
        if not target.exists():
            return None
        return Run.model_validate_json(target.read_text(encoding="utf-8"))

    def list(self) -> list[Run]:
        if not self.root.exists():
            return []
        runs = []
        for target in sorted(self.root.glob("*.json")):
            try:
                runs.append(Run.model_validate(json.loads(target.read_text(encoding="utf-8"))))
            except (ValueError, json.JSONDecodeError):
                continue
        return runs
