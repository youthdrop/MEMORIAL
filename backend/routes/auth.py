from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from datetime import timedelta

bp_auth = Blueprint("auth", __name__)

@bp_auth.route("/login", methods=["POST", "OPTIONS"])
def login():
    # Allow CORS preflight
    if request.method == "OPTIONS":
        return ("", 204)

    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    token = create_access_token(identity=email, expires_delta=timedelta(hours=8))
    return jsonify({"access_token": token})
