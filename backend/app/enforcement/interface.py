"""The role executor boundary used by agents to access data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from app.roles.context import RoleContext
from app.schemas import EvidenceEntry, TableColumn


@dataclass(frozen=True)
class ExecutionResult:
    columns: tuple[TableColumn, ...]
    rows: tuple[dict[str, Any], ...]
    total_rows: int
    truncated: bool
    evidence: EvidenceEntry


class RoleExecutor(Protocol):
    """Executes named, typed operations under a validated role context."""

    def execute(
        self,
        context: RoleContext,
        operation: str,
        parameters: Mapping[str, Any],
        *,
        row_limit: int,
        timeout_ms: int,
    ) -> ExecutionResult:
        """Run an allowed operation within row and time budgets."""


class ExecutionDenied(Exception):
    """Raised when the role executor cannot allow the requested operation."""


class RoleNotConfigured(Exception):
    """Raised when a role has no approved access policy."""


class QueryTimeout(Exception):
    """Raised when an execution exceeds the configured query timeout."""
