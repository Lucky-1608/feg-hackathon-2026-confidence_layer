# FastAPI App & Database Session

> 45 nodes · cohesion 0.06

## Key Concepts

- **load_config()** (13 connections) — `src/confidence/config.py`
- **config.py** (11 connections) — `src/confidence/config.py`
- **app.py** (8 connections) — `src/confidence/api/app.py`
- **connection.py** (7 connections) — `src/confidence/db/connection.py`
- **create_app()** (6 connections) — `src/confidence/api/app.py`
- **DatabaseConfig** (6 connections) — `src/confidence/config.py`
- **create_async_session_factory()** (5 connections) — `src/confidence/db/connection.py`
- **create_sync_session_factory()** (5 connections) — `src/confidence/db/connection.py`
- **get_logger()** (5 connections) — `src/confidence/log.py`
- **FastAPI** (4 connections)
- **create_async_db_engine()** (4 connections) — `src/confidence/db/connection.py`
- **create_sync_db_engine()** (4 connections) — `src/confidence/db/connection.py`
- **log.py** (4 connections) — `src/confidence/log.py`
- **configure_logging()** (4 connections) — `src/confidence/log.py`
- **AppConfig** (3 connections) — `src/confidence/config.py`
- **DecisionConfig** (3 connections) — `src/confidence/config.py`
- **_load_env()** (3 connections) — `src/confidence/config.py`
- **SafetyConfig** (3 connections) — `src/confidence/config.py`
- **ServerConfig** (3 connections) — `src/confidence/config.py`
- **.__init__()** (3 connections) — `src/confidence/infrastructure/persistence.py`
- **async_sessionmaker** (2 connections)
- **Engine** (2 connections)
- **AsyncEngine** (2 connections)
- **Any** (1 connections)
- **AsyncSession** (1 connections)
- *... and 20 more nodes in this community*

## Relationships

- [API Dependencies & Context Providers](API_Dependencies_&_Context_Providers.md) (6 shared connections)
- [Decision Engine & API Models](Decision_Engine_&_API_Models.md) (1 shared connections)
- [Domain Model & Safety Tests](Domain_Model_&_Safety_Tests.md) (1 shared connections)

## Source Files

- `src/confidence/api/app.py`
- `src/confidence/config.py`
- `src/confidence/db/connection.py`
- `src/confidence/infrastructure/persistence.py`
- `src/confidence/log.py`

## Audit Trail

- EXTRACTED: 67 (96%)
- INFERRED: 3 (4%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*