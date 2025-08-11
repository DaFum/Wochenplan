from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

from .modules.content_library import ContentLibrary
from .modules.task_manager import TaskManager
from .modules.ical_exporter import ICalExporter
from .modules.notification_service import NotificationService

def create_app():
    """
    Erstellt und konfiguriert eine Flask-Anwendung mit Datenbank, Migrationen, CSRF-Schutz und Ratenbegrenzung.
    
    Die Anwendung lädt Konfigurationen aus Umgebungsvariablen, initialisiert Erweiterungen und registriert Blueprints für Haupt-, API- und Exportfunktionen.
    
    Returns:
        app (Flask): Die vollständig konfigurierte Flask-Anwendung.
    """
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.secret_key = os.getenv('SECRET_KEY')
    if not app.secret_key:
        raise ValueError("No SECRET_KEY set for Flask application")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URI', 'sqlite:///planner.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    limiter.init_app(app)

    with app.app_context():
        from .main import routes as main_routes
        from .api import api_bp
        from .exports import exports_bp

        app.register_blueprint(main_routes.main_bp)
        app.register_blueprint(api_bp, url_prefix='/api')
        app.register_blueprint(exports_bp)

        app.content_library = ContentLibrary()
        app.task_manager = TaskManager()
        app.ical_exporter = ICalExporter()
        app.notification_service = NotificationService()

    return app
