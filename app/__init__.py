from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bcrypt.init_app(app)

    login.login_view = 'auth.login'
    login.login_message = "Please, authorize first."

    from app.auth.routes import auth_bp
    from app.main.routes import main_bp
    from app.admin.routes import admin_bp
    from app.mentor.routes import mentor_bp
    from app.mentor.material import material_bp
    from app.intern.routes import intern_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(mentor_bp)
    app.register_blueprint(material_bp)
    app.register_blueprint(intern_bp)

    return app
