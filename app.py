
"""Application factory and entry point.

Run locally:
    python app.py            # serves on http://127.0.0.1:5000

Seed sample data:
    flask --app app seed-db
"""
import click
from flask import Flask, jsonify
from flask_migrate import Migrate

from auth import auth_bp
from config import Config
from extensions import bcrypt, db, jwt
from students import students_bp


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Init extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    Migrate(app, db, render_as_batch=True)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(students_bp)

    _register_error_handlers(app)
    _register_cli(app)

    @app.get("/")
    def index():
        return jsonify(
            {
                "service": "Student Management API",
                "endpoints": {
                    "register": "POST /api/auth/register",
                    "login": "POST /api/auth/login",
                    "list_students": "GET /api/students",
                    "get_student": "GET /api/students/<id>",
                    "create_student": "POST /api/students (auth)",
                    "replace_student": "PUT /api/students/<id> (auth)",
                    "update_student": "PATCH /api/students/<id> (auth)",
                    "delete_student": "DELETE /api/students/<id> (auth)",
                },
            }
        )

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    return app


def _register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(_):
        return jsonify({"error": "Bad request"}), 400

    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(_):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def server_error(_):
        return jsonify({"error": "Internal server error"}), 500


def _register_cli(app):
    @app.cli.command("seed-db")
    def seed_db():
        """Insert a few sample students for demos."""
        from models import Student

        if Student.query.first():
            click.echo("Students already exist; skipping seed.")
            return
        samples = [
            Student(first_name="Ayesha", last_name="Khan",
                    email="ayesha.khan@example.com", age=20, course="Computer Science"),
            Student(first_name="Bilal", last_name="Ahmed",
                    email="bilal.ahmed@example.com", age=22, course="Electrical Engineering"),
            Student(first_name="Sara", last_name="Malik",
                    email="sara.malik@example.com", age=19, course="Software Engineering"),
        ]
        db.session.add_all(samples)
        db.session.commit()
        click.echo(f"Seeded {len(samples)} students.")


# Expose a module-level app so `flask --app app` and `python app.py` both work.
app = create_app()


if __name__ == "__main__":
    # debug is controlled by the FLASK_DEBUG env var; defaults to off.
    import os

    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1")
