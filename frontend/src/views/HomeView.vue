<template>
  <section class="card">
    <div class="stack">
      <div>
        <p class="eyebrow">Magic Partner</p>
        <h2 class="page-title">图片分析工作台</h2>
        <p class="muted">保留最小必要功能：健康检查、问候接口和图片上传分析。</p>
      </div>

      <div class="panel">
        <h3 class="section-title">基础接口</h3>
        <div class="row">
          <label for="name">姓名：</label>
          <input id="name" v-model="name" placeholder="输入你的名字" />
          <button type="button" @click="loadGreeting">调用后端接口</button>
        </div>
        <p v-if="health" class="ok">后端状态：{{ health.status }}</p>
        <p v-if="greeting">返回消息：{{ greeting.message }}</p>
      </div>

      <div class="panel">
        <h3 class="section-title">图片上传分析</h3>
        <p class="muted">支持 jpg/jpeg/png/webp，大小不超过 5MB。</p>

        <div class="row">
          <input
            ref="fileInputRef"
            type="file"
            accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"
            @change="onFileChange"
          />
        </div>

        <div v-if="previewUrl" class="preview-wrap">
          <img :src="previewUrl" alt="preview" class="preview-image" />
        </div>

        <div class="row">
          <input
            v-model="prompt"
            placeholder="可选：输入分析提示词（留空使用默认提示）"
            class="prompt-input"
          />
          <button type="button" :disabled="isAnalyzing || !selectedFile" @click="submitAnalyze">
            {{ isAnalyzing ? '分析中...' : '上传并分析' }}
          </button>
        </div>

        <p v-if="analyzeError" class="error">{{ analyzeError }}</p>

        <div v-if="analyzeResult" class="result-card">
          <p><strong>请求 ID：</strong>{{ analyzeResult.request_id }}</p>
          <p><strong>摘要：</strong>{{ analyzeResult.summary }}</p>
          <p><strong>模型：</strong>{{ analyzeResult.model }}</p>
          <p><strong>耗时：</strong>{{ analyzeResult.latency_ms }} ms</p>
          <div class="tags">
            <span
              v-for="tag in analyzeResult.tags"
              :key="`${tag.name}-${tag.confidence}`"
              class="tag"
            >
              {{ tag.name }} ({{ toPercent(tag.confidence) }})
            </span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { AxiosError } from 'axios'
import { onBeforeUnmount, onMounted, ref } from 'vue'

import { fetchGreeting, fetchHealth, type GreetingResponse } from '@/api/demo'
import { analyzeImage, type AnalyzeImageErrorResponse, type AnalyzeImageResponse } from '@/api/images'
import { mapAnalyzeError, validateImageFile } from '@/features/image-analyzer/validation'

const name = ref('FastAPI')
const health = ref<{ status: string } | null>(null)
const greeting = ref<GreetingResponse | null>(null)
const selectedFile = ref<File | null>(null)
const previewUrl = ref('')
const prompt = ref('')
const analyzeResult = ref<AnalyzeImageResponse | null>(null)
const analyzeError = ref('')
const isAnalyzing = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)

const loadHealth = async () => {
  health.value = await fetchHealth()
}

const loadGreeting = async () => {
  greeting.value = await fetchGreeting(name.value || 'World')
}

const resetAnalyzeState = () => {
  analyzeResult.value = null
  analyzeError.value = ''
}

const revokePreview = () => {
  if (!previewUrl.value) {
    return
  }
  URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = ''
}

const onFileChange = (event: Event) => {
  resetAnalyzeState()
  revokePreview()

  const input = event.target as HTMLInputElement
  const file = input.files?.[0] || null
  selectedFile.value = file

  if (!file) {
    return
  }

  const errorMessage = validateImageFile(file)
  if (errorMessage) {
    analyzeError.value = errorMessage
    selectedFile.value = null
    if (fileInputRef.value) {
      fileInputRef.value.value = ''
    }
    return
  }

  previewUrl.value = URL.createObjectURL(file)
}

const submitAnalyze = async () => {
  if (!selectedFile.value || isAnalyzing.value) {
    return
  }

  const errorMessage = validateImageFile(selectedFile.value)
  if (errorMessage) {
    analyzeError.value = errorMessage
    return
  }

  resetAnalyzeState()
  isAnalyzing.value = true

  try {
    analyzeResult.value = await analyzeImage(selectedFile.value, prompt.value)
  } catch (error) {
    const axiosError = error as AxiosError<AnalyzeImageErrorResponse>
    analyzeError.value = mapAnalyzeError(
      axiosError.response?.data?.error?.code,
      axiosError.response?.data?.error?.message
    )
  } finally {
    isAnalyzing.value = false
  }
}

const toPercent = (value: number) => `${Math.round(value * 100)}%`

onMounted(loadHealth)
onBeforeUnmount(revokePreview)
</script>
