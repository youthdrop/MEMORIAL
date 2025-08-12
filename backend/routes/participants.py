# backend/routes/participants.py
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Participant, CaseNote, Service, Referral, Employer, Provider

bp = Blueprint("participants", __name__)

# -------- helpers --------
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
    return {"id": n.id, "content": n.content, "created_at": n.created_at.isoformat() if n.created_at else None}

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
        kind = "employer"
        org_id = r.employer_id
    elif r.provider_id:
        pr = db.session.get(Provider, r.provider_id)
        org_name = pr.name if pr else None
        kind = "provider"
        org_id = r.provider_id
    else:
        kind, org_id = None, None

    return {
        "id": r.id,
        "kind": kind,
        "org_id": org_id,
        "org_name": org_name,
        "status": r.status,
        "note": r.note,
        "referred_at": r.referred_at.isoformat() if r.referred_at else None,
    }

# -------- Participants CRUD --------
@bp.get("/participants")
@jwt_required()
def list_participants():
    q = Participant.query.filter_by(is_active=True).order_by(Participant.last_name, Participant.first_name)
    items = [_p_row(p) for p in q.all()]
    return jsonify(items), 200

@bp.post("/participants")
@jwt_required()
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

@bp.get("/participants/<int:pid>")
@jwt_required()
def get_participant(pid):
    p = Participant.query.get_or_404(pid)
    return jsonify(_p_row(p)), 200

@bp.put("/participants/<int:pid>")
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

@bp.delete("/participants/<int:pid>")
@jwt_required()
def delete_participant(pid):
    p = Participant.query.get_or_404(pid)
    p.is_active = False
    db.session.commit()
    return jsonify({"msg": "deactivated"}), 200

# -------- Case Notes --------
@bp.get("/participants/<int:pid>/notes")
@jwt_required()
def list_notes(pid):
    Participant.query.get_or_404(pid)
    notes = CaseNote.query.filter_by(participant_id=pid).order_by(CaseNote.created_at.desc()).all()
    return jsonify([_note_row(n) for n in notes]), 200

@bp.post("/participants/<int:pid>/notes")
@jwt_required()
def create_note(pid):
    Participant.query.get_or_404(pid)
    data = request.get_json() or {}
    content = (data.get("content") or "").strip()
    if not content:
        return jsonify({"msg": "content is required"}), 400

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

# -------- Services --------
@bp.get("/participants/<int:pid>/services")
@jwt_required()
def list_services(pid):
    Participant.query.get_or_404(pid)
    svcs = Service.query.filter_by(participant_id=pid).order_by(Service.provided_at.desc()).all()
    return jsonify([_svc_row(s) for s in svcs]), 200

@bp.post("/participants/<int:pid>/services")
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

# -------- Referrals --------
@bp.get("/participants/<int:pid>/referrals")
@jwt_required()
def list_referrals(pid):
    Participant.query.get_or_404(pid)
    refs = Referral.query.filter_by(participant_id=pid).order_by(Referral.referred_at.desc()).all()
    return jsonify([_ref_row(r) for r in refs]), 200

@bp.post("/participants/<int:pid>/referrals")
@jwt_required()
def create_referral(pid):
    Participant.query.get_or_404(pid)
    data = request.get_json() or {}
    kind = (data.get("kind") or "").strip()
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
