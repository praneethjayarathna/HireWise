<template>
  <div class="page">
    <!-- Header -->
    <nav class="navbar">
      <span class="brand">HireWise</span>
      <div class="nav-links">
        <RouterLink to="/dashboard">Dashboard</RouterLink>
        <RouterLink to="/jobs/analyze">Job Analyzer</RouterLink>
        <button class="btn-logout" @click="handleLogout">Logout</button>
      </div>
    </nav>

    <main class="content">
      <h1>Resume Matcher</h1>
      <p class="subtitle">
        Upload your resume and compare it against a job description to see how well you fit.
      </p>

      <!-- Step 1: Job Description Selection -->
      <div class="section">
        <h2 class="section-title">1. Select Job Description</h2>
        <p class="hint">Upload or enter a job description to match against.</p>

        <div
          class="upload-card"
          :class="{ dragging: jdDragging }"
          @dragover.prevent="jdDragging = true"
          @dragleave.prevent="jdDragging = false"
          @drop.prevent="onJdDrop"
        >
          <input
            ref="jdFileInput"
            type="file"
            accept=".pdf,.docx,.doc"
            class="hidden-input"
            @change="onJdFileChange"
          />

          <div v-if="!jdFile && !jdText" class="upload-prompt" @click="jdFileInput.click()">
            <span class="upload-icon">📄</span>
            <p>Drag & drop job description or <span class="link">browse</span></p>
            <p class="hint">Supports PDF and DOCX</p>
          </div>

          <div v-else-if="jdFile" class="file-selected">
            <span class="file-icon">{{ jdFileIcon }}</span>
            <div class="file-info">
              <span class="file-name">{{ jdFile.name }}</span>
              <span class="file-size">{{ jdFileSizeLabel }}</span>
            </div>
            <button class="btn-remove" title="Remove" @click.stop="clearJd">✕</button>
          </div>
        </div>

        <div v-if="jdFile && jdLoading" class="progress">
          <span class="spinner-small" />
          <span>Analyzing job description...</span>
        </div>
      </div>

      <!-- Error -->
      <p v-if="error" class="error">{{ error }}</p>

      <!-- Step 2: Resume Upload -->
      <div class="section" :class="{ disabled: !jobDescriptionResult }">
        <h2 class="section-title">2. Upload Your Resume</h2>
        <p class="hint">Upload your resume to compare against the job description.</p>

        <div
          class="upload-card"
          :class="{ dragging: resumeDragging, disabled: !jobDescriptionResult }"
          @dragover.prevent="resumeDragging = true"
          @dragleave.prevent="resumeDragging = false"
          @drop.prevent="onResumeDrop"
        >
          <input
            ref="resumeFileInput"
            type="file"
            accept=".pdf,.docx,.doc"
            class="hidden-input"
            :disabled="!jobDescriptionResult"
            @change="onResumeFileChange"
          />

          <div v-if="!resumeFile" class="upload-prompt" @click="jobDescriptionResult && resumeFileInput?.click()">
            <span class="upload-icon">📃</span>
            <p>Drag & drop your resume or <span class="link">browse</span></p>
            <p class="hint">Supports PDF and DOCX</p>
          </div>

          <div v-else-if="resumeFile" class="file-selected">
            <span class="file-icon">{{ resumeFileIcon }}</span>
            <div class="file-info">
              <span class="file-name">{{ resumeFile.name }}</span>
              <span class="file-size">{{ resumeFileSizeLabel }}</span>
            </div>
            <button class="btn-remove" title="Remove" @click.stop="clearResume">✕</button>
          </div>
        </div>
      </div>

      <!-- Analyze button -->
      <button
        class="btn-analyze"
        :disabled="!jobDescriptionResult || !resumeFile || loading"
        @click="analyze"
      >
        <span v-if="loading" class="spinner" />
        {{ loading ? 'Analyzing...' : 'Compare Resume to Job' }}
      </button>

      <!-- Similarity Results -->
      <section v-if="similarityScores" class="scores-section">
        <div class="overall-score">
          <div class="score-circle" :class="overallScoreClass">
            <span class="score-value">{{ (similarityScores.overall * 100).toFixed(0) }}</span>
            <span class="score-label">Overall Match</span>
          </div>
          <p class="score-message">{{ overallScoreMessage }}</p>
        </div>

        <div class="category-scores">
          <div
            v-for="cat in categories"
            :key="cat.key"
            class="score-bar-card"
          >
            <div class="score-bar-header">
              <span class="cat-icon">{{ cat.icon }}</span>
              <span class="cat-label">{{ cat.label }}</span>
              <span class="cat-score">{{ (similarityScores[cat.key] * 100).toFixed(0) }}%</span>
            </div>
            <div class="score-bar-track">
              <div
                class="score-bar-fill"
                :style="{ width: `${similarityScores[cat.key] * 100}%`, backgroundColor: cat.color }"
              />
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { analyzeJobDescription, analyzeResume } from '@/api/jobs'

const auth = useAuthStore()
const router = useRouter()

const jdFileInput = ref(null)
const resumeFileInput = ref(null)
const jdFile = ref(null)
const resumeFile = ref(null)
const jdText = ref('')
const jobDescriptionResult = ref(null)
const similarityScores = ref(null)
const loading = ref(false)
const jdLoading = ref(false)
const error = ref('')
const jdDragging = ref(false)
const resumeDragging = ref(false)

const categories = [
  { key: 'overview', label: 'Overview', icon: '🏢', color: '#6366f1' },
  { key: 'responsibilities', label: 'Responsibilities', icon: '📋', color: '#0ea5e9' },
  { key: 'qualifications', label: 'Qualifications', icon: '🎓', color: '#10b981' },
  { key: 'skills', label: 'Skills', icon: '⚡', color: '#f59e0b' },
]

const jdFileIcon = computed(() => {
  if (!jdFile.value) return ''
  return jdFile.value.name.endsWith('.pdf') ? '📕' : '📘'
})

const resumeFileIcon = computed(() => {
  if (!resumeFile.value) return ''
  return resumeFile.value.name.endsWith('.pdf') ? '📕' : '📘'
})

const jdFileSizeLabel = computed(() => {
  if (!jdFile.value) return ''
  const kb = jdFile.value.size / 1024
  return kb > 1024 ? `${(kb / 1024).toFixed(1)} MB` : `${kb.toFixed(0)} KB`
})

const resumeFileSizeLabel = computed(() => {
  if (!resumeFile.value) return ''
  const kb = resumeFile.value.size / 1024
  return kb > 1024 ? `${(kb / 1024).toFixed(1)} MB` : `${kb.toFixed(0)} KB`
})

const overallScoreClass = computed(() => {
  if (!similarityScores.value) return ''
  const score = similarityScores.value.overall
  if (score >= 0.7) return 'high'
  if (score >= 0.4) return 'medium'
  return 'low'
})

const overallScoreMessage = computed(() => {
  if (!similarityScores.value) return ''
  const score = similarityScores.value.overall
  if (score >= 0.8) return 'Excellent match! Your resume strongly aligns with this role.'
  if (score >= 0.6) return 'Good match. Consider highlighting more relevant skills.'
  if (score >= 0.4) return 'Moderate match. You may need to tailor your resume more.'
  return 'Low match. Consider customizing your resume for this position.'
})

function validateFile(file) {
  const ext = file.name.split('.').pop().toLowerCase()
  if (!['pdf', 'docx', 'doc'].includes(ext)) {
    error.value = 'Only PDF and DOCX files are supported.'
    return false
  }
  if (file.size > 10 * 1024 * 1024) {
    error.value = 'File size must not exceed 10 MB.'
    return false
  }
  return true
}

function onJdFileChange(e) {
  const file = e.target.files[0]
  if (file && validateFile(file)) {
    jdFile.value = file
    error.value = ''
    analyzeJd()
  }
}

function onJdDrop(e) {
  jdDragging.value = false
  const file = e.dataTransfer.files[0]
  if (file && validateFile(file)) {
    jdFile.value = file
    error.value = ''
    analyzeJd()
  }
}

function onResumeFileChange(e) {
  const file = e.target.files[0]
  if (file && validateFile(file)) {
    resumeFile.value = file
    error.value = ''
  }
}

function onResumeDrop(e) {
  resumeDragging.value = false
  const file = e.dataTransfer.files[0]
  if (file && validateFile(file)) {
    resumeFile.value = file
    error.value = ''
  }
}

function clearJd() {
  jdFile.value = null
  jobDescriptionResult.value = null
  error.value = ''
  if (jdFileInput.value) jdFileInput.value.value = ''
}

function clearResume() {
  resumeFile.value = null
  similarityScores.value = null
  error.value = ''
  if (resumeFileInput.value) resumeFileInput.value.value = ''
}

async function analyzeJd() {
  if (!jdFile.value) return
  jdLoading.value = true
  try {
    const { data } = await analyzeJobDescription(jdFile.value)
    jobDescriptionResult.value = data
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to analyze job description.'
  } finally {
    jdLoading.value = false
  }
}

async function analyze() {
  if (!jobDescriptionResult.value || !resumeFile.value) return
  loading.value = true
  error.value = ''
  similarityScores.value = null
  try {
    const { data } = await analyzeResume(resumeFile.value, jobDescriptionResult.value)
    similarityScores.value = data.similarity_scores
  } catch (e) {
    error.value = e.response?.data?.detail || 'Analysis failed. Please try again.'
  } finally {
    loading.value = false
  }
}

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8fafc 0%, #f0f2f5 100%);
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: #fff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  position: sticky;
  top: 0;
  z-index: 100;
}

.brand {
  font-weight: 800;
  font-size: 1.35rem;
  color: #4f46e5;
  letter-spacing: -0.02em;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.nav-links a {
  color: #6b7280;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.95rem;
  transition: color 0.15s;
}

.nav-links a:hover {
  color: #4f46e5;
}

.btn-logout {
  padding: 0.5rem 1.25rem;
  background: transparent;
  color: #4f46e5;
  border: 1.5px solid #4f46e5;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-logout:hover {
  background: #4f46e5;
  color: #fff;
}

.content {
  max-width: 900px;
  margin: 0 auto;
  padding: 3rem 1.5rem;
}

h1 {
  margin: 0 0 0.4rem;
  font-size: 1.85rem;
  font-weight: 800;
  color: #1e1b4b;
  letter-spacing: -0.02em;
}

.subtitle {
  color: #6b7280;
  font-size: 1rem;
  margin: 0 0 2rem;
}

.section {
  margin-bottom: 2rem;
}

.section.disabled {
  opacity: 0.5;
  pointer-events: none;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1e1b4b;
  margin: 0 0 0.25rem;
}

.hint {
  color: #9ca3af;
  font-size: 0.9rem;
  margin: 0 0 1rem;
}

.upload-card {
  border: 2px dashed #c7d2fe;
  border-radius: 16px;
  background: #fff;
  transition: all 0.25s;
  cursor: pointer;
  overflow: hidden;
}

.upload-card:hover {
  border-color: #a5b4fc;
  box-shadow: 0 4px 20px rgba(79, 70, 229, 0.08);
}

.upload-card.dragging {
  border-color: #4f46e5;
  background: #eef2ff;
  transform: scale(1.01);
}

.upload-card.disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.hidden-input {
  display: none;
}

.upload-prompt {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 3rem 1rem;
  gap: 0.75rem;
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: 0.5rem;
}

.upload-prompt p {
  margin: 0;
  color: #6b7280;
  font-size: 1rem;
}

.link {
  color: #4f46e5;
  font-weight: 600;
  cursor: pointer;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.hint {
  font-size: 0.85rem;
  color: #9ca3af;
}

.file-selected {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
}

.file-icon {
  font-size: 2.25rem;
}

.file-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.file-name {
  font-weight: 600;
  color: #1f2937;
  word-break: break-all;
  font-size: 1rem;
}

.file-size {
  font-size: 0.85rem;
  color: #9ca3af;
}

.btn-remove {
  background: none;
  border: none;
  font-size: 1.25rem;
  color: #9ca3af;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.15s;
}

.btn-remove:hover {
  background: #fef2f2;
  color: #ef4444;
}

.progress {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.75rem;
  color: #6b7280;
  font-size: 0.9rem;
}

.spinner-small {
  width: 14px;
  height: 14px;
  border: 2px solid #e5e7eb;
  border-top-color: #4f46e5;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

.error {
  color: #dc2626;
  font-size: 0.9rem;
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  background: #fef2f2;
  border-radius: 10px;
  border-left: 3px solid #dc2626;
}

.btn-analyze {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  margin-top: 1.5rem;
  padding: 0.9rem 2.5rem;
  background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
  color: #fff;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-analyze:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(79, 70, 229, 0.35);
}

.btn-analyze:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.scores-section {
  margin-top: 2.5rem;
}

.overall-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 2rem;
}

.score-circle {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #fff;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 4px solid #e5e7eb;
}

.score-circle.high {
  border-color: #10b981;
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
}

.score-circle.medium {
  border-color: #f59e0b;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
}

.score-circle.low {
  border-color: #ef4444;
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
}

.score-value {
  font-size: 2.5rem;
  font-weight: 800;
  color: #1e1b4b;
}

.score-label {
  font-size: 0.85rem;
  color: #6b7280;
  font-weight: 600;
}

.score-message {
  margin-top: 1rem;
  color: #4b5563;
  font-size: 1rem;
  text-align: center;
  max-width: 500px;
}

.category-scores {
  display: grid;
  gap: 1rem;
}

.score-bar-card {
  background: #fff;
  padding: 1rem 1.25rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.score-bar-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.cat-icon {
  font-size: 1.1rem;
}

.cat-label {
  flex: 1;
  font-weight: 600;
  color: #1f2937;
}

.cat-score {
  font-weight: 700;
  color: #1e1b4b;
}

.score-bar-track {
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.score-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease-out;
}
</style>