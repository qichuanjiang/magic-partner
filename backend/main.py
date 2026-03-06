import base64
import json
import logging
import os
import uuid
from time import monotonic, time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import FastAPI, File, Form, Query, Request as FastAPIRequest, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn


class GreetingResponse(BaseModel):
    message: str
    timestamp: int


class TagItem(BaseModel):
    name: str
    confidence: float = Field(ge=0, le=1)


class AnalyzeImageResponse(BaseModel):
    request_id: str
    summary: str
    tags: list[TagItem]
    model: str
    latency_ms: int
    created_at: int


class ErrorBody(BaseModel):
    code: str
    message: str


class AnalyzeImageErrorResponse(BaseModel):
    request_id: str
    error: ErrorBody


class APIError(Exception):
    def __init__(self, *, status_code: int, code: str, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(message)


app = FastAPI(title="magic-partner backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

logger = logging.getLogger("magic_partner")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
DEFAULT_MODEL = os.getenv("IMAGE_ANALYZER_MODEL", "gpt-4.1-mini")
DEFAULT_PROMPT = (
    "Analyze the image and return a compact JSON with fields: "
    "summary (string), tags (array of {name, confidence[0..1]}). "
    "Use max 6 tags and keep summary under 40 Chinese characters when possible."
)


def build_request_id() -> str:
    return f"req_{uuid.uuid4().hex[:12]}"


def _extract_error_text(exc: HTTPError) -> str:
    try:
        body = exc.read().decode("utf-8")
    except Exception:
        return ""
    return body[:300]


def _call_openai_image_analyzer(
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
    schema = {
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
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    },
                    "required": ["name", "confidence"],
                },
            },
        },
        "required": ["summary", "tags"],
    }

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
                "schema": schema,
                "strict": True,
            }
        },
        "max_output_tokens": 500,
    }

    req = Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(req, timeout=timeout_sec) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except TimeoutError as exc:
        raise APIError(
            status_code=504,
            code="MODEL_TIMEOUT",
            message="Model request timed out",
        ) from exc
    except HTTPError as exc:
        detail = _extract_error_text(exc)
        raise APIError(
            status_code=502,
            code="MODEL_UPSTREAM_ERROR",
            message=f"Model upstream HTTP error: {exc.code} {detail}".strip(),
        ) from exc
    except URLError as exc:
        raise APIError(
            status_code=502,
            code="MODEL_UPSTREAM_ERROR",
            message=f"Model upstream network error: {exc.reason}",
        ) from exc

    try:
        output_text = data.get("output_text", "")
        parsed = json.loads(output_text)
        summary = str(parsed.get("summary") or "")
        tags = parsed.get("tags") or []
        if not summary:
            summary = "图片分析完成。"
        if not isinstance(tags, list):
            tags = []

        normalized_tags: list[dict[str, float]] = []
        for item in tags[:6]:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or "").strip()
            confidence_raw = item.get("confidence", 0)
            try:
                confidence = float(confidence_raw)
            except (TypeError, ValueError):
                confidence = 0.0
            confidence = max(0.0, min(1.0, confidence))
            if name:
                normalized_tags.append({"name": name, "confidence": confidence})

        if not normalized_tags:
            normalized_tags = [{"name": "unknown", "confidence": 0.0}]

        return summary, normalized_tags, os.getenv("IMAGE_ANALYZER_MODEL", DEFAULT_MODEL)
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise APIError(
            status_code=502,
            code="MODEL_UPSTREAM_ERROR",
            message="Model returned invalid JSON payload",
        ) from exc


def analyze_image(*, image_bytes: bytes, mime_type: str, prompt: str) -> tuple[str, list[dict[str, float]], str]:
    mode = os.getenv("IMAGE_ANALYZER_MODE", "mock").lower()
    timeout_sec = float(os.getenv("IMAGE_ANALYZER_TIMEOUT_SEC", "15"))

    if mode == "openai":
        return _call_openai_image_analyzer(
            image_bytes=image_bytes,
            mime_type=mime_type,
            prompt=prompt,
            timeout_sec=timeout_sec,
        )

    # Default mock mode keeps local development deterministic without external dependency.
    return (
        "检测到一张图片，包含可识别主体和场景信息。",
        [
            {"name": "object", "confidence": 0.92},
            {"name": "indoor", "confidence": 0.81},
        ],
        "mock-image-analyzer-v1",
    )


@app.exception_handler(APIError)
async def api_error_handler(_: FastAPIRequest, exc: APIError) -> JSONResponse:
    request_id = build_request_id()
    payload = AnalyzeImageErrorResponse(
        request_id=request_id,
        error=ErrorBody(code=exc.code, message=exc.message),
    )
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_: FastAPIRequest, __: RequestValidationError) -> JSONResponse:
    request_id = build_request_id()
    payload = AnalyzeImageErrorResponse(
        request_id=request_id,
        error=ErrorBody(code="INVALID_REQUEST", message="Invalid request payload"),
    )
    return JSONResponse(status_code=422, content=payload.model_dump())


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/greeting", response_model=GreetingResponse)
def greeting(name: str = Query(default="World")) -> GreetingResponse:
    return GreetingResponse(message=f"Hello, {name}!", timestamp=int(time() * 1000))


@app.post(
    "/api/images/analyze",
    response_model=AnalyzeImageResponse,
    responses={
        400: {"model": AnalyzeImageErrorResponse},
        413: {"model": AnalyzeImageErrorResponse},
        422: {"model": AnalyzeImageErrorResponse},
        502: {"model": AnalyzeImageErrorResponse},
        504: {"model": AnalyzeImageErrorResponse},
    },
)
async def analyze_uploaded_image(
    image: UploadFile = File(...),
    prompt: str = Form(default=DEFAULT_PROMPT),
) -> AnalyzeImageResponse:
    request_id = build_request_id()
    start = monotonic()

    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise APIError(
            status_code=400,
            code="UNSUPPORTED_IMAGE_TYPE",
            message="Only jpg/jpeg/png/webp images are supported",
        )

    image_bytes = await image.read()
    size = len(image_bytes)

    if size == 0:
        raise APIError(
            status_code=422,
            code="INVALID_REQUEST",
            message="Image file cannot be empty",
        )

    if size > MAX_IMAGE_SIZE_BYTES:
        raise APIError(
            status_code=413,
            code="INVALID_IMAGE_SIZE",
            message=f"Image size exceeds {MAX_IMAGE_SIZE_BYTES // (1024 * 1024)}MB limit",
        )

    summary, tags_raw, model = analyze_image(
        image_bytes=image_bytes,
        mime_type=image.content_type,
        prompt=prompt,
    )

    tags = [TagItem(name=item["name"], confidence=item["confidence"]) for item in tags_raw]
    latency_ms = int((monotonic() - start) * 1000)

    logger.info(
        "image_analysis_done request_id=%s mime=%s size=%s latency_ms=%s tags=%s",
        request_id,
        image.content_type,
        size,
        latency_ms,
        len(tags),
    )

    return AnalyzeImageResponse(
        request_id=request_id,
        summary=summary,
        tags=tags,
        model=model,
        latency_ms=latency_ms,
        created_at=int(time() * 1000),
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
