from flask import Blueprint, request, jsonify
from models import db, Provider
from utils import roles_required
from flask_jwt_extended import jwt_required

bp_providers = Blueprint('providers', __name__, url_prefix='/api/v1/providers')

@bp_providers.post('')
@roles_required('admin')
def create():
    d = request.get_json() or {}
    p = Provider(name=d.get('name'), contact_name=d.get('contact_name'), phone=d.get('phone'), email=d.get('email'), address=d.get('address'))
    db.session.add(p); db.session.commit(); return jsonify({'id': p.id}), 201

@bp_providers.get('')
@jwt_required()
def list_all():
    q = request.args.get('q', '')
    rows = Provider.query if not q else Provider.query.filter(Provider.name.ilike(f'%{q}%'))
    rows = rows.order_by(Provider.name).limit(200).all()
    return jsonify([{'id': r.id, 'name': r.name, 'contact_name': r.contact_name, 'phone': r.phone, 'email': r.email, 'address': r.address} for r in rows])
