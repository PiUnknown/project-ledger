"""Check classified query uses before a role-scoped data operation."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from .policy import Policy

_ERROR_MESSAGES = {
    "invalid_role": "The role is not supported.",
    "role_not_configured": "This role is not configured.",
    "unsupported_request": "The requested data operation is not supported.",
    "outside_role_access": "The requested data operation is outside this role's access.",
}


class QueryValidationError(ValueError):
    """A safe rejection that does not include classified field details."""

    def __init__(self, reason_code: str) -> None:
        self.reason_code = reason_code
        super().__init__(_ERROR_MESSAGES[reason_code])


@dataclass(frozen=True)
class AccessUse:
    """A schema-classified use, without a database field name."""

    classification: str
    operation: str


def validate_query(
    policy: Policy,
    role: str,
    uses: Iterable[AccessUse],
    *,
    facts: Mapping[str, object] | None = None,
) -> None:
    """Reject unknown or forbidden uses; callers supply trusted classifications.

    Schema classification is pending inspection. Restricted roles therefore
    receive no permission for an unclassified use. Conditional permissions are
    denied unless their required schema fact is explicitly supplied as true.
    """
    if not isinstance(role, str) or role not in policy.roles:
        raise QueryValidationError("invalid_role")

    role_policy = policy.roles[role]
    if not role_policy.configured:
        raise QueryValidationError("role_not_configured")

    if isinstance(uses, (str, bytes)):
        raise QueryValidationError("unsupported_request")
    try:
        checked_uses = tuple(uses)
    except TypeError:
        raise QueryValidationError("unsupported_request") from None
    if not checked_uses:
        raise QueryValidationError("unsupported_request")

    if facts is None:
        checked_facts: Mapping[str, object] = {}
    elif isinstance(facts, Mapping):
        checked_facts = facts
    else:
        raise QueryValidationError("unsupported_request")

    for use in checked_uses:
        if (
            not isinstance(use, AccessUse)
            or not isinstance(use.classification, str)
            or not use.classification
            or not isinstance(use.operation, str)
        ):
            raise QueryValidationError("unsupported_request")
        if use.operation not in policy.operations:
            raise QueryValidationError("unsupported_request")

        if role_policy.default_effect == "allow":
            continue
        if use.classification in role_policy.denied_categories:
            raise QueryValidationError("outside_role_access")
        if use.classification in role_policy.allowed_categories:
            continue

        condition = role_policy.conditional_categories.get(use.classification)
        if condition is not None and checked_facts.get(condition.fact) is condition.expected:
            continue
        raise QueryValidationError("outside_role_access")
