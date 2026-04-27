import pytest


class TestRegister:
    def test_register_first_user_becomes_admin(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "first@example.com",
                "username": "firstuser",
                "password": "FirstPass1",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["role"] == "admin"
        assert data["email"] == "first@example.com"
        assert data["username"] == "firstuser"
        assert "hashed_password" not in data

    def test_register_second_user_gets_user_role(self, client, admin_user):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "second@example.com",
                "username": "seconduser",
                "password": "SecondPass1",
            },
        )
        assert response.status_code == 201
        assert response.json()["role"] == "user"

    def test_register_duplicate_email(self, client, admin_user):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "admin@example.com",
                "username": "otherusername",
                "password": "OtherPass1",
            },
        )
        assert response.status_code == 409

    def test_register_duplicate_username(self, client, admin_user):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "other@example.com",
                "username": "admin",
                "password": "OtherPass1",
            },
        )
        assert response.status_code == 409

    def test_register_weak_password(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "weak",
            },
        )
        assert response.status_code == 422

    def test_register_password_no_uppercase(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "nouppercase1",
            },
        )
        assert response.status_code == 422

    def test_register_invalid_email(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "username": "testuser",
                "password": "ValidPass1",
            },
        )
        assert response.status_code == 422


class TestLogin:
    def test_login_success(self, client, admin_user):
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "AdminPass1"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, admin_user):
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "WrongPassword1"},
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "ghost", "password": "GhostPass1"},
        )
        assert response.status_code == 401


class TestGetMe:
    def test_get_me_authenticated(self, client, admin_headers):
        response = client.get("/api/v1/auth/me", headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["username"] == "admin"

    def test_get_me_no_token(self, client):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 403

    def test_get_me_invalid_token(self, client):
        response = client.get(
            "/api/v1/auth/me", headers={"Authorization": "Bearer invalidtoken"}
        )
        assert response.status_code == 401
