import { createApp, nextTick } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import ImageFolderView from './ImageFolderView.vue'

const fetchImageFolder = vi.fn()
const deleteImage = vi.fn()

vi.mock('@/api/imageLibrary', () => ({
  fetchImageFolder: (...args: unknown[]) => fetchImageFolder(...args),
  deleteImage: (...args: unknown[]) => deleteImage(...args)
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
      { path: '/images', component: { template: '<div>list page</div>' } },
      { path: '/images/:slug', component: ImageFolderView }
    ]
  })

  router.push('/images/album')
  await router.isReady()

  createApp({ template: '<RouterView />' }).use(router).mount(container)
  await flushPromises()

  return { container, router }
}

describe('ImageFolderView', () => {
  beforeEach(() => {
    fetchImageFolder.mockReset()
    deleteImage.mockReset()
    fetchImageFolder.mockResolvedValue({
      folder: {
        slug: 'album',
        image_count: 2,
        cover_url: '/image/album/detail.png',
        updated_at: 1760000000002
      },
      images: [
        {
          file_name: 'detail.png',
          preview_url: '/image/album/detail.png',
          updated_at: 1760000000002
        },
        {
          file_name: 'cover.png',
          preview_url: '/image/album/cover.png',
          updated_at: 1760000000001
        }
      ]
    })
    vi.stubGlobal('confirm', vi.fn(() => true))
  })

  afterEach(() => {
    document.body.innerHTML = ''
    vi.unstubAllGlobals()
  })

  it('renders folder images in updated order', async () => {
    const { container } = await mountView()

    expect(fetchImageFolder).toHaveBeenCalledWith('album')
    const cards = [...container.querySelectorAll('[data-testid="image-card"]')]
    expect(cards).toHaveLength(2)
    expect(cards[0].textContent).toContain('detail.png')
    expect(cards[1].textContent).toContain('cover.png')
  })

  it('deletes an image after confirmation and redirects when folder becomes empty', async () => {
    deleteImage.mockResolvedValueOnce({ deleted: true, folder_deleted: true, request_id: 'req_xxx' })
    const { container, router } = await mountView()

    ;(container.querySelector('[data-testid="delete-image-detail.png"]') as HTMLButtonElement).click()
    await flushPromises()

    expect(deleteImage).toHaveBeenCalledWith('album', 'detail.png')
    await flushPromises()
    expect(router.currentRoute.value.fullPath).toBe('/images')
  })
})
