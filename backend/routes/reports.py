from flask import Blueprint, request, jsonify, Response
from datetime import datetime, timedelta
import csv
from io import StringIO

try:
    from ..models import db, Participant, CaseNote, Service, Referral, Employer, Provider
except ImportError:
    from models import db, Participant, CaseNote, Service, Referral, Employer, Provider

bp_reports = Blueprint("reports", __name__)

def _parse_date(s, default=None):
    if not s:
        return default
    try:
        # support 'YYYY-MM-DD' or full ISO
        return datetime.fromisoformat(s).replace(tzinfo=None)
    except Exception:
        return default

def _range():
    # default: last 90 days
    now = datetime.utcnow()
    date_to = _parse_date(request.args.get("to"), now)
    date_from = _parse_date(request.args.get("from"), date_to - timedelta(days=90))
    # normalize to midnight boundaries
    start = datetime(date_from.year, date_from.month, date_from.day)
    end = datetime(date_to.year, date_to.month, date_to.day, 23, 59, 59)
    return start, end

@bp_reports.get("/reports/summary")
def summary():
    start, end = _range()

    def between(col):
        return (col >= start) & (col <= end)

    # not every table has the same timestamp/column, so we pick reasonable ones:
    p_count = db.session.query(db.func.count(Participant.id)).filter(
        between(Participant.created_at)
    ).scalar()

    notes_count = db.session.query(db.func.count(CaseNote.id)).filter(
        between(CaseNote.created_at)
    ).scalar()

    svc_count = db.session.query(db.func.count(Service.id)).filter(
        between(Service.provided_at)
    ).scalar()

    ref_count = db.session.query(db.func.count(Referral.id)).filter(
        between(Referral.referred_at)
    ).scalar()

    emp_count = db.session.query(db.func.count(Employer.id)).scalar()
    prov_count = db.session.query(db.func.count(Provider.id)).scalar()

    return jsonify({
        "range": {"from": start.date().isoformat(), "to": end.date().isoformat()},
        "totals": {
            "participants": p_count or 0,
            "case_notes": notes_count or 0,
            "services": svc_count or 0,
            "referrals": ref_count or 0,
            "employers": emp_count or 0,
            "providers": prov_count or 0,
        }
    })

def _csv_response(filename, rows, headers):
    sio = StringIO()
    w = csv.writer(sio)
    w.writerow(headers)
    for r in rows:
        w.writerow(r)
    out = sio.getvalue()
    return Response(
        out,
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@bp_reports.get("/reports/participants.csv")
def participants_csv():
    start, end = _range()
    q = (db.session.query(
            Participant.id, Participant.first_name, Participant.last_name,
            Participant.dob, Participant.race, Participant.address,
            Participant.email, Participant.phone, Participant.created_at
        )
        .filter((Participant.created_at >= start) & (Participant.created_at <= end))
        .order_by(Participant.created_at.desc()))
    rows = []
    for (pid, fn, ln, dob, race, addr, email, phone, created) in q.all():
        rows.append([
            pid, fn or "", ln or "",
            dob.isoformat() if dob else "",
            race or "", addr or "", email or "", phone or "",
            created.isoformat() if created else "",
        ])
    return _csv_response("participants.csv",
                         rows,
                         ["id","first_name","last_name","dob","race","address","email","phone","created_at"])

@bp_reports.get("/reports/services.csv")
def services_csv():
    start, end = _range()
    # join services with participants (no relationship needed)
    q = (db.session.query(
            Service.id, Service.participant_id, Service.service_type,
            Service.note, Service.staff_id, Service.provided_at,
            Participant.first_name, Participant.last_name
        )
        .join(Participant, Participant.id == Service.participant_id)
        .filter((Service.provided_at >= start) & (Service.provided_at <= end))
        .order_by(Service.provided_at.desc()))
    rows = []
    for (sid, pid, stype, note, staff_id, provided_at, fn, ln) in q.all():
        rows.append([
            sid, pid, stype or "", (note or "").replace("\n"," ").strip(),
            staff_id or "", provided_at.isoformat() if provided_at else "",
            f"{fn or ''} {ln or ''}".strip()
        ])
    return _csv_response("services.csv",
                         rows,
                         ["id","participant_id","service_type","note","staff_id","provided_at","participant_name"])
