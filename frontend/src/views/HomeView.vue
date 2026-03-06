<template>
  <section class="card">
    <h2>首页</h2>

    <div class="row">
      <label for="name">姓名：</label>
      <input id="name" v-model="name" placeholder="输入你的名字" />
      <button type="button" @click="loadGreeting">调用后端接口</button>
    </div>

    <p v-if="health" class="ok">后端状态：{{ health.status }}</p>
    <p v-if="greeting">返回消息：{{ greeting.message }}</p>

    <div class="row">
      <button type="button" @click="counter.increment">Pinia 计数 +1</button>
      <span>当前计数：{{ counter.count }}</span>
    </div>

    <hr class="divider" />

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
        <span v-for="tag in analyzeResult.tags" :key="`${tag.name}-${tag.confidence}`" class="tag">
          {{ tag.name }} ({{ toPercent(tag.confidence) }})
        </span>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { AxiosError } from 'axios'
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { fetchGreeting, fetchHealth, type GreetingResponse } from '@/api/demo'
import {
  analyzeImage,
  type AnalyzeImageErrorResponse,
  type AnalyzeImageResponse
} from '@/api/images'
import { useCounterStore } from '@/stores/counter'

const name = ref('SpringBoot')
const health = ref<{ status: string } | null>(null)
const greeting = ref<GreetingResponse | null>(null)
const counter = useCounterStore()
const selectedFile = ref<File | null>(null)
const previewUrl = ref('')
const prompt = ref('')
const analyzeResult = ref<AnalyzeImageResponse | null>(null)
const analyzeError = ref('')
const isAnalyzing = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)

const MAX_IMAGE_BYTES = 5 * 1024 * 1024
const ALLOWED_TYPES = new Set(['image/jpeg', 'image/png', 'image/webp'])
const ERROR_MESSAGE_MAP: Record<string, string> = {
  INVALID_IMAGE_SIZE: '图片超过 5MB，请压缩后重试。',
  UNSUPPORTED_IMAGE_TYPE: '仅支持 jpg/jpeg/png/webp 格式。',
  MODEL_TIMEOUT: '模型分析超时，请稍后重试。',
  MODEL_UPSTREAM_ERROR: '模型服务暂不可用，请稍后重试。',
  INVALID_REQUEST: '请求参数不完整，请重新选择图片后再试。'
}

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
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
    previewUrl.value = ''
  }
}

const validateFile = (file: File): string | null => {
  if (!ALLOWED_TYPES.has(file.type)) {
    return '仅支持 jpg/jpeg/png/webp 格式。'
  }
  if (file.size <= 0) {
    return '图片文件不能为空。'
  }
  if (file.size > MAX_IMAGE_BYTES) {
    return '图片超过 5MB，请压缩后重试。'
  }
  return null
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

  const error = validateFile(file)
  if (error) {
    analyzeError.value = error
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

  const validationError = validateFile(selectedFile.value)
  if (validationError) {
    analyzeError.value = validationError
    return
  }

  resetAnalyzeState()
  isAnalyzing.value = true
  try {
    analyzeResult.value = await analyzeImage(selectedFile.value, prompt.value)
  } catch (error) {
    const axiosError = error as AxiosError<AnalyzeImageErrorResponse>
    const code = axiosError.response?.data?.error?.code
    analyzeError.value =
      (code && ERROR_MESSAGE_MAP[code]) ||
      axiosError.response?.data?.error?.message ||
      '请求失败，请检查后端服务是否正常。'
  } finally {
    isAnalyzing.value = false
  }
}

const toPercent = (value: number) => `${Math.round(value * 100)}%`

onMounted(async () => {
  await loadHealth()
})

onBeforeUnmount(() => {
  revokePreview()
})
</script>
