from flask import Flask
from .database import db
from .routes import recommendations_bp


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "postgresql+psycopg://cinema:P%40ssw0rd@db:5432/cinema"

    app.config["SQLALCHEMY_ECHO"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(recommendations_bp, url_prefix="/api/v1")

    return app
