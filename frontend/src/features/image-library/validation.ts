import type { ImageLibraryErrorCode } from './types'

const MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024
const MAX_IMAGE_BATCH_COUNT = 10
const ALLOWED_CONTENT_TYPES = new Set(['image/jpeg', 'image/png', 'image/webp'])
const FOLDER_SLUG_PATTERN = /^[\u4e00-\u9fffA-Za-z0-9_-]+$/

export const validateFolderSlug = (value: string) => {
  const normalized = value.trim()
  if (!normalized) {
    return '图片简称不能为空'
  }
  if (!FOLDER_SLUG_PATTERN.test(normalized)) {
    return '图片简称仅允许中文、英文、数字、中划线和下划线'
  }
  return ''
}

export const validateImageBatch = (files: File[]) => {
  if (files.length > MAX_IMAGE_BATCH_COUNT) {
    return '单次最多上传 10 张图片'
  }

  for (const file of files) {
    if (!ALLOWED_CONTENT_TYPES.has(file.type)) {
      return '仅支持 jpg、jpeg、png、webp'
    }
    if (file.size > MAX_IMAGE_SIZE_BYTES) {
      return '图片大小不能超过 5MB'
    }
  }

  return ''
}

export const mapImageLibraryError = (
  code?: ImageLibraryErrorCode,
  message?: string
) => {
  const fallback = message || '操作失败，请稍后重试'
  const mapped: Partial<Record<ImageLibraryErrorCode, string>> = {
    IMAGE_FOLDER_REQUIRED: '图片简称不能为空',
    IMAGE_FOLDER_INVALID: '图片简称仅允许中文、英文、数字、中划线和下划线',
    IMAGE_BATCH_LIMIT_EXCEEDED: '单次最多上传 10 张图片',
    UNSUPPORTED_IMAGE_TYPE: '仅支持 jpg、jpeg、png、webp',
    INVALID_IMAGE_SIZE: '图片大小不能超过 5MB',
    IMAGE_FOLDER_NOT_FOUND: '图片目录不存在',
    IMAGE_NOT_FOUND: '图片不存在',
    INVALID_REQUEST: '请求参数不合法'
  }

  return (code && mapped[code]) || fallback
}
