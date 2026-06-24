"""Application configuration.

Configuration is environment-driven (12-factor style). Sensible defaults let
the app run with zero setup on SQLite, while a single DATABASE_URL switches it
to PostgreSQL/MySQL in production.
"""
import os
from datetime import timedelta
from pathlib import Path

# Absolute path to the project root (directory containing this file).
_PROJECT_ROOT = Path(__file__).parent.resolve()
_DEFAULT_DB = "sqlite:///" + (_PROJECT_ROOT / "students.db").as_posix()


class Config:
    # --- Database -----------------------------------------------------------
    # Default: local SQLite file anchored to the project root (zero setup).
    # Production: set DATABASE_URL, e.g.
    #   postgresql://user:pass@host:5432/students
    #   mysql+pymysql://user:pass@host:3306/students
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", _DEFAULT_DB)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Auth / JWT ---------------------------------------------------------
    # MUST be overridden in production via the JWT_SECRET_KEY env var.
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        hours=int(os.environ.get("JWT_ACCESS_TOKEN_HOURS", "1"))
    )


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "test-secret"
