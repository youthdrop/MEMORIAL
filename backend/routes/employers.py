from flask import Blueprint, request, jsonify
from models import db, Employer
from utils import roles_required
from flask_jwt_extended import jwt_required

bp_employers = Blueprint('employers', __name__, url_prefix='/api/v1/employers')

@bp_employers.post('')
@roles_required('admin')
def create():
    d = request.get_json() or {}
    e = Employer(name=d.get('name'), contact_name=d.get('contact_name'), phone=d.get('phone'), email=d.get('email'), address=d.get('address'))
    db.session.add(e); db.session.commit(); return jsonify({'id': e.id}), 201

@bp_employers.get('')
@jwt_required()
def list_all():
    q = request.args.get('q', '')
    rows = Employer.query if not q else Employer.query.filter(Employer.name.ilike(f'%{q}%'))
    rows = rows.order_by(Employer.name).limit(200).all()
    return jsonify([{'id': r.id, 'name': r.name, 'contact_name': r.contact_name, 'phone': r.phone, 'email': r.email, 'address': r.address} for r in rows])
