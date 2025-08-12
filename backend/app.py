# Resilient bootstrap: runs as package (backend.app) or bare script (app)
import os, sys
if __package__ in (None, ""):
    sys.path.append(os.path.dirname(__file__))
    from extensions import db, migrate  # noqa: E402
    from routes.participants import bp as participants_bp  # noqa: E402
    try:
        from routes.nested import bp_nested  # noqa: E402
    except Exception:
        bp_nested = None
    try:
        from routes.auth import bp_auth  # noqa: E402
    except Exception:
        bp_auth = None
    try:
        from spa_static import register_spa  # noqa: E402
    except Exception:
        def register_spa(app):  # no-op
            pass
else:
    from .extensions import db, migrate  # noqa: E402
    from .routes.participants import bp as participants_bp  # noqa: E402
    try:
        from .routes.nested import bp_nested  # noqa: E402
    except Exception:
        bp_nested = None
    try:
        from .routes.auth import bp_auth  # noqa: E402
    except Exception:
        bp_auth = None
    try:
        from .spa_static import register_spa  # noqa: E402
    except Exception:
        def register_spa(app):
            pass

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# Ensure models are registered (either context)
try:
    from . import models  # noqa: F401
except Exception:
    import models  # noqa: F401

def create_app():
    app = Flask(__name__)
    # CORS across the app (adjust if you need credentials/cookies)
    CORS(app)

    # Config
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///local.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "please-change-me")

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    JWTManager(app)

    # Healthcheck
    @app.get("/healthz")
    def healthz():
        return {"ok": True}

    # API blueprints
    app.register_blueprint(participants_bp, url_prefix="/api")
    if bp_nested:
        app.register_blueprint(bp_nested, url_prefix="/api/v1")
    if bp_auth:
        app.register_blueprint(bp_auth, url_prefix="/api")

    # Serve the React SPA at /
    register_spa(app)

    return app

# Export app for gunicorn / flask run
app = create_app()
