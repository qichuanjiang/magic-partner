import logging
from time import monotonic, time

from fastapi import APIRouter, File, Form, Query, UploadFile

from .config import DEFAULT_PROMPT
from .schemas import AnalyzeImageErrorResponse, AnalyzeImageResponse, GreetingResponse, TagItem
from .services.image_analysis import analyze_image, validate_image_upload
from .services.request_ids import build_request_id

logger = logging.getLogger("magic_partner")

router = APIRouter(prefix="/api")


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/greeting", response_model=GreetingResponse)
def greeting(name: str = Query(default="World")) -> GreetingResponse:
    return GreetingResponse(message=f"Hello, {name}!", timestamp=int(time() * 1000))


@router.post(
    "/images/analyze",
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
    started_at = monotonic()
    image_bytes = await image.read()

    validate_image_upload(image, image_bytes)
    summary, tags_raw, model = analyze_image(
        image_bytes=image_bytes,
        mime_type=image.content_type or "",
        prompt=prompt,
    )

    tags = [TagItem(name=item["name"], confidence=item["confidence"]) for item in tags_raw]
    latency_ms = int((monotonic() - started_at) * 1000)

    logger.info(
        "image_analysis_done request_id=%s mime=%s size=%s latency_ms=%s tags=%s",
        request_id,
        image.content_type,
        len(image_bytes),
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
