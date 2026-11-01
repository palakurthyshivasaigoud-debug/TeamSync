import pytest


class TestUserRegistration:
    def test_register_success(self, client):
        response = client.post("/api/auth/register", json={
            "name": "Alice Dev",
            "email": "alice@teamsync.test",
            "password": "securepassword",
            "role": "developer",
        })
        assert response.status_code == 201
        data = response.get_json()
        assert "user" in data
        assert data["user"]["email"] == "alice@teamsync.test"
        assert data["user"]["role"] == "developer"

    def test_register_duplicate_email(self, client):
        client.post("/api/auth/register", json={
            "name": "Bob Dev", "email": "bob@teamsync.test",
            "password": "password", "role": "developer",
        })
        response = client.post("/api/auth/register", json={
            "name": "Bob Dev2", "email": "bob@teamsync.test",
            "password": "password2", "role": "developer",
        })
        assert response.status_code == 409
        assert "error" in response.get_json()

    def test_register_missing_fields(self, client):
        response = client.post("/api/auth/register", json={"name": "Incomplete"})
        assert response.status_code == 400


class TestUserLogin:
    def test_login_success(self, client):
        client.post("/api/auth/register", json={
            "name": "Carol Login", "email": "carol@teamsync.test",
            "password": "mypassword", "role": "developer",
        })
        response = client.post("/api/auth/login", json={
            "email": "carol@teamsync.test", "password": "mypassword",
        })
        assert response.status_code == 200
        data = response.get_json()
        assert "user" in data
        assert data["user"]["name"] == "Carol Login"

    def test_login_wrong_password(self, client):
        client.post("/api/auth/register", json={
            "name": "Dave Dev", "email": "dave@teamsync.test",
            "password": "correctpassword", "role": "developer",
        })
        response = client.post("/api/auth/login", json={
            "email": "dave@teamsync.test", "password": "wrongpassword",
        })
        assert response.status_code == 401

    def test_login_nonexistent_email(self, client):
        response = client.post("/api/auth/login", json={
            "email": "nobody@teamsync.test", "password": "anypassword",
        })
        assert response.status_code == 401

    def test_logout(self, client):
        response = client.post("/api/auth/logout")
        assert response.status_code == 200


class TestHealthEndpoint:
    def test_health_check(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "ok"
        assert data["app"] == "TeamSync API"
