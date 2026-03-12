export const toFileArray = (fileList: FileList | null | undefined) => Array.from(fileList || [])

export const buildConflictMessage = (conflicts: string[]) =>
  conflicts.length ? `以下文件将被覆盖：${conflicts.join('、')}。是否继续？` : '存在同名文件，是否继续覆盖？'

export const resetFileInput = (input: HTMLInputElement | null) => {
  if (input) {
    input.value = ''
  }
}

export const formatImageCount = (count: number) => `${count} 张图片`

export const formatDateTime = (value: number) => new Date(value).toLocaleString('zh-CN', { hour12: false })
