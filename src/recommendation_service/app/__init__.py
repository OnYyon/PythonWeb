from flask import Flask
from .database import db
from .routes import recommendations_bp


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "postgresql+psycopg://cinema:P@ssw0rd@localhost:5432/cinema"
    )

    db.init_app(app)

    app.register_blueprint(recommendations_bp, url_prefix="/api/v1")

    return app