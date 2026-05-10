<template>
  <div class="page">
    <!-- Header -->
    <nav class="navbar">
      <span class="brand">HireWise</span>
      <div class="nav-links">
        <RouterLink to="/dashboard">Dashboard</RouterLink>
        <!-- <RouterLink to="/jobs/analyze">Job Analyzer</RouterLink> -->
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

      <!-- Similarity Scores -->
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

      <!-- Overview Comparison -->
      <section v-if="overviewMatches !== null" class="overview-section">
        <h2 class="overview-title">Overview Comparison</h2>
        <p class="overview-hint">
          Semantic matches between job description overview and resume summary
        </p>

        <div class="overview-stats">
          <div class="stat-badge">
            <span class="stat-value">{{ overviewMatches.length }}</span>
            <span class="stat-label">Matched Pairs</span>
          </div>
          <div class="stat-badge highlight">
            <span class="stat-value">{{ overviewMatches.length ? overviewAvgScore : '0' }}%</span>
            <span class="stat-label">Avg Similarity</span>
          </div>
        </div>

        <div v-if="overviewMatches.length" class="overview-list">
          <div
            v-for="(match, idx) in overviewMatches"
            :key="idx"
            class="overview-item"
            :class="getMatchClass(match.similarity)"
          >
            <div class="overview-pair">
              <div class="overview-side job">
                <span class="overview-label">Job Description</span>
                <p class="overview-text">{{ match.job_sentence }}</p>
              </div>
              <div class="overview-connector">
                <span class="overview-arrow">↔</span>
                <span class="overview-score">{{ (match.similarity * 100).toFixed(0) }}%</span>
              </div>
              <div class="overview-side resume">
                <span class="overview-label">Resume Summary</span>
                <p class="overview-text">{{ match.resume_sentence }}</p>
              </div>
            </div>
            <div class="overview-bar-track">
              <div
                class="overview-bar-fill"
                :style="{ width: `${match.similarity * 100}%`, backgroundColor: getMatchColor(match.similarity) }"
              />
            </div>
          </div>
        </div>

        <div v-else class="overview-empty">
          No semantically matching overview sentences found — 0% match
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

        <div class="education-comparison">
          <div class="education-column">
            <h3 class="education-column-title">
              <span class="column-icon">📋</span>
              Job Requirement
            </h3>
            <div v-if="educationAnalysis.job_highest" class="education-details">
              <div class="edu-level-badge" :class="getLevelClass(educationAnalysis.job_highest.level_value)">
                {{ educationAnalysis.job_highest.level }}
              </div>
              <div v-if="educationAnalysis.job_highest.qualification_type" class="edu-detail">
                <span class="edu-label">Type:</span>
                <span class="edu-value">{{ educationAnalysis.job_highest.qualification_type }}</span>
              </div>
              <div v-if="educationAnalysis.job_highest.major" class="edu-detail">
                <span class="edu-label">Major:</span>
                <span class="edu-value">{{ educationAnalysis.job_highest.major }}</span>
              </div>
              <div class="edu-majors">
                <span class="majors-label">Majors Found:</span>
                <div class="majors-list">
                  <span v-for="major in educationAnalysis.job_majors" :key="major" class="major-tag job">
                    {{ major }}
                  </span>
                </div>
              </div>
            </div>
            <p v-else class="education-empty">No specific education requirement</p>
          </div>

          <div class="education-column">
            <h3 class="education-column-title">
              <span class="column-icon">📄</span>
              Resume Qualification
            </h3>
            <div v-if="educationAnalysis.resume_highest" class="education-details">
              <div class="edu-level-badge" :class="getLevelClass(educationAnalysis.resume_highest.level_value)">
                {{ educationAnalysis.resume_highest.level }}
              </div>
              <div v-if="educationAnalysis.resume_highest.qualification_type" class="edu-detail">
                <span class="edu-label">Type:</span>
                <span class="edu-value">{{ educationAnalysis.resume_highest.qualification_type }}</span>
              </div>
              <div v-if="educationAnalysis.resume_highest.major" class="edu-detail">
                <span class="edu-label">Major:</span>
                <span class="edu-value">{{ educationAnalysis.resume_highest.major }}</span>
              </div>
              <div class="edu-majors">
                <span class="majors-label">Majors Found:</span>
                <div class="majors-list">
                  <span v-for="major in educationAnalysis.resume_majors" :key="major" class="major-tag resume">
                    {{ major }}
                  </span>
                </div>
              </div>
            </div>
            <p v-else class="education-empty">No education found in resume</p>
          </div>
        </div>

        <div class="education-message" :class="educationAnalysis.meets_requirement ? 'success' : 'warning'">
          <span class="message-icon">{{ educationAnalysis.meets_requirement ? '✓' : '!' }}</span>
          <span>{{ educationAnalysis.meets_requirement_message }}</span>
        </div>

        <div v-if="educationAnalysis.matching_majors?.length" class="matching-majors">
          <h4 class="matching-title">
            <span class="matching-icon">🎯</span>
            Matching Majors
          </h4>
          <div class="matching-list">
            <span v-for="major in educationAnalysis.matching_majors" :key="major" class="matching-tag">
              {{ major }}
            </span>
          </div>
        </div>
      </section>

      <!-- Experience Analysis -->
      <section v-if="experienceAnalysis" class="experience-section">
        <h2 class="experience-title">Work Experience</h2>

        <div class="experience-cards">
          <div class="experience-card">
            <h3 class="experience-card-title">
              <span class="exp-icon">📋</span>
              Job Requirement
            </h3>
            <div v-if="experienceAnalysis.job_experience?.level" class="exp-details">
              <div class="exp-years-badge" :class="getExpClass(experienceAnalysis.job_experience.level_value)">
                {{ experienceAnalysis.job_experience.level }}
              </div>
              <p v-if="experienceAnalysis.job_experience.context" class="exp-context">
                "{{ experienceAnalysis.job_experience.context }}"
              </p>
            </div>
            <p v-else class="exp-empty">No specific experience requirement</p>
          </div>

          <div class="experience-card">
            <h3 class="experience-card-title">
              <span class="exp-icon">💼</span>
              Resume Experience
            </h3>
            <div v-if="experienceAnalysis.resume_experience?.level" class="exp-details">
              <div class="exp-years-badge" :class="getExpClass(experienceAnalysis.resume_experience.level_value)">
                {{ experienceAnalysis.resume_experience.level }}
              </div>
              <p v-if="experienceAnalysis.resume_experience.context" class="exp-context">
                "{{ experienceAnalysis.resume_experience.context }}"
              </p>
            </div>
            <p v-else class="exp-empty">No experience found in resume</p>
          </div>
        </div>

        <div class="exp-message" :class="experienceAnalysis.meets_requirement ? 'success' : 'warning'">
          <span class="exp-msg-icon">{{ experienceAnalysis.meets_requirement ? '✓' : '!' }}</span>
          <span>{{ experienceAnalysis.meets_message }}</span>
        </div>
      </section>

      <!-- Responsibility & Duties Analysis -->
      <section v-if="responsibilityAnalysis" class="responsibility-section">
        <h2 class="resp-title">Responsibilities vs Experience Analysis</h2>

        <div class="resp-score-card" :class="getRespScoreClass(responsibilityAnalysis.score)">
          <div class="resp-score-value">{{ responsibilityAnalysis.score }}%</div>
          <div class="resp-score-label">Duties Match</div>
        </div>

        <p class="resp-explanation">{{ responsibilityAnalysis.explanation }}</p>

        <div v-if="responsibilityAnalysis.matched_duties?.length" class="resp-matched">
          <h3 class="resp-subtitle">Matched Duties</h3>
          <div class="duty-list">
            <div v-for="(duty, idx) in responsibilityAnalysis.matched_duties" :key="idx" class="duty-item">
              <div class="duty-connection">
                <span class="duty-job">{{ duty.job_duty }}</span>
                <span class="duty-arrow">↔</span>
                <span class="duty-resume">{{ duty.experience_duty }}</span>
              </div>
              <span class="duty-similarity">{{ (duty.similarity * 100).toFixed(0) }}% match</span>
            </div>
          </div>
        </div>

        <div v-if="responsibilityAnalysis.unmatched_responsibilities?.length" class="resp-unmatched">
          <h3 class="resp-subtitle">Job Duties Not Found in Resume</h3>
          <div class="unmatched-list">
            <span v-for="duty in responsibilityAnalysis.unmatched_responsibilities" :key="duty" class="unmatched-item">
              {{ duty }}
            </span>
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
const skillAnalysis = ref(null)
const educationAnalysis = ref(null)
const experienceAnalysis = ref(null)
const responsibilityAnalysis = ref(null)
const similarityScores = ref(null)
const overviewMatches = ref(null)
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

const overviewAvgScore = computed(() => {
  if (!overviewMatches.value?.length) return 0
  const sum = overviewMatches.value.reduce((acc, m) => acc + m.similarity, 0)
  return ((sum / overviewMatches.value.length) * 100).toFixed(0)
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
  overviewMatches.value = null
  skillAnalysis.value = null
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
  overviewMatches.value = null
  skillAnalysis.value = null
  educationAnalysis.value = null
  experienceAnalysis.value = null
  responsibilityAnalysis.value = null
  try {
    const { data } = await analyzeResume(resumeFile.value, jobDescriptionResult.value)
    similarityScores.value = data.similarity_scores
    overviewMatches.value = data.overview_matches
    skillAnalysis.value = data.skill_analysis
    educationAnalysis.value = data.education_analysis
    experienceAnalysis.value = data.experience_analysis
    responsibilityAnalysis.value = data.responsibility_analysis
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

function getLevelClass(levelValue) {
  if (!levelValue) return ''
  if (levelValue >= 5) return 'phd'
  if (levelValue >= 4) return 'master'
  if (levelValue >= 3) return 'bachelor'
  if (levelValue >= 2) return 'associate'
  return 'certificate'
}

function getExpClass(levelValue) {
  if (!levelValue) return ''
  if (levelValue >= 7) return 'expert'
  if (levelValue >= 6) return 'principal'
  if (levelValue >= 5) return 'lead'
  if (levelValue >= 4) return 'senior'
  if (levelValue >= 3) return 'mid'
  if (levelValue >= 2) return 'junior'
  return 'entry'
}

function getRespScoreClass(score) {
  if (!score) return ''
  if (score >= 80) return 'high'
  if (score >= 50) return 'medium'
  return 'low'
}

function getMatchClass(similarity) {
  if (similarity >= 0.7) return 'high'
  if (similarity >= 0.4) return 'medium'
  return 'low'
}

function getMatchColor(similarity) {
  if (similarity >= 0.7) return '#10b981'
  if (similarity >= 0.4) return '#f59e0b'
  return '#ef4444'
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

.overview-section {
  margin-top: 2.5rem;
}

.overview-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e1b4b;
  margin: 0 0 0.25rem;
}

.overview-hint {
  color: #9ca3af;
  font-size: 0.85rem;
  margin: 0 0 1rem;
}

.overview-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.overview-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.overview-item {
  background: #fff;
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  border-left: 4px solid #e5e7eb;
}

.overview-item.high {
  border-left-color: #10b981;
}

.overview-item.medium {
  border-left-color: #f59e0b;
}

.overview-item.low {
  border-left-color: #ef4444;
}

.overview-pair {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.overview-side {
  flex: 1;
  min-width: 0;
}

.overview-label {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #9ca3af;
  display: block;
  margin-bottom: 0.35rem;
}

.overview-side.job .overview-label {
  color: #7c3aed;
}

.overview-side.resume .overview-label {
  color: #059669;
}

.overview-text {
  margin: 0;
  font-size: 0.875rem;
  color: #374151;
  line-height: 1.55;
}

.overview-connector {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  padding-top: 1.25rem;
  flex-shrink: 0;
}

.overview-arrow {
  color: #9ca3af;
  font-size: 1.1rem;
}

.overview-score {
  font-size: 0.8rem;
  font-weight: 700;
  color: #6b7280;
  white-space: nowrap;
}

.overview-bar-track {
  height: 4px;
  background: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
}

.overview-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.5s ease-out;
}

@media (max-width: 640px) {
  .overview-pair {
    flex-direction: column;
    gap: 0.5rem;
  }
  .overview-connector {
    flex-direction: row;
    padding-top: 0;
    width: 100%;
    justify-content: center;
  }
}

.overview-empty {
  text-align: center;
  padding: 2rem 1rem;
  color: #9ca3af;
  font-size: 0.95rem;
  font-style: italic;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
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

.education-comparison {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 1rem;
}

@media (max-width: 640px) {
  .education-comparison {
    grid-template-columns: 1fr;
  }
}

.education-column {
  background: #fff;
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.education-column-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 1rem;
  color: #1f2937;
}

.column-icon {
  font-size: 1.25rem;
}

.education-details {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.edu-level-badge {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 700;
  width: fit-content;
}

.edu-level-badge.phd {
  background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
  color: #fff;
}

.edu-level-badge.master {
  background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
  color: #fff;
}

.edu-level-badge.bachelor {
  background: linear-gradient(135deg, #059669 0%, #10b981 100%);
  color: #fff;
}

.edu-level-badge.associate {
  background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%);
  color: #fff;
}

.edu-level-badge.certificate {
  background: linear-gradient(135deg, #6b7280 0%, #9ca3af 100%);
  color: #fff;
}

.edu-detail {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.edu-label {
  font-size: 0.75rem;
  color: #9ca3af;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.edu-value {
  font-size: 0.95rem;
  color: #1f2937;
  font-weight: 500;
}

.edu-majors {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 0.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid #e5e7eb;
}

.majors-label {
  font-size: 0.75rem;
  color: #9ca3af;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.majors-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.major-tag {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 16px;
  font-size: 0.85rem;
  font-weight: 500;
}

.major-tag.job {
  background: #ede9fe;
  color: #7c3aed;
}

.major-tag.resume {
  background: #d1fae5;
  color: #065f46;
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

.matching-majors {
  margin-top: 1rem;
  background: #fff;
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  border-left: 4px solid #10b981;
}

.matching-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 0.75rem;
  color: #1f2937;
}

.matching-icon {
  font-size: 1.1rem;
}

.matching-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.matching-tag {
  display: inline-block;
  padding: 0.35rem 0.85rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #065f46;
}

.experience-section {
  margin-top: 2.5rem;
}

.experience-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e1b4b;
  margin: 0 0 1rem;
}

.experience-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 1rem;
}

@media (max-width: 640px) {
  .experience-cards {
    grid-template-columns: 1fr;
  }
}

.experience-card {
  background: #fff;
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.experience-card-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 1rem;
  color: #1f2937;
}

.exp-icon {
  font-size: 1.25rem;
}

.exp-details {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.exp-years-badge {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  width: fit-content;
  color: #fff;
}

.exp-years-badge.expert {
  background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
}

.exp-years-badge.principal {
  background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
}

.exp-years-badge.lead {
  background: linear-gradient(135deg, #ea580c 0%, #f97316 100%);
}

.exp-years-badge.senior {
  background: linear-gradient(135deg, #ca8a04 0%, #eab308 100%);
}

.exp-years-badge.mid {
  background: linear-gradient(135deg, #16a34a 0%, #22c55e 100%);
}

.exp-years-badge.junior {
  background: linear-gradient(135deg, #0891b2 0%, #06b6d4 100%);
}

.exp-years-badge.entry {
  background: linear-gradient(135deg, #6b7280 0%, #9ca3af 100%);
}

.exp-context {
  font-size: 0.85rem;
  color: #6b7280;
  font-style: italic;
  margin: 0;
  padding: 0.5rem;
  background: #f9fafb;
  border-radius: 6px;
}

.exp-empty {
  color: #9ca3af;
  font-size: 0.9rem;
  margin: 0;
  font-style: italic;
}

.exp-message {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-radius: 10px;
  font-size: 0.95rem;
  font-weight: 500;
}

.exp-message.success {
  background: #d1fae5;
  color: #065f46;
}

.exp-message.warning {
  background: #fef3c7;
  color: #92400e;
}

.exp-msg-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  font-size: 1rem;
  font-weight: 700;
}

.exp-message.success .exp-msg-icon {
  background: #10b981;
  color: #fff;
}

.exp-message.warning .exp-msg-icon {
  background: #f59e0b;
  color: #fff;
}

.responsibility-section {
  margin-top: 2.5rem;
  background: #fff;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.resp-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e1b4b;
  margin: 0 0 1rem;
}

.resp-score-card {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  margin-bottom: 1rem;
}

.resp-score-card.high {
  background: linear-gradient(135deg, #059669 0%, #10b981 100%);
  color: #fff;
}

.resp-score-card.medium {
  background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%);
  color: #fff;
}

.resp-score-card.low {
  background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
  color: #fff;
}

.resp-score-value {
  font-size: 2rem;
  font-weight: 800;
}

.resp-score-label {
  font-size: 0.85rem;
  font-weight: 500;
}

.resp-explanation {
  font-size: 0.95rem;
  color: #4b5563;
  line-height: 1.5;
  margin-bottom: 1.25rem;
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 8px;
  border-left: 3px solid #6366f1;
}

.resp-subtitle {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.75rem;
}

.resp-matched {
  margin-bottom: 1.25rem;
}

.duty-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.duty-item {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding: 0.75rem;
  background: #f0fdf4;
  border-radius: 8px;
  border-left: 3px solid #10b981;
}

.duty-connection {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
}

.duty-job {
  flex: 1;
  font-size: 0.85rem;
  color: #7c3aed;
  font-weight: 500;
}

.duty-arrow {
  color: #9ca3af;
}

.duty-resume {
  flex: 1;
  font-size: 0.85rem;
  color: #059669;
  font-weight: 500;
}

.duty-similarity {
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: 600;
}

.resp-unmatched {
  margin-top: 1rem;
}

.unmatched-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.unmatched-item {
  display: inline-block;
  padding: 0.35rem 0.75rem;
  background: #fef2f2;
  color: #991b1b;
  border-radius: 16px;
  font-size: 0.85rem;
  font-weight: 500;
}
</style>