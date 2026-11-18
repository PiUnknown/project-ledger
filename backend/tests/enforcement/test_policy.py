import json

import pytest

from app.enforcement.policy import PolicyLoadError, load_policy


def test_load_policy_mirrors_the_defined_roles() -> None:
    policy = load_policy()

    assert set(policy.roles) == {"owner", "inventory_manager", "purchase_manager"}
    assert policy.roles["owner"].default_effect == "allow"
    assert policy.roles["inventory_manager"].default_effect == "deny"
    assert policy.roles["purchase_manager"].configured is False
    assert policy.roles["purchase_manager"].allowed_categories == frozenset()


def test_policy_has_no_schema_classifications() -> None:
    policy = load_policy()

    assert policy.roles["inventory_manager"].allowed_categories == frozenset(
        {
            "item_identity",
            "descriptive_attributes",
            "stock_levels",
            "reorder_information",
        }
    )
    assert policy.roles["inventory_manager"].conditional_categories["units_sold"].fact == (
        "stored_separately_from_amounts"
    )


def test_policy_load_fails_closed_when_file_is_missing(tmp_path) -> None:
    with pytest.raises(PolicyLoadError, match="invalid or unavailable"):
        load_policy(tmp_path / "missing.json")


def test_policy_load_fails_closed_when_policy_is_malformed(tmp_path) -> None:
    policy_path = tmp_path / "roles.json"
    policy_path.write_text(json.dumps({"policy_version": 1}), encoding="utf-8")

    with pytest.raises(PolicyLoadError, match="invalid or unavailable"):
        load_policy(policy_path)
