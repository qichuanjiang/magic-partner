import http from '@/api/http'
import type { AnalyzeImageResponse } from './types'

export const analyzeImage = async (file: File, prompt?: string) => {
  const formData = new FormData()
  formData.append('image', file)
  if (prompt && prompt.trim()) {
    formData.append('prompt', prompt.trim())
  }

  const { data } = await http.post<AnalyzeImageResponse>('/images/analyze', formData)
  return data
}
