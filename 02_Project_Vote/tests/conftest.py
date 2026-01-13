import os
import tempfile
import pytest
from app import create_app, db


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    os.environ["SECRET_KEY"] = "test-secret"
    os.environ["WTF_CSRF_ENABLED"] = "false"
    application = create_app()
    with application.app_context():
        db.create_all()
    yield application
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
