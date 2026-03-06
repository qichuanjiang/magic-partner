import http from './http'

export interface GreetingResponse {
  message: string
  timestamp: number
}

export const fetchHealth = async () => {
  const { data } = await http.get<{ status: string }>('/health')
  return data
}

export const fetchGreeting = async (name: string) => {
  const { data } = await http.get<GreetingResponse>('/greeting', {
    params: { name }
  })
  return data
}
