"""Terminal + file report generation for harness runs."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich import box

from app.logger import get_logger

logger = get_logger(__name__)
console = Console()
HARNESS_LOG = Path("logs/harness.jsonl")


def print_report(suite: str, results: list[dict], duration_s: float) -> None:
    passed = sum(1 for r in results if r["passed"])
    failed = len(results) - passed
    avg = sum(r["judge_score"] for r in results) / len(results) if results else 0

    console.rule(f"[bold cyan]Harness: {suite}[/bold cyan]")

    table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("#", width=3)
    table.add_column("Question", max_width=40)
    table.add_column("Score", width=7)
    table.add_column("Status", width=8)
    table.add_column("Answer preview", max_width=50)

    for i, r in enumerate(results, 1):
        status = "[green]PASS[/green]" if r["passed"] else "[red]FAIL[/red]"
        table.add_row(
            str(i),
            r["question"][:40],
            f"{r['judge_score']:.1f}",
            status,
            r.get("answer", "")[:50],
        )

    console.print(table)
    console.print(
        f"[bold]Suite:[/bold] {suite} | "
        f"[green]{passed} passed[/green] / [red]{failed} failed[/red] | "
        f"Avg score: [bold]{avg:.2f}[/bold] | "
        f"Duration: {duration_s:.1f}s"
    )


def save_to_log(suite: str, results: list[dict], duration_s: float) -> None:
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "suite": suite,
        "total": len(results),
        "passed": sum(1 for r in results if r["passed"]),
        "failed": sum(1 for r in results if not r["passed"]),
        "avg_score": sum(r["judge_score"] for r in results) / len(results) if results else 0,
        "duration_s": round(duration_s, 2),
        "results": results,
    }
    HARNESS_LOG.parent.mkdir(exist_ok=True)
    with open(HARNESS_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    logger.info("Harness run saved to log", extra={"suite": suite, "file": str(HARNESS_LOG)})
