import pytest
from pydantic import ValidationError

from shopai.config import Settings

KEY = "sk-ant-test-key"


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    # Tests must not depend on the shell they run in. Each test also passes
    # _env_file explicitly, so the developer's own .env is never read.
    for name in ("ANTHROPIC_API_KEY", "DEEPSEEK_API_KEY", "LOG_LEVEL", "ENVIRONMENT"):
        monkeypatch.delenv(name, raising=False)


def test_missing_api_key_fails_at_startup():
    with pytest.raises(ValidationError, match="anthropic_api_key"):
        Settings(_env_file=None)


def test_defaults_apply_when_only_the_key_is_set(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", KEY)
    settings = Settings(_env_file=None)
    assert settings.log_level == "INFO"
    assert settings.environment == "local"
    assert settings.deepseek_api_key is None


def test_api_key_is_masked_when_printed(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", KEY)
    settings = Settings(_env_file=None)
    assert KEY not in str(settings)
    assert KEY not in repr(settings)
    assert settings.anthropic_api_key.get_secret_value() == KEY


def test_environment_variable_beats_env_file(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(f"ANTHROPIC_API_KEY={KEY}\nLOG_LEVEL=INFO\n")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    assert Settings(_env_file=env_file).log_level == "DEBUG"


def test_invalid_log_level_is_rejected(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", KEY)
    monkeypatch.setenv("LOG_LEVEL", "INFOO")
    with pytest.raises(ValidationError, match="log_level"):
        Settings(_env_file=None)
