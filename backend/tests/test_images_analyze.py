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
    assert data["request_id"].startswith("req_")
    assert data["summary"]
    assert isinstance(data["tags"], list)
    assert data["tags"]


def test_analyze_image_error_cases():
    cases = [
        {
            "name": "unsupported type",
            "files": {"image": ("bad.txt", b"hello", "text/plain")},
            "expected_status": 400,
            "expected_code": "UNSUPPORTED_IMAGE_TYPE",
        },
        {
            "name": "too large",
            "files": {"image": ("big.jpg", b"a" * (5 * 1024 * 1024 + 1), "image/jpeg")},
            "expected_status": 413,
            "expected_code": "INVALID_IMAGE_SIZE",
        },
        {
            "name": "empty image",
            "files": {"image": ("empty.jpg", b"", "image/jpeg")},
            "expected_status": 422,
            "expected_code": "INVALID_REQUEST",
        },
    ]

    for case in cases:
        response = client.post("/api/images/analyze", files=case["files"])
        data = response.json()

        assert response.status_code == case["expected_status"], case["name"]
        assert data["error"]["code"] == case["expected_code"], case["name"]


def test_analyze_image_missing_file():
    response = client.post("/api/images/analyze")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_REQUEST"
