import os

MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
DEFAULT_MODEL = os.getenv("IMAGE_ANALYZER_MODEL", "gpt-4.1-mini")
DEFAULT_PROMPT = (
    "Analyze the image and return a compact JSON with fields: "
    "summary (string), tags (array of {name, confidence[0..1]}). "
    "Use max 6 tags and keep summary under 40 Chinese characters when possible."
)
IMAGE_ANALYZER_MODE = os.getenv("IMAGE_ANALYZER_MODE", "mock").lower()
IMAGE_ANALYZER_TIMEOUT_SEC = float(os.getenv("IMAGE_ANALYZER_TIMEOUT_SEC", "15"))
OPENAI_API_URL = "https://api.openai.com/v1/responses"
