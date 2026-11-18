import pytest

from app.enforcement.interface import (
    ExecutionDenied,
    ExecutionResult,
    RoleExecutor,
    RoleNotConfigured,
)
from app.enforcement.mock_executor import build_mock_executor
from app.roles.context import Role, RoleContext
from app.schemas import EvidenceEntry, TableColumn


@pytest.fixture
def executor() -> RoleExecutor:
    return build_mock_executor()


def _execute_sample(
    executor: RoleExecutor,
    role: Role,
    *,
    row_limit: int = 10,
    timeout_ms: int = 1000,
) -> ExecutionResult:
    return executor.execute(
        context=RoleContext.from_request(role.value),
        operation="list_sample_items",
        parameters={},
        row_limit=row_limit,
        timeout_ms=timeout_ms,
    )


@pytest.mark.parametrize("role", [Role.OWNER, Role.INVENTORY_MANAGER])
def test_mock_returns_documented_result_and_evidence_shapes(executor, role) -> None:
    result = _execute_sample(executor, role)

    assert isinstance(result, ExecutionResult)
    assert isinstance(result.columns, tuple)
    assert all(isinstance(column, TableColumn) for column in result.columns)
    assert isinstance(result.rows, tuple)
    assert all(type(row) is dict for row in result.rows)
    assert isinstance(result.total_rows, int)
    assert result.total_rows >= len(result.rows)
    assert isinstance(result.truncated, bool)
    assert result.truncated is (result.total_rows > len(result.rows))
    assert all(set(row).issubset({column.key for column in result.columns}) for row in result.rows)

    evidence = result.evidence
    assert isinstance(evidence, EvidenceEntry)
    assert evidence.kind == "tool"
    assert isinstance(evidence.id, str)
    assert isinstance(evidence.label, str)
    assert isinstance(evidence.detail, str)
    assert evidence.columns == [column.key for column in result.columns]
    assert evidence.row_count == len(result.rows)
    assert evidence.rows_preview == list(result.rows)


def test_mock_applies_row_limit_and_reports_total_before_truncation(executor) -> None:
    full = _execute_sample(executor, Role.OWNER, row_limit=10000)
    limited = _execute_sample(executor, Role.OWNER, row_limit=1)

    assert len(limited.rows) <= 1
    assert limited.rows == full.rows[:1]
    assert limited.total_rows == full.total_rows
    assert limited.truncated is (limited.total_rows > len(limited.rows))
    assert limited.evidence.row_count == len(limited.rows)
    assert limited.evidence.rows_preview == list(limited.rows)


@pytest.mark.parametrize(
    ("operation", "parameters"),
    [
        ("unsupported_operation", {}),
        ("list_sample_items", {"unsupported": True}),
    ],
)
def test_mock_uses_documented_denial_for_unsupported_requests(
    executor, operation, parameters
) -> None:
    with pytest.raises(ExecutionDenied, match="^unsupported_operation$"):
        executor.execute(
            RoleContext.from_request("owner"),
            operation,
            parameters,
            row_limit=1,
            timeout_ms=1000,
        )


def test_mock_uses_documented_error_for_unconfigured_role(executor) -> None:
    with pytest.raises(RoleNotConfigured, match="^role_not_configured$"):
        executor.execute(
            RoleContext.from_request("purchase_manager"),
            "list_sample_items",
            {},
            row_limit=1,
            timeout_ms=1000,
        )


@pytest.mark.parametrize("row_limit", [0, -1])
def test_mock_requires_a_positive_row_limit(executor, row_limit) -> None:
    with pytest.raises(ValueError, match="^row_limit must be positive$"):
        _execute_sample(executor, Role.OWNER, row_limit=row_limit)


@pytest.mark.parametrize("timeout_ms", [0, -1])
def test_mock_requires_a_positive_timeout_budget(executor, timeout_ms) -> None:
    with pytest.raises(ValueError, match="^timeout_ms must be positive$"):
        _execute_sample(executor, Role.OWNER, timeout_ms=timeout_ms)


def test_mock_accepts_a_positive_timeout_budget_without_measuring_elapsed_time(executor) -> None:
    result = _execute_sample(executor, Role.OWNER, timeout_ms=1)

    assert isinstance(result, ExecutionResult)
