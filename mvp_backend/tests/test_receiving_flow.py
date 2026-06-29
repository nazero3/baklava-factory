"""
Tests for raw material receiving API flow.
Covers both happy path (successful receipt) and error paths (validation errors).
"""
from typing import Any

from fastapi.testclient import TestClient


class TestReceivingHappyPath:
    """Test successful receiving flow with valid qty_kg."""

    def test_receiving_success(
        self,
        client: TestClient,
        receiving_supplier: Any,
        receiving_raw_product: Any,
        receiving_headers: dict[str, str],
    ):
        """Happy path: receive raw material with valid positive qty."""
        payload = {
            "supplier_id": receiving_supplier.id,
            "product_id": receiving_raw_product.id,
            "qty_kg": 150.0,
            "unit_cost": 2.5,
            "lot_no": "LOT-A1",
        }

        response = client.post("/receivings", json=payload, headers=receiving_headers)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["product_id"] == receiving_raw_product.id
        assert data["qty_kg"] == 150.0

    def test_receiving_with_minimal_payload(
        self,
        client: TestClient,
        receiving_supplier: Any,
        receiving_raw_product: Any,
        receiving_headers: dict[str, str],
    ):
        """Happy path: receive with required fields only."""
        payload = {
            "supplier_id": receiving_supplier.id,
            "product_id": receiving_raw_product.id,
            "qty_kg": 75.5,
            "unit_cost": 1.0,
        }

        response = client.post("/receivings", json=payload, headers=receiving_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["qty_kg"] == 75.5


class TestReceivingErrorPaths:
    """Test receiving validation error paths."""

    def test_receiving_rejects_negative_qty(
        self,
        client: TestClient,
        receiving_supplier: Any,
        receiving_raw_product: Any,
        receiving_headers: dict[str, str],
    ):
        """Error path: qty_kg < 0 should return 422."""
        payload = {
            "supplier_id": receiving_supplier.id,
            "product_id": receiving_raw_product.id,
            "qty_kg": -5.0,
            "unit_cost": 1.0,
        }

        response = client.post("/receivings", json=payload, headers=receiving_headers)
        assert response.status_code == 422

    def test_receiving_rejects_zero_qty(
        self,
        client: TestClient,
        receiving_supplier: Any,
        receiving_raw_product: Any,
        receiving_headers: dict[str, str],
    ):
        """Error path: qty_kg == 0 should be rejected."""
        payload = {
            "supplier_id": receiving_supplier.id,
            "product_id": receiving_raw_product.id,
            "qty_kg": 0,
            "unit_cost": 1.0,
        }

        response = client.post("/receivings", json=payload, headers=receiving_headers)
        assert response.status_code == 422

    def test_receiving_rejects_missing_product(
        self,
        client: TestClient,
        receiving_supplier: Any,
        receiving_headers: dict[str, str],
    ):
        """Error path: non-existent product ID should fail."""
        payload = {
            "supplier_id": receiving_supplier.id,
            "product_id": 999999,
            "qty_kg": 100.0,
            "unit_cost": 1.0,
        }

        response = client.post("/receivings", json=payload, headers=receiving_headers)
        assert response.status_code == 404
        assert "product" in response.json()["detail"].lower()

    def test_receiving_rejects_missing_supplier(
        self,
        client: TestClient,
        receiving_raw_product: Any,
        receiving_headers: dict[str, str],
    ):
        """Error path: non-existent supplier ID should fail."""
        payload = {
            "supplier_id": 999999,
            "product_id": receiving_raw_product.id,
            "qty_kg": 100.0,
            "unit_cost": 1.0,
        }

        response = client.post("/receivings", json=payload, headers=receiving_headers)
        assert response.status_code == 404
        assert "supplier" in response.json()["detail"].lower()

    def test_receiving_rejects_missing_qty(
        self,
        client: TestClient,
        receiving_supplier: Any,
        receiving_raw_product: Any,
        receiving_headers: dict[str, str],
    ):
        """Error path: missing qty_kg field should fail validation."""
        payload = {
            "supplier_id": receiving_supplier.id,
            "product_id": receiving_raw_product.id,
            "unit_cost": 1.0,
        }

        response = client.post("/receivings", json=payload, headers=receiving_headers)
        assert response.status_code == 422
