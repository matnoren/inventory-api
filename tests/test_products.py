import pytest


class TestProductCreate:
    def test_admin_can_create_product(self, client, admin_headers, sample_category):
        response = client.post(
            "/api/v1/products/",
            json={
                "name": "Gaming Mouse",
                "sku": "MOUSE-001",
                "price": "49.99",
                "stock_quantity": 100,
                "low_stock_threshold": 10,
                "category_id": sample_category["id"],
            },
            headers=admin_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Gaming Mouse"
        assert data["sku"] == "MOUSE-001"
        assert data["stock_quantity"] == 100
        assert data["is_low_stock"] is False

    def test_sku_is_uppercased(self, client, admin_headers):
        response = client.post(
            "/api/v1/products/",
            json={"name": "Test", "sku": "lower-sku", "price": "10.00"},
            headers=admin_headers,
        )
        assert response.status_code == 201
        assert response.json()["sku"] == "LOWER-SKU"

    def test_duplicate_sku_rejected(self, client, admin_headers, sample_product):
        response = client.post(
            "/api/v1/products/",
            json={"name": "Other", "sku": "LAP-001", "price": "5.00"},
            headers=admin_headers,
        )
        assert response.status_code == 409

    def test_user_cannot_create_product(self, client, user_headers):
        response = client.post(
            "/api/v1/products/",
            json={"name": "Test", "sku": "TEST-001", "price": "10.00"},
            headers=user_headers,
        )
        assert response.status_code == 403

    def test_negative_price_rejected(self, client, admin_headers):
        response = client.post(
            "/api/v1/products/",
            json={"name": "Test", "sku": "TEST-002", "price": "-5.00"},
            headers=admin_headers,
        )
        assert response.status_code == 422

    def test_negative_stock_rejected(self, client, admin_headers):
        response = client.post(
            "/api/v1/products/",
            json={"name": "Test", "sku": "TEST-003", "price": "5.00", "stock_quantity": -1},
            headers=admin_headers,
        )
        assert response.status_code == 422


class TestProductRead:
    def test_list_products(self, client, user_headers, sample_product):
        response = client.get("/api/v1/products/", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1

    def test_get_product_by_id(self, client, user_headers, sample_product):
        product_id = sample_product["id"]
        response = client.get(f"/api/v1/products/{product_id}", headers=user_headers)
        assert response.status_code == 200
        assert response.json()["id"] == product_id

    def test_get_nonexistent_product(self, client, user_headers):
        response = client.get("/api/v1/products/99999", headers=user_headers)
        assert response.status_code == 404

    def test_search_products(self, client, user_headers, sample_product):
        response = client.get("/api/v1/products/?search=Laptop", headers=user_headers)
        assert response.status_code == 200
        assert response.json()["total"] == 1

        response = client.get("/api/v1/products/?search=nonexistent", headers=user_headers)
        assert response.json()["total"] == 0

    def test_filter_by_category(self, client, user_headers, sample_product, sample_category):
        response = client.get(
            f"/api/v1/products/?category_id={sample_category['id']}",
            headers=user_headers,
        )
        assert response.json()["total"] == 1

    def test_pagination(self, client, admin_headers):
        for i in range(5):
            client.post(
                "/api/v1/products/",
                json={"name": f"Product {i}", "sku": f"SKU-{i:03d}", "price": "10.00"},
                headers=admin_headers,
            )
        response = client.get("/api/v1/products/?page=1&size=3", headers=admin_headers)
        data = response.json()
        assert len(data["items"]) == 3
        assert data["total"] == 5
        assert data["pages"] == 2

    def test_unauthenticated_cannot_list(self, client):
        response = client.get("/api/v1/products/")
        assert response.status_code == 403


class TestProductUpdate:
    def test_admin_can_update_product(self, client, admin_headers, sample_product):
        response = client.patch(
            f"/api/v1/products/{sample_product['id']}",
            json={"price": "1299.99", "name": "Updated Laptop"},
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Laptop"
        assert float(data["price"]) == 1299.99

    def test_user_cannot_update_product(self, client, user_headers, sample_product):
        response = client.patch(
            f"/api/v1/products/{sample_product['id']}",
            json={"price": "1.00"},
            headers=user_headers,
        )
        assert response.status_code == 403


class TestProductDelete:
    def test_admin_can_delete_product(self, client, admin_headers, sample_product):
        response = client.delete(
            f"/api/v1/products/{sample_product['id']}",
            headers=admin_headers,
        )
        assert response.status_code == 204

    def test_user_cannot_delete_product(self, client, user_headers, sample_product):
        response = client.delete(
            f"/api/v1/products/{sample_product['id']}",
            headers=user_headers,
        )
        assert response.status_code == 403


class TestStockManagement:
    def test_add_stock(self, client, admin_headers, sample_product):
        response = client.post(
            f"/api/v1/products/{sample_product['id']}/stock",
            json={"quantity": 20},
            headers=admin_headers,
        )
        assert response.status_code == 200
        assert response.json()["stock_quantity"] == 70  # 50 + 20

    def test_remove_stock(self, client, admin_headers, sample_product):
        response = client.post(
            f"/api/v1/products/{sample_product['id']}/stock",
            json={"quantity": -10},
            headers=admin_headers,
        )
        assert response.status_code == 200
        assert response.json()["stock_quantity"] == 40  # 50 - 10

    def test_cannot_go_below_zero(self, client, admin_headers, sample_product):
        response = client.post(
            f"/api/v1/products/{sample_product['id']}/stock",
            json={"quantity": -9999},
            headers=admin_headers,
        )
        assert response.status_code == 400

    def test_low_stock_flag(self, client, admin_headers, sample_product):
        # Set stock below threshold (threshold=5)
        client.post(
            f"/api/v1/products/{sample_product['id']}/stock",
            json={"quantity": -47},  # 50 - 47 = 3, threshold=5 → low
            headers=admin_headers,
        )
        response = client.get(
            f"/api/v1/products/{sample_product['id']}", headers=admin_headers
        )
        assert response.json()["is_low_stock"] is True

    def test_low_stock_endpoint(self, client, admin_headers, sample_product):
        # Drain stock below threshold
        client.post(
            f"/api/v1/products/{sample_product['id']}/stock",
            json={"quantity": -47},
            headers=admin_headers,
        )
        response = client.get("/api/v1/products/low-stock", headers=admin_headers)
        assert response.status_code == 200
        assert len(response.json()) == 1
