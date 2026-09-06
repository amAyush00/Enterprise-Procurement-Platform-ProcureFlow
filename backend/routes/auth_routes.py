from flask import Blueprint
from backend.controllers.auth_controller import AuthController

auth_bp = Blueprint('auth', __name__)

# Register auth routes
auth_bp.route('/login', methods=['POST'])(AuthController.login)
auth_bp.route('/logout', methods=['POST'])(AuthController.logout)
auth_bp.route('/refresh', methods=['POST'])(AuthController.refresh)
