"""Exercise the entire migration chain against a clean database and offline PostgreSQL."""

from io import StringIO

from alembic.config import Config
from sqlalchemy import create_engine, inspect

from alembic import command


def test_upgrade_downgrade_and_postgres_sql(tmp_path, monkeypatch):
    monkeypatch.setattr("dotenv.load_dotenv", lambda: None)
    database = "sqlite:///" + str(tmp_path / "migrations.db")
    monkeypatch.setenv("DATABASE_URL_SYNC", database)
    config = Config("alembic.ini")
    command.upgrade(config, "head")
    engine = create_engine(database)
    assert {"outbox", "experiment_assignments", "session_quality_scores"} <= set(inspect(engine).get_table_names())
    assert "shadow_mode" in {c["name"] for c in inspect(engine).get_columns("decisions")}
    engine.dispose()
    command.downgrade(config, "base")
    stream = StringIO()
    config = Config("alembic.ini", output_buffer=stream)
    monkeypatch.setenv("DATABASE_URL_SYNC", "postgresql+psycopg://unused:unused@localhost/unused")
    command.upgrade(config, "head", sql=True)
    assert "CREATE TABLE outbox" in stream.getvalue()
