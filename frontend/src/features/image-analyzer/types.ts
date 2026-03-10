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
