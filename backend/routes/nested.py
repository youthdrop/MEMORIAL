from flask import Blueprint, request, jsonify
from ..models import db, CaseNote, Service, Assessment, Employment, Education, Milestone, Referral, Employer, Provider
from flask_jwt_extended import get_jwt, jwt_required

bp_nested = Blueprint('nested', __name__, url_prefix='/api/v1/participants/<int:pid>')

@bp_nested.get('/casenotes')
@jwt_required()
def list_casenotes(pid):
    rows = CaseNote.query.filter_by(participant_id=pid).order_by(CaseNote.created_at.desc()).limit(200).all()
    return jsonify([{'id': r.id, 'content': r.content, 'staff_id': r.staff_id, 'created_at': r.created_at.isoformat()} for r in rows])

@bp_nested.post('/casenotes')
@jwt_required()
def add_casenote(pid):
    d = request.get_json() or {}
    sub = get_jwt().get('sub')
    note = CaseNote(participant_id=pid, staff_id=sub, content=d.get('content'))
    db.session.add(note); db.session.commit(); return jsonify({'id': note.id}), 201

@bp_nested.get('/services')
@jwt_required()
def list_services(pid):
    rows = Service.query.filter_by(participant_id=pid).order_by(Service.provided_at.desc()).limit(200).all()
    return jsonify([{'id': r.id, 'service_type': r.service_type, 'note': r.note, 'staff_id': r.staff_id, 'provided_at': r.provided_at.isoformat()} for r in rows])

@bp_nested.post('/services')
@jwt_required()
def add_service(pid):
    d = request.get_json() or {}
    sub = get_jwt().get('sub')
    svc = Service(participant_id=pid, staff_id=sub, service_type=d.get('service_type'), note=d.get('note'))
    db.session.add(svc); db.session.commit(); return jsonify({'id': svc.id}), 201

@bp_nested.post('/assessments')
@jwt_required()
def add_assessment(pid):
    d = request.get_json() or {}
    sub = get_jwt().get('sub')
    asm = Assessment(participant_id=pid, staff_id=sub, assessment_type=d.get('assessment_type'), score_json=d.get('score_json'))
    db.session.add(asm); db.session.commit(); return jsonify({'id': asm.id}), 201

@bp_nested.post('/employment')
@jwt_required()
def add_employment(pid):
    d = request.get_json() or {}
    emp = Employment(participant_id=pid, employer_name=d.get('employer_name'), job_title=d.get('job_title'))
    db.session.add(emp); db.session.commit(); return jsonify({'id': emp.id}), 201

@bp_nested.post('/education')
@jwt_required()
def add_education(pid):
    d = request.get_json() or {}
    edu = Education(participant_id=pid, school_name=d.get('school_name'), program=d.get('program'))
    db.session.add(edu); db.session.commit(); return jsonify({'id': edu.id}), 201

@bp_nested.post('/milestones')
@jwt_required()
def add_milestone(pid):
    d = request.get_json() or {}
    sub = get_jwt().get('sub')
    m = Milestone(participant_id=pid, staff_id=sub, type=d.get('type'), status=d.get('status'), note=d.get('note'))
    db.session.add(m); db.session.commit(); return jsonify({'id': m.id}), 201

@bp_nested.get('/referrals')
@jwt_required()
def list_referrals(pid):
    rows = Referral.query.filter_by(participant_id=pid).order_by(Referral.referred_at.desc()).all()
    out = []
    for r in rows:
        name = None
        kind = None
        if r.employer_id:
            e = Employer.query.get(r.employer_id)
            name = e.name if e else None
            kind = 'employer'
        if r.provider_id:
            p = Provider.query.get(r.provider_id)
            name = p.name if p else name
            kind = 'provider' if kind is None else kind
        out.append({'id': r.id, 'kind': kind, 'org_id': r.employer_id or r.provider_id, 'org_name': name, 'status': r.status, 'note': r.note, 'referred_at': r.referred_at.isoformat()})
    return jsonify(out)

@bp_nested.post('/referrals')
@jwt_required()
def add_referral(pid):
    d = request.get_json() or {}
    sub = get_jwt().get('sub')
    kind = d.get('kind')
    org_id = d.get('org_id')
    if kind not in ('employer','provider'):
        return jsonify({'msg':'invalid kind'}), 400
    ref = Referral(participant_id=pid, staff_id=sub, employer_id=org_id if kind=='employer' else None, provider_id=org_id if kind=='provider' else None, status=d.get('status','referred'), note=d.get('note'))
    db.session.add(ref); db.session.commit(); return jsonify({'id': ref.id}), 201

@bp_nested.patch('/referrals/<int:rid>')
@jwt_required()
def update_referral(pid, rid):
    r = Referral.query.filter_by(id=rid, participant_id=pid).first_or_404()
    d = request.get_json() or {}
    if 'status' in d: r.status = d['status']
    if 'note' in d: r.note = d['note']
    db.session.commit(); return jsonify({'msg':'updated'})
