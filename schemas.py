"""Marshmallow schemas for request validation.

These validate and coerce incoming JSON. Serialization back to the client is
handled by each model's to_dict() to keep responses explicit.
"""
from marshmallow import Schema, fields, validate


class RegisterSchema(Schema):
    full_name = fields.String(required=True, validate=validate.Length(min=1, max=255))
    email = fields.Email(required=True, validate=validate.Length(max=255))
    password = fields.String(required=True, validate=validate.Length(min=8, max=128))


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


class StudentCreateSchema(Schema):
    first_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True, validate=validate.Length(max=255))
    age = fields.Integer(required=False, validate=validate.Range(min=1, max=150))
    course = fields.String(required=False, validate=validate.Length(max=150))


class StudentUpdateSchema(Schema):
    """All fields optional for PATCH; PUT enforces presence in the view."""

    first_name = fields.String(validate=validate.Length(min=1, max=100))
    last_name = fields.String(validate=validate.Length(min=1, max=100))
    email = fields.Email(validate=validate.Length(max=255))
    age = fields.Integer(validate=validate.Range(min=1, max=150))
    course = fields.String(validate=validate.Length(max=150))
