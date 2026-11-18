"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping


class ConfigurationError(ValueError):
    """Raised when an environment configuration is unsafe or invalid."""


def _positive_int(name: str, value: str | None, default: int) -> int:
    if value is None or not value.strip():
        return default
    try:
        parsed = int(value)
    except ValueError as error:
        raise ConfigurationError(f"{name} must be a positive integer") from error
    if parsed <= 0:
        raise ConfigurationError(f"{name} must be a positive integer")
    return parsed


def _bool_value(name: str, value: str | None, default: bool = False) -> bool:
    if value is None or not value.strip():
        return default
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "on"}:
        return True
    if normalized in {"false", "0", "no", "off"}:
        return False
    raise ConfigurationError(f"{name} must be true or false")


@dataclass(frozen=True)
class Settings:
    app_env: str = "local"
    data_profile: str = "private"
    writes_enabled: bool = False
    rate_limit_per_minute: int = 30
    daily_request_cap: int = 500
    query_row_limit: int = 100
    query_timeout_ms: int = 5000
    cors_allowed_origins: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.app_env not in {"local", "hosted"}:
            raise ConfigurationError("APP_ENV must be local or hosted")
        if self.data_profile not in {"private", "fabricated"}:
            raise ConfigurationError("DATA_PROFILE must be private or fabricated")
        if self.app_env == "hosted" and self.data_profile == "private":
            raise ConfigurationError("hosted mode cannot use the private data profile")
        if self.app_env == "hosted" and self.writes_enabled:
            raise ConfigurationError("hosted mode cannot enable writes")
        for name in (
            "rate_limit_per_minute",
            "daily_request_cap",
            "query_row_limit",
            "query_timeout_ms",
        ):
            if getattr(self, name) <= 0:
                raise ConfigurationError(f"{name} must be a positive integer")

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> Settings:
        values = os.environ if environ is None else environ
        app_env = values.get("APP_ENV", "local").strip().lower() or "local"
        data_profile = values.get("DATA_PROFILE", "private").strip().lower() or "private"
        cors_value = values.get("CORS_ALLOWED_ORIGINS", "")
        cors_origins = tuple(origin.strip() for origin in cors_value.split(",") if origin.strip())
        return cls(
            app_env=app_env,
            data_profile=data_profile,
            writes_enabled=_bool_value("WRITES_ENABLED", values.get("WRITES_ENABLED")),
            rate_limit_per_minute=_positive_int(
                "RATE_LIMIT_PER_MINUTE", values.get("RATE_LIMIT_PER_MINUTE"), 30
            ),
            daily_request_cap=_positive_int(
                "DAILY_REQUEST_CAP", values.get("DAILY_REQUEST_CAP"), 500
            ),
            query_row_limit=_positive_int("QUERY_ROW_LIMIT", values.get("QUERY_ROW_LIMIT"), 100),
            query_timeout_ms=_positive_int(
                "QUERY_TIMEOUT_MS", values.get("QUERY_TIMEOUT_MS"), 5000
            ),
            cors_allowed_origins=cors_origins,
        )
