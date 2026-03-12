<template>
  <section class="card image-library-page">
    <div class="page-head">
      <div>
        <p class="eyebrow">Image Library</p>
        <h2 class="page-title">图片上传并保存</h2>
        <p class="muted">支持 jpg/jpeg/png/webp，单张不超过 5MB，单次最多 10 张。</p>
      </div>
    </div>

    <div class="library-layout">
      <div class="panel upload-panel">
        <label class="field-label" for="folderSlug">图片简称</label>
        <input
          id="folderSlug"
          data-testid="folder-slug-input"
          :value="folderSlug"
          class="text-input"
          placeholder="例如：素材集_01"
          @input="onFolderSlugInput"
        />

        <label class="field-label" for="images">选择图片</label>
        <input
          id="images"
          ref="fileInputRef"
          data-testid="images-input"
          type="file"
          class="text-input"
          multiple
          accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"
          @change="onFileChange"
        />

        <div v-if="selectedFiles.length" class="selected-files">
          <div v-for="file in selectedFiles" :key="`${file.name}-${file.size}`" class="selected-file">
            {{ file.name }}
          </div>
        </div>

        <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

        <div class="actions">
          <button
            data-testid="upload-submit"
            type="button"
            class="primary-button"
            :disabled="isUploading"
            @click="submitUpload"
          >
            {{ isUploading ? '上传中...' : '上传并保存' }}
          </button>
        </div>
      </div>

      <div class="panel folder-panel">
        <div class="panel-head">
          <h3 class="section-title">已保存图片</h3>
          <button type="button" class="secondary-button" :disabled="isLoadingFolders" @click="loadFolders">
            刷新
          </button>
        </div>

        <p v-if="isLoadingFolders" class="muted">加载中...</p>
        <p v-else-if="folders.length === 0" class="muted">还没有已保存的图片</p>

        <div v-else class="folder-grid">
          <article v-for="folder in folders" :key="folder.slug" class="folder-card">
            <RouterLink class="folder-link" :to="`/images/${encodeURIComponent(folder.slug)}`">
              <div class="folder-copy">
                <h4>{{ folder.slug }}</h4>
                <p class="meta-text">{{ formatImageCount(folder.image_count) }}</p>
                <p class="meta-text">更新于 {{ formatDateTime(folder.updated_at) }}</p>
              </div>
            </RouterLink>
            <button
              :data-testid="`delete-folder-${folder.slug}`"
              type="button"
              class="danger-button"
              @click="removeFolder(folder.slug)"
            >
              删除文件夹
            </button>
          </article>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { AxiosError } from 'axios'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { deleteImageFolder, fetchImageFolders, uploadImages } from '@/api/imageLibrary'
import {
  buildConflictMessage,
  formatDateTime,
  formatImageCount,
  resetFileInput,
  toFileArray
} from '@/features/image-library/upload-state'
import type { APIErrorResponse, ImageFolderSummary, UploadConflictResponse } from '@/features/image-library/types'
import { mapImageLibraryError, validateFolderSlug, validateImageBatch } from '@/features/image-library/validation'

const router = useRouter()
const fileInputRef = ref<HTMLInputElement | null>(null)
const folderSlug = ref('')
const selectedFiles = ref<File[]>([])
const folders = ref<ImageFolderSummary[]>([])
const isUploading = ref(false)
const isLoadingFolders = ref(false)
const errorMessage = ref('')

const loadFolders = async () => {
  isLoadingFolders.value = true
  try {
    folders.value = await fetchImageFolders()
  } finally {
    isLoadingFolders.value = false
  }
}

const onFolderSlugInput = (event: Event) => {
  folderSlug.value = (event.target as HTMLInputElement).value
}

const onFileChange = (event: Event) => {
  selectedFiles.value = toFileArray((event.target as HTMLInputElement).files)
}

const validateBeforeSubmit = () => {
  const slugError = validateFolderSlug(folderSlug.value)
  if (slugError) {
    return slugError
  }

  const fileError = validateImageBatch(selectedFiles.value)
  if (fileError) {
    return fileError
  }

  if (selectedFiles.value.length === 0) {
    return '请选择至少一张图片'
  }

  return ''
}

const submitUpload = async () => {
  if (isUploading.value) {
    return
  }

  errorMessage.value = validateBeforeSubmit()
  if (errorMessage.value) {
    return
  }

  isUploading.value = true

  try {
    const result = await uploadImages(folderSlug.value.trim(), selectedFiles.value, false)
    alert('保存成功')
    resetFileInput(fileInputRef.value)
    selectedFiles.value = []
    await loadFolders()
    await router.push(`/images/${encodeURIComponent(result.folder.slug)}`)
  } catch (error) {
    const axiosError = error as AxiosError<APIErrorResponse & Partial<UploadConflictResponse>>
    const response = axiosError.response?.data
    if (response?.error?.code === 'OVERWRITE_CONFIRMATION_REQUIRED') {
      const shouldOverwrite = confirm(buildConflictMessage(response.conflicts || []))
      if (shouldOverwrite) {
        const retry = await uploadImages(folderSlug.value.trim(), selectedFiles.value, true)
        alert('保存成功')
        resetFileInput(fileInputRef.value)
        selectedFiles.value = []
        await loadFolders()
        await router.push(`/images/${encodeURIComponent(retry.folder.slug)}`)
        return
      }
    }
    errorMessage.value = mapImageLibraryError(response?.error?.code, response?.error?.message)
  } finally {
    isUploading.value = false
  }
}

const removeFolder = async (slug: string) => {
  if (!confirm(`确定删除文件夹“${slug}”吗？`)) {
    return
  }

  await deleteImageFolder(slug)
  await loadFolders()
}

onMounted(loadFolders)
</script>
