"""Student CRUD endpoints.

Reads (GET) are public; writes (POST/PUT/PATCH/DELETE) require a valid JWT.
This demonstrates selective, per-route authorization rather than all-or-nothing.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from extensions import db
from models import Student
from schemas import StudentCreateSchema, StudentUpdateSchema

students_bp = Blueprint("students", __name__, url_prefix="/api/students")


def _get_or_404(student_id):
    student = db.session.get(Student, student_id)
    if student is None:
        return None, (jsonify({"error": "Student not found"}), 404)
    return student, None


@students_bp.get("")
def list_students():
    """List students with optional ?search= and pagination (?page=&per_page=)."""
    search = request.args.get("search", "", type=str).strip()
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)

    query = Student.query
    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(
                Student.first_name.ilike(like),
                Student.last_name.ilike(like),
                Student.email.ilike(like),
                Student.course.ilike(like),
            )
        )

    pagination = query.order_by(Student.id).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify(
        {
            "students": [s.to_dict() for s in pagination.items],
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        }
    ), 200


@students_bp.get("/<int:student_id>")
def get_student(student_id):
    student, err = _get_or_404(student_id)
    if err:
        return err
    return jsonify(student.to_dict()), 200


@students_bp.post("")
@jwt_required()
def create_student():
    try:
        data = StudentCreateSchema().load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    if Student.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "A student with this email already exists"}), 409

    student = Student(**data)
    db.session.add(student)
    db.session.commit()
    return jsonify(student.to_dict()), 201


@students_bp.put("/<int:student_id>")
@jwt_required()
def replace_student(student_id):
    """Full update: all required fields must be present."""
    student, err = _get_or_404(student_id)
    if err:
        return err
    try:
        data = StudentCreateSchema().load(request.get_json(silent=True) or {})
    except ValidationError as e:
        return jsonify({"errors": e.messages}), 422

    conflict = _check_email_conflict(data.get("email"), student_id)
    if conflict:
        return conflict
    for key, value in data.items():
        setattr(student, key, value)
    db.session.commit()
    return jsonify(student.to_dict()), 200


@students_bp.patch("/<int:student_id>")
@jwt_required()
def update_student(student_id):
    """Partial update: only supplied fields are changed."""
    student, err = _get_or_404(student_id)
    if err:
        return err
    try:
        data = StudentUpdateSchema().load(request.get_json(silent=True) or {})
    except ValidationError as e:
        return jsonify({"errors": e.messages}), 422

    if not data:
        return jsonify({"error": "No fields provided to update"}), 400

    conflict = _check_email_conflict(data.get("email"), student_id)
    if conflict:
        return conflict
    for key, value in data.items():
        setattr(student, key, value)
    db.session.commit()
    return jsonify(student.to_dict()), 200


@students_bp.delete("/<int:student_id>")
@jwt_required()
def delete_student(student_id):
    student, err = _get_or_404(student_id)
    if err:
        return err
    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": "Student deleted"}), 200


def _check_email_conflict(email, student_id):
    """Return a 409 response if `email` belongs to a different student."""
    if not email:
        return None
    existing = Student.query.filter_by(email=email).first()
    if existing and existing.id != student_id:
        return jsonify({"error": "A student with this email already exists"}), 409
    return None
