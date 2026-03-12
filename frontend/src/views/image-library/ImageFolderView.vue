<template>
  <section class="card image-library-page">
    <div class="panel-head">
      <div>
        <p class="eyebrow">Folder</p>
        <h2 class="page-title">{{ folderSlug }}</h2>
        <p class="muted" v-if="folderMeta">共 {{ formatImageCount(folderMeta.image_count) }}</p>
      </div>
      <RouterLink to="/images" class="secondary-link">返回列表</RouterLink>
    </div>

    <p v-if="isLoading" class="muted">加载中...</p>
    <p v-else-if="errorMessage" class="error-text">{{ errorMessage }}</p>

    <div v-else-if="images.length === 0" class="panel">
      <p class="muted">当前文件夹没有图片</p>
    </div>

    <div v-else class="image-grid">
      <article v-for="image in images" :key="image.file_name" class="image-card" data-testid="image-card">
        <img :src="image.preview_url" :alt="image.file_name" class="image-preview" />
        <div class="image-meta">
          <h3>{{ image.file_name }}</h3>
          <p class="meta-text">更新于 {{ formatDateTime(image.updated_at) }}</p>
        </div>
        <button
          :data-testid="`delete-image-${image.file_name}`"
          type="button"
          class="danger-button"
          @click="removeImage(image.file_name)"
        >
          删除图片
        </button>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { AxiosError } from 'axios'
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import { deleteImage, fetchImageFolder } from '@/api/imageLibrary'
import { formatDateTime, formatImageCount } from '@/features/image-library/upload-state'
import type { APIErrorResponse, ImageFolderDetailResponse, ImageFolderSummary, StoredImage } from '@/features/image-library/types'
import { mapImageLibraryError } from '@/features/image-library/validation'

const route = useRoute()
const router = useRouter()
const folderMeta = ref<ImageFolderSummary | null>(null)
const images = ref<StoredImage[]>([])
const isLoading = ref(false)
const errorMessage = ref('')

const folderSlug = computed(() => decodeURIComponent(String(route.params.slug || '')))

const loadFolder = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const response: ImageFolderDetailResponse = await fetchImageFolder(folderSlug.value)
    folderMeta.value = response.folder
    images.value = response.images
  } catch (error) {
    const axiosError = error as AxiosError<APIErrorResponse>
    errorMessage.value = mapImageLibraryError(
      axiosError.response?.data?.error?.code,
      axiosError.response?.data?.error?.message
    )
  } finally {
    isLoading.value = false
  }
}

const removeImage = async (fileName: string) => {
  if (!confirm(`确定删除图片“${fileName}”吗？`)) {
    return
  }

  const result = await deleteImage(folderSlug.value, fileName)
  if (result.folder_deleted) {
    await router.push('/images')
    return
  }
  await loadFolder()
}

onMounted(loadFolder)
</script>
