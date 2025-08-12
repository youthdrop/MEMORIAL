# inside backend/app.py (after create_app(), put these inside the function)
@app.get('/api/participants/<int:pid>/notes')
@jwt_required()
def list_notes(pid):
    Participant.query.get_or_404(pid)
    return jsonify([]), 200

@app.post('/api/participants/<int:pid>/notes')
@jwt_required()
def create_note(pid):
    Participant.query.get_or_404(pid)
    data = request.get_json() or {}
    content = (data.get('content') or '').strip()
    if not content:
        return jsonify({'msg':'content is required'}), 400
    # TODO: save to DB with CaseNote(...)
    return jsonify({'msg':'created','id': None}), 201

@app.get('/api/participants/<int:pid>/services')
@jwt_required()
def list_services(pid):
    Participant.query.get_or_404(pid)
    return jsonify([]), 200

@app.post('/api/participants/<int:pid>/services')
@jwt_required()
def create_service(pid):
    Participant.query.get_or_404(pid)
    data = request.get_json() or {}
    service_type = (data.get('service_type') or '').strip()
    if not service_type:
        return jsonify({'msg':'service_type is required'}), 400
    # TODO: save to DB with Service(...)
    return jsonify({'msg':'created','id': None}), 201

@app.get('/api/participants/<int:pid>/referrals')
@jwt_required()
def list_referrals(pid):
    Participant.query.get_or_404(pid)
    return jsonify([]), 200

@app.post('/api/participants/<int:pid>/referrals')
@jwt_required()
def create_referral(pid):
    Participant.query.get_or_404(pid)
    data = request.get_json() or {}
    if not data.get('org_id'):
        return jsonify({'msg':'org_id is required'}), 400
    # TODO: save to DB with Referral(...)
    return jsonify({'msg':'created','id': None}), 201
