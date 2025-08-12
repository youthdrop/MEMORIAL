import requests
from flask import Blueprint, request, jsonify
bp_geo = Blueprint("geo", __name__)
@bp_geo.route("/addresses", methods=["GET","OPTIONS"])
def addresses():
    if request.method == "OPTIONS":
        return ("", 204)
    q = (request.args.get("q") or "").strip()
    if not q:
        return jsonify([])
    r = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"format":"json","q":q,"addressdetails":1,"limit":5},
        headers={"User-Agent":"memorial-app/1.0"},
        timeout=8
    )
    r.raise_for_status()
    data = r.json()
    return jsonify([
        {"label": d.get("display_name"), "lat": d.get("lat"), "lon": d.get("lon")}
        for d in data
    ])
