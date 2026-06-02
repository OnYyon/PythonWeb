import os
from urllib.parse import quote

from flask import Flask

from .database import db
from .routes import recommendations_bp


def _database_dsn() -> str:
    configured_dsn = os.environ.get("RECOMMENDATION_DATABASE_DSN")
    if configured_dsn:
        return configured_dsn

    user = quote(os.environ.get("DB_USER", "cinema"), safe="")
    password = quote(os.environ.get("DB_PASSWORD", "P@ssw0rd"), safe="")
    host = os.environ.get("DB_HOST", "db")
    port = os.environ.get("DB_PORT", "5432")
    name = os.environ.get("DB_NAME", "cinema")
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}"


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = _database_dsn()

    app.config["SQLALCHEMY_ECHO"] = False

    db.init_app(app)

    app.register_blueprint(recommendations_bp, url_prefix="/api/v1")

    return app
