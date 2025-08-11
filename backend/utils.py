from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt
from flask import jsonify
def roles_required(*roles):
    def deco(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if claims.get('role') not in roles:
                return jsonify({'msg': 'Forbidden'}), 403
            return fn(*args, **kwargs)
        return wrapper
    return deco
