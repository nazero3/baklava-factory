"""
Tests for raw material receiving API flow.
Covers both happy path (successful receipt) and error paths (validation errors).
"""
from typing import Any

import pytest
from fastapi.testclient import TestClient


# Receiving tests: request receiving_supplier, receiving_raw_product, receiving_headers, client fixtures.


@pytest.fixture
def supplier_fixture(receiving_supplier):
    """Return the supplier fixture."""
    return receiving_supplier


@pytest.fixture
def product_fixture(receiving_raw_product):
    """Return the product fixture."""
    return receiving_raw_product


class TestReceivingHappyPath:
    """Test successful receiving flow with valid qty_kg."""

    def test_receiving_success(
        self,
        client: TestClient,
        receiving_supplier: Any,
        receiving_raw_product: Any,
        receiving_headers: dict[str, str]
    ):
        """Happy path: receive raw material with valid positive qty."""
        payload = {
            "supplier_id": str(receiving_supplier.id),
            "product_code": receiving_raw_product.code,
            "qty_kg": 150.0,
            "location": "WH-A1",
        }

        response = client.post("/receivings", json=payload, headers=receiving_headers)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "product_code" in data
        assert "qty_kg" in data
        assert data["qty_kg"] == 150.0

    def test_receiving_with_minimal_payload(
        self,
        client: TestClient,
        receiving_supplier: Any,
        receiving_raw_product: Any,
        receiving_headers: dict[str, str]
    ):
        """Happy path: receive with just required fields."""
        payload = {
            "supplier_id": str(receiving_supplier.id),
            "product_code": receiving_raw_product.code,
            "qty_kg": 75.5,
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
        receiving_headers: dict[str, str]
    ):
        """Error path: qty_kg < 0 should return 422/400 with clear error."""
        payload = {
            "supplier_id": "urn:test-supplier-123",
            "product_code": "RM-BAD-QTY",
            "qty_kg": -5.0,
        }

        response = client.post("/receivings", json=payload, headers=receiving_headers)
        assert response.status_code in (400, 422)
        data = response.json()
        # Assert the error is documented in detail or message field
        if "detail" in data:
            assert any("qty_kg" in str(err) and ("negative" in str(err).lower() or "invalid" in str(err).lower())
                       for err in data["detail"]) or "qty_kg" in str(data.get("detail", ""))
        elif "message" in data:
            assert "qty_kg" in str(data["message"]).lower() or "qty_kg" in data["message"]

    def test_receiving_rejects_zero_qty(
        self,
        client: TestClient,
        receiving_headers: dict[str, str]
    ):
        """Error path: qty_kg == 0 should be rejected."""
        payload = {
            "supplier_id": "urn:test-supplier-456",
            "product_code": "RM-ZERO-QTY",
            "qty_kg": 0,
        }

        response = client.post("/receivings", json=payload, headers=receiving_headers)
        assert response.status_code in (400, 422)
        data = response.json()
        # Verify error mentions qty_kg being invalid/required/greater than zero
        error_msg = str(data.get("detail", [])).lower() if isinstance(data.get("detail"), list) else str(data.get("detail", "")).lower()
        assert "qty_kg" in error_msg or any(
            kw in str(data.get("message", "")).lower() for kw in ["invalid", "required", "zero", "non-positive"]
        )

    def test_receiving_rejects_missing_product(
        self,
        client: TestClient,
        receiving_supplier: Any,
        receiving_headers: dict[str, str]
    ):
        """Error path: non-existent product code should fail."""
        payload = {
            "supplier_id": str(receiving_supplier.id),
            "product_code": "RM-NONEXISTENT-12345",
            "qty_kg": 100.0,
        }

        response = client.post("/api/receivings", json=payload, headers=receiving_headers)
        assert response.status_code in (400, 422)
        # Check for product not found or invalid error message
        data = response.json()
        detail = data.get("detail") if isinstance(data.get("detail"), list) else data.get("detail")
        if isinstance(detail, list):
            assert any("product" in str(e).lower() for e in detail)
        elif detail:
            assert "product" in str(detail).lower()

    def test_receiving_rejects_missing_supplier(
        self,
        client: TestClient,
        receiving_headers: dict[str, str]
    ):
        """Error path: non-existent supplier ID should fail."""
        payload = {
            "supplier_id": "urn:test-supplier-INVALID",
            "product_code": "RM-TEST",
            "qty_kg": 100.0,
        }

        response = client.post("/receivings", json=payload, headers=receiving_headers)
        assert response.status_code in (400, 422)
        # Verify supplier not found error is returned
        data = response.json()
        if "detail" in data:
            detail = data["detail"]
            if isinstance(detail, list):
                assert any("supplier" in str(e).lower() for e in detail)
            else:
                assert "supplier" in detail.lower()

    def test_receiving_rejects_missing_qty(
        self,
        client: TestClient,
        receiving_supplier: Any,
        receiving_raw_product: Any,
        receiving_headers: dict[str, str]
    ):
        """Error path: missing qty_kg field should fail validation."""
        payload = {
            "supplier_id": str(receiving_supplier.id),
            "product_code": receiving_raw_product.code,
            # Missing qty_kg intentionally
        }

        response = client.post("/api/receivings", json=payload, headers=receiving_headers)
        assert response.status_code in (400, 422)
        data = response.json()
        if "detail" in data:
            detail = data["detail"]
            if isinstance(detail, list):
                assert any("qty_kg" in str(e).lower() or "required" in str(e).lower() for e in detail)
            else:
                assert "qty_kg" in detail.lower() or "required" in detail.lower()
