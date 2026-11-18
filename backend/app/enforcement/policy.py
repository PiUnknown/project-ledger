"""Load the schema-independent, deny-by-default role policy."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

_REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_POLICY_PATH = _REPOSITORY_ROOT / "db" / "policy" / "roles.json"
_REQUIRED_ROLES = {"owner", "inventory_manager", "purchase_manager"}
_SUPPORTED_OPERATIONS = {
    "select",
    "filter",
    "order",
    "group",
    "join",
    "aggregate",
    "derive",
}
_INVENTORY_CATEGORIES = {
    "item_identity",
    "descriptive_attributes",
    "stock_levels",
    "reorder_information",
}
_DENIED_INVENTORY_CATEGORIES = {"monetary", "proxy"}


class PolicyLoadError(ValueError):
    """Raised with a non-sensitive message when policy cannot be trusted."""

    def __init__(self) -> None:
        super().__init__("Policy configuration is invalid or unavailable.")


@dataclass(frozen=True)
class ConditionalCategory:
    fact: str
    expected: bool


@dataclass(frozen=True)
class RolePolicy:
    configured: bool
    default_effect: str
    allowed_categories: frozenset[str]
    denied_categories: frozenset[str]
    conditional_categories: Mapping[str, ConditionalCategory]


@dataclass(frozen=True)
class Policy:
    roles: Mapping[str, RolePolicy]
    operations: frozenset[str]


def _invalid_policy() -> PolicyLoadError:
    return PolicyLoadError()


def _as_object(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise _invalid_policy()
    return value


def _as_string_set(value: object) -> frozenset[str]:
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item for item in value
    ):
        raise _invalid_policy()
    if len(set(value)) != len(value):
        raise _invalid_policy()
    return frozenset(value)


def _parse_role(role_id: str, value: object) -> RolePolicy:
    raw = _as_object(value)
    configured = raw.get("configured")
    default_effect = raw.get("default_effect")
    if type(configured) is not bool or default_effect not in {"allow", "deny"}:
        raise _invalid_policy()

    conditional_raw = _as_object(raw.get("conditional_categories"))
    conditional: dict[str, ConditionalCategory] = {}
    for category, condition_value in conditional_raw.items():
        if not isinstance(category, str) or not category:
            raise _invalid_policy()
        condition = _as_object(condition_value)
        fact = condition.get("fact")
        expected = condition.get("expected")
        if not isinstance(fact, str) or not fact or type(expected) is not bool:
            raise _invalid_policy()
        conditional[category] = ConditionalCategory(fact=fact, expected=expected)

    return RolePolicy(
        configured=configured,
        default_effect=default_effect,
        allowed_categories=_as_string_set(raw.get("allowed_categories")),
        denied_categories=_as_string_set(raw.get("denied_categories")),
        conditional_categories=MappingProxyType(conditional),
    )


def _validate_role_rules(roles: Mapping[str, RolePolicy], raw_roles: Mapping[str, object]) -> None:
    owner = roles["owner"]
    if (
        not owner.configured
        or owner.default_effect != "allow"
        or owner.allowed_categories != frozenset({"*"})
        or owner.denied_categories
        or owner.conditional_categories
    ):
        raise _invalid_policy()

    inventory = roles["inventory_manager"]
    if (
        not inventory.configured
        or inventory.default_effect != "deny"
        or not _INVENTORY_CATEGORIES.issubset(inventory.allowed_categories)
        or not _DENIED_INVENTORY_CATEGORIES.issubset(inventory.denied_categories)
        or set(inventory.conditional_categories) != {"units_sold"}
        or inventory.conditional_categories["units_sold"].fact
        != "stored_separately_from_amounts"
        or not inventory.conditional_categories["units_sold"].expected
    ):
        raise _invalid_policy()

    purchase = roles["purchase_manager"]
    purchase_raw = _as_object(raw_roles["purchase_manager"])
    outcome = _as_object(purchase_raw.get("unconfigured_outcome"))
    if (
        purchase.configured
        or purchase.default_effect != "deny"
        or purchase.allowed_categories
        or outcome.get("status") != "refused"
        or outcome.get("reason_code") != "role_not_configured"
    ):
        raise _invalid_policy()


def load_policy(path: str | Path | None = None) -> Policy:
    """Load and validate the policy; there is no permissive fallback."""
    policy_path = Path(path) if path is not None else DEFAULT_POLICY_PATH
    try:
        document = json.loads(policy_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise _invalid_policy() from None

    raw = _as_object(document)
    if (
        type(raw.get("policy_version")) is not int
        or raw["policy_version"] != 1
        or raw.get("source_document") != "docs/roles.md"
        or raw.get("schema_classifications") != "pending schema inspection"
        or raw.get("column_classifications") != []
    ):
        raise _invalid_policy()

    operations = _as_string_set(raw.get("query_operations"))
    if operations != frozenset(_SUPPORTED_OPERATIONS):
        raise _invalid_policy()

    raw_roles = _as_object(raw.get("roles"))
    if set(raw_roles) != _REQUIRED_ROLES:
        raise _invalid_policy()
    roles = {role_id: _parse_role(role_id, raw_roles[role_id]) for role_id in _REQUIRED_ROLES}
    _validate_role_rules(roles, raw_roles)

    return Policy(roles=MappingProxyType(roles), operations=operations)
