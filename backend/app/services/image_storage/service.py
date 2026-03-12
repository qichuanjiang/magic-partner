from pathlib import Path
from time import time

from ...errors import APIError
from .local_storage import LocalImageStorage
from .models import FolderSummary, IncomingImage, UploadCandidate, UploadPlan, UploadResult
from .naming import deduplicate_file_names
from .validators import validate_batch, validate_folder_slug


class ImageStorageService:
    def __init__(self, storage_root: Path):
        self.storage = LocalImageStorage(storage_root=storage_root)

    def upload_images(
        self,
        folder_slug: str,
        images: list[IncomingImage],
        overwrite: bool = False,
    ) -> UploadResult:
        plan = self.plan_upload(folder_slug=folder_slug, images=images)
        if plan.conflicts and not overwrite:
            raise APIError(
                status_code=409,
                code="OVERWRITE_CONFIRMATION_REQUIRED",
                message=",".join(plan.conflicts),
                details={"conflicts": plan.conflicts},
            )

        self.storage.write_candidates(plan.folder_slug, plan.candidates, overwrite=overwrite)
        saved_files = self.storage.list_images(plan.folder_slug)
        folder = self._build_folder_summary(plan.folder_slug, saved_files)
        current_batch_names = {candidate.file_name for candidate in plan.candidates}
        batch_files = [item for item in saved_files if item.file_name in current_batch_names]
        batch_files.sort(key=lambda item: plan.candidates.index(next(candidate for candidate in plan.candidates if candidate.file_name == item.file_name)))
        return UploadResult(
            folder=folder,
            saved_files=batch_files,
            created_at=int(time() * 1000),
        )

    def plan_upload(self, folder_slug: str, images: list[IncomingImage]) -> UploadPlan:
        normalized_slug = validate_folder_slug(folder_slug)
        validate_batch(images)

        resolved_names = deduplicate_file_names([Path(image.file_name).name for image in images])
        candidates = [
            UploadCandidate(
                source_name=image.file_name,
                file_name=resolved_name,
                content_type=image.content_type,
                content=image.content,
            )
            for image, resolved_name in zip(images, resolved_names, strict=False)
        ]
        conflicts = self.storage.existing_conflicts(normalized_slug, [candidate.file_name for candidate in candidates])
        folder_path = self.storage.get_folder_path(normalized_slug)
        return UploadPlan(
            folder_slug=normalized_slug,
            folder_exists=folder_path.exists(),
            conflicts=conflicts,
            candidates=candidates,
        )

    def list_folders(self):
        return self.storage.list_folders()

    def list_images(self, folder_slug: str):
        normalized_slug = validate_folder_slug(folder_slug)
        return self.storage.list_images(normalized_slug)

    def delete_image(self, folder_slug: str, file_name: str):
        normalized_slug = validate_folder_slug(folder_slug)
        return self.storage.delete_image(normalized_slug, file_name)

    def delete_folder(self, folder_slug: str):
        normalized_slug = validate_folder_slug(folder_slug)
        return self.storage.delete_folder(normalized_slug)

    def _build_folder_summary(self, folder_slug: str, images) -> FolderSummary:
        return FolderSummary(
            slug=folder_slug,
            image_count=len(images),
            cover_url=images[0].preview_url if images else None,
            updated_at=max((item.updated_at for item in images), default=int(time() * 1000)),
        )
