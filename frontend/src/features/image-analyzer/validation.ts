const MAX_IMAGE_BYTES = 5 * 1024 * 1024
const ALLOWED_TYPES = new Set(['image/jpeg', 'image/png', 'image/webp'])

const ERROR_MESSAGE_MAP: Record<string, string> = {
  INVALID_IMAGE_SIZE: '图片超过 5MB，请压缩后重试。',
  UNSUPPORTED_IMAGE_TYPE: '仅支持 jpg/jpeg/png/webp 格式。',
  MODEL_TIMEOUT: '模型分析超时，请稍后重试。',
  MODEL_UPSTREAM_ERROR: '模型服务暂不可用，请稍后重试。',
  INVALID_REQUEST: '请求参数不完整，请重新选择图片后再试。'
}

export const validateImageFile = (file: File) => {
  if (!ALLOWED_TYPES.has(file.type)) {
    return '仅支持 jpg/jpeg/png/webp 格式。'
  }
  if (file.size <= 0) {
    return '图片文件不能为空。'
  }
  if (file.size > MAX_IMAGE_BYTES) {
    return '图片超过 5MB，请压缩后重试。'
  }
  return ''
}

export const mapAnalyzeError = (code?: string, fallbackMessage?: string) => {
  if (code && ERROR_MESSAGE_MAP[code]) {
    return ERROR_MESSAGE_MAP[code]
  }
  return fallbackMessage || '请求失败，请检查后端服务是否正常。'
}
