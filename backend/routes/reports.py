from flask import Blueprint, request, jsonify, Response
from datetime import datetime, timedelta
import csv
from io import StringIO

try:
    from ..models import db, Participant, CaseNote, Service, Referral, Employer, Provider
except ImportError:
    from models import db, Participant, CaseNote, Service, Referral, Employer, Provider

bp_reports = Blueprint("reports", __name__)

# ---- date parsing helpers ----------------------------------------------------
def _parse_date(s, default=None):
    if not s:
        return default
    try:
        # support 'YYYY-MM-DD' or full ISO strings
        return datetime.fromisoformat(s).replace(tzinfo=None)
    except Exception:
        return default

def _range():
    now = datetime.utcnow()
    date_to = _parse_date(request.args.get("to"), now)
    date_from = _parse_date(request.args.get("from"), date_to - timedelta(days=90))
    # clamp to day boundaries
    start = datetime(date_from.year, date_from.month, date_from.day)
    end = datetime(date_to.year, date_to.month, date_to.day, 23, 59, 59)
    return start, end

def _csv_response(filename, rows, headers):
    sio = StringIO()
    writer = csv.writer(sio)
    writer.writerow(headers)
    for r in rows:
        writer.writerow(r)
    out = sio.getvalue()
    return Response(out, mimetype="text/csv",
                    headers={"Content-Disposition": f'attachment; filename="{filename}"'})

# ---- summary (multiple paths supported) -------------------------------------
def _summary_payload(start, end):
    def between(col):
        return (col >= start) & (col <= end)

    # counts with defensive defaults
    p_count = db.session.query(db.func.count(Participant.id)) \
        .filter(between(Participant.created_at)).scalar() or 0

    notes_count = db.session.query(db.func.count(CaseNote.id)) \
        .filter(between(CaseNote.created_at)).scalar() or 0

    svc_count = db.session.query(db.func.count(Service.id)) \
        .filter(between(Service.provided_at)).scalar() or 0

    ref_count = db.session.query(db.func.count(Referral.id)) \
        .filter(between(Referral.referred_at)).scalar() or 0

    emp_count = db.session.query(db.func.count(Employer.id)).scalar() or 0
    prov_count = db.session.query(db.func.count(Provider.id)).scalar() or 0

    return {
        "range": {"from": start.date().isoformat(), "to": end.date().isoformat()},
        "totals": {
            "participants": p_count,
            "case_notes": notes_count,
            "services": svc_count,
            "referrals": ref_count,
            "employers": emp_count,
            "providers": prov_count,
        },
    }

@bp_reports.route("/report", methods=["GET", "OPTIONS"])
@bp_reports.route("/reports", methods=["GET", "OPTIONS"])
@bp_reports.route("/reports/summary", methods=["GET", "OPTIONS"])
def summary():
    if request.method == "OPTIONS":
        return ("", 204)
    try:
        start, end = _range()
        return jsonify(_summary_payload(start, end))
    except Exception as e:
        return jsonify({"error": "summary_failed", "detail": str(e)}), 400

# ---- participants: JSON + CSV ------------------------------------------------
@bp_reports.route("/reports/participants", methods=["GET", "OPTIONS"])
def participants_json():
    if request.method == "OPTIONS":
        return ("", 204)
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
        rows.append({
            "id": pid,
            "first_name": fn or "",
            "last_name": ln or "",
            "dob": dob.isoformat() if dob else None,
            "race": race or "",
            "address": addr or "",
            "email": email or "",
            "phone": phone or "",
            "created_at": created.isoformat() if created else None,
        })
    return jsonify(rows)

@bp_reports.route("/reports/participants.csv", methods=["GET", "OPTIONS"])
def participants_csv():
    if request.method == "OPTIONS":
        return ("", 204)
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

# ---- services: JSON + CSV (joined with participant name) ---------------------
@bp_reports.route("/reports/services", methods=["GET", "OPTIONS"])
def services_json():
    if request.method == "OPTIONS":
        return ("", 204)
    start, end = _range()
    q = (db.session.query(
            Service.id, Service.participant_id, Service.service_type,
            Service.note, Service.staff_id, Service.provided_at,
            Participant.first_name, Participant.last_name
        )
        .join(Participant, Participant.id == Service.participant_id)
        .filter((Service.provided_at >= start) & (Service.provided_at <= end))
        .order_by(Service.provided_at.desc()))
    out = []
    for (sid, pid, stype, note, staff_id, provided_at, fn, ln) in q.all():
        out.append({
            "id": sid,
            "participant_id": pid,
            "service_type": stype or "",
            "note": (note or "").strip(),
            "staff_id": staff_id,
            "provided_at": provided_at.isoformat() if provided_at else None,
            "participant_name": f"{(fn or '').strip()} {(ln or '').strip()}".strip(),
        })
    return jsonify(out)

@bp_reports.route("/reports/services.csv", methods=["GET", "OPTIONS"])
def services_csv():
    if request.method == "OPTIONS":
        return ("", 204)
    start, end = _range()
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
            f"{(fn or '').strip()} {(ln or '').strip()}".strip()
        ])
    return _csv_response("services.csv",
                         rows,
                         ["id","participant_id","service_type","note","staff_id","provided_at","participant_name"])
