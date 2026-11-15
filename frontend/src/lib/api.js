import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000,
  headers: { 'Content-Type': 'application/json' },
})

export const healthCheck = () => api.get('/api/health')
export const getModels = () => api.get('/api/models')
export const createEvaluation = (data) => api.post('/api/evaluations', data)
export const getDemoEvaluation = () => api.get('/api/evaluations/demo')
export const getEvaluationReport = (id) => api.get(`/api/evaluations/${id}/report`)

// Routes to demo endpoint automatically when id === 'demo'
export const getEvaluation = (id) =>
  id === 'demo' ? getDemoEvaluation() : api.get(`/api/evaluations/${id}`)

export default api
