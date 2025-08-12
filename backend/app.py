# backend/app.py
import os
import logging
from datetime import datetime
from flask import Flask, jsonify, request, redirect, abort, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import jwt_required, get_jwt_identity

# ----- Project modules (adjust if your paths differ) -----
from config import settings                 # must exist
from models import (
    db, User, Participant, CaseNote, Service, Referral, Employer, Provider
)
from auth import auth_bp, bcrypt, jwt       # must exist
from utils import roles_required            # must exist

# Optional blueprints — register only if present in your repo
try:
    from routes.nested import bp_nested
except Exception:
    bp_nested = None

# register reports under /api/reports
try:
    from reports import reports_bp
    app.register_blueprint(reports_bp, url_prefix="/api/reports")
except Exception as e:
    app.logger.info(f"reports_bp not registered: {e}")


# .env is nice in dev; safe to skip in prod
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(HERE, "..", "frontend", "dist")


def create_app() -> Flask:
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

    # --- CORS (API only) ---
    origins = settings.CORS_ORIGINS or ["http://localhost:5173", "http://127.0.0.1:5173"]
    CORS(
        app,
        resources={r"/api/*": {"origins": origins}, r"/api/v1/*": {"origins": origins}},
        supports_credentials=False,
    )

    # --- Register any external blueprints you already have ---
    app.register_blueprint(auth_bp, url_prefix="/api")
    if bp_nested:
        app.register_blueprint(bp_nested, url_prefix="/api")
    if reports_bp:
        app.register_blueprint(reports_bp, url_prefix="/api")

    # ---------------- Helpers (serializers) ----------------
    def _p_row(p: Participant):
        return {
            "id": p.id,
            "first_name": p.first_name,
            "last_name": p.last_name,
            "dob": p.dob.isoformat() if p.dob else None,
            "race": p.race,
            "address": p.address,
            "email": p.email,
            "phone": p.phone,
            "name": f"{(p.first_name or '').strip()} {(p.last_name or '').strip()}".strip(),
        }

    def _note_row(n: CaseNote):
        return {"id": n.id, "content": n.content, "created_at": n.created_at.isoformat()}

    def _svc_row(s: Service):
        return {
            "id": s.id,
            "service_type": s.service_type,
            "note": s.note,
            "provided_at": s.provided_at.isoformat() if s.provided_at else None,
        }

    def _ref_row(r: Referral):
        org_name = None
        if r.employer_id:
            e = db.session.get(Employer, r.employer_id)
            org_name = e.name if e else None
        if r.provider_id:
            pr = db.session.get(Provider, r.provider_id)
            org_name = pr.name if pr else org_name
        return {
            "id": r.id,
            "kind": "employer" if r.employer_id else "provider",
            "org_id": r.employer_id or r.provider_id,
            "org_name": org_name,
            "status": r.status,
            "note": r.note,
            "referred_at": r.referred_at.isoformat() if r.referred_at else None,
        }

    # ---------------- Health & Env ----------------
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

    # ---------------- Participants CRUD ----------------
    @app.get("/api/participants")
    @jwt_required()
    def list_participants():
        q = Participant.query.filter_by(is_active=True).order_by(
            Participant.last_name, Participant.first_name
        )
        return jsonify([_p_row(p) for p in q.all()]), 200

    @app.post("/api/participants")
    @roles_required("admin")
    def create_participant():
        data = request.get_json() or {}
        first = (data.get("first_name") or "").strip()
        last = (data.get("last_name") or "").strip()
        if not first or not last:
            return jsonify({"msg": "first_name and last_name are required"}), 400
        dob = None
        if data.get("dob"):
            try:
                dob = datetime.fromisoformat(data["dob"]).date()
            except ValueError:
                return jsonify({"msg": "dob must be YYYY-MM-DD"}), 400
        p = Participant(
            first_name=first,
            last_name=last,
            dob=dob,
            race=data.get("race"),
            address=data.get("address"),
            email=data.get("email"),
            phone=data.get("phone"),
            is_active=True,
        )
        db.session.add(p)
        db.session.commit()
        return jsonify({"id": p.id}), 201

    @app.get("/api/participants/<int:pid>")
    @jwt_required()
    def get_participant(pid):
        p = Participant.query.get_or_404(pid)
        return jsonify(_p_row(p)), 200

    @app.put("/api/participants/<int:pid>")
    @jwt_required()
    def update_participant(pid):
        p = Participant.query.get_or_404(pid)
        data = request.get_json() or {}

        if "first_name" in data:
            if not (data["first_name"] or "").strip():
                return jsonify({"msg": "first_name cannot be empty"}), 400
            p.first_name = data["first_name"]

        if "last_name" in data:
            if not (data["last_name"] or "").strip():
                return jsonify({"msg": "last_name cannot be empty"}), 400
            p.last_name = data["last_name"]

        if "dob" in data:
            if data["dob"]:
                try:
                    p.dob = datetime.fromisoformat(data["dob"]).date()
                except ValueError:
                    return jsonify({"msg": "dob must be YYYY-MM-DD"}), 400
            else:
                p.dob = None

        for f in ["race", "address", "email", "phone"]:
            if f in data:
                setattr(p, f, data[f])

        db.session.commit()
        return jsonify({"msg": "updated"}), 200

    @app.delete("/api/participants/<int:pid>")
    @jwt_required()
    def delete_participant(pid):
        p = Participant.query.get_or_404(pid)
        p.is_active = False
        db.session.commit()
        return jsonify({"msg": "deactivated"}), 200

    # ---------------- Case Notes ----------------
    @app.get("/api/participants/<int:pid>/notes")
    @jwt_required()
    def list_notes(pid):
        Participant.query.get_or_404(pid)
        notes = (
            CaseNote.query.filter_by(participant_id=pid)
            .order_by(CaseNote.created_at.desc())
            .all()
        )
        return jsonify([_note_row(n) for n in notes]), 200

    @app.post("/api/participants/<int:pid>/notes")
    @jwt_required()
    def create_note(pid):
        Participant.query.get_or_404(pid)
        data = request.get_json() or {}
        content = (data.get("content") or "").strip()
        if not content:
            return jsonify({"msg": "content is required"}), 400

        # Optional: derive staff_id from JWT identity dict
        staff_id = None
        try:
            ident = get_jwt_identity()
            if isinstance(ident, dict):
                staff_id = ident.get("id")
        except Exception:
            pass

        n = CaseNote(participant_id=pid, staff_id=staff_id, content=content)
        db.session.add(n)
        db.session.commit()
        return jsonify({"id": n.id, **_note_row(n)}), 201

    # ---------------- Services ----------------
    @app.get("/api/participants/<int:pid>/services")
    @jwt_required()
    def list_services(pid):
        Participant.query.get_or_404(pid)
        svcs = (
            Service.query.filter_by(participant_id=pid)
            .order_by(Service.provided_at.desc())
            .all()
        )
        return jsonify([_svc_row(s) for s in svcs]), 200

    @app.post("/api/participants/<int:pid>/services")
    @jwt_required()
    def create_service(pid):
        Participant.query.get_or_404(pid)
        data = request.get_json() or {}
        service_type = (data.get("service_type") or "").strip()
        if not service_type:
            return jsonify({"msg": "service_type is required"}), 400

        s = Service(
            participant_id=pid,
            service_type=service_type,
            note=data.get("note"),
            provided_at=datetime.utcnow(),
        )
        db.session.add(s)
        db.session.commit()
        return jsonify({"id": s.id, **_svc_row(s)}), 201

    # ---------------- Referrals ----------------
    @app.get("/api/participants/<int:pid>/referrals")
    @jwt_required()
    def list_referrals(pid):
        Participant.query.get_or_404(pid)
        refs = (
            Referral.query.filter_by(participant_id=pid)
            .order_by(Referral.referred_at.desc())
            .all()
        )
        return jsonify([_ref_row(r) for r in refs]), 200

    @app.post("/api/participants/<int:pid>/referrals")
    @jwt_required()
    def create_referral(pid):
        Participant.query.get_or_404(pid)
        data = request.get_json() or {}
        kind = (data.get("kind") or "").strip()  # 'employer' | 'provider'
        org_id = data.get("org_id")
        if kind not in ("employer", "provider") or not org_id:
            return jsonify({"msg": "kind ('employer'|'provider') and org_id are required"}), 400

        r = Referral(
            participant_id=pid,
            employer_id=org_id if kind == "employer" else None,
            provider_id=org_id if kind == "provider" else None,
            status=(data.get("status") or "referred"),
            note=data.get("note"),
            referred_at=datetime.utcnow(),
        )
        db.session.add(r)
        db.session.commit()
        return jsonify({"id": r.id, **_ref_row(r)}), 201

    # ---------------- Employers / Providers ----------------
    @app.get("/api/employers")
    @jwt_required()
    def list_employers():
        rows = Employer.query.order_by(Employer.name).all()
        return jsonify([
            {
                "id": r.id, "name": r.name, "contact_name": r.contact_name,
                "phone": r.phone, "email": r.email, "address": r.address
            } for r in rows
        ]), 200

    @app.post("/api/employers")
    @roles_required("admin")
    def add_employer():
        d = request.get_json() or {}
        name = (d.get("name") or "").strip()
        if not name:
            return jsonify({"msg": "name is required"}), 400
        e = Employer(
            name=name,
            contact_name=d.get("contact_name"),
            phone=d.get("phone"),
            email=d.get("email"),
            address=d.get("address"),
        )
        db.session.add(e)
        db.session.commit()
        return jsonify({"id": e.id}), 201

    @app.get("/api/providers")
    @jwt_required()
    def list_providers():
        rows = Provider.query.order_by(Provider.name).all()
        return jsonify([
            {
                "id": r.id, "name": r.name, "contact_name": r.contact_name,
                "phone": r.phone, "email": r.email, "address": r.address
            } for r in rows
        ]), 200

    @app.post("/api/providers")
    @roles_required("admin")
    def add_provider():
        d = request.get_json() or {}
        name = (d.get("name") or "").strip()
        if not name:
            return jsonify({"msg": "name is required"}), 400
        p = Provider(
            name=name,
            contact_name=d.get("contact_name"),
            phone=d.get("phone"),
            email=d.get("email"),
            address=d.get("address"),
        )
        db.session.add(p)
        db.session.commit()
        return jsonify({"id": p.id}), 201

    # ---------------- Misc (addresses & static) ----------------
    @app.route("/api/addresses", methods=["GET"])
    def address_search():
        q = request.args.get("q", "").strip()
        if not q:
            return jsonify([]), 200
        # TODO: replace with real geocoder
        return jsonify([{"label": q}]), 200

    # Error handlers (API JSON only)
    @app.errorhandler(400)
    @app.errorhandler(401)
    @app.errorhandler(403)
    @app.errorhandler(405)
    @app.errorhandler(500)
    def handle_api_errors(err):
        if request.path.startswith("/api"):
            code = getattr(err, "code", 500)
            app.logger.exception(err)
            return jsonify(error=str(err), code=code), code
        return err

    # Static & SPA
    @app.route("/assets/<path:filename>")
    def vite_assets(filename):
        assets_dir = os.path.join(app.static_folder, "assets")
        full = os.path.join(assets_dir, filename)
        if not os.path.exists(full):
            abort(404)
        return send_from_directory(assets_dir, filename)

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

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def spa(path):
        if path.startswith("api/"):
            abort(404)
        candidate = os.path.join(app.static_folder, path)
        if path and os.path.exists(candidate):
            return send_from_directory(app.static_folder, path)
        index_path = os.path.join(app.static_folder, "index.html")
        if os.path.exists(index_path):
            return send_from_directory(app.static_folder, "index.html")
        return "Frontend build missing. Did Vite run?", 500

    return app


app = create_app()

# Alias /api/v1/* → /api/*
@app.before_request
def apiv1_alias():
    if request.path.startswith("/api/v1/"):
        return redirect(request.path.replace("/api/v1", "/api", 1), code=307)

# Dev-only: create tables & seed admin if needed
if os.getenv("FLASK_ENV") == "development":
    with app.app_context():
        try:
            db.create_all()
            if not User.query.filter_by(email="admin@stocktonmemorial.org").first():
                u = User(name="Admin", email="admin@stocktonmemorial.org", role="admin")
                u.password_hash = bcrypt.generate_password_hash("ChangeMe123!").decode("utf-8")
                db.session.add(u)
                db.session.commit()
                app.logger.info("Seeded admin user.")
            app.logger.info("DB ready (dev create_all).")
        except Exception:
            app.logger.exception("DB init failed on boot (dev)")

# CLI: flask initdb
@app.cli.command("initdb")
def initdb():
    with app.app_context():
        if not User.query.filter_by(email="admin@stocktonmemorial.org").first():
            u = User(name="Admin", email="admin@stocktonmemorial.org", role="admin")
            u.password_hash = bcrypt.generate_password_hash("ChangeMe123!").decode("utf-8")
            db.session.add(u)
            db.session.commit()
            print("Admin created: admin@stocktonmemorial.org / ChangeMe123!")
        print("DB ready")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
