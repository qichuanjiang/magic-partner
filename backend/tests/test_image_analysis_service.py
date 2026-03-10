from io import BytesIO

from fastapi import UploadFile
import pytest
from starlette.datastructures import Headers

from app.errors import APIError
from app.services.image_analysis import validate_image_upload


@pytest.mark.parametrize(
    ("filename", "content_type", "payload", "expected_code"),
    [
        ("bad.txt", "text/plain", b"hello", "UNSUPPORTED_IMAGE_TYPE"),
        ("empty.jpg", "image/jpeg", b"", "INVALID_REQUEST"),
        ("large.jpg", "image/jpeg", b"a" * (5 * 1024 * 1024 + 1), "INVALID_IMAGE_SIZE"),
    ],
)
def test_validate_image_upload_rejects_invalid_inputs(
    filename: str, content_type: str, payload: bytes, expected_code: str
):
    image = UploadFile(
        filename=filename,
        file=BytesIO(payload),
        headers=Headers({"content-type": content_type}),
    )

    with pytest.raises(APIError) as error_info:
        validate_image_upload(image, payload)

    assert error_info.value.code == expected_code
