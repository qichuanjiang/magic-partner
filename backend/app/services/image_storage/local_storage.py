import shutil
import os
from time import time_ns
from pathlib import Path
from urllib.parse import quote

from ...errors import APIError
from .models import DeleteFolderResult, DeleteImageResult, FolderSummary, StoredImage, UploadCandidate


class LocalImageStorage:
    def __init__(self, storage_root: Path):
        self.storage_root = storage_root
        self.storage_root.mkdir(parents=True, exist_ok=True)

    def get_folder_path(self, folder_slug: str) -> Path:
        path = (self.storage_root / folder_slug).resolve()
        if self.storage_root.resolve() not in path.parents:
            raise APIError(status_code=400, code="INVALID_REQUEST", message="Invalid folder path")
        return path

    def get_file_path(self, folder_slug: str, file_name: str) -> Path:
        normalized_name = Path(file_name).name
        path = (self.get_folder_path(folder_slug) / normalized_name).resolve()
        if self.get_folder_path(folder_slug) not in path.parents:
            raise APIError(status_code=400, code="INVALID_REQUEST", message="Invalid file path")
        return path

    def build_preview_url(self, folder_slug: str, file_name: str) -> str:
        return f"/image/{quote(folder_slug)}/{quote(file_name)}"

    def list_folders(self) -> list[FolderSummary]:
        folders: list[FolderSummary] = []
        for folder in self.storage_root.iterdir():
            if not folder.is_dir():
                continue
            images = self.list_images(folder.name)
            if not images:
                continue
            folders.append(
                FolderSummary(
                    slug=folder.name,
                    image_count=len(images),
                    cover_url=images[0].preview_url,
                    updated_at=max(image.updated_at for image in images),
                )
            )
        return sorted(folders, key=lambda item: item.updated_at, reverse=True)

    def list_images(self, folder_slug: str) -> list[StoredImage]:
        folder_path = self.get_folder_path(folder_slug)
        if not folder_path.exists() or not folder_path.is_dir():
            raise APIError(status_code=404, code="IMAGE_FOLDER_NOT_FOUND", message="图片目录不存在")

        image_paths = [path for path in folder_path.iterdir() if path.is_file()]
        image_paths.sort(key=lambda path: path.stat().st_mtime_ns, reverse=True)

        images = [
            StoredImage(
                file_name=path.name,
                preview_url=self.build_preview_url(folder_slug, path.name),
                updated_at=path.stat().st_mtime_ns // 1_000_000,
            )
            for path in image_paths
        ]
        return images

    def ensure_folder(self, folder_slug: str) -> Path:
        folder_path = self.get_folder_path(folder_slug)
        folder_path.mkdir(parents=True, exist_ok=True)
        return folder_path

    def existing_conflicts(self, folder_slug: str, file_names: list[str]) -> list[str]:
        folder_path = self.get_folder_path(folder_slug)
        if not folder_path.exists():
            return []
        return [file_name for file_name in file_names if (folder_path / file_name).exists()]

    def write_candidates(self, folder_slug: str, candidates: list[UploadCandidate], overwrite: bool) -> list[Path]:
        folder_path = self.ensure_folder(folder_slug)
        written_paths: list[Path] = []
        backups: list[tuple[Path, Path]] = []
        try:
            for index, candidate in enumerate(candidates):
                target = folder_path / candidate.file_name
                if overwrite and target.exists():
                    backup = folder_path / f".{candidate.file_name}.bak"
                    shutil.copy2(target, backup)
                    backups.append((target, backup))
                target.write_bytes(candidate.content)
                stamp = time_ns() + index
                os.utime(target, ns=(stamp, stamp))
                written_paths.append(target)
            for _, backup in backups:
                if backup.exists():
                    backup.unlink()
            return written_paths
        except OSError as exc:
            for path in written_paths:
                if path.exists():
                    path.unlink()
            for target, backup in backups:
                if backup.exists():
                    backup.replace(target)
            raise APIError(status_code=500, code="FILE_STORAGE_WRITE_FAILED", message=str(exc)) from exc

    def delete_image(self, folder_slug: str, file_name: str) -> DeleteImageResult:
        folder_path = self.get_folder_path(folder_slug)
        if not folder_path.exists():
            raise APIError(status_code=404, code="IMAGE_FOLDER_NOT_FOUND", message="图片目录不存在")

        file_path = self.get_file_path(folder_slug, file_name)
        if not file_path.exists():
            raise APIError(status_code=404, code="IMAGE_NOT_FOUND", message="图片不存在")

        try:
            file_path.unlink()
            folder_deleted = False
            if not any(folder_path.iterdir()):
                folder_path.rmdir()
                folder_deleted = True
            return DeleteImageResult(deleted=True, folder_deleted=folder_deleted)
        except OSError as exc:
            raise APIError(status_code=500, code="FILE_STORAGE_DELETE_FAILED", message=str(exc)) from exc

    def delete_folder(self, folder_slug: str) -> DeleteFolderResult:
        folder_path = self.get_folder_path(folder_slug)
        if not folder_path.exists():
            raise APIError(status_code=404, code="IMAGE_FOLDER_NOT_FOUND", message="图片目录不存在")
        try:
            shutil.rmtree(folder_path)
            return DeleteFolderResult(deleted=True)
        except OSError as exc:
            raise APIError(status_code=500, code="FILE_STORAGE_DELETE_FAILED", message=str(exc)) from exc
