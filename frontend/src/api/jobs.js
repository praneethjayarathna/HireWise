import api from './axios'

export function analyzeJobDescription(file) {
  const form = new FormData()
  form.append('file', file)
  return api.post('/jobs/analyze/', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
