from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect as sa_inspect

from .config import settings
from .database import Base, engine


def _alembic_config() -> Config:
    alembic_ini = Path(__file__).resolve().parent.parent / "alembic.ini"
    cfg = Config(str(alembic_ini))
    cfg.set_main_option("sqlalchemy.url", settings.database_url)
    return cfg


def ensure_database_schema() -> None:
    """Bring the database schema to the current Alembic head.

    Strategy:
    - If the database has no ``alembic_version`` table it is either brand-new or
      was bootstrapped by a previous ``create_all`` call.  In both cases we
      create all tables from the ORM metadata and then stamp the DB at head so
      that future startups only run genuinely pending migrations.
    - If ``alembic_version`` already exists we simply run ``upgrade head``,
      which is a no-op when the schema is current.
    """
    cfg = _alembic_config()
    inspector = sa_inspect(engine)

    if not inspector.has_table("alembic_version"):
        Base.metadata.create_all(bind=engine)
        command.stamp(cfg, "head")
    else:
        command.upgrade(cfg, "head")
