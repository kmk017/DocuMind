import os
from datetime import datetime, timedelta, timezone

import jwt
from flask import Blueprint, jsonify, request

from ..auth.decorators import token_required
from ..extensions import db
from ..models import User


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _error(message, status_code):
    return jsonify({"error": message}), status_code


def _create_token(user):
    secret_key = os.getenv("JWT_SECRET_KEY")

    if not secret_key:
        raise RuntimeError("JWT_SECRET_KEY is not configured.")

    now = datetime.now(timezone.utc)

    payload = {
        "user_id": user.id,
        "email": user.email,
        "iat": now,
        "exp": now + timedelta(days=7),
    }

    return jwt.encode(
        payload,
        secret_key,
        algorithm="HS256",
    )


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)

    if not data:
        return _error("Request body is required.", 400)

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email:
        return _error("Email is required.", 400)

    if not password:
        return _error("Password is required.", 400)

    if len(password) < 8:
        return _error(
            "Password must be at least 8 characters long.",
            400,
        )

    try:
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return _error(
                "An account with this email already exists.",
                409,
            )

        user = User(email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        token = _create_token(user)

        return jsonify({
            "message": "Account created successfully.",
            "token": token,
            "user": user.to_dict(),
        }), 201

    except Exception:
        db.session.rollback()
        raise


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if not data:
        return _error("Request body is required.", 400)

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return _error(
            "Email and password are required.",
            400,
        )

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return _error(
            "Invalid email or password.",
            401,
        )

    token = _create_token(user)

    return jsonify({
        "message": "Login successful.",
        "token": token,
        "user": user.to_dict(),
    }), 200


@auth_bp.route("/me", methods=["GET"])
@token_required
def me():
    user = db.session.get(User, request.user_id)

    if not user:
        return _error("User not found.", 404)

    return jsonify({
        "user": user.to_dict()
    }), 200