#!/usr/bin/env python3
"""Analyze synthetic customer-support tickets using only Python's standard library."""
from __future__ import annotations
import argparse
import csv
import json
from collections import Counter
from datetime import datetime, UTC
from pathlib import Path

POSITIVE = {"thanks", "helpful", "resolved", "excellent", "good", "quick"}
NEGATIVE = {"angry", "broken", "failed", "slow", "bad", "urgent", "error", "issue"}


def sentiment(text: str) -> str:
    words = {w.strip(".,!?;:").lower() for w in text.split()}
    score = len(words & POSITIVE) - len(words & NEGATIVE)
    return "positive" if score > 0 else "negative" if score < 0 else "neutral"


def load_tickets(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    required = {"ticket_id", "created_at", "category", "priority", "status", "resolution_hours", "message"}
    if not rows:
        raise ValueError("Input CSV contains no tickets")
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"Missing columns: {', '.join(sorted(missing))}")
    return rows


def analyze(rows: list[dict[str, str]]) -> dict:
    categories = Counter(r["category"] for r in rows)
    priorities = Counter(r["priority"] for r in rows)
    statuses = Counter(r["status"] for r in rows)
    sentiments = Counter(sentiment(r["message"]) for r in rows)
    hours = [float(r["resolution_hours"]) for r in rows if r["resolution_hours"].strip()]
    breached = [r for r in rows if float(r["resolution_hours"] or 0) > (4 if r["priority"] == "High" else 24)]
    return {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "total_tickets": len(rows),
        "category_counts": dict(categories),
        "priority_counts": dict(priorities),
        "status_counts": dict(statuses),
        "sentiment_counts": dict(sentiments),
        "average_resolution_hours": round(sum(hours) / len(hours), 2) if hours else None,
        "sla_breach_count": len(breached),
        "sla_breach_rate_percent": round(len(breached) * 100 / len(rows), 2),
    }


def markdown_report(result: dict) -> str:
    def bullets(values: dict) -> str:
        return "\n".join(f"- **{k}:** {v}" for k, v in sorted(values.items()))
    return f"""# Customer Support Insights Report

Generated: {result['generated_at']}

## Executive summary
- **Total tickets:** {result['total_tickets']}
- **Average resolution time:** {result['average_resolution_hours']} hours
- **SLA breaches:** {result['sla_breach_count']} ({result['sla_breach_rate_percent']}%)

## Tickets by category
{bullets(result['category_counts'])}

## Tickets by priority
{bullets(result['priority_counts'])}

## Ticket status
{bullets(result['status_counts'])}

## Keyword-based sentiment
{bullets(result['sentiment_counts'])}

## Notes
This portfolio project uses synthetic data and a transparent keyword-based sentiment rule. It is intended to demonstrate clean Python, CSV processing, automated testing, reporting, and CI rather than production-grade NLP.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze customer-support ticket data")
    parser.add_argument("--input", default="data/sample_tickets.csv")
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    result = analyze(load_tickets(Path(args.input)))
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (out / "report.md").write_text(markdown_report(result), encoding="utf-8")
    print(f"Analyzed {result['total_tickets']} tickets. Reports written to {out}/")


if __name__ == "__main__":
    main()
