# Baklava Factory MVP Backend

This is the first working MVP backend implementation aligned with the project documents.

## Included Business Flows
- Raw material receiving
- Recipe-based production completion
- Factory-to-store transfer dispatch/receive
- Store movement (sale, return, waste)
- Inventory view and daily KPI summary
- Authentication and role-based authorization
- Approval workflow for large stock adjustments and transfer discrepancies
- CSV import/export for products and store movements

## Tech Stack
- FastAPI
- SQLite
- SQLAlchemy
- Pytest

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `dev-insecure-change-me` | HMAC secret for signing JWT access tokens. **Required in production.** |
| `DATABASE_URL` | `sqlite:///./mvp.db` | SQLAlchemy database URL (SQLite for dev; Postgres for production) |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token lifetime in minutes |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Opaque refresh token lifetime in days |
| `BOOTSTRAP_ADMIN` | *(unset)* | One-time admin bootstrap as `username:password`. Only creates the user if it does not exist. **Unset in production after first deploy.** |
| `ENV` | `development` | Set to `production` to disable `/docs`, `/redoc`, and `/openapi.json` |
| `LOGIN_RATE_LIMIT` | `10/minute` | slowapi rate limit for `POST /auth/login` (per client IP) |
| `CORS_ALLOW_ORIGINS` | *(unset)* | Comma-separated allowed browser origins; unset disables CORS middleware (same-origin only) |

Copy `.env.example` to `.env` for local development:

```bash
SECRET_KEY=local-dev-secret
BOOTSTRAP_ADMIN=admin:admin123
ENV=development
```

## Run Locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export BOOTSTRAP_ADMIN=admin:admin123  # dev only
uvicorn app.main:app --reload
```

API docs (development only):
- `http://127.0.0.1:8000/docs`

## Authentication

- Passwords are hashed with **bcrypt**. Legacy SHA-256 hashes are transparently upgraded on successful login.
- `POST /auth/login` returns a short-lived **JWT access token** plus an opaque **refresh token**.
- `POST /auth/refresh` exchanges a valid refresh token for a new access token.
- `POST /auth/logout` invalidates the current session (bumps `token_version`, clears refresh token).
- Send `Authorization: Bearer <access_token>` on protected routes.

**Production:** Do not set `BOOTSTRAP_ADMIN` after initial admin creation. Rotate `SECRET_KEY` via your secrets manager.

## Run Tests
```bash
pytest -q
```

## CI (local equivalent)

GitHub Actions runs the same checks on push/PR to `main` (see `.github/workflows/ci.yml` at repo root):

```bash
pip install -r requirements.txt
pytest -q
ruff check .
bandit -r app
```

## Docker Compose (Postgres)

From the repository root:

```bash
cp .env.compose.example .env   # optional: set SECRET_KEY
docker compose up --build
```

- **Postgres** on `localhost:5432` (user/db/password: `manbaj`)
- **API** on `http://localhost:8000` — `ENV=production`, Alembic migrations on startup
- Data persisted in Docker volume `postgres_data`

## Docker

Build and run the API container (from `mvp_backend/`):

```bash
docker build -t manbaj-mvp-api .
docker run --rm -p 8000:8000 \
  -e SECRET_KEY=local-dev-secret \
  -e ENV=production \
  manbaj-mvp-api
```

`/health` returns `503` when the database is unreachable (readiness probe).

Production (`ENV=production`) emits JSON request logs with `request_id`, route, status, and latency. Every response includes `X-Request-ID`.

## Database Migrations

Schema is managed with Alembic. In **production** (`ENV=production`), app startup runs `alembic upgrade head`. In development, `create_all` is used for convenience.

```bash
export DATABASE_URL=sqlite:///./mvp.db   # or postgres://...
alembic upgrade head                      # apply migrations manually in dev
alembic revision --autogenerate -m "msg"  # new migration after model changes
```

## Notes
- Database file: `mvp.db` in project root (SQLite dev default)
- Postgres path: `docker compose up` from repo root (see above)
