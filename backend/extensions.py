from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt  # type: ignore[import-untyped]
from flask_login import LoginManager

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
