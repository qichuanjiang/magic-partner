from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_analyze_image_success():
    response = client.post(
        "/api/images/analyze",
        files={"image": ("ok.jpg", b"fake-image-bytes", "image/jpeg")},
    )

    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    assert "summary" in data
    assert isinstance(data.get("tags"), list)
    assert len(data["tags"]) > 0


def test_analyze_image_unsupported_type():
    response = client.post(
        "/api/images/analyze",
        files={"image": ("bad.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "UNSUPPORTED_IMAGE_TYPE"


def test_analyze_image_too_large():
    too_large = b"a" * (5 * 1024 * 1024 + 1)
    response = client.post(
        "/api/images/analyze",
        files={"image": ("big.jpg", too_large, "image/jpeg")},
    )

    assert response.status_code == 413
    data = response.json()
    assert data["error"]["code"] == "INVALID_IMAGE_SIZE"


def test_analyze_image_missing_file():
    response = client.post("/api/images/analyze")

    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "INVALID_REQUEST"
