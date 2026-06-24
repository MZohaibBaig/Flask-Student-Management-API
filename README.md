# Student Management API

A RESTful API for managing student records, built with **Flask**. It supports full
**CRUD** operations on students, with **JWT-based authentication** protecting all
write operations. Reads are public; creating, updating, and deleting students
requires a valid token.

Built with an application-factory + blueprint structure, SQLAlchemy ORM, and
marshmallow request validation. Runs on **SQLite out of the box** (zero setup) and
switches to **PostgreSQL or MySQL** with a single environment variable.

---

## Features

- Full CRUD for student records (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`)
- JWT authentication (register / login) with bcrypt-hashed passwords
- Selective authorization — public reads, token-protected writes
- Request validation and clear error responses via marshmallow
- Pagination and search on the student list endpoint
- Database-agnostic via SQLAlchemy (SQLite default, Postgres/MySQL ready)
- Environment-based configuration (12-factor style)
- Test suite with pytest

## Tech Stack

| Concern        | Choice                          |
| -------------- | ------------------------------- |
| Framework      | Flask 3                         |
| ORM            | Flask-SQLAlchemy                |
| Auth           | Flask-JWT-Extended + Flask-Bcrypt |
| Validation     | marshmallow                     |
| Database       | SQLite (default) / PostgreSQL / MySQL |
| Testing        | pytest                          |

---

## Quick Start

```bash
# 1. Clone and enter the project
git clone https://github.com/MZohaibBaig/Flask-Student-Management-API.git
cd Flask-Student-Management-API

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) configure environment
cp .env.example .env             # defaults work as-is for local SQLite

# 5. Run
python app.py                    # http://127.0.0.1:5000
```

Seed a few sample students for a quick demo:

```bash
flask --app app seed-db
```

---

## Configuration

The app runs with no configuration at all (SQLite + a dev secret). For production,
set these environment variables (see `.env.example`):

| Variable                 | Default              | Notes                                   |
| ------------------------ | -------------------- | --------------------------------------- |
| `DATABASE_URL`           | `sqlite:///students.db` | e.g. `postgresql://user:pass@host:5432/students` |
| `JWT_SECRET_KEY`         | `dev-secret-change-me`  | **Required in production.** Use a long random string. |
| `JWT_ACCESS_TOKEN_HOURS` | `1`                  | Token lifetime in hours                 |
| `FLASK_DEBUG`            | `0`                  | Set to `1` for local debugging only     |

Generate a secret:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

To use PostgreSQL, install the driver and set the URL:

```bash
pip install psycopg2-binary
export DATABASE_URL=postgresql://user:pass@localhost:5432/students
```

---

## API Reference

Base URL: `http://127.0.0.1:5000`

### Auth

| Method | Endpoint             | Auth | Body                              |
| ------ | -------------------- | ---- | --------------------------------- |
| POST   | `/api/auth/register` | No   | `full_name`, `email`, `password`  |
| POST   | `/api/auth/login`    | No   | `email`, `password` → `access_token` |

### Students

| Method | Endpoint              | Auth  | Description                          |
| ------ | --------------------- | ----- | ------------------------------------ |
| GET    | `/api/students`       | No    | List (supports `?search=`, `?page=`, `?per_page=`) |
| GET    | `/api/students/<id>`  | No    | Retrieve one student                 |
| POST   | `/api/students`       | Yes   | Create a student                     |
| PUT    | `/api/students/<id>`  | Yes   | Replace a student (all fields)       |
| PATCH  | `/api/students/<id>`  | Yes   | Update some fields                   |
| DELETE | `/api/students/<id>`  | Yes   | Delete a student                     |

Protected endpoints expect an `Authorization: Bearer <token>` header.

### Example

```bash
# Register and log in
curl -X POST localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Admin","email":"admin@example.com","password":"password123"}'

TOKEN=$(curl -s -X POST localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password123"}' \
  | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# Create a student (authenticated)
curl -X POST localhost:5000/api/students \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"first_name":"Ali","last_name":"Raza","email":"ali@example.com","age":21,"course":"Computer Science"}'

# List students (public)
curl localhost:5000/api/students
```

---

## Database Migrations

Schema changes are managed with **Alembic** via Flask-Migrate.

```bash
# Apply all pending migrations (run this after cloning or pulling new migrations)
flask --app app db upgrade

# Generate a new migration after editing models.py
flask --app app db migrate -m "describe your change"
flask --app app db upgrade
```

The `migrations/` folder is committed to the repository. Never edit migration files by hand after they have been applied to a shared database.

---

## Running Tests

```bash
pytest -q
```

The suite covers registration, login, the full CRUD cycle, authorization
enforcement (writes rejected without a token), duplicate-email conflicts, and
input validation.

---

## Project Structure

```
.
├── app.py            # application factory, error handlers, CLI seed command
├── config.py         # environment-based configuration
├── extensions.py     # shared db / jwt / bcrypt instances
├── models.py         # User and Student models
├── schemas.py        # marshmallow validation schemas
├── auth.py           # auth blueprint (register, login)
├── students.py       # students blueprint (CRUD)
├── requirements.txt
├── .env.example
└── tests/
    └── test_api.py
```

---

## Security Notes

- Passwords are hashed with bcrypt; plaintext is never stored.
- Login returns an identical message for unknown emails and wrong passwords to
  avoid user enumeration.
- All database access goes through the ORM with bound parameters (no string-built SQL).
- Debug mode is off by default and gated behind `FLASK_DEBUG`.
- The JWT secret must be set via environment variable in production.

## License

MIT
