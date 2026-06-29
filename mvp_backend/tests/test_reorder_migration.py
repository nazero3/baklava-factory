"""Verify the Alembic migration chain creates the products.reorder_level column."""
from pathlib import Path

import sqlalchemy as sa
from alembic import command
from alembic.config import Config

from app.config import settings


def test_alembic_upgrade_adds_reorder_level(tmp_path, monkeypatch):
    db_path = tmp_path / "migration_check.db"
    url = f"sqlite:///{db_path}"

    # alembic/env.py reads the URL from settings.database_url, so point it at a fresh DB.
    monkeypatch.setattr(settings, "database_url", url)

    backend_root = Path(__file__).resolve().parent.parent
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "alembic"))
    config.set_main_option("sqlalchemy.url", url)

    command.upgrade(config, "head")

    engine = sa.create_engine(url)
    try:
        inspector = sa.inspect(engine)
        columns = {col["name"] for col in inspector.get_columns("products")}
        assert "reorder_level" in columns
    finally:
        engine.dispose()
