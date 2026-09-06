from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

def role_required(*roles):
    """
    Decorator to restrict route access to specific roles.
    Assumes identity is stored as a dictionary containing user details including 'role'.
    Example identity: {'id': 1, 'username': 'admin', 'role': 'Admin'}
    """
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            identity = get_jwt_identity()
            
            # Parse identity JSON string if serialized
            if isinstance(identity, str):
                import json
                try:
                    identity = json.loads(identity)
                except Exception:
                    pass
            
            if not identity or not isinstance(identity, dict) or 'role' not in identity:
                return jsonify({
                    "success": False,
                    "error": "Unauthorized",
                    "message": "Token claims are invalid or incomplete."
                }), 401
                
            user_role = identity.get('role')
            if user_role not in roles:
                return jsonify({
                    "success": False,
                    "error": "Forbidden",
                    "message": f"Access denied. User role '{user_role}' is not authorized for this resource."
                }), 403
                
            return fn(*args, **kwargs)
        return wrapper
    return decorator
