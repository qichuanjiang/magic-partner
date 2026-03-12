from pathlib import Path

from fastapi.testclient import TestClient

from app.services.image_storage.service import ImageStorageService
from main import app


client = TestClient(app)


def make_png(name: str, content: bytes = b"image-bytes"):
    return (name, content, "image/png")


def install_storage_root(tmp_path: Path, monkeypatch):
    service = ImageStorageService(storage_root=tmp_path)
    monkeypatch.setattr("app.routes.image_storage_service", service)
    return service


def test_upload_images_api_success(tmp_path: Path, monkeypatch):
    install_storage_root(tmp_path, monkeypatch)

    response = client.post(
        "/api/images",
        data={"folder_slug": "album"},
        files=[("images", make_png("cover.png")), ("images", make_png("detail.png"))],
    )

    assert response.status_code == 200
    data = response.json()
    assert data["folder"]["slug"] == "album"
    assert data["folder"]["image_count"] == 2
    assert [item["file_name"] for item in data["saved_files"]] == ["cover.png", "detail.png"]


def test_upload_images_api_validation_and_conflict_cases(tmp_path: Path, monkeypatch):
    install_storage_root(tmp_path, monkeypatch)
    too_large = b"a" * (5 * 1024 * 1024 + 1)
    cases = [
        {
            "name": "missing folder",
            "data": {"folder_slug": ""},
            "files": [("images", make_png("cover.png"))],
            "expected_status": 400,
            "expected_code": "IMAGE_FOLDER_REQUIRED",
        },
        {
            "name": "unsupported type",
            "data": {"folder_slug": "album"},
            "files": [("images", ("bad.txt", b"text", "text/plain"))],
            "expected_status": 400,
            "expected_code": "UNSUPPORTED_IMAGE_TYPE",
        },
        {
            "name": "too large",
            "data": {"folder_slug": "album"},
            "files": [("images", make_png("big.png", too_large))],
            "expected_status": 413,
            "expected_code": "INVALID_IMAGE_SIZE",
        },
    ]

    for case in cases:
        response = client.post("/api/images", data=case["data"], files=case["files"])
        assert response.status_code == case["expected_status"], case["name"]
        assert response.json()["error"]["code"] == case["expected_code"], case["name"]

    client.post(
        "/api/images",
        data={"folder_slug": "album"},
        files=[("images", make_png("cover.png", b"old"))],
    )
    conflict = client.post(
        "/api/images",
        data={"folder_slug": "album"},
        files=[("images", make_png("cover.png", b"new"))],
    )
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "OVERWRITE_CONFIRMATION_REQUIRED"
    assert conflict.json()["conflicts"] == ["cover.png"]


def test_upload_images_api_overwrites_after_confirmation(tmp_path: Path, monkeypatch):
    install_storage_root(tmp_path, monkeypatch)
    client.post(
        "/api/images",
        data={"folder_slug": "album"},
        files=[("images", make_png("cover.png", b"old"))],
    )

    response = client.post(
        "/api/images",
        data={"folder_slug": "album", "overwrite": "true"},
        files=[("images", make_png("cover.png", b"new"))],
    )

    assert response.status_code == 200
    assert (tmp_path / "album" / "cover.png").read_bytes() == b"new"


def test_list_folders_and_images_api(tmp_path: Path, monkeypatch):
    install_storage_root(tmp_path, monkeypatch)
    client.post(
        "/api/images",
        data={"folder_slug": "album"},
        files=[("images", make_png("cover.png")), ("images", make_png("detail.png"))],
    )

    folders_response = client.get("/api/image-folders")
    folder_response = client.get("/api/image-folders/album")

    assert folders_response.status_code == 200
    folders = folders_response.json()["folders"]
    assert len(folders) == 1
    assert folders[0]["slug"] == "album"
    assert folders[0]["image_count"] == 2

    assert folder_response.status_code == 200
    images = folder_response.json()["images"]
    assert [item["file_name"] for item in images] == ["detail.png", "cover.png"]


def test_delete_image_and_folder_api(tmp_path: Path, monkeypatch):
    install_storage_root(tmp_path, monkeypatch)
    client.post(
        "/api/images",
        data={"folder_slug": "album"},
        files=[("images", make_png("cover.png")), ("images", make_png("detail.png"))],
    )

    delete_image_response = client.delete("/api/image-folders/album/images/cover.png")
    delete_folder_response = client.delete("/api/image-folders/album")

    assert delete_image_response.status_code == 200
    assert delete_image_response.json()["deleted"] is True
    assert delete_image_response.json()["folder_deleted"] is False

    assert delete_folder_response.status_code == 200
    assert delete_folder_response.json()["deleted"] is True


def test_delete_missing_targets_api_returns_not_found(tmp_path: Path, monkeypatch):
    install_storage_root(tmp_path, monkeypatch)

    missing_folder = client.get("/api/image-folders/missing")
    missing_image = client.delete("/api/image-folders/missing/images/a.png")
    missing_folder_delete = client.delete("/api/image-folders/missing")

    assert missing_folder.status_code == 404
    assert missing_folder.json()["error"]["code"] == "IMAGE_FOLDER_NOT_FOUND"
    assert missing_image.status_code == 404
    assert missing_image.json()["error"]["code"] == "IMAGE_FOLDER_NOT_FOUND"
    assert missing_folder_delete.status_code == 404
    assert missing_folder_delete.json()["error"]["code"] == "IMAGE_FOLDER_NOT_FOUND"
