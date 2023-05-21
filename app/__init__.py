from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin

from config import Config
from app.user import User

app = Flask(__name__)

db = SQLAlchemy()
migrate = Migrate()

login_manager = LoginManager()
login_manager.login_view = 'login'




@login_manager.user_loader
def load_user(user_id):
    # return User object or None
    if user_id == 'eadmin':
        return User(user_id, 'ChangePass88!')   # change to your password
    return None

def create_app(config_class=Config):
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)

    # login.init_app(app)

    # from app.errors import bp as errors_bp
    # app.register_blueprint(errors_bp)

    # from app.auth import bp as auth_bp
    # app.register_blueprint(auth_bp, url_prefix='/auth')

    # from app.main import bp as main_bp
    # app.register_blueprint(main_bp)
    # app.register_blueprint(routes.app)
    return app


from app import routes, models
