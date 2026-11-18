"""Fixture-backed executor for API development without database access."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from app.enforcement.interface import (
    ExecutionDenied,
    ExecutionResult,
    RoleExecutor,
    RoleNotConfigured,
)
from app.roles.context import Role, RoleContext
from app.schemas import EvidenceEntry, TableColumn


class MockExecutor:
    """Serve synthetic fixture rows through one fixed operation."""

    def __init__(self, fixture_path: Path | None = None) -> None:
        path = fixture_path or Path(__file__).parent / "fixtures" / "mock_items.json"
        with path.open(encoding="utf-8") as fixture_file:
            self._fixture = json.load(fixture_file)

    def execute(
        self,
        context: RoleContext,
        operation: str,
        parameters: Mapping[str, Any],
        *,
        row_limit: int,
        timeout_ms: int,
    ) -> ExecutionResult:
        if context.role is Role.PURCHASE_MANAGER:
            raise RoleNotConfigured("role_not_configured")
        if operation != "list_sample_items" or parameters:
            raise ExecutionDenied("unsupported_operation")
        if row_limit <= 0:
            raise ValueError("row_limit must be positive")
        if timeout_ms <= 0:
            raise ValueError("timeout_ms must be positive")

        fixture_columns = tuple(
            TableColumn.model_validate(column) for column in self._fixture["columns"]
        )
        all_rows = self._fixture["rows"]
        selected_rows = tuple(dict(row) for row in all_rows[:row_limit])
        column_keys = [column.key for column in fixture_columns]
        evidence = EvidenceEntry(
            id="mock-list-sample-items",
            kind="tool",
            label="Fabricated sample items",
            detail="Fixture-backed mock operation: list_sample_items",
            columns=column_keys,
            row_count=len(selected_rows),
            rows_preview=list(selected_rows),
            executed_at=datetime.now(timezone.utc),
        )
        return ExecutionResult(
            columns=fixture_columns,
            rows=selected_rows,
            total_rows=len(all_rows),
            truncated=len(all_rows) > len(selected_rows),
            evidence=evidence,
        )


def build_mock_executor() -> RoleExecutor:
    """Return the default fixture-backed RoleExecutor implementation."""

    return MockExecutor()
