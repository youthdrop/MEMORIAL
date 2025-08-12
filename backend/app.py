try:
    from .routes.more import bp_more
except Exception:
    from routes.more import bp_more
import os, sys
if __package__ in (None, ""):
    sys.path.append(os.path.dirname(__file__))
    from extensions import db, migrate
    from routes.participants import bp as participants_bp
    try:
        from routes.geo import bp_geo
    except Exception:
        bp_geo = None
    try:
        from routes.auth import bp_auth
    except Exception:
        bp_auth = None
    try:
        from spa_static import register_spa
    except Exception:
        def app.register_blueprint(bp_more, url_prefix="/api")
    register_spa(app): pass
else:
    from .extensions import db, migrate
    from .routes.participants import bp as participants_bp
    try:
        from .routes.geo import bp_geo
    except Exception:
        bp_geo = None
    try:
        from .routes.auth import bp_auth
    except Exception:
        bp_auth = None
    try:
        from .spa_static import register_spa
    except Exception:
        def app.register_blueprint(bp_more, url_prefix="/api")
    register_spa(app): pass

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

try:
    from . import models  # ensure models loaded
except Exception:
    import models

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///local.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "please-change-me")
    db.init_app(app)
    migrate.init_app(app, db)
    JWTManager(app)

    @app.get("/healthz")
    def healthz():
        return {"ok": True}

    app.register_blueprint(participants_bp, url_prefix="/api")
    if bp_geo:
        app.register_blueprint(bp_geo, url_prefix="/api")
    if bp_auth:
        app.register_blueprint(bp_auth, url_prefix="/api")

    with app.app_context():
        try:
            db.create_all()
        except Exception:
            pass

    app.register_blueprint(bp_more, url_prefix="/api")
    register_spa(app)
    return app

app = create_app()
