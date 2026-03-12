from pydantic import BaseModel


class ErrorBody(BaseModel):
    code: str
    message: str


class APIErrorResponse(BaseModel):
    request_id: str
    error: ErrorBody


class StoredImageResponse(BaseModel):
    file_name: str
    preview_url: str
    updated_at: int


class FolderSummaryResponse(BaseModel):
    slug: str
    image_count: int
    cover_url: str | None = None
    updated_at: int


class UploadImagesResponse(BaseModel):
    request_id: str
    folder: FolderSummaryResponse
    saved_files: list[StoredImageResponse]
    created_at: int


class UploadConflictResponse(APIErrorResponse):
    conflicts: list[str]


class FolderListResponse(BaseModel):
    folders: list[FolderSummaryResponse]


class FolderDetailResponse(BaseModel):
    folder: FolderSummaryResponse
    images: list[StoredImageResponse]


class DeleteImageResponse(BaseModel):
    request_id: str
    deleted: bool
    folder_deleted: bool


class DeleteFolderResponse(BaseModel):
    request_id: str
    deleted: bool
