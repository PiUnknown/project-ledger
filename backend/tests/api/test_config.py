"""Configuration validation and hosted-mode startup guards."""

import pytest

from app.config import ConfigurationError, Settings


@pytest.mark.parametrize(
    "overrides",
    [
        {"APP_ENV": "hosted", "DATA_PROFILE": "private", "WRITES_ENABLED": "false"},
        {"APP_ENV": "hosted", "DATA_PROFILE": "fabricated", "WRITES_ENABLED": "true"},
    ],
)
def test_hosted_startup_refuses_private_data_and_writes(overrides: dict[str, str]) -> None:
    with pytest.raises(ConfigurationError):
        Settings.from_env(overrides)


def test_hosted_fabricated_read_only_configuration_is_valid() -> None:
    settings = Settings.from_env(
        {"APP_ENV": "hosted", "DATA_PROFILE": "fabricated", "WRITES_ENABLED": "false"}
    )
    assert settings.app_env == "hosted"
    assert settings.data_profile == "fabricated"
    assert settings.writes_enabled is False


def test_invalid_limit_configuration_is_rejected() -> None:
    with pytest.raises(ConfigurationError, match="DAILY_REQUEST_CAP"):
        Settings.from_env({"DAILY_REQUEST_CAP": "0"})
