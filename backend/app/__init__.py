from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from .config import Config
from .models import db
from .schemas import ma
import logging
from logging.handlers import RotatingFileHandler
import os
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    jwt = JWTManager(app)
    CORS(app)

    # Logging Configuration
    # (Disabled file-based logging for Vercel compatibility)
    app.logger.setLevel(logging.INFO)
    app.logger.info('AgroSaaS API Startup (Vercel Optimized)')

    # Register Blueprints
    from .api.auth import auth_bp
    from .api.yield_bp import yield_bp
    from .api.pest import pest_bp
    from .api.sensors import sensors_bp
    from .api.history import history_bp
    from .api.home import home_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    app.register_blueprint(yield_bp, url_prefix='/api/yield')
    app.register_blueprint(pest_bp, url_prefix='/api/pest')
    app.register_blueprint(sensors_bp, url_prefix='/api/sensors')
    app.register_blueprint(history_bp, url_prefix='/api/history')

    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f"404 Not Found: {request.url}")
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f"500 Internal Error on {request.url}: {str(error)}")
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Global fallback error handler
        app.logger.error(f"Unhandled Exception: {str(e)}", exc_info=True)
        return jsonify({
            "error": "An unexpected error occurred",
            "message": str(e) if app.debug else "Please contact support if the issue persists."
        }), 500

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "The token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"error": "Signature verification failed"}), 401

    # Request Logging Middleware
    @app.before_request
    def log_request_info():
        # Avoid logging metrics endpoint excessively
        if request.path != '/metrics' and request.path != '/health':
            app.logger.info(f"[{request.method}] {request.url} - IP: {request.remote_addr}")

    @app.route('/health')
    def health_check():
        """Hardened Health check endpoint for Render zero-downtime deployment."""
        from .utils.weather import weather_service
        is_mock_ai = os.environ.get("RENDER") == "1" or os.environ.get("VERCEL") == "1" or os.environ.get("USE_MOCK_AI") == "1"
        
        status = {
            "status": "ok",
            "ai": "mock" if is_mock_ai else "active",
            "db": "disconnected",
            "cache": "redis" if weather_service.redis is not None else "in-memory"
        }
        
        try:
            # Check DB connection using text format safely
            db.session.execute(db.text('SELECT 1'))
            status["db"] = "connected"
        except Exception as e:
            status["db"] = "disconnected"
            status["status"] = "degraded"
            app.logger.error(f"Health check DB error (transient drop): {e}")
            
        return jsonify(status), 200 if status["status"] == "ok" else 503

    @app.route('/metrics')
    def metrics():
        return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

    return app

