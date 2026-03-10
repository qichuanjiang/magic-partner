from pydantic import BaseModel, Field


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
