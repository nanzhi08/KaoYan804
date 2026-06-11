"""Shared import report helpers for data import and cleanup scripts."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


REPORT_DIR = Path("data") / "import_reports"


@dataclass
class ImportReport:
    script: str
    dry_run: bool = True
    source_filter: str | None = None
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    finished_at: str | None = None
    counters: dict[str, int] = field(default_factory=dict)
    sources: dict[str, dict[str, Any]] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def inc(self, key: str, amount: int = 1) -> None:
        self.counters[key] = self.counters.get(key, 0) + amount

    def set_source(self, name: str, data: dict[str, Any]) -> None:
        self.sources[name] = data

    def add_error(self, message: str) -> None:
        self.errors.append(message)

    def finish(self) -> None:
        self.finished_at = datetime.utcnow().isoformat()


def write_report(report: ImportReport, report_dir: Path = REPORT_DIR) -> Path:
    report.finish()
    report_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_script = report.script.replace("\\", "_").replace("/", "_").replace(".", "_")
    path = report_dir / f"{timestamp}_{safe_script}.json"
    path.write_text(
        json.dumps(asdict(report), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path
