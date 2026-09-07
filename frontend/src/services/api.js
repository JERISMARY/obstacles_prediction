import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor
api.interceptors.request.use(config => config)

// Response error handling
api.interceptors.response.use(
  res => res,
  err => {
    const msg = err.response?.data?.detail || err.message || 'Network error'
    console.error('[API Error]', msg)
    return Promise.reject(new Error(msg))
  }
)

// ── Buses ──────────────────────────────────────────────────────────
export const busesApi = {
  list: () => api.get('/api/buses').then(r => r.data),
  get: (id) => api.get(`/api/buses/${id}`).then(r => r.data),
  getEvents: (id, limit = 20) => api.get(`/api/buses/${id}/events`, { params: { limit } }).then(r => r.data),
  getLocation: (id) => api.get(`/api/buses/${id}/location`).then(r => r.data),
}

// ── Events ─────────────────────────────────────────────────────────
export const eventsApi = {
  list: (filters = {}) => api.get('/api/events', { params: filters }).then(r => r.data),
  get: (id) => api.get(`/api/events/${id}`).then(r => r.data),
  create: (data) => api.post('/api/events', data).then(r => r.data),
  update: (id, data) => api.patch(`/api/events/${id}`, data).then(r => r.data),
}

// ── Statistics ─────────────────────────────────────────────────────
export const statisticsApi = {
  get: () => api.get('/api/statistics').then(r => r.data),
  traffic: (params = {}) => api.get('/api/traffic', { params }).then(r => r.data),
  heatmap: () => api.get('/api/heatmap').then(r => r.data),
}

// ── Video ──────────────────────────────────────────────────────────
export const videoApi = {
  upload: (file, busId, onProgress) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('bus_id', busId)
    return api.post('/api/video/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        if (onProgress && e.total) {
          onProgress(Math.round((e.loaded / e.total) * 100))
        }
      },
    }).then(r => r.data)
  },
  process: (uploadId, busId) => {
    const formData = new FormData()
    formData.append('upload_id', uploadId)
    formData.append('bus_id', busId)
    return api.post('/api/video/process', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(r => r.data)
  },
  status: (jobId) => api.get(`/api/video/status/${jobId}`).then(r => r.data),
  jobs: () => api.get('/api/video/jobs').then(r => r.data),
}

// ── Health ─────────────────────────────────────────────────────────
export const healthApi = {
  check: () => api.get('/api/health').then(r => r.data),
}

export default api
