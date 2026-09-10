import os
from functools import wraps

import jwt
from flask import jsonify, request


def token_required(view_function):
    @wraps(view_function)
    def decorated(*args, **kwargs):
        authorization = request.headers.get("Authorization")

        if not authorization:
            return jsonify({
                "error": "Authentication token is required."
            }), 401

        parts = authorization.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({
                "error": "Invalid authentication header."
            }), 401

        token = parts[1]

        secret_key = os.getenv("JWT_SECRET_KEY")

        if not secret_key:
            raise RuntimeError("JWT_SECRET_KEY is not configured.")

        try:
            payload = jwt.decode(
                token,
                secret_key,
                algorithms=["HS256"],
            )
        except jwt.ExpiredSignatureError:
            return jsonify({
                "error": "Authentication token has expired."
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                "error": "Invalid authentication token."
            }), 401

        request.user_id = payload.get("user_id")

        if not request.user_id:
            return jsonify({
                "error": "Invalid authentication token."
            }), 401

        return view_function(*args, **kwargs)

    return decorated