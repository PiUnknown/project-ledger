"""Role validation and role-scoped conversation identity."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Role(str, Enum):
    OWNER = "owner"
    INVENTORY_MANAGER = "inventory_manager"
    PURCHASE_MANAGER = "purchase_manager"


class InvalidRole(ValueError):
    """Raised when a request supplies a role outside the contract."""


@dataclass(frozen=True)
class RoleContext:
    role: Role

    @classmethod
    def from_request(cls, role_name: str) -> RoleContext:
        try:
            return cls(role=Role(role_name))
        except ValueError as error:
            raise InvalidRole(role_name) from error

    def effective_thread_id(self, client_thread_id: str) -> str:
        return f"{self.role.value}:{client_thread_id}"

    @property
    def configured(self) -> bool:
        return self.role is not Role.PURCHASE_MANAGER
