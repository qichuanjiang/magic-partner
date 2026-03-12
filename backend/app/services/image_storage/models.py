from dataclasses import dataclass, field


@dataclass(frozen=True)
class IncomingImage:
    file_name: str
    content_type: str
    content: bytes


@dataclass(frozen=True)
class StoredImage:
    file_name: str
    preview_url: str
    updated_at: int


@dataclass(frozen=True)
class FolderSummary:
    slug: str
    image_count: int
    cover_url: str | None
    updated_at: int


@dataclass(frozen=True)
class UploadCandidate:
    source_name: str
    file_name: str
    content_type: str
    content: bytes


@dataclass(frozen=True)
class UploadPlan:
    folder_slug: str
    folder_exists: bool
    conflicts: list[str] = field(default_factory=list)
    candidates: list[UploadCandidate] = field(default_factory=list)


@dataclass(frozen=True)
class UploadResult:
    folder: FolderSummary
    saved_files: list[StoredImage]
    created_at: int


@dataclass(frozen=True)
class DeleteImageResult:
    deleted: bool
    folder_deleted: bool


@dataclass(frozen=True)
class DeleteFolderResult:
    deleted: bool
