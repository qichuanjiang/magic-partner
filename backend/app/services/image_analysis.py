import base64
import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import UploadFile

from ..config import (
    ALLOWED_CONTENT_TYPES,
    DEFAULT_MODEL,
    DEFAULT_PROMPT,
    IMAGE_ANALYZER_MODE,
    IMAGE_ANALYZER_TIMEOUT_SEC,
    MAX_IMAGE_SIZE_BYTES,
    OPENAI_API_URL,
)
from ..errors import APIError


def validate_image_upload(image: UploadFile, image_bytes: bytes) -> None:
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise APIError(
            status_code=400,
            code="UNSUPPORTED_IMAGE_TYPE",
            message="Only jpg/jpeg/png/webp images are supported",
        )

    if len(image_bytes) == 0:
        raise APIError(
            status_code=422,
            code="INVALID_REQUEST",
            message="Image file cannot be empty",
        )

    if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
        raise APIError(
            status_code=413,
            code="INVALID_IMAGE_SIZE",
            message=f"Image size exceeds {MAX_IMAGE_SIZE_BYTES // (1024 * 1024)}MB limit",
        )


def analyze_image(*, image_bytes: bytes, mime_type: str, prompt: str) -> tuple[str, list[dict[str, float]], str]:
    if IMAGE_ANALYZER_MODE == "openai":
        return call_openai_image_analyzer(
            image_bytes=image_bytes,
            mime_type=mime_type,
            prompt=prompt,
            timeout_sec=IMAGE_ANALYZER_TIMEOUT_SEC,
        )

    return (
        "检测到一张图片，包含可识别主体和场景信息。",
        [
            {"name": "object", "confidence": 0.92},
            {"name": "indoor", "confidence": 0.81},
        ],
        "mock-image-analyzer-v1",
    )


def call_openai_image_analyzer(
    *, image_bytes: bytes, mime_type: str, prompt: str, timeout_sec: float
) -> tuple[str, list[dict[str, float]], str]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise APIError(
            status_code=502,
            code="MODEL_UPSTREAM_ERROR",
            message="OPENAI_API_KEY is not configured",
        )

    image_data_url = (
        f"data:{mime_type};base64,{base64.b64encode(image_bytes).decode('utf-8')}"
    )
    payload = {
        "model": os.getenv("IMAGE_ANALYZER_MODEL", DEFAULT_MODEL),
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt or DEFAULT_PROMPT},
                    {"type": "input_image", "image_url": image_data_url},
                ],
            }
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "image_analysis",
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "summary": {"type": "string"},
                        "tags": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "name": {"type": "string"},
                                    "confidence": {
                                        "type": "number",
                                        "minimum": 0,
                                        "maximum": 1,
                                    },
                                },
                                "required": ["name", "confidence"],
                            },
                        },
                    },
                    "required": ["summary", "tags"],
                },
                "strict": True,
            }
        },
        "max_output_tokens": 500,
    }

    request = Request(
        OPENAI_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=timeout_sec) as response:
            data = json.loads(response.read().decode("utf-8"))
    except TimeoutError as exc:
        raise APIError(
            status_code=504,
            code="MODEL_TIMEOUT",
            message="Model request timed out",
        ) from exc
    except HTTPError as exc:
        raise APIError(
            status_code=502,
            code="MODEL_UPSTREAM_ERROR",
            message=f"Model upstream HTTP error: {exc.code} {_extract_error_text(exc)}".strip(),
        ) from exc
    except URLError as exc:
        raise APIError(
            status_code=502,
            code="MODEL_UPSTREAM_ERROR",
            message=f"Model upstream network error: {exc.reason}",
        ) from exc

    return _parse_model_response(data)


def _extract_error_text(exc: HTTPError) -> str:
    try:
        body = exc.read().decode("utf-8")
    except Exception:
        return ""
    return body[:300]


def _parse_model_response(data: dict) -> tuple[str, list[dict[str, float]], str]:
    try:
        parsed = json.loads(data.get("output_text", ""))
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise APIError(
            status_code=502,
            code="MODEL_UPSTREAM_ERROR",
            message="Model returned invalid JSON payload",
        ) from exc

    summary = str(parsed.get("summary") or "图片分析完成。")
    tags = parsed.get("tags") if isinstance(parsed.get("tags"), list) else []
    normalized_tags: list[dict[str, float]] = []

    for item in tags[:6]:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "").strip()
        if not name:
            continue
        try:
            confidence = float(item.get("confidence", 0))
        except (TypeError, ValueError):
            confidence = 0.0
        normalized_tags.append({"name": name, "confidence": max(0.0, min(1.0, confidence))})

    if not normalized_tags:
        normalized_tags = [{"name": "unknown", "confidence": 0.0}]

    return summary, normalized_tags, os.getenv("IMAGE_ANALYZER_MODEL", DEFAULT_MODEL)
