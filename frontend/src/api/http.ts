import axios from 'axios'

const http = axios.create({
  baseURL: '/api',
  timeout: 8000
})

export default http
