import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import create_app
from backend.extensions import db as _db


@pytest.fixture(scope="session")
def app():
    """Create Flask app for testing."""
    import tempfile
    db_fd, db_path = tempfile.mkstemp()

    test_app = create_app()
    test_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key",
    })

    with test_app.app_context():
        _db.create_all()
        yield test_app
        _db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def auth_headers(client):
    """Get auth headers for test user."""
    # Register test user
    client.post("/api/auth/register", json={
        "name": "Test User",
        "email": "test@teamsync.test",
        "password": "testpassword123",
        "role": "admin",
    })
    # Login
    resp = client.post("/api/auth/login", json={
        "email": "test@teamsync.test",
        "password": "testpassword123",
    })
    return {"Content-Type": "application/json"}
