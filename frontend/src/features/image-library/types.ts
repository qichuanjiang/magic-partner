export type ImageLibraryErrorCode =
  | 'IMAGE_FOLDER_REQUIRED'
  | 'IMAGE_FOLDER_INVALID'
  | 'IMAGE_BATCH_LIMIT_EXCEEDED'
  | 'UNSUPPORTED_IMAGE_TYPE'
  | 'INVALID_IMAGE_SIZE'
  | 'OVERWRITE_CONFIRMATION_REQUIRED'
  | 'IMAGE_FOLDER_NOT_FOUND'
  | 'IMAGE_NOT_FOUND'
  | 'FILE_STORAGE_WRITE_FAILED'
  | 'FILE_STORAGE_DELETE_FAILED'
  | 'INVALID_REQUEST'

export interface StoredImage {
  file_name: string
  preview_url: string
  updated_at: number
}

export interface ImageFolderSummary {
  slug: string
  image_count: number
  cover_url: string | null
  updated_at: number
}

export interface UploadImagesResponse {
  request_id: string
  folder: ImageFolderSummary
  saved_files: StoredImage[]
  created_at: number
}

export interface UploadConflictResponse {
  request_id?: string
  error: {
    code: ImageLibraryErrorCode
    message: string
  }
  conflicts: string[]
}

export interface ImageFolderListResponse {
  folders: ImageFolderSummary[]
}

export interface ImageFolderDetailResponse {
  folder: ImageFolderSummary
  images: StoredImage[]
}

export interface DeleteImageResponse {
  request_id: string
  deleted: boolean
  folder_deleted: boolean
}

export interface DeleteFolderResponse {
  request_id: string
  deleted: boolean
}

export interface APIErrorResponse {
  request_id?: string
  error: {
    code?: ImageLibraryErrorCode
    message?: string
  }
}
