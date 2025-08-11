# backend/app.py
import os
import logging
from flask import Flask, jsonify, request, redirect, abort, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate

# Your project modules
from config import settings
from models import db, User
from auth import auth_bp, bcrypt, jwt
from routes.participants import bp as participants_bp
from routes.nested import bp_nested
from routes.reports import reports_bp

# .env is nice in dev; safe to skip if not present in prod
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Resolve the absolute path to ../frontend/dist (Vite build output)
HERE = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(HERE, "..", "frontend", "dist")


def create_app() -> Flask:
    # Serve static from the absolute dist path so it works anywhere
    app = Flask(__name__, static_folder=DIST_DIR, static_url_path="/")

    # --- Logging ---
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)

    # --- Config ---
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET_KEY or "dev-only"

    # --- Extensions ---
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    Migrate(app, db)

    # --- CORS ---
    origins = settings.CORS_ORIGINS or ["http://localhost:5173", "http://127.0.0.1:5173"]
    CORS(
        app,
        resources={
            r"/api/*": {"origins": origins},
            r"/api/v1/*": {"origins": origins},
        },
        supports_credentials=False,
    )

    # --- Blueprints mounted at /api ---
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(participants_bp, url_prefix="/api")
    app.register_blueprint(bp_nested, url_prefix="/api")
    app.register_blueprint(reports_bp, url_prefix="/api")

    # --- Health + env sanity ---
    @app.route("/api/health")
    def health():
        return jsonify(status="ok"), 200

    @app.route("/api/whoami")
    def whoami():
        return jsonify(
            env=os.getenv("FLASK_ENV", "production"),
            db_uri_configured=bool(app.config.get("SQLALCHEMY_DATABASE_URI")),
            jwt_key_set=bool(app.config.get("JWT_SECRET_KEY")),
        ), 200

    # --- Helpful error handlers (JSON for API only) ---
    @app.errorhandler(400)
    @app.errorhandler(401)
    @app.errorhandler(403)
    @app.errorhandler(405)
    @app.errorhandler(500)
    def handle_api_errors(err):
        # Only JSON-format API routes; let SPA/static behave normally
        if request.path.startswith("/api"):
            code = getattr(err, "code", 500)
            app.logger.exception(err)
            return jsonify(error=str(err), code=code), code
        return err  # non-API: default behavior (no noisy logs for 404s)

    # -------- Static & SPA (Vite) --------

    # Serve asset files from dist/assets
    @app.route("/assets/<path:filename>")
    def vite_assets(filename):
        assets_dir = os.path.join(app.static_folder, "assets")
        full = os.path.join(assets_dir, filename)
        if not os.path.exists(full):
            abort(404)
        return send_from_directory(assets_dir, filename)

    # Optional files: quietly 404 if missing
    @app.route("/favicon.ico")
    def favicon():
        f = os.path.join(app.static_folder, "favicon.ico")
        if os.path.exists(f):
            return send_from_directory(app.static_folder, "favicon.ico")
        abort(404)

    @app.route("/manifest.webmanifest")
    def webmanifest():
        m = os.path.join(app.static_folder, "manifest.webmanifest")
        if os.path.exists(m):
            return send_from_directory(app.static_folder, "manifest.webmanifest")
        abort(404)

    # SPA fallback: serve actual file if present, else index.html
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def spa(path):
        # never swallow API routes
        if path.startswith("api/"):
            abort(404)

        candidate = os.path.join(app.static_folder, path)
        if path and os.path.exists(candidate):
            return send_from_directory(app.static_folder, path)

        index_path = os.path.join(app.static_folder, "index.html")
        if os.path.exists(index_path):
            return send_from_directory(app.static_folder, "index.html")

        # If dist is missing (bad build), show a clear message
        return "Frontend build missing. Did Vite run?", 500

    return app


app = create_app()

# ✅ Aliases & compatibility (keep POST bodies via 307)
@app.before_request
def apiv1_alias():
    # Alias /api/v1/* → /api/*
    if request.path.startswith("/api/v1/"):
        return redirect(request.path.replace("/api/v1", "/api", 1), code=307)

    # Example extra alias (uncomment if your frontend still posts here):
    # if request.path in ("/api/participants", "/api/v1/participants"):
    #     return redirect("/api", code=307)


# --- Optional: auto-create tables & seed admin on first boot (Railway friendly) ---
if os.getenv("AUTO_CREATE_DB", "1") == "1":
    with app.app_context():
        try:
            db.create_all()
            if not User.query.filter_by(email="admin@stocktonmemorial.org").first():
                u = User(name="Admin", email="admin@stocktonmemorial.org", role="admin")
                u.password_hash = bcrypt.generate_password_hash("ChangeMe123!").decode("utf-8")
                db.session.add(u)
                db.session.commit()
                app.logger.info("Seeded admin user.")
            app.logger.info("DB ready (auto-create).")
        except Exception as e:
            app.logger.exception("DB init failed on boot")


# --- CLI seed (still handy locally) ---
@app.cli.command("initdb")
def initdb():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email="admin@stocktonmemorial.org").first():
            u = User(name="Admin", email="admin@stocktonmemorial.org", role="admin")
            u.password_hash = bcrypt.generate_password_hash("ChangeMe123!").decode("utf-8")
            db.session.add(u)
            db.session.commit()
            print("Admin created: admin@stocktonmemorial.org / ChangeMe123!")
        print("DB ready")


if __name__ == "__main__":
    # Local dev run (Railway uses gunicorn)
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
