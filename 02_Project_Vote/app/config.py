import os
from typing import Any
from flask import Flask
from dotenv import load_dotenv


def load_config(app: Flask) -> None:
    load_dotenv()
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///vote.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["LOG_DIR"] = os.getenv("LOG_DIR", "logs")
    app.config["WTF_CSRF_TIME_LIMIT"] = None
    app.config["WTF_CSRF_ENABLED"] = os.getenv("WTF_CSRF_ENABLED", "true").lower() != "false"
    app.config["MAX_CHOICES_PER_POLL"] = int(os.getenv("MAX_CHOICES_PER_POLL", "10"))
    app.config["VOTE_COOLDOWN_SECONDS"] = int(os.getenv("VOTE_COOLDOWN_SECONDS", "30"))
    app.config["SECURITY_LOG_SENSITIVE"] = True


def get_config(app: Flask, key: str, default: Any = None) -> Any:
    return app.config.get(key, default)
