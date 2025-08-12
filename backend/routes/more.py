from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

try:
    from ..models import db, Participant, CaseNote, Service, Referral, Employer, Provider
except ImportError:
    from models import db, Participant, CaseNote, Service, Referral, Employer, Provider

bp_more = Blueprint("more", __name__)

# ---------- participants/<pid>/notes ----------
@bp_more.get("/participants/<int:pid>/notes")
@jwt_required(optional=True)
def list_notes(pid):
    Participant.query.get_or_404(pid)
    rows = (CaseNote.query
            .filter_by(participant_id=pid)
            .order_by(CaseNote.created_at.desc())
            .limit(200).all())
    return jsonify([{
        "id": n.id, "participant_id": n.participant_id, "content": n.content,
        "staff_id": n.staff_id, "created_at": n.created_at.isoformat() if n.created_at else None
    } for n in rows]), 200

@bp_more.post("/participants/<int:pid>/notes")
@jwt_required(optional=True)
def create_note(pid):
    Participant.query.get_or_404(pid)
    d = request.get_json() or {}
    content = (d.get("content") or "").strip()
    if not content:
        return jsonify({"msg": "content required"}), 400
    note = CaseNote(participant_id=pid, content=content, staff_id=d.get("staff_id"))
    db.session.add(note); db.session.commit()
    return jsonify({"id": note.id}), 201

# ---------- participants/<pid>/services ----------
@bp_more.get("/participants/<int:pid>/services")
@jwt_required(optional=True)
def list_services(pid):
    Participant.query.get_or_404(pid)
    rows = (Service.query
            .filter_by(participant_id=pid)
            .order_by(Service.provided_at.desc())
            .limit(200).all())
    return jsonify([{
        "id": s.id, "participant_id": s.participant_id, "service_type": s.service_type,
        "note": s.note, "staff_id": s.staff_id,
        "provided_at": s.provided_at.isoformat() if s.provided_at else None
    } for s in rows]), 200

@bp_more.post("/participants/<int:pid>/services")
@jwt_required(optional=True)
def create_service(pid):
    Participant.query.get_or_404(pid)
    d = request.get_json() or {}
    stype = (d.get("service_type") or "").strip()
    if not stype:
        return jsonify({"msg": "service_type required"}), 400
    s = Service(participant_id=pid, service_type=stype,
                note=d.get("note"), staff_id=d.get("staff_id"))
    db.session.add(s); db.session.commit()
    return jsonify({"id": s.id}), 201

# ---------- participants/<pid>/referrals ----------
@bp_more.get("/participants/<int:pid>/referrals")
@jwt_required(optional=True)
def list_referrals(pid):
    Participant.query.get_or_404(pid)
    rows = (Referral.query
            .filter_by(participant_id=pid)
            .order_by(Referral.referred_at.desc())
            .limit(200).all())
    return jsonify([{
        "id": r.id, "participant_id": r.participant_id, "employer_id": r.employer_id,
        "provider_id": r.provider_id, "staff_id": r.staff_id,
        "status": r.status, "note": r.note,
        "referred_at": r.referred_at.isoformat() if r.referred_at else None
    } for r in rows]), 200

@bp_more.post("/participants/<int:pid>/referrals")
@jwt_required(optional=True)
def create_referral(pid):
    Participant.query.get_or_404(pid)
    d = request.get_json() or {}
    ref = Referral(participant_id=pid,
                   employer_id=d.get("employer_id"),
                   provider_id=d.get("provider_id"),
                   staff_id=d.get("staff_id"),
                   status=d.get("status") or "referred",
                   note=d.get("note"))
    db.session.add(ref); db.session.commit()
    return jsonify({"id": ref.id}), 201

# ---------- employers ----------
@bp_more.get("/employers")
@jwt_required(optional=True)
def list_employers():
    rows = Employer.query.order_by(Employer.id.desc()).limit(200).all()
    return jsonify([{
        "id": e.id, "name": e.name, "contact_name": e.contact_name,
        "phone": e.phone, "email": e.email, "address": e.address
    } for e in rows]), 200

@bp_more.post("/employers")
@jwt_required(optional=True)
def create_employer():
    d = request.get_json() or {}
    name = (d.get("name") or "").strip()
    if not name:
        return jsonify({"msg": "name required"}), 400
    e = Employer(name=name, contact_name=d.get("contact_name"),
                 phone=d.get("phone"), email=d.get("email"), address=d.get("address"))
    db.session.add(e); db.session.commit()
    return jsonify({"id": e.id}), 201

# ---------- providers ----------
@bp_more.get("/providers")
@jwt_required(optional=True)
def list_providers():
    rows = Provider.query.order_by(Provider.id.desc()).limit(200).all()
    return jsonify([{
        "id": p.id, "name": p.name, "contact_name": p.contact_name,
        "phone": p.phone, "email": p.email, "address": p.address
    } for p in rows]), 200

@bp_more.post("/providers")
@jwt_required(optional=True)
def create_provider():
    d = request.get_json() or {}
    name = (d.get("name") or "").strip()
    if not name:
        return jsonify({"msg": "name required"}), 400
    p = Provider(name=name, contact_name=d.get("contact_name"),
                 phone=d.get("phone"), email=d.get("email"), address=d.get("address"))
    db.session.add(p); db.session.commit()
    return jsonify({"id": p.id}), 201
