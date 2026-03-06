import http from './http'

export interface AnalyzeTag {
  name: string
  confidence: number
}

export interface AnalyzeImageResponse {
  request_id: string
  summary: string
  tags: AnalyzeTag[]
  model: string
  latency_ms: number
  created_at: number
}

export interface AnalyzeImageErrorResponse {
  request_id: string
  error: {
    code: string
    message: string
  }
}

export const analyzeImage = async (file: File, prompt?: string) => {
  const formData = new FormData()
  formData.append('image', file)
  if (prompt && prompt.trim().length > 0) {
    formData.append('prompt', prompt.trim())
  }

  const { data } = await http.post<AnalyzeImageResponse>('/images/analyze', formData)
  return data
}
