import pytest


class TestCategories:
    def test_create_category(self, client, admin_headers):
        response = client.post(
            "/api/v1/categories/",
            json={"name": "Tools", "description": "Hand and power tools"},
            headers=admin_headers,
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Tools"

    def test_user_cannot_create_category(self, client, user_headers):
        response = client.post(
            "/api/v1/categories/",
            json={"name": "Unauthorized"},
            headers=user_headers,
        )
        assert response.status_code == 403

    def test_duplicate_category_rejected(self, client, admin_headers, sample_category):
        response = client.post(
            "/api/v1/categories/",
            json={"name": "Electronics"},
            headers=admin_headers,
        )
        assert response.status_code == 409

    def test_list_categories(self, client, user_headers, sample_category):
        response = client.get("/api/v1/categories/", headers=user_headers)
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_update_category(self, client, admin_headers, sample_category):
        response = client.patch(
            f"/api/v1/categories/{sample_category['id']}",
            json={"description": "Updated description"},
            headers=admin_headers,
        )
        assert response.status_code == 200
        assert response.json()["description"] == "Updated description"

    def test_delete_category(self, client, admin_headers, sample_category):
        response = client.delete(
            f"/api/v1/categories/{sample_category['id']}",
            headers=admin_headers,
        )
        assert response.status_code == 204

    def test_get_nonexistent_category(self, client, user_headers):
        response = client.get("/api/v1/categories/99999", headers=user_headers)
        assert response.status_code == 404


class TestUsers:
    def test_admin_lists_users(self, client, admin_headers, regular_user):
        response = client.get("/api/v1/users/", headers=admin_headers)
        assert response.status_code == 200
        assert len(response.json()) == 2  # admin + regular

    def test_user_cannot_list_all_users(self, client, user_headers):
        response = client.get("/api/v1/users/", headers=user_headers)
        assert response.status_code == 403

    def test_user_can_view_own_profile(self, client, user_headers, regular_user):
        user_id = regular_user["id"]
        response = client.get(f"/api/v1/users/{user_id}", headers=user_headers)
        assert response.status_code == 200

    def test_user_cannot_view_others_profile(self, client, user_headers, admin_user):
        admin_id = admin_user["id"]
        response = client.get(f"/api/v1/users/{admin_id}", headers=user_headers)
        assert response.status_code == 403

    def test_admin_can_change_user_role(self, client, admin_headers, regular_user):
        user_id = regular_user["id"]
        response = client.patch(
            f"/api/v1/users/{user_id}/role",
            json={"role": "admin"},
            headers=admin_headers,
        )
        assert response.status_code == 200
        assert response.json()["role"] == "admin"

    def test_admin_cannot_change_own_role(self, client, admin_headers, admin_user):
        response = client.patch(
            f"/api/v1/users/{admin_user['id']}/role",
            json={"role": "user"},
            headers=admin_headers,
        )
        assert response.status_code == 403

    def test_deactivate_user(self, client, admin_headers, regular_user):
        response = client.delete(
            f"/api/v1/users/{regular_user['id']}",
            headers=admin_headers,
        )
        assert response.status_code == 204

    def test_deactivated_user_cannot_login(self, client, admin_headers, regular_user):
        client.delete(
            f"/api/v1/users/{regular_user['id']}",
            headers=admin_headers,
        )
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "regularuser", "password": "UserPass1"},
        )
        assert response.status_code == 401
