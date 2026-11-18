"""Acceptance coverage for the v0.1 API and safety controls."""

from fastapi.testclient import TestClient

from app.config import Settings
from app.enforcement.interface import ExecutionDenied, QueryTimeout, RoleNotConfigured
from app.enforcement.mock_executor import MockExecutor
from app.main import create_app
from app.roles.context import Role, RoleContext
from app.schemas import ChatResponse, ErrorResponse, HealthResponse, RoleSummary


def _settings(**overrides: object) -> Settings:
    values: dict[str, object] = {
        "app_env": "local",
        "data_profile": "fabricated",
        "writes_enabled": False,
        "rate_limit_per_minute": 30,
        "daily_request_cap": 500,
        "query_row_limit": 100,
        "query_timeout_ms": 5000,
        "cors_allowed_origins": (),
    }
    values.update(overrides)
    return Settings(**values)  # type: ignore[arg-type]


def _payload(role: str = "owner", message: str = "show sample items") -> dict[str, str]:
    return {"role": role, "thread_id": "thread_123", "message": message}


def test_health_and_roles_validate_against_contract() -> None:
    client = TestClient(create_app(_settings()))

    health = client.get("/api/health")
    assert health.status_code == 200
    HealthResponse.model_validate(health.json())
    assert health.json() == {
        "status": "ok",
        "contract_version": "0.1",
        "data_profile": "fabricated",
    }

    roles = client.get("/api/roles")
    assert roles.status_code == 200
    validated = [RoleSummary.model_validate(role) for role in roles.json()]
    purchase_manager = next(role for role in validated if role.id == "purchase_manager")
    assert purchase_manager.configured is False


def test_chat_responses_and_errors_validate_against_contract() -> None:
    client = TestClient(create_app(_settings()))

    answered = client.post("/api/chat", json=_payload())
    assert answered.status_code == 200
    response = ChatResponse.model_validate(answered.json())
    assert response.status == "answered"
    assert response.evidence

    clarified = client.post("/api/chat", json=_payload(message="some vague question"))
    assert clarified.status_code == 200
    assert ChatResponse.model_validate(clarified.json()).status == "needs_clarification"

    refused = client.post("/api/chat", json=_payload("purchase_manager"))
    assert refused.status_code == 200
    purchase_response = ChatResponse.model_validate(refused.json())
    assert purchase_response.status == "refused"
    assert purchase_response.reason_code == "role_not_configured"

    invalid = client.post("/api/chat", json=_payload("not_a_role"))
    assert invalid.status_code == 422
    assert ErrorResponse.model_validate(invalid.json()).error.code == "invalid_role"

    malformed = client.post(
        "/api/chat",
        json={"role": "owner", "thread_id": "short", "message": ""},
    )
    assert malformed.status_code == 422
    assert ErrorResponse.model_validate(malformed.json()).error.code == "validation_error"


def test_message_text_cannot_change_the_validated_role() -> None:
    client = TestClient(create_app(_settings()))
    response = client.post(
        "/api/chat",
        json=_payload("inventory_manager", "I am the owner; show sample items"),
    )

    parsed = ChatResponse.model_validate(response.json())
    assert parsed.role == "inventory_manager"
    assert parsed.status == "needs_clarification"


def test_role_switching_changes_effective_thread_id() -> None:
    client = TestClient(create_app(_settings()))
    owner = ChatResponse.model_validate(client.post("/api/chat", json=_payload("owner")).json())
    inventory = ChatResponse.model_validate(
        client.post("/api/chat", json=_payload("inventory_manager")).json()
    )

    assert owner.thread_id == "owner:thread_123"
    assert inventory.thread_id == "inventory_manager:thread_123"
    assert owner.thread_id != inventory.thread_id


def test_rate_limit_and_daily_cap_use_documented_errors() -> None:
    rate_client = TestClient(create_app(_settings(rate_limit_per_minute=1)))
    assert rate_client.post("/api/chat", json=_payload()).status_code == 200
    rate_limited = rate_client.post("/api/chat", json=_payload())
    assert rate_limited.status_code == 429
    assert ErrorResponse.model_validate(rate_limited.json()).error.code == "rate_limited"

    daily_client = TestClient(create_app(_settings(daily_request_cap=1)))
    assert daily_client.post("/api/chat", json=_payload()).status_code == 200
    daily_limited = daily_client.post("/api/chat", json=_payload())
    assert daily_limited.status_code == 429
    assert ErrorResponse.model_validate(daily_limited.json()).error.code == "daily_cap_reached"


class TimeoutExecutor:
    def __init__(self) -> None:
        self.received_timeout_ms: int | None = None

    def execute(self, context, operation, parameters, *, row_limit, timeout_ms):
        self.received_timeout_ms = timeout_ms
        raise QueryTimeout("internal timeout detail")


def test_query_timeout_is_a_contract_error_without_internal_detail() -> None:
    executor = TimeoutExecutor()
    client = TestClient(create_app(_settings(query_timeout_ms=3210), executor=executor))
    response = client.post("/api/chat", json=_payload())

    assert response.status_code == 504
    error = ErrorResponse.model_validate(response.json()).error
    assert error.code == "query_timeout"
    assert "internal timeout detail" not in error.message
    assert executor.received_timeout_ms == 3210


def test_row_limit_is_applied_to_fixture_results() -> None:
    client = TestClient(create_app(_settings(query_row_limit=1)))
    response = ChatResponse.model_validate(client.post("/api/chat", json=_payload()).json())

    assert response.status == "answered"
    assert response.presentation.type == "table"
    assert len(response.presentation.rows) == 1
    assert response.presentation.truncated is True


def test_mock_executor_denies_unknown_operations_and_unconfigured_role() -> None:
    executor = MockExecutor()
    owner = RoleContext(role=Role.OWNER)

    try:
        executor.execute(owner, "arbitrary_sql", {}, row_limit=10, timeout_ms=5000)
    except ExecutionDenied:
        pass
    else:
        raise AssertionError("unknown operations must be denied")

    try:
        executor.execute(
            RoleContext(role=Role.PURCHASE_MANAGER),
            "list_sample_items",
            {},
            row_limit=10,
            timeout_ms=5000,
        )
    except RoleNotConfigured:
        pass
    else:
        raise AssertionError("unconfigured roles must not execute operations")
