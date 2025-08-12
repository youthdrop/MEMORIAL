from flask import Blueprint, request, jsonify
from sqlalchemy import func, case
from models import db, Participant, Service, Employment, Education, Referral, Employer, Provider
from flask_jwt_extended import jwt_required

reports_bp = Blueprint('reports', __name__)  # ← remove url_prefix here

@reports_bp.get('/enrollments')
@jwt_required()
def enrollments():
    start = request.args.get('start'); end = request.args.get('end')
    q = db.session.query(func.date(Participant.created_at), func.count(Participant.id))\
                  .filter(Participant.is_active.is_(True))
    if start: q = q.filter(Participant.created_at >= start)
    if end:   q = q.filter(Participant.created_at <= end)
    rows = q.group_by(func.date(Participant.created_at))\
            .order_by(func.date(Participant.created_at)).all()
    return jsonify([{'date': str(d), 'count': c} for d, c in rows])

@reports_bp.get('/services_by_type')
@jwt_required()
def services_by_type():
    rows = db.session.query(Service.service_type, func.count(Service.id))\
                     .group_by(Service.service_type)\
                     .order_by(Service.service_type).all()
    return jsonify([{'service_type': t, 'count': c} for t, c in rows])

@reports_bp.get('/referrals')
@jwt_required()
def referrals():
    rows = db.session.query(
        func.coalesce(Employer.name, Provider.name).label('org_name'),
        case((Referral.employer_id.isnot(None), 'employer'), else_='provider').label('kind'),
        Referral.status.label('status'),
        func.count(Referral.id).label('count')
    ).outerjoin(Employer, Referral.employer_id == Employer.id
    ).outerjoin(Provider, Referral.provider_id == Provider.id
    ).group_by('org_name', 'kind', Referral.status
    ).order_by('org_name').all()
    return jsonify([{'org_name': n, 'kind': k, 'status': s, 'count': c} for n, k, s, c in rows])
