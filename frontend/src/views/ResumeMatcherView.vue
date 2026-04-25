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

      <!-- Skill Analysis -->
      <section v-if="skillAnalysis" class="skills-section">
        <h2 class="skills-title">Skills Analysis</h2>

        <div class="skills-stats">
          <div class="stat-badge">
            <span class="stat-value">{{ skillAnalysis.job_skills_count }}</span>
            <span class="stat-label">Job Required</span>
          </div>
          <div class="stat-badge">
            <span class="stat-value">{{ skillAnalysis.resume_skills_count }}</span>
            <span class="stat-label">Resume Skills</span>
          </div>
          <div class="stat-badge highlight">
            <span class="stat-value">{{ skillAnalysis.match_rate }}%</span>
            <span class="stat-label">Match Rate</span>
          </div>
        </div>

        <div class="skills-container">
          <div class="skills-card matching">
            <h3 class="skills-card-title">
              <span class="skills-icon">✓</span>
              Matching Skills
            </h3>
            <div v-if="skillAnalysis.matching_skills?.length" class="skills-list">
              <span
                v-for="skill in skillAnalysis.matching_skills"
                :key="skill"
                class="skill-tag matching"
              >
                {{ skill }}
              </span>
            </div>
            <p v-else class="skills-empty">No matching skills found</p>
          </div>

          <div class="skills-card missing">
            <h3 class="skills-card-title">
              <span class="skills-icon">✗</span>
              Missing Skills
            </h3>
            <div v-if="skillAnalysis.missing_skills?.length" class="skills-list">
              <span
                v-for="skill in skillAnalysis.missing_skills"
                :key="skill"
                class="skill-tag missing"
              >
                {{ skill }}
              </span>
            </div>
            <p v-else class="skills-empty">All required skills found!</p>
          </div>
        </div>

        <div v-if="skillAnalysis.skill_variations && Object.keys(skillAnalysis.skill_variations).length" class="variations-card">
          <h3 class="variations-title">
            <span class="variations-icon">≈</span>
            Semantic Matches
          </h3>
          <p class="variations-hint">Similar skills detected between job and resume</p>
          <div class="variations-list">
            <div
              v-for="(value, key) in skillAnalysis.skill_variations"
              :key="key"
              class="variation-item"
            >
              <span class="variation-job">{{ key }}</span>
              <span class="variation-arrow">→</span>
              <span class="variation-resume">{{ value }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Education Analysis -->
      <section v-if="educationAnalysis" class="education-section">
        <h2 class="education-title">Education Qualification</h2>

        <div class="education-cards">
          <div class="education-card">
            <h3 class="education-card-title">
              <span class="education-icon">🎓</span>
              Job Requirement
            </h3>
            <div v-if="educationAnalysis.job_highest" class="education-info">
              <span class="education-level">{{ educationAnalysis.job_highest.type }}</span>
              <span class="education-status" :class="educationAnalysis.meets_requirement ? 'meets' : 'below'">
                {{ educationAnalysis.meets_requirement ? 'Meets Requirement' : 'Below Requirement' }}
              </span>
            </div>
            <p v-else class="education-empty">No specific education requirement</p>
          </div>

          <div class="education-card">
            <h3 class="education-card-title">
              <span class="education-icon">📜</span>
              Resume Qualification
            </h3>
            <div v-if="educationAnalysis.resume_highest" class="education-info">
              <span class="education-level">{{ educationAnalysis.resume_highest.type }}</span>
            </div>
            <p v-else class="education-empty">No education found in resume</p>
          </div>
        </div>

        <div class="education-message" :class="educationAnalysis.meets_requirement ? 'success' : 'warning'">
          <span class="message-icon">{{ educationAnalysis.meets_requirement ? '✓' : '!' }}</span>
          <span>{{ educationAnalysis.meets_requirement_message }}</span>
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
const skillAnalysis = ref(null)
const educationAnalysis = ref(null)
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
  skillAnalysis.value = null
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
  skillAnalysis.value = null
  educationAnalysis.value = null
  try {
    const { data } = await analyzeResume(resumeFile.value, jobDescriptionResult.value)
    similarityScores.value = data.similarity_scores
    skillAnalysis.value = data.skill_analysis
    educationAnalysis.value = data.education_analysis
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

.skills-section {
  margin-top: 2.5rem;
}

.skills-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e1b4b;
  margin: 0 0 1rem;
}

.skills-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.75rem 1.25rem;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  border: 1px solid #e5e7eb;
}

.stat-badge.highlight {
  background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
  border: none;
}

.stat-badge.highlight .stat-value,
.stat-badge.highlight .stat-label {
  color: #fff;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e1b4b;
}

.stat-label {
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: 500;
}

.skills-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

@media (max-width: 640px) {
  .skills-container {
    grid-template-columns: 1fr;
  }
  .skills-stats {
    flex-wrap: wrap;
  }
}

.skills-card {
  background: #fff;
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.skills-card.matching {
  border-left: 4px solid #10b981;
}

.skills-card.missing {
  border-left: 4px solid #ef4444;
}

.skills-card-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 1rem;
  color: #1f2937;
}

.skills-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  font-size: 0.85rem;
  font-weight: 700;
}

.skills-card.matching .skills-icon {
  background: #d1fae5;
  color: #10b981;
}

.skills-card.missing .skills-icon {
  background: #fee2e2;
  color: #ef4444;
}

.skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.skill-tag {
  display: inline-block;
  padding: 0.35rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.skill-tag.matching {
  background: #d1fae5;
  color: #065f46;
}

.skill-tag.missing {
  background: #fee2e2;
  color: #991b1b;
}

.skills-empty {
  color: #9ca3af;
  font-size: 0.9rem;
  margin: 0;
  font-style: italic;
}

.variations-card {
  margin-top: 1.5rem;
  background: #fff;
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  border-left: 4px solid #8b5cf6;
}

.variations-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 0.25rem;
  color: #1f2937;
}

.variations-hint {
  color: #9ca3af;
  font-size: 0.85rem;
  margin: 0 0 1rem;
}

.variations-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  font-size: 0.85rem;
  font-weight: 700;
  background: #ede9fe;
  color: #7c3aed;
}

.variations-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.variation-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  background: #f9fafb;
  border-radius: 8px;
}

.variation-job {
  font-weight: 500;
  color: #1f2937;
}

.variation-arrow {
  color: #9ca3af;
  font-weight: 600;
}

.variation-resume {
  font-weight: 500;
  color: #059669;
}

.education-section {
  margin-top: 2.5rem;
}

.education-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e1b4b;
  margin: 0 0 1rem;
}

.education-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 1rem;
}

@media (max-width: 640px) {
  .education-cards {
    grid-template-columns: 1fr;
  }
}

.education-card {
  background: #fff;
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.education-card-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 1rem;
  color: #1f2937;
}

.education-icon {
  font-size: 1.25rem;
}

.education-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.education-level {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e1b4b;
}

.education-status {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  width: fit-content;
}

.education-status.meets {
  background: #d1fae5;
  color: #065f46;
}

.education-status.below {
  background: #fee2e2;
  color: #991b1b;
}

.education-empty {
  color: #9ca3af;
  font-size: 0.9rem;
  margin: 0;
  font-style: italic;
}

.education-message {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-radius: 10px;
  font-size: 0.95rem;
  font-weight: 500;
}

.education-message.success {
  background: #d1fae5;
  color: #065f46;
}

.education-message.warning {
  background: #fef3c7;
  color: #92400e;
}

.message-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  font-size: 1rem;
  font-weight: 700;
}

.education-message.success .message-icon {
  background: #10b981;
  color: #fff;
}

.education-message.warning .message-icon {
  background: #f59e0b;
  color: #fff;
}
</style>