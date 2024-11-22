from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.models import db
from app.routes.auth_routes import auth_routes
from app.routes.home_routes import home_routes
from app.routes.song_routes import song_routes

from .config import Config

from app.seeds import seed_commands


app = Flask(__name__)

# Configuration
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

app.cli.add_command(seed_commands)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))

# Register blueprints
app.register_blueprint(auth_routes)
app.register_blueprint(home_routes)
app.register_blueprint(song_routes, url_prefix='/songs')


