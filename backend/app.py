import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .extensions import db, migrate

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///local.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "please-change-me")

    db.init_app(app)
    migrate.init_app(app, db)
    JWTManager(app)

    from . import models  # noqa: F401

    from .routes.participants import bp as participants_bp
    app.register_blueprint(participants_bp, url_prefix="/api")

    try:
        from .routes.nested import bp_nested
        app.register_blueprint(bp_nested)
    except Exception:
        pass

    @app.get("/healthz")
    def healthz():
        return {"ok": True}

    return app

app = create_app()
