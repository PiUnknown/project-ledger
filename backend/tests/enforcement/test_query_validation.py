import pytest

from app.enforcement.policy import load_policy
from app.enforcement.query_validation import (
    AccessUse,
    QueryValidationError,
    validate_query,
)


@pytest.fixture
def policy():
    return load_policy()


@pytest.mark.parametrize(
    "classification",
    ["item_identity", "descriptive_attributes", "stock_levels", "reorder_information"],
)
def test_inventory_manager_can_use_explicitly_allowed_categories(policy, classification) -> None:
    validate_query(policy, "inventory_manager", [AccessUse(classification, "select")])


@pytest.mark.parametrize(
    "operation",
    ["select", "filter", "order", "group", "join", "aggregate", "derive"],
)
@pytest.mark.parametrize("classification", ["monetary", "proxy", "unclassified"])
def test_inventory_manager_denies_monetary_proxy_and_unclassified_uses(
    policy, operation, classification
) -> None:
    with pytest.raises(QueryValidationError) as error:
        validate_query(
            policy,
            "inventory_manager",
            [AccessUse(classification, operation)],
        )

    assert error.value.reason_code == "outside_role_access"
    assert "monetary" not in str(error.value)
    assert "proxy" not in str(error.value)


def test_units_sold_is_denied_until_schema_fact_is_confirmed(policy) -> None:
    use = [AccessUse("units_sold", "select")]

    with pytest.raises(QueryValidationError, match="outside this role"):
        validate_query(policy, "inventory_manager", use)
    with pytest.raises(QueryValidationError):
        validate_query(
            policy,
            "inventory_manager",
            use,
            facts={"stored_separately_from_amounts": False},
        )

    validate_query(
        policy,
        "inventory_manager",
        use,
        facts={"stored_separately_from_amounts": True},
    )


def test_owner_is_not_restricted_by_schema_independent_classification(policy) -> None:
    validate_query(policy, "owner", [AccessUse("unclassified", "select")])


def test_unconfigured_and_unknown_roles_are_denied(policy) -> None:
    with pytest.raises(QueryValidationError) as unconfigured:
        validate_query(policy, "purchase_manager", [AccessUse("stock_levels", "select")])
    assert unconfigured.value.reason_code == "role_not_configured"

    with pytest.raises(QueryValidationError) as unknown:
        validate_query(policy, "unknown", [AccessUse("stock_levels", "select")])
    assert unknown.value.reason_code == "invalid_role"


def test_unknown_operations_and_empty_access_sets_are_denied(policy) -> None:
    with pytest.raises(QueryValidationError) as unsupported:
        validate_query(policy, "owner", [AccessUse("anything", "unknown")])
    assert unsupported.value.reason_code == "unsupported_request"

    with pytest.raises(QueryValidationError) as empty:
        validate_query(policy, "owner", [])
    assert empty.value.reason_code == "unsupported_request"
