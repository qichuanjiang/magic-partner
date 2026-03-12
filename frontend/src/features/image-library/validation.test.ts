import { describe, expect, it } from 'vitest'

import { mapImageLibraryError, validateFolderSlug, validateImageBatch } from './validation'

const makeFile = (name: string, type = 'image/png', size = 10) =>
  new File([new Uint8Array(size)], name, { type })

describe('image library validation', () => {
  it('validates folder slug cases with table-driven tests', () => {
    const cases = [
      { name: 'required', value: '', expected: '图片简称不能为空' },
      { name: 'blank', value: '   ', expected: '图片简称不能为空' },
      { name: 'invalid chars', value: 'bad folder!', expected: '图片简称仅允许中文、英文、数字、中划线和下划线' },
      { name: 'valid chinese', value: '素材集', expected: '' },
      { name: 'valid mixed', value: 'album_01-封面', expected: '' }
    ]

    for (const testCase of cases) {
      expect(validateFolderSlug(testCase.value), testCase.name).toBe(testCase.expected)
    }
  })

  it('validates image batch cases with table-driven tests', () => {
    const tooLarge = makeFile('big.png', 'image/png', 5 * 1024 * 1024 + 1)
    const cases = [
      {
        name: 'batch limit exceeded',
        files: Array.from({ length: 11 }, (_, index) => makeFile(`${index}.png`)),
        expected: '单次最多上传 10 张图片'
      },
      {
        name: 'unsupported type',
        files: [makeFile('bad.txt', 'text/plain')],
        expected: '仅支持 jpg、jpeg、png、webp'
      },
      {
        name: 'file too large',
        files: [tooLarge],
        expected: '图片大小不能超过 5MB'
      },
      {
        name: 'valid files',
        files: [makeFile('ok.png'), makeFile('ok.webp', 'image/webp')],
        expected: ''
      }
    ]

    for (const testCase of cases) {
      expect(validateImageBatch(testCase.files), testCase.name).toBe(testCase.expected)
    }
  })

  it('maps backend error codes to display messages', () => {
    expect(mapImageLibraryError('IMAGE_FOLDER_REQUIRED')).toBe('图片简称不能为空')
    expect(mapImageLibraryError('OVERWRITE_CONFIRMATION_REQUIRED', '存在同名文件')).toBe('存在同名文件')
    expect(mapImageLibraryError('UNKNOWN_CODE' as never, 'fallback')).toBe('fallback')
    expect(mapImageLibraryError(undefined, undefined)).toBe('操作失败，请稍后重试')
  })
})
