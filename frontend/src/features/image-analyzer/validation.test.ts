import { describe, expect, it } from 'vitest'

import { mapAnalyzeError, validateImageFile } from './validation'

describe('validateImageFile', () => {
  it('rejects invalid files with table-driven cases', () => {
    const cases = [
      {
        file: new File(['hello'], 'bad.txt', { type: 'text/plain' }),
        expected: '仅支持 jpg/jpeg/png/webp 格式。'
      },
      {
        file: new File([], 'empty.jpg', { type: 'image/jpeg' }),
        expected: '图片文件不能为空。'
      },
      {
        file: new File(['a'.repeat(5 * 1024 * 1024 + 1)], 'large.jpg', { type: 'image/jpeg' }),
        expected: '图片超过 5MB，请压缩后重试。'
      }
    ]

    for (const testCase of cases) {
      expect(validateImageFile(testCase.file)).toBe(testCase.expected)
    }
  })

  it('accepts supported images inside size limit', () => {
    const file = new File(['small-image'], 'ok.jpg', { type: 'image/jpeg' })
    expect(validateImageFile(file)).toBe('')
  })
})

describe('mapAnalyzeError', () => {
  it('returns explicit error messages', () => {
    expect(mapAnalyzeError('MODEL_TIMEOUT')).toBe('模型分析超时，请稍后重试。')
    expect(mapAnalyzeError(undefined, 'fallback')).toBe('fallback')
  })
})
