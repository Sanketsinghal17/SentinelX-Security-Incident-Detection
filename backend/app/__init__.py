import os
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from app.config import Config
from app.db import init_db, get_db, SessionLocal
from app.services.seeder import seed_database
from app.routes import (
    auth_bp, dashboard_bp, log_bp, incident_bp,
    simulation_bp, threat_bp, analytics_bp, report_bp
)

def create_app(config_class=Config):
    frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
    assets_dir = os.path.join(frontend_dist, "assets")

    app = Flask(
        __name__,
        static_folder=assets_dir if os.path.exists(assets_dir) else None,
        static_url_path="/assets"
    )
    app.config.from_object(config_class)

    # Enable CORS for frontend Vite dev server (port 5173) and any origin
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # Ensure required runtime directories exist
    os.makedirs(app.config["REPORTS_DIR"], exist_ok=True)
    os.makedirs(app.config["SAMPLE_DATA_DIR"], exist_ok=True)

    # Register API blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(log_bp)
    app.register_blueprint(incident_bp)
    app.register_blueprint(simulation_bp)
    app.register_blueprint(threat_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(report_bp)

    # Database initialization and seeder
    with app.app_context():
        init_db()
        db = get_db()
        seed_database(db)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        SessionLocal.remove()

    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "online",
            "service": "SentinelX SOC Engine",
            "version": "2.4.0-enterprise",
            "database": "SQLite (Connected)"
        })

    # Root route and SPA Catch-All fallback for React Router
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_spa(path):
        # Do not intercept API requests
        if path.startswith("api/") or path == "api":
            return jsonify({"error": "API route not found"}), 404

        if os.path.exists(frontend_dist):
            # If a specific static file was requested and exists (e.g. favicon, robots.txt)
            target_file = os.path.join(frontend_dist, path)
            if path and os.path.isfile(target_file):
                return send_from_directory(frontend_dist, path)

            # Serve index.html for React SPA root and client-side routes (/login, /incidents, etc.)
            index_file = os.path.join(frontend_dist, "index.html")
            if os.path.exists(index_file):
                return send_from_directory(frontend_dist, "index.html")

        return jsonify({
            "message": "SentinelX SOC Backend is running. Frontend build not detected in frontend/dist. Please run 'npm run build'."
        }), 404

    @app.errorhandler(404)
    def not_found(e):
        # Return JSON error for missing API routes
        if request.path.startswith("/api/"):
            return jsonify({"error": "API endpoint not found"}), 404

        # For browser page requests, return index.html to allow React Router to handle
        index_file = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_file):
            return send_from_directory(frontend_dist, "index.html")

        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Internal server error occurred"}), 500

    return app
