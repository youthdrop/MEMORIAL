from flask import Blueprint, request, jsonify
from sqlalchemy import func
from models import db, Participant, Service, Employment, Education, Referral, Employer, Provider
from flask_jwt_extended import jwt_required

reports_bp = Blueprint('reports', __name__, url_prefix='/api/v1/reports')

@reports_bp.get('/enrollments')
@jwt_required()
def enrollments():
    start = request.args.get('start'); end = request.args.get('end')
    q = db.session.query(func.date(Participant.created_at), func.count(Participant.id)).filter(Participant.is_active == True)
    if start: q = q.filter(Participant.created_at >= start)
    if end: q = q.filter(Participant.created_at <= end)
    rows = q.group_by(func.date(Participant.created_at)).order_by(func.date(Participant.created_at)).all()
    return jsonify([{'date': str(d), 'count': c} for d, c in rows])

@reports_bp.get('/services')
@jwt_required()
def services_by_type():
    start = request.args.get('start'); end = request.args.get('end')
    q = db.session.query(Service.service_type, func.date(Service.provided_at), func.count(Service.id))
    if start: q = q.filter(Service.provided_at >= start)
    if end: q = q.filter(Service.provided_at <= end)
    rows = q.group_by(Service.service_type, func.date(Service.provided_at)).order_by(func.date(Service.provided_at)).all()
    return jsonify([{'service_type': t, 'date': str(d), 'count': c} for t, d, c in rows])

@reports_bp.get('/outcomes')
@jwt_required()
def outcomes():
    emp = db.session.query('employment', Employment.status, func.count(Employment.id)).group_by(Employment.status).all()
    edu = db.session.query('education', Education.status, func.count(Education.id)).group_by(Education.status).all()
    rows = [{'kind': k, 'status': s, 'count': c} for k, s, c in emp + edu]
    return jsonify(rows)

@reports_bp.get('/referrals')
@jwt_required()
def referrals():
    rows = db.session.query(
        func.coalesce(Employer.name, Provider.name),
        func.case((Referral.employer_id.isnot(None), 'employer'), else_='provider'),
        Referral.status,
        func.count(Referral.id)
    ).outerjoin(Employer, Referral.employer_id == Employer.id
    ).outerjoin(Provider, Referral.provider_id == Provider.id
    ).group_by(func.coalesce(Employer.name, Provider.name), func.case((Referral.employer_id.isnot(None), 'employer'), else_='provider'), Referral.status
    ).order_by(func.coalesce(Employer.name, Provider.name)).all()
    return jsonify([{'org_name': n, 'kind': k, 'status': s, 'count': c} for n, k, s, c in rows])
