from time import time

from fastapi import APIRouter, File, Form, UploadFile

from .config import IMAGE_STORAGE_ROOT
from .schemas import (
    APIErrorResponse,
    DeleteFolderResponse,
    DeleteImageResponse,
    FolderDetailResponse,
    FolderListResponse,
    FolderSummaryResponse,
    StoredImageResponse,
    UploadConflictResponse,
    UploadImagesResponse,
)
from .services.image_storage.models import IncomingImage
from .services.image_storage.service import ImageStorageService
from .services.request_ids import build_request_id

router = APIRouter(prefix="/api")
image_storage_service = ImageStorageService(storage_root=IMAGE_STORAGE_ROOT)


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post(
    "/images",
    response_model=UploadImagesResponse,
    responses={
        400: {"model": APIErrorResponse},
        409: {"model": UploadConflictResponse},
        413: {"model": APIErrorResponse},
        422: {"model": APIErrorResponse},
        500: {"model": APIErrorResponse},
    },
)
async def upload_images(
    folder_slug: str = Form(...),
    overwrite: bool = Form(default=False),
    images: list[UploadFile] = File(...),
) -> UploadImagesResponse:
    uploads = [
        IncomingImage(
            file_name=upload.filename or "image",
            content_type=upload.content_type or "",
            content=await upload.read(),
        )
        for upload in images
    ]
    result = image_storage_service.upload_images(folder_slug=folder_slug, images=uploads, overwrite=overwrite)
    return UploadImagesResponse(
        request_id=build_request_id(),
        folder=FolderSummaryResponse(**result.folder.__dict__),
        saved_files=[StoredImageResponse(**item.__dict__) for item in result.saved_files],
        created_at=result.created_at,
    )


@router.get("/image-folders", response_model=FolderListResponse)
def list_image_folders() -> FolderListResponse:
    folders = image_storage_service.list_folders()
    return FolderListResponse(folders=[FolderSummaryResponse(**item.__dict__) for item in folders])


@router.get(
    "/image-folders/{folder_slug}",
    response_model=FolderDetailResponse,
    responses={404: {"model": APIErrorResponse}, 400: {"model": APIErrorResponse}},
)
def get_image_folder(folder_slug: str) -> FolderDetailResponse:
    images = image_storage_service.list_images(folder_slug)
    folder = FolderSummaryResponse(
        slug=folder_slug,
        image_count=len(images),
        cover_url=images[0].preview_url if images else None,
        updated_at=max((item.updated_at for item in images), default=int(time() * 1000)),
    )
    return FolderDetailResponse(
        folder=folder,
        images=[StoredImageResponse(**item.__dict__) for item in images],
    )


@router.delete(
    "/image-folders/{folder_slug}/images/{file_name}",
    response_model=DeleteImageResponse,
    responses={404: {"model": APIErrorResponse}, 400: {"model": APIErrorResponse}},
)
def delete_image(folder_slug: str, file_name: str) -> DeleteImageResponse:
    result = image_storage_service.delete_image(folder_slug, file_name)
    return DeleteImageResponse(
        request_id=build_request_id(),
        deleted=result.deleted,
        folder_deleted=result.folder_deleted,
    )


@router.delete(
    "/image-folders/{folder_slug}",
    response_model=DeleteFolderResponse,
    responses={404: {"model": APIErrorResponse}, 400: {"model": APIErrorResponse}},
)
def delete_folder(folder_slug: str) -> DeleteFolderResponse:
    result = image_storage_service.delete_folder(folder_slug)
    return DeleteFolderResponse(request_id=build_request_id(), deleted=result.deleted)
