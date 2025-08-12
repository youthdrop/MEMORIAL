import os, sys

# --- Resilient imports: works as package or bare script ---
if __package__ in (None, ""):
    sys.path.append(os.path.dirname(__file__))
    from extensions import db, migrate
    from routes.participants import bp as participants_bp
    # optional blueprints
    try: from routes.more import bp_more
    except Exception: bp_more = None
    try: from routes.geo import bp_geo
    except Exception: bp_geo = None
    try: from routes.auth import bp_auth
    except Exception: bp_auth = None
    try: from routes.reports import bp_reports
    except Exception: bp_reports = None
    # SPA helper
    try: from spa_static import register_spa
    except Exception:
        def register_spa(app):  # no-op if helper missing
            pass
else:
    from .extensions import db, migrate
    from .routes.participants import bp as participants_bp
    try: from .routes.more import bp_more
    except Exception: bp_more = None
    try: from .routes.geo import bp_geo
    except Exception: bp_geo = None
    try: from .routes.auth import bp_auth
    except Exception: bp_auth = None
    try: from .routes.reports import bp_reports
    except Exception: bp_reports = None
    try: from .spa_static import register_spa
    except Exception:
        def register_spa(app):
            pass

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# Ensure models are loaded so SQLAlchemy knows them
try:
    from . import models  # noqa: F401
except Exception:
    import models  # noqa: F401

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Config (Railway sets DATABASE_URL)
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

    # --- Register API blueprints under /api ---
    app.register_blueprint(participants_bp, url_prefix="/api")
    if bp_more:
        app.register_blueprint(bp_more, url_prefix="/api")
    if bp_geo:
        app.register_blueprint(bp_geo, url_prefix="/api")
    if bp_auth:
        app.register_blueprint(bp_auth, url_prefix="/api")
    if bp_reports:
        app.register_blueprint(bp_reports, url_prefix="/api")

    # Create tables on first run (safe if already present)
    with app.app_context():
        try:
            db.create_all()
        except Exception:
            pass

    # Serve React SPA at /
    register_spa(app)

    return app

# WSGI entrypoint
app = create_app()
