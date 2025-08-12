from flask import Blueprint, request, jsonify
from models import db, Employer, Provider
from flask_jwt_extended import jwt_required
from utils import roles_required

bp_orgs = Blueprint('orgs', __name__)  # ← no url_prefix here

@bp_orgs.post('/employers')
@roles_required('admin')
def add_employer():
    d = request.get_json() or {}
    e = Employer(
        name=d.get('name'),
        contact_name=d.get('contact_name'),
        phone=d.get('phone'),
        email=d.get('email'),
        address=d.get('address'),
    )
    db.session.add(e)
    db.session.commit()
    return jsonify({'id': e.id}), 201

@bp_orgs.get('/employers')
@jwt_required()
def list_employers():
    rows = Employer.query.order_by(Employer.name).all()
    return jsonify([
        {'id': r.id, 'name': r.name, 'contact_name': r.contact_name,
         'phone': r.phone, 'email': r.email, 'address': r.address}
        for r in rows
    ]), 200

@bp_orgs.post('/providers')
@roles_required('admin')
def add_provider():
    d = request.get_json() or {}
    p = Provider(
        name=d.get('name'),
        contact_name=d.get('contact_name'),
        phone=d.get('phone'),
        email=d.get('email'),
        address=d.get('address'),
    )
    db.session.add(p)
    db.session.commit()
    return jsonify({'id': p.id}), 201

@bp_orgs.get('/providers')
@jwt_required()
def list_providers():
    rows = Provider.query.order_by(Provider.name).all()
    return jsonify([
        {'id': r.id, 'name': r.name, 'contact_name': r.contact_name,
         'phone': r.phone, 'email': r.email, 'address': r.address}
        for r in rows
    ]), 200
