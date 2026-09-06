from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from backend.services.auth_service import AuthService

class AuthController:
    @staticmethod
    def login():
        """
        Handle user login. Expects JSON payload with username/email and password.
        """
        data = request.get_json() or {}
        username = data.get('username') or data.get('email')
        password = data.get('password')

        # Request validations
        if not username or not password:
            return jsonify({
                "success": False,
                "error": "Bad Request",
                "message": "Username/Email and password are required."
            }), 400

        # Authenticate user
        auth_data = AuthService.authenticate_user(username, password)
        if not auth_data:
            return jsonify({
                "success": False,
                "error": "Unauthorized",
                "message": "Invalid credentials or inactive account."
            }), 401

        return jsonify({
            "success": True,
            "message": "Authentication successful.",
            "data": auth_data
        }), 200

    @staticmethod
    def logout():
        """
        Handle user logout. In stateless JWT, the client discards the token.
        We return success response to let the client perform cleanup.
        """
        return jsonify({
            "success": True,
            "message": "Successfully logged out."
        }), 200

    @staticmethod
    @jwt_required(refresh=True)
    def refresh():
        """
        Generate a new access token using a valid refresh token.
        """
        identity = get_jwt_identity()
        new_access_token = create_access_token(identity=identity)
        
        return jsonify({
            "success": True,
            "message": "Access token refreshed successfully.",
            "data": {
                "access_token": new_access_token
            }
        }), 200
