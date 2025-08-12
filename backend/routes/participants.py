from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

# Works whether run as package or bare script
try:
    from ..models import db, Participant
except ImportError:
    from models import db, Participant

bp = Blueprint("participants", __name__)  # no url_prefix; app.py mounts at /api

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
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }

@bp.get("/participants")
@jwt_required(optional=True)
def list_participants():
    q = Participant.query.order_by(Participant.id.desc())
    return jsonify([_p_row(p) for p in q.limit(200).all()]), 200

@bp.post("/participants")
@jwt_required(optional=True)
def create_participant():
    data = request.get_json() or {}
    first = (data.get("first_name") or "").strip()
    last  = (data.get("last_name")  or "").strip()
    if not first or not last:
        return jsonify({"msg": "first_name and last_name required"}), 400
    p = Participant(
        first_name=first,
        last_name=last,
        dob=data.get("dob"),
        race=data.get("race"),
        address=data.get("address"),
        email=data.get("email"),
        phone=data.get("phone"),
    )
    db.session.add(p)
    db.session.commit()
    return jsonify({"id": p.id}), 201

@bp.get("/participants/<int:pid>")
@jwt_required(optional=True)
def get_participant(pid):
    p = Participant.query.get_or_404(pid)
    return jsonify(_p_row(p)), 200

@bp.put("/participants/<int:pid>")
@jwt_required(optional=True)
def update_participant(pid):
    p = Participant.query.get_or_404(pid)
    data = request.get_json() or {}

    if "first_name" in data:
        v = (data["first_name"] or "").strip()
        if not v:
            return jsonify({"msg": "first_name cannot be empty"}), 400
        p.first_name = v
    if "last_name" in data:
        v = (data["last_name"] or "").strip()
        if not v:
            return jsonify({"msg": "last_name cannot be empty"}), 400
        p.last_name = v
    for k in ("dob","race","address","email","phone"):
        if k in data:
            setattr(p, k, data[k])

    db.session.commit()
    return jsonify(_p_row(p)), 200

@bp.delete("/participants/<int:pid>")
@jwt_required(optional=True)
def delete_participant(pid):
    p = Participant.query.get_or_404(pid)
    db.session.delete(p)
    db.session.commit()
    return ("", 204)
