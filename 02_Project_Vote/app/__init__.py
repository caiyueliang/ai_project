import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from .config import load_config

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    load_config(app)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"

    from .models import User  # noqa: F401

    @login_manager.user_loader
    def load_user(user_id: str):
        from .models import User

        return User.query.get(int(user_id))

    from .routes.auth import bp as auth_bp
    from .routes.polls import bp as polls_bp
    from .routes.main import bp as main_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(polls_bp, url_prefix="/polls")
    app.register_blueprint(main_bp)

    _configure_logging(app)
    _ensure_dirs(app)

    with app.app_context():
        db.create_all()

    return app


def _configure_logging(app: Flask) -> None:
    log_dir = Path(app.config.get("LOG_DIR", "logs"))
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(log_dir / "app.log", maxBytes=1_000_000, backupCount=3)
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)


def _ensure_dirs(app: Flask) -> None:
    Path(app.static_folder).mkdir(parents=True, exist_ok=True)
    Path(app.template_folder).mkdir(parents=True, exist_ok=True)
