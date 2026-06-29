"""Tests for ensure_database_schema migration strategy."""
import pytest
from unittest.mock import MagicMock, patch

from app import migrations


def test_ensure_schema_creates_and_stamps_on_fresh_db(monkeypatch: pytest.MonkeyPatch):
    """On a fresh DB (no alembic_version table), create_all and stamp head are called."""
    create_all_called = []
    stamp_called = []

    def fake_create_all(bind):  # noqa: ANN001
        create_all_called.append(True)

    # Simulate inspector reporting no alembic_version table
    mock_inspector = MagicMock()
    mock_inspector.has_table.return_value = False

    monkeypatch.setattr(migrations.Base.metadata, "create_all", fake_create_all)

    with patch("app.migrations.sa_inspect", return_value=mock_inspector), \
         patch("app.migrations.command.stamp") as mock_stamp, \
         patch("app.migrations.command.upgrade") as mock_upgrade:

        migrations.ensure_database_schema()

    assert create_all_called, "create_all should be called on a fresh database"
    mock_stamp.assert_called_once()
    mock_upgrade.assert_not_called()


def test_ensure_schema_upgrades_existing_db(monkeypatch: pytest.MonkeyPatch):
    """On an existing DB (alembic_version present), upgrade head is called."""
    create_all_called = []

    def fake_create_all(bind):  # noqa: ANN001
        create_all_called.append(True)

    # Simulate inspector reporting alembic_version table exists
    mock_inspector = MagicMock()
    mock_inspector.has_table.return_value = True

    monkeypatch.setattr(migrations.Base.metadata, "create_all", fake_create_all)

    with patch("app.migrations.sa_inspect", return_value=mock_inspector), \
         patch("app.migrations.command.stamp") as mock_stamp, \
         patch("app.migrations.command.upgrade") as mock_upgrade:

        migrations.ensure_database_schema()

    assert not create_all_called, "create_all should NOT be called on an existing database"
    mock_upgrade.assert_called_once()
    mock_stamp.assert_not_called()
