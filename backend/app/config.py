from pathlib import Path


MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024
MAX_IMAGE_BATCH_COUNT = 10
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
REPO_ROOT = Path(__file__).resolve().parents[2]
IMAGE_STORAGE_ROOT = REPO_ROOT / "frontend" / "public" / "image"
