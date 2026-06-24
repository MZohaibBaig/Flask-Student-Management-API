# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the dev server (http://127.0.0.1:5000)
python app.py

# Seed sample students
flask --app app seed-db

# Run all tests
pytest -q

# Run a single test
pytest tests/test_api.py::test_full_crud_cycle -v
```

Set `FLASK_DEBUG=1` to enable debug mode (off by default).

## Architecture

The app uses Flask's **application factory** pattern. `create_app()` in `app.py` initializes extensions, registers blueprints, creates DB tables, and wires error handlers and CLI commands. A module-level `app = create_app()` at the bottom allows both `python app.py` and `flask --app app` to work.

**Extension singletons** (`db`, `jwt`, `bcrypt`) live in `extensions.py` to avoid circular imports — modules import from there, not from `app.py`.

**Two blueprints:**
- `auth_bp` (`auth.py`) — `/api/auth/register` and `/api/auth/login`
- `students_bp` (`students.py`) — `/api/students` CRUD

**Authorization model:** GET endpoints are public; POST/PUT/PATCH/DELETE require `@jwt_required()`. The JWT identity is the user's string ID (`str(user.id)`).

**Validation / serialization split:** Marshmallow schemas in `schemas.py` validate and coerce *incoming* JSON only. Responses are serialized by `Model.to_dict()` methods — marshmallow is never used for output.

- `StudentCreateSchema` — used for both POST and PUT (all required fields)
- `StudentUpdateSchema` — used for PATCH (all fields optional)

**Configuration** (`config.py`) is environment-driven via `DATABASE_URL`, `JWT_SECRET_KEY`, and `JWT_ACCESS_TOKEN_HOURS`. `TestConfig` overrides to an in-memory SQLite DB and a fixed JWT secret.

## Testing

Tests use Flask's test client with a `client` fixture that creates a fresh in-memory DB per test and drops it on teardown. The helper `_auth_header(client)` registers + logs in an admin user and returns the `Authorization` header dict — use it for any test that hits a write endpoint.

## Key env vars

| Variable | Default | Notes |
|---|---|---|
| `DATABASE_URL` | `sqlite:///students.db` | Switch to `postgresql://...` for Postgres |
| `JWT_SECRET_KEY` | `dev-secret-change-me` | Must be set in production |
| `JWT_ACCESS_TOKEN_HOURS` | `1` | Token lifetime |
| `FLASK_DEBUG` | `0` | Set to `1` for local debugging |
