"""Initialisation de l'application Flask."""
import os

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.config.settings import config_by_name

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_name: str | None = None) -> Flask:
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")
        if config_name not in config_by_name:
            config_name = "development"

    app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(__file__), "..", "..", "dashboard", "static"),
        template_folder=os.path.join(os.path.dirname(__file__), "..", "..", "dashboard", "templates"),
    )
    app.config.from_object(config_by_name[config_name])
    app.config.pop('SQLALCHEMY_ENGINE_OPTIONS', None)
    # Forcer la suppression de toute valeur problématique
    

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, origins=app.config["CORS_ORIGINS"], supports_credentials=True)

    # Import des modèles pour Alembic / create_all
    from app import models  # noqa: F401

    # Blueprints API
    from app.routes.auth import auth_bp
    from app.routes.sessions import sessions_bp
    from app.routes.stats import stats_bp
    from app.routes.goals import goals_bp
    from app.routes.challenges import challenges_bp
    from app.routes.dashboard_routes import dashboard_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(sessions_bp, url_prefix="/api/session")
    app.register_blueprint(stats_bp, url_prefix="/api/stats")
    app.register_blueprint(goals_bp, url_prefix="/api/goals")
    app.register_blueprint(challenges_bp, url_prefix="/api/challenges")
    app.register_blueprint(dashboard_bp)

    @app.route("/health")
    def health():
        # Vérification de la connexion à la base de données
        try:
            from sqlalchemy import text
            db.session.execute(text("SELECT 1"))
            return {"status": "ok", "service": "luciole-api", "db": "connected"}, 200
        except Exception as e:
            return {"status": "error", "service": "luciole-api", "db": str(e)}, 500

    @app.route("/dashboard/assets/<path:filename>")
    def dashboard_assets(filename):
        assets_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "dashboard", "assets"
        )
        return send_from_directory(assets_dir, filename)

    # ⚠️ On retire db.create_all() et seed_initial_data() d'ici
    # Elles seront appelées dans run.py avec gestion d'erreur

    return app