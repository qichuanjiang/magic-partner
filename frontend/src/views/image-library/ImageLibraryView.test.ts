import { createApp, nextTick } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import ImageLibraryView from './ImageLibraryView.vue'

const fetchImageFolders = vi.fn()
const uploadImages = vi.fn()
const deleteImageFolder = vi.fn()

vi.mock('@/api/imageLibrary', () => ({
  fetchImageFolders: (...args: unknown[]) => fetchImageFolders(...args),
  uploadImages: (...args: unknown[]) => uploadImages(...args),
  deleteImageFolder: (...args: unknown[]) => deleteImageFolder(...args)
}))

const flushPromises = async () => {
  await Promise.resolve()
  await Promise.resolve()
  await new Promise((resolve) => window.setTimeout(resolve, 0))
  await nextTick()
}

const mountView = async () => {
  const container = document.createElement('div')
  document.body.appendChild(container)

  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/images', component: ImageLibraryView },
      { path: '/images/:slug', component: { template: '<div>folder page</div>' } }
    ]
  })

  router.push('/images')
  await router.isReady()

  createApp({ template: '<RouterView />' }).use(router).mount(container)
  await flushPromises()

  return { container, router }
}

describe('ImageLibraryView', () => {
  beforeEach(() => {
    fetchImageFolders.mockReset()
    uploadImages.mockReset()
    deleteImageFolder.mockReset()
    fetchImageFolders.mockResolvedValue([
      {
        slug: 'album',
        image_count: 2,
        cover_url: '/image/album/cover.png',
        updated_at: 1760000000000
      }
    ])
    vi.stubGlobal('confirm', vi.fn(() => true))
    vi.stubGlobal('alert', vi.fn())
  })

  afterEach(() => {
    document.body.innerHTML = ''
    vi.unstubAllGlobals()
  })

  it('renders upload form and folder list', async () => {
    const { container } = await mountView()

    expect(fetchImageFolders).toHaveBeenCalledTimes(1)
    expect(container.querySelector('[data-testid="folder-slug-input"]')).not.toBeNull()
    expect(container.textContent).toContain('album')
    expect(container.textContent).toContain('2 张图片')
  })

  it('retries upload after overwrite confirmation and navigates to folder page', async () => {
    const { container, router } = await mountView()
    const file = new File([new Uint8Array([1, 2, 3])], 'cover.png', { type: 'image/png' })

    uploadImages.mockRejectedValueOnce({
      response: {
        data: {
          error: {
            code: 'OVERWRITE_CONFIRMATION_REQUIRED',
            message: '存在同名文件，确认后将覆盖'
          },
          conflicts: ['cover.png']
        }
      }
    })
    uploadImages.mockResolvedValueOnce({
      folder: {
        slug: 'album',
        image_count: 1,
        cover_url: '/image/album/cover.png',
        updated_at: 1760000000000
      },
      saved_files: [
        {
          file_name: 'cover.png',
          preview_url: '/image/album/cover.png',
          updated_at: 1760000000000
        }
      ],
      created_at: 1760000000000,
      request_id: 'req_xxx'
    })

    const input = container.querySelector('[data-testid="folder-slug-input"]') as HTMLInputElement
    input.value = 'album'
    input.dispatchEvent(new Event('input'))

    const fileInput = container.querySelector('[data-testid="images-input"]') as HTMLInputElement
    Object.defineProperty(fileInput, 'files', {
      configurable: true,
      value: [file]
    })
    fileInput.dispatchEvent(new Event('change'))
    await flushPromises()

    ;(container.querySelector('[data-testid="upload-submit"]') as HTMLButtonElement).click()
    await flushPromises()

    expect(uploadImages).toHaveBeenNthCalledWith(1, 'album', [file], false)
    expect(uploadImages).toHaveBeenNthCalledWith(2, 'album', [file], true)
    await flushPromises()
    expect(router.currentRoute.value.fullPath).toBe('/images/album')
  })

  it('confirms before deleting folder and refreshes list', async () => {
    fetchImageFolders
      .mockResolvedValueOnce([
        {
          slug: 'album',
          image_count: 1,
          cover_url: '/image/album/cover.png',
          updated_at: 1760000000000
        }
      ])
      .mockResolvedValueOnce([])
    deleteImageFolder.mockResolvedValue({ deleted: true, request_id: 'req_xxx' })

    const { container } = await mountView()

    ;(container.querySelector('[data-testid="delete-folder-album"]') as HTMLButtonElement).click()
    await flushPromises()

    expect(deleteImageFolder).toHaveBeenCalledWith('album')
    expect(fetchImageFolders).toHaveBeenCalledTimes(2)
    expect(container.textContent).toContain('还没有已保存的图片')
  })
})
