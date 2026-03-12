from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .schemas import APIErrorResponse, ErrorBody
from .services.request_ids import build_request_id


class APIError(Exception):
    def __init__(self, *, status_code: int, code: str, message: str, details: dict | None = None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


async def api_error_handler(_: Request, exc: APIError) -> JSONResponse:
    payload = APIErrorResponse(
        request_id=build_request_id(),
        error=ErrorBody(code=exc.code, message=exc.message),
    )
    content = payload.model_dump()
    content.update(exc.details)
    return JSONResponse(status_code=exc.status_code, content=content)


async def validation_error_handler(_: Request, __: RequestValidationError) -> JSONResponse:
    payload = APIErrorResponse(
        request_id=build_request_id(),
        error=ErrorBody(code="INVALID_REQUEST", message="Invalid request payload"),
    )
    return JSONResponse(status_code=422, content=payload.model_dump())
