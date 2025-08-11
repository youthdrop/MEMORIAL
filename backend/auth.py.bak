from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token
from models import db, User

bcrypt = Bcrypt()
jwt = JWTManager()

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth_bp.post('/login')
def login():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({'msg': 'Bad credentials'}), 401

    token = create_access_token(
        identity=str(user.id),  # subject must be a STRING
        additional_claims={'role': user.role, 'name': user.name}
    )
    return jsonify({'access_token': token, 'user': {'id': user.id, 'name': user.name, 'role': user.role}})
