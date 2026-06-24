"""Shared extension instances.

Kept in their own module so models, blueprints, and the app factory can all
import them without circular-import problems.
"""
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
