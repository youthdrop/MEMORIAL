import os
import logging
from flask import Flask, jsonify, send_from_directory, request, redirect, abort
from flask_cors import CORS
from config import settings
from models import db, User
from auth import auth_bp, bcrypt, jwt
from routes.participants import bp as participants_bp
from routes.nested import bp_nested
from routes.reports import reports_bp
from flask_migrate import Migrate
from dotenv import load_dotenv

load_dotenv()

# ✅ Point to ../frontend/dist relative to this file
HERE = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(HERE, "..", "frontend", "dist")

def create_app():
    # use absolute path so it works no matter where you run from
    app = Flask(__name__, static_folder=DIST_DIR, static_url_path="/")

    # --- Logging ---
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)

    # --- Config ---
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = settings.JWT_SECRET_KEY or "dev-only"

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
        supports_credentials=False
    )

    # --- Blueprints (mounted at /api) ---
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
            db_uri_configured=bool(app.config.get('SQLALCHEMY_DATABASE_URI')),
            jwt_key_set=bool(app.config.get('JWT_SECRET_KEY')),
        ), 200

    # --- Helpful error handlers (JSON always) ---
    @app.errorhandler(400)
    @app.errorhandler(401)
    @app.errorhandler(403)
    @app.errorhandler(404)
    @app.errorhandler(405)
    @app.errorhandler(500)
    def handle_errors(err):
        code = getattr(err, "code", 500)
        app.logger.exception(err)
        return jsonify(error=str(err), code=code), code

    # --- Static asset routes for Vite build ---
    @app.route("/assets/<path:filename>")
    def assets(filename):
        assets_dir = os.path.join(app.static_folder, "assets")
        full = os.path.join(assets_dir, filename)
        if not os.path.exists(full):
            abort(404)
        return send_from_directory(assets_dir, filename)

    @app.route("/favicon.ico")
    def favicon():
        path = os.path.join(app.static_folder, "favicon.ico")
        if os.path.exists(path):
            return send_from_directory(app.static_folder, "favicon.ico")
        abort(404)

    @app.route("/manifest.webmanifest")
    def manifest():
        path = os.path.join(app.static_folder, "manifest.webmanifest")
        if os.path.exists(path):
            return send_from_directory(app.static_folder, "manifest.webmanifest")
        abort(404)

    # --- Root: serve index.html if present ---
    @app.route("/")
    def index():
        index_path = os.path.join(app.static_folder, "index.html")
        if os.path.exists(index_path):
            return send_from_directory(app.static_folder, "index.html")
        return "API is running. Try GET /api/health", 200

    return app


app = create_app()

# ✅ Aliases & compatibility
# ✅ Aliases & compatibility
@app.before_request
def route_aliases():
    # Let CORS preflight pass
    if request.method == "OPTIONS":
        return None

    path = request.path

    # /api/v1/* → /api/*
    if path.startswith("/api/v1/"):
        return redirect(path.replace("/api/v1", "/api", 1), code=307)

    # 🔐 Auth: map old login paths to the actual /api/login
    if path in ("/api/auth/login", "/api/v1/auth/login"):
        return redirect("/api/login", code=307)  # 307 keeps POST + body

    # Participants collection alias (frontend uses /api/participants)
    if path == "/api/participants":
        return redirect("/api", code=307)

    # Participants nested aliases (…/participants/<pid>[/*])
    if path.startswith("/api/participants/"):
        parts = path.strip("/").split("/")
        if len(parts) >= 3 and parts[2].isdigit():
            pid = parts[2]
            if len(parts) == 3:
                return redirect(f"/api/{pid}", code=307)
            resource = parts[3]
            allowed = {
                "casenotes", "services", "referrals",
                "assessments", "employment", "education",
                "milestones", "enrollments", "outcomes"
            }
            if resource in allowed:
                qs = request.query_string.decode("utf-8")
                pid_qs = f"pid={pid}"
                new_qs = f"{qs}&{pid_qs}" if qs else pid_qs
                if resource == "referrals" and len(parts) >= 5 and parts[4].isdigit():
                    rid = parts[4]
                    return redirect(f"/api/referrals/{rid}?{new_qs}", code=307)
                return redirect(f"/api/{resource}?{new_qs}", code=307)

    return None



# 🟡 Debug: print all routes on boot
with app.app_context():
    print("== ROUTES ==")
    for r in app.url_map.iter_rules():
        print(r)

# (Optional) confirm admin user exists
@app.route("/api/_debug/user")
def _debug_user():
    u = User.query.filter_by(email="admin@stocktonmemorial.org").first()
    return {
        "exists": bool(u),
        "has_password_hash": bool(getattr(u, "password_hash", None)) if u else False
    }, 200

# --- SPA fallback for React Router ---
@app.route("/<path:path>")
def spa_fallback(path):
    if path.startswith("api/"):
        abort(404)
    index_path = os.path.join(app.static_folder, "index.html")
    if os.path.exists(index_path):
        return send_from_directory(app.static_folder, "index.html")
    abort(404)

# --- CLI: init DB & seed admin ---
@app.cli.command('initdb')
def initdb():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email='admin@stocktonmemorial.org').first():
            u = User(name='Admin', email='admin@stocktonmemorial.org', role='admin')
            u.password_hash = bcrypt.generate_password_hash('ChangeMe123!').decode('utf-8')
            db.session.add(u)
            db.session.commit()
            print('Admin created: admin@stocktonmemorial.org / ChangeMe123!')
        print('DB ready')

if __name__ == '__main__':
    # run from the backend folder:  python app.py
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)), debug=True)
