from pathlib import Path

import pytest

from app.errors import APIError
from app.services.image_storage.models import IncomingImage
from app.services.image_storage.service import ImageStorageService


def make_image(
    file_name: str,
    content_type: str = "image/png",
    content: bytes = b"image-bytes",
) -> IncomingImage:
    return IncomingImage(
        file_name=file_name,
        content_type=content_type,
        content=content,
    )


def build_service(tmp_path: Path) -> ImageStorageService:
    return ImageStorageService(storage_root=tmp_path)


def test_upload_images_validation_cases(tmp_path: Path):
    service = build_service(tmp_path)
    too_large = b"a" * (5 * 1024 * 1024 + 1)
    cases = [
        {
            "name": "folder required",
            "folder_slug": "",
            "images": [make_image("ok.png")],
            "expected_status": 400,
            "expected_code": "IMAGE_FOLDER_REQUIRED",
        },
        {
            "name": "folder invalid",
            "folder_slug": "bad folder!",
            "images": [make_image("ok.png")],
            "expected_status": 400,
            "expected_code": "IMAGE_FOLDER_INVALID",
        },
        {
            "name": "batch limit exceeded",
            "folder_slug": "album",
            "images": [make_image(f"{index}.png") for index in range(11)],
            "expected_status": 400,
            "expected_code": "IMAGE_BATCH_LIMIT_EXCEEDED",
        },
        {
            "name": "unsupported type",
            "folder_slug": "album",
            "images": [make_image("bad.txt", content_type="text/plain", content=b"text")],
            "expected_status": 400,
            "expected_code": "UNSUPPORTED_IMAGE_TYPE",
        },
        {
            "name": "size exceeded",
            "folder_slug": "album",
            "images": [make_image("big.png", content=too_large)],
            "expected_status": 413,
            "expected_code": "INVALID_IMAGE_SIZE",
        },
    ]

    for case in cases:
        with pytest.raises(APIError) as exc_info:
            service.upload_images(folder_slug=case["folder_slug"], images=case["images"])

        assert exc_info.value.status_code == case["expected_status"], case["name"]
        assert exc_info.value.code == case["expected_code"], case["name"]


def test_upload_images_creates_folder_and_lists_sorted_images(tmp_path: Path):
    service = build_service(tmp_path)

    result = service.upload_images(
        folder_slug="素材集",
        images=[
            make_image("cover.png", content=b"first"),
            make_image("detail.png", content=b"second"),
        ],
    )

    folder_path = tmp_path / "素材集"
    assert folder_path.exists()
    assert result.folder.slug == "素材集"
    assert result.folder.image_count == 2

    images = service.list_images("素材集")
    assert [item.file_name for item in images] == ["detail.png", "cover.png"]
    assert all(item.preview_url.startswith("/image/%E7%B4%A0%E6%9D%90%E9%9B%86/") for item in images)


def test_upload_images_renames_duplicates_within_same_batch(tmp_path: Path):
    service = build_service(tmp_path)

    result = service.upload_images(
        folder_slug="album",
        images=[
            make_image("a.png", content=b"1"),
            make_image("a.png", content=b"2"),
            make_image("a.png", content=b"3"),
        ],
    )

    assert [item.file_name for item in result.saved_files] == ["a.png", "a(1).png", "a(2).png"]
    assert sorted(path.name for path in (tmp_path / "album").iterdir()) == ["a(1).png", "a(2).png", "a.png"]


def test_upload_images_requires_confirmation_for_existing_conflicts(tmp_path: Path):
    service = build_service(tmp_path)
    service.upload_images(folder_slug="album", images=[make_image("a.png", content=b"old")])

    with pytest.raises(APIError) as exc_info:
        service.upload_images(folder_slug="album", images=[make_image("a.png", content=b"new")])

    assert exc_info.value.status_code == 409
    assert exc_info.value.code == "OVERWRITE_CONFIRMATION_REQUIRED"
    assert exc_info.value.message == "a.png"
    assert (tmp_path / "album" / "a.png").read_bytes() == b"old"


def test_upload_images_overwrites_existing_files_after_confirmation(tmp_path: Path):
    service = build_service(tmp_path)
    service.upload_images(folder_slug="album", images=[make_image("a.png", content=b"old")])

    result = service.upload_images(
        folder_slug="album",
        images=[make_image("a.png", content=b"new")],
        overwrite=True,
    )

    assert [item.file_name for item in result.saved_files] == ["a.png"]
    assert (tmp_path / "album" / "a.png").read_bytes() == b"new"


def test_delete_image_removes_empty_folder(tmp_path: Path):
    service = build_service(tmp_path)
    service.upload_images(folder_slug="album", images=[make_image("a.png")])

    result = service.delete_image("album", "a.png")

    assert result.deleted is True
    assert result.folder_deleted is True
    assert not (tmp_path / "album").exists()


def test_delete_folder_removes_all_images(tmp_path: Path):
    service = build_service(tmp_path)
    service.upload_images(
        folder_slug="album",
        images=[make_image("a.png"), make_image("b.png")],
    )

    result = service.delete_folder("album")

    assert result.deleted is True
    assert not (tmp_path / "album").exists()


def test_delete_missing_targets_raise_not_found(tmp_path: Path):
    service = build_service(tmp_path)
    folder = tmp_path / "album"
    folder.mkdir()
    (folder / "a.png").write_bytes(b"a")

    with pytest.raises(APIError) as image_exc:
        service.delete_image("album", "missing.png")
    assert image_exc.value.status_code == 404
    assert image_exc.value.code == "IMAGE_NOT_FOUND"

    with pytest.raises(APIError) as folder_exc:
        service.delete_folder("missing")
    assert folder_exc.value.status_code == 404
    assert folder_exc.value.code == "IMAGE_FOLDER_NOT_FOUND"


def test_upload_images_rolls_back_new_files_when_write_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    service = build_service(tmp_path)
    target = tmp_path / "album"

    original_write_bytes = Path.write_bytes
    failed = {"triggered": False}

    def flaky_write(path: Path, content: bytes) -> int:
        if path == target / "b.png":
            failed["triggered"] = True
            raise OSError("disk full")
        return original_write_bytes(path, content)

    monkeypatch.setattr(Path, "write_bytes", flaky_write)

    with pytest.raises(APIError) as exc_info:
        service.upload_images(
            folder_slug="album",
            images=[make_image("a.png", content=b"a"), make_image("b.png", content=b"b")],
        )

    assert failed["triggered"] is True
    assert exc_info.value.status_code == 500
    assert exc_info.value.code == "FILE_STORAGE_WRITE_FAILED"
    assert not any(target.iterdir()) if target.exists() else True
