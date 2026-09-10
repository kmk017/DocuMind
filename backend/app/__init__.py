from dotenv import load_dotenv

load_dotenv()

from flask import Flask, jsonify
from flask_cors import CORS

from .config import Config
from .extensions import db
from .routes.health import health_bp
from .routes.documents import documents_bp
from .routes.auth import auth_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    if not app.config["SQLALCHEMY_DATABASE_URI"]:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set. "
            "Copy .env.example to .env and configure it."
        )

    CORS(app)
    db.init_app(app)

    from app.models import User, Document, DocumentChunk  # noqa: F401

    app.register_blueprint(health_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(auth_bp)

    @app.errorhandler(413)
    def handle_file_too_large(e):
        return jsonify({
            "error": (
                "File exceeds the maximum allowed size (20 MB)."
            )
        }), 413

    return app