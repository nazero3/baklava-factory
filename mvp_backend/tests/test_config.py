import pytest

from app.config import Settings


def test_settings_database_url_from_constructor():
    settings = Settings(database_url="sqlite:///./custom.db")
    assert settings.database_url == "sqlite:///./custom.db"


def test_settings_database_url_reads_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./from-env.db")
    settings = Settings()
    assert settings.database_url == "sqlite:///./from-env.db"


def test_settings_cors_origins_parses_comma_separated_list():
    settings = Settings(cors_allow_origins="http://localhost:5173, https://app.example.com")
    assert settings.cors_origins == ["http://localhost:5173", "https://app.example.com"]


def test_settings_cors_origins_empty_when_unset():
    settings = Settings(cors_allow_origins="")
    assert settings.cors_origins == []


def test_sqlite_connect_args_only_for_sqlite_urls():
    from app.database import _sqlite_connect_args

    assert _sqlite_connect_args("sqlite:///./mvp.db") == {"check_same_thread": False}
    assert _sqlite_connect_args("postgresql+psycopg2://user:pass@db:5432/manbaj") == {}
