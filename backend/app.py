try:
    from .spa_static import register_spa
except ImportError:
    from spa_static import register_spa

# --- resilient imports so app works as package OR bare script ---
try:
    from .extensions import db, migrate
except ImportError:
    from extensions import db, migrate  # fallback if run without package

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# If you import blueprints, do it resiliently too:
try:
    from .routes.participants import bp as participants_bp
except ImportError:
    from routes.participants import bp as participants_bp

# nested routes are optional; import if present
try:
    from .routes.nested import bp_nested
except ImportError:
    try:
        from routes.nested import bp_nested
    except Exception:
        bp_nested = None

import os

def create_app():
    app = Flask(__name__)
    CORS(app)

    # config (Railway will set DATABASE_URL and your JWT secret)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///local.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "please-change-me")

    db.init_app(app)
    migrate.init_app(app, db)
    JWTManager(app)

    # ensure models are registered
    try:
        from . import models  # noqa: F401
    except ImportError:
        import models  # noqa: F401

    # register blueprints
    app.register_blueprint(participants_bp, url_prefix="/api")
    if bp_nested:
        app.register_blueprint(bp_nested)

    @app.get("/healthz")
    def healthz():
        return {"ok": True}

    @app.get("/")
    def index():
        return {"ok": True, "service": "backend", "docs": ["/healthz", "/api/..."]}

    register_spa(app)

    return app

# export app when run as "python backend/app.py"
app = create_app()
