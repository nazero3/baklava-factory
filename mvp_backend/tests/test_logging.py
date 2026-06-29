from fastapi.testclient import TestClient


def test_request_logging_adds_request_id_header(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID")


def test_request_logging_preserves_incoming_request_id(client: TestClient):
    request_id = "test-request-id-12345"
    response = client.get("/health", headers={"X-Request-ID": request_id})
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == request_id
