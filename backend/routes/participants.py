from flask import Blueprint, request, jsonify
from datetime import datetime
from models import db, Participant
from utils import roles_required
from flask_jwt_extended import jwt_required

bp = Blueprint('participants', __name__, url_prefix='/api/v1/participants')

def _row(p):
    return {'id': p.id, 'name': f"{p.first_name} {p.last_name}", 'dob': p.dob.isoformat() if p.dob else None, 'race': p.race}

@bp.post('')
@roles_required('admin')
def create_participant():
    data = request.get_json() or {}
    first = (data.get('first_name') or '').strip()
    last = (data.get('last_name') or '').strip()
    if not first or not last:
        return jsonify({'msg':'first_name and last_name are required'}), 400
    email = data.get('email') or ''
    if email and '@' not in email:
        return jsonify({'msg':'invalid email'}), 400
    p = Participant(first_name=first, last_name=last, dob=datetime.fromisoformat(data['dob']).date() if data.get('dob') else None, race=data.get('race'), address=data.get('address'), email=email, phone=data.get('phone'))
    db.session.add(p); db.session.commit()
    return jsonify({'id': p.id}), 201

@bp.get('')
@jwt_required()
def list_participants():
    q = Participant.query.filter_by(is_active=True)
    paginated = request.args.get('paginated')
    if paginated:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 25)), 100)
        p = q.order_by(Participant.last_name).paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({'items': [_row(x) for x in p.items], 'page': p.page, 'per_page': p.per_page, 'total': p.total})
    items = q.order_by(Participant.last_name).all()
    return jsonify([_row(p) for p in items])

@bp.get('/<int:pid>')
@jwt_required()
def get_participant(pid):
    p = Participant.query.get_or_404(pid)
    return jsonify({'id': p.id,'first_name': p.first_name,'last_name': p.last_name,'dob': p.dob.isoformat() if p.dob else None,'race': p.race,'address': p.address,'email': p.email,'phone': p.phone})

@bp.put('/<int:pid>')
@jwt_required()
def update_participant(pid):
    p = Participant.query.get_or_404(pid)
    data = request.get_json() or {}
    if 'first_name' in data and not (data['first_name'] or '').strip():
        return jsonify({'msg':'first_name cannot be empty'}), 400
    if 'last_name' in data and not (data['last_name'] or '').strip():
        return jsonify({'msg':'last_name cannot be empty'}), 400
    if 'email' in data and data['email'] and '@' not in data['email']:
        return jsonify({'msg':'invalid email'}), 400
    for f in ['first_name','last_name','race','address','email','phone']:
        if f in data: setattr(p, f, data[f])
    if 'dob' in data: p.dob = datetime.fromisoformat(data['dob']).date() if data['dob'] else None
    db.session.commit(); return jsonify({'msg': 'updated'})

@bp.delete('/<int:pid>')
@roles_required('admin')
def delete_participant(pid):
    p = Participant.query.get_or_404(pid)
    p.is_active = False; db.session.commit()
    return jsonify({'msg': 'deactivated'})
