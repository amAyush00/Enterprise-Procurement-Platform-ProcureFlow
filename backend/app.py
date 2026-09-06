from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from backend.config.settings import Config

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    
    # Enable CORS for frontend communications
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # Deferred imports to avoid circular dependencies in blueprints
    from backend.routes.auth_routes import auth_bp
    from backend.routes.vendor_routes import vendor_bp
    from backend.routes.product_routes import product_bp
    from backend.routes.inventory_routes import inventory_bp
    from backend.routes.purchase_request_routes import pr_bp
    from backend.routes.purchase_order_routes import po_bp
    from backend.routes.report_routes import report_bp
    from backend.routes.analytics_routes import analytics_bp

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(vendor_bp, url_prefix='/api/vendors')
    app.register_blueprint(product_bp, url_prefix='/api/products')
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    app.register_blueprint(pr_bp, url_prefix='/api/purchase-requests')
    app.register_blueprint(po_bp, url_prefix='/api/purchase-orders')
    app.register_blueprint(report_bp, url_prefix='/api/reports')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')

    # JWT Error Callbacks Customization for API Consistency
    @jwt.unauthorized_loader
    def unauthorized_callback(err_str):
        return jsonify({
            "success": False,
            "error": "Unauthorized",
            "message": err_str
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(err_str):
        return jsonify({
            "success": False,
            "error": "Unauthorized",
            "message": "Signature verification failed: " + err_str
        }), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "success": False,
            "error": "Unauthorized",
            "message": "The token has expired."
        }), 401

    # Global Error Handling
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False, 
            "error": "Bad Request", 
            "message": getattr(error, 'description', str(error))
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            "success": False, 
            "error": "Unauthorized", 
            "message": getattr(error, 'description', str(error))
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            "success": False, 
            "error": "Forbidden", 
            "message": getattr(error, 'description', str(error))
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False, 
            "error": "Not Found", 
            "message": getattr(error, 'description', str(error))
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({
            "success": False, 
            "error": "Internal Server Error", 
            "message": "An unexpected error occurred on the server."
        }), 500

    return app
