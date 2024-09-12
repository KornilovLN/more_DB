from flask import Flask
import subprocess
import sys
import flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

    db.init_app(app)
    login_manager.init_app(app)

    from .routes import bp as bp
    app.register_blueprint(bp)

    # Импорт и регистрация Blueprint ===========
    #from questdb.routes import questdb_bp
    #app.register_blueprint(questdb_bp)
    # ==========================================

    with app.app_context():
        db.create_all()

    @app.context_processor
    def inject_versions():
        pip_version = subprocess.check_output(['pip', '--version']).decode('utf-8').split()[1]
        flask_version = flask.__version__
        python_version = sys.version
        return dict(python_version=python_version, pip_version=pip_version, flask_version=flask_version)
        
    return app

@login_manager.user_loader
def load_user(user_id):
    from .models import User  # Импорт модели User внутри функции
    return User.query.get(int(user_id))

