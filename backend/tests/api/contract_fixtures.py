"""Synthetic fixtures covering contract statuses, presentations and variants."""

from __future__ import annotations

from datetime import datetime, timezone
from itertools import product
from typing import Any

STATUSES = {
    "answered": None,
    "refused": "outside_role_access",
    "no_data": "data_not_available",
    "needs_clarification": "ambiguous_entity",
    "error": "unsupported_request",
}
PRESENTATIONS = ("text", "table", "chart")


def _presentation(kind: str) -> dict[str, Any]:
    if kind == "text":
        return {"type": "text"}
    if kind == "table":
        return {
            "type": "table",
            "columns": [{"key": "fixture_value", "label": "Fixture value", "type": "string"}],
            "rows": [{"fixture_value": "Fabricated contract row"}],
            "total_rows": 1,
            "truncated": False,
        }
    return {
        "type": "chart",
        "kind": "bar",
        "title": "Fabricated contract chart",
        "x": {"key": "fixture_x", "label": "Fixture x", "type": "string"},
        "series": [{"key": "fixture_y", "label": "Fixture y"}],
        "rows": [{"fixture_x": "A", "fixture_y": 1}],
        "truncated": False,
    }


def contract_response_fixtures() -> dict[str, dict[str, Any]]:
    fixtures: dict[str, dict[str, Any]] = {}
    for status, presentation in product(STATUSES, PRESENTATIONS):
        reason_code = STATUSES[status]
        evidence: list[dict[str, Any]] = []
        if status == "answered":
            evidence = [
                {
                    "id": "fixture-evidence",
                    "kind": "tool",
                    "label": "Fabricated fixture",
                    "detail": "Synthetic contract fixture.",
                    "columns": ["fixture_value"],
                    "row_count": 1,
                    "rows_preview": [{"fixture_value": "Fabricated contract row"}],
                    "executed_at": datetime(2026, 1, 1, tzinfo=timezone.utc).isoformat(),
                }
            ]
        key = f"{status}__{presentation}"
        fixtures[key] = {
            "contract_version": "0.1",
            "request_id": f"fixture-{key}",
            "role": "owner",
            "thread_id": "owner:fixture_thread",
            "status": status,
            "reason_code": reason_code,
            "answer_text": "Fabricated contract fixture.",
            "presentation": _presentation(presentation),
            "evidence": evidence,
            "notes": [],
        }

    inventory_fixture = fixtures["answered__table"]
    inventory_fixture["role"] = "inventory_manager"
    inventory_fixture["thread_id"] = "inventory_manager:fixture_thread"

    purchase_fixture = fixtures["refused__text"]
    purchase_fixture["role"] = "purchase_manager"
    purchase_fixture["thread_id"] = "purchase_manager:fixture_thread"
    purchase_fixture["reason_code"] = "role_not_configured"

    line_chart_fixture = fixtures["answered__chart"]
    line_chart_fixture["presentation"]["kind"] = "line"
    line_chart_fixture["evidence"][0]["kind"] = "sql_view"

    return fixtures
