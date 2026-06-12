import api from './axios'

export function analyzeJobDescription(file) {
  const form = new FormData()
  form.append('file', file)
  return api.post('/jobs/analyze/', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function analyzeResume(file, jobDescription) {
  const form = new FormData()
  form.append('resume_file', file)
  form.append('job_description', JSON.stringify(jobDescription))
  return api.post('/jobs/resume/analyze/', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

// --- Screening dashboard ---

export function createJobSession(file) {
  const form = new FormData()
  form.append('file', file)
  return api.post('/jobs/sessions/', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function uploadResumeToSession(sessionId, file) {
  const form = new FormData()
  form.append('file', file)
  return api.post(`/jobs/sessions/${sessionId}/resumes/`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function getSessionRankings(sessionId) {
  return api.get(`/jobs/sessions/${sessionId}/rankings/`)
}

export function getResumeDetail(sessionId, resumeId) {
  return api.get(`/jobs/sessions/${sessionId}/resumes/${resumeId}/`)
}
