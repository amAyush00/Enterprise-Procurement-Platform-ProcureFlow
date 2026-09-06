from flask_jwt_extended import create_access_token, create_refresh_token
from backend.models.user import User

class AuthService:
    @staticmethod
    def authenticate_user(username_or_email, password):
        """
        Authenticate user by username or email.
        Returns tokens and user info dictionary on success, or None on failure.
        """
        # Look up user by username or email
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        # Check if user exists and is active
        if not user or user.status != 'ACTIVE':
            return None

        # Check password hash
        if not user.check_password(password):
            return None

        # Prepare identity claim for JWT
        # Store user ID, username, and role in token to avoid db queries on every request
        identity = {
            'id': user.id,
            'username': user.username,
            'role': user.role.name if user.role else 'Employee'
        }

        import json
        identity_str = json.dumps(identity)
        access_token = create_access_token(identity=identity_str)
        refresh_token = create_refresh_token(identity=identity_str)

        return {
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }
