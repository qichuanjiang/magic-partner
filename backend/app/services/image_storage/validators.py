import re

from ...config import ALLOWED_CONTENT_TYPES, MAX_IMAGE_BATCH_COUNT, MAX_IMAGE_SIZE_BYTES
from ...errors import APIError
from .models import IncomingImage

FOLDER_SLUG_PATTERN = re.compile(r"^[\u4e00-\u9fffA-Za-z0-9_-]+$")


def validate_folder_slug(folder_slug: str) -> str:
    normalized = folder_slug.strip()
    if not normalized:
        raise APIError(status_code=400, code="IMAGE_FOLDER_REQUIRED", message="图片简称不能为空")
    if not FOLDER_SLUG_PATTERN.fullmatch(normalized):
        raise APIError(
            status_code=400,
            code="IMAGE_FOLDER_INVALID",
            message="图片简称仅允许中文、英文、数字、中划线和下划线",
        )
    return normalized


def validate_batch(images: list[IncomingImage]) -> None:
    if len(images) > MAX_IMAGE_BATCH_COUNT:
        raise APIError(status_code=400, code="IMAGE_BATCH_LIMIT_EXCEEDED", message="单次最多上传 10 张图片")

    for image in images:
        if image.content_type not in ALLOWED_CONTENT_TYPES:
            raise APIError(status_code=400, code="UNSUPPORTED_IMAGE_TYPE", message="仅支持 jpg、jpeg、png、webp")
        if len(image.content) > MAX_IMAGE_SIZE_BYTES:
            raise APIError(status_code=413, code="INVALID_IMAGE_SIZE", message="图片大小不能超过 5MB")
