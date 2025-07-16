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

def create_app():
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

    return app
