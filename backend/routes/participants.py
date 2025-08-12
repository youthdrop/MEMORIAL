from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
try:
    from ..models import db, Participant
except ImportError:
    from models import db, Participant
bp = Blueprint("participants", __name__)
def _row(p):
    return {
        "id": p.id, "first_name": p.first_name, "last_name": p.last_name,
        "dob": p.dob.isoformat() if p.dob else None, "race": p.race,
        "address": p.address, "email": p.email, "phone": p.phone,
        "created_at": p.created_at.isoformat() if p.created_at else None
    }
@bp.get("/participants")
@jwt_required(optional=True)
def list_participants():
    items = Participant.query.order_by(Participant.id.desc()).limit(200).all()
    return jsonify([_row(p) for p in items]), 200
@bp.post("/participants")
@jwt_required(optional=True)
def create_participant():
    d = request.get_json() or {}
    first = (d.get("first_name") or "").strip()
    last  = (d.get("last_name")  or "").strip()
    if not first or not last:
        return jsonify({"msg":"first_name and last_name required"}), 400
    p = Participant(first_name=first, last_name=last, dob=d.get("dob"),
                    race=d.get("race"), address=d.get("address"),
                    email=d.get("email"), phone=d.get("phone"))
    db.session.add(p); db.session.commit()
    return jsonify({"id": p.id}), 201
@bp.get("/participants/<int:pid>")
@jwt_required(optional=True)
def get_participant(pid):
    from flask import abort
    p = Participant.query.get(pid)
    if not p: abort(404)
    return jsonify(_row(p)), 200
@bp.put("/participants/<int:pid>")
@jwt_required(optional=True)
def update_participant(pid):
    from flask import abort
    p = Participant.query.get(pid)
    if not p: abort(404)
    d = request.get_json() or {}
    if "first_name" in d:
        v = (d["first_name"] or "").strip()
        if not v: return jsonify({"msg":"first_name cannot be empty"}), 400
        p.first_name = v
    if "last_name" in d:
        v = (d["last_name"] or "").strip()
        if not v: return jsonify({"msg":"last_name cannot be empty"}), 400
        p.last_name = v
    for k in ("dob","race","address","email","phone"):
        if k in d: setattr(p, k, d[k])
    db.session.commit()
    return jsonify(_row(p)), 200
@bp.delete("/participants/<int:pid>")
@jwt_required(optional=True)
def delete_participant(pid):
    from flask import abort
    p = Participant.query.get(pid)
    if not p: abort(404)
    db.session.delete(p); db.session.commit()
    return ("", 204)
