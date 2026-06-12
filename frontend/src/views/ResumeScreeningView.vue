<template>
  <div class="page">
    <nav class="navbar">
      <span class="brand">HireWise</span>
      <div class="nav-links">
        <RouterLink to="/dashboard">Dashboard</RouterLink>
        <button class="btn-logout" @click="handleLogout">Logout</button>
      </div>
    </nav>

    <main class="content">

      <!-- ── Phase 1: upload JD ───────────────────────────────────────── -->
      <template v-if="!session">
        <h1>Resume Screening Dashboard</h1>
        <p class="subtitle">Upload a job description to start screening and ranking multiple resumes.</p>

        <div class="setup-card">
          <div class="setup-icon">🏆</div>
          <h2 class="setup-title">Step 1 — Upload Job Description</h2>
          <p class="setup-hint">Supports PDF and DOCX · max 10 MB</p>

          <div
            class="upload-zone"
            :class="{ dragging: jdDragging, loading: jdLoading }"
            @dragover.prevent="jdDragging = true"
            @dragleave.prevent="jdDragging = false"
            @drop.prevent="onJdDrop"
            @click="!jdLoading && jdFileInput.click()"
          >
            <input ref="jdFileInput" type="file" accept=".pdf,.docx,.doc" class="hidden" @change="onJdChange" />

            <template v-if="jdLoading">
              <span class="spinner-lg" />
              <p class="upload-status">Analyzing job description…</p>
            </template>
            <template v-else-if="jdFile">
              <span class="file-emoji">{{ jdFile.name.endsWith('.pdf') ? '📕' : '📘' }}</span>
              <p class="upload-filename">{{ jdFile.name }}</p>
              <p class="upload-size">{{ fileSizeLabel(jdFile) }}</p>
            </template>
            <template v-else>
              <span class="upload-emoji">📄</span>
              <p class="upload-cta">Drag & drop or <span class="link">browse</span></p>
            </template>
          </div>

          <p v-if="error" class="error">{{ error }}</p>
        </div>
      </template>

      <!-- ── Phase 2: screening ──────────────────────────────────────── -->
      <template v-else>
        <div class="screening-header">
          <div class="screening-jd-info">
            <span class="jd-chip">Job Description</span>
            <h1 class="screening-title">{{ session.title }}</h1>
          </div>
          <button class="btn-outline" @click="resetSession">Change JD</button>
        </div>

        <!-- Upload bar -->
        <div class="upload-bar">
          <div
            class="upload-bar-zone"
            :class="{ dragging: resumeDragging }"
            @dragover.prevent="resumeDragging = true"
            @dragleave.prevent="resumeDragging = false"
            @drop.prevent="onResumeDrop"
            @click="resumeFileInput.click()"
          >
            <input
              ref="resumeFileInput"
              type="file"
              accept=".pdf,.docx,.doc"
              multiple
              class="hidden"
              @change="onResumeFilesChange"
            />
            <span class="upload-bar-icon">📃</span>
            <span class="upload-bar-text">
              Drop resumes here or <span class="link">browse</span> — multiple files supported
            </span>
          </div>
        </div>

        <p v-if="uploadError" class="error">{{ uploadError }}</p>

        <!-- Processing queue -->
        <div v-if="processingQueue.length" class="queue-list">
          <div
            v-for="item in processingQueue"
            :key="item.id"
            class="queue-item"
            :class="item.status"
          >
            <span v-if="item.status === 'processing'" class="spinner-sm" />
            <span v-else-if="item.status === 'error'" class="queue-icon-err">✗</span>
            <span v-else class="queue-icon-wait">…</span>
            <span class="queue-filename">{{ item.name }}</span>
            <span class="queue-label">
              {{ item.status === 'processing' ? 'Analyzing…' : item.status === 'error' ? item.error : 'Queued' }}
            </span>
          </div>
        </div>

        <!-- Empty state -->
        <div v-if="rankedResumes.length === 0 && processingQueue.length === 0" class="empty-state">
          <div class="empty-icon">📋</div>
          <p class="empty-title">No resumes yet</p>
          <p class="empty-hint">Upload one or more resumes above to see them ranked.</p>
        </div>

        <!-- Ranked list -->
        <div v-else-if="rankedResumes.length > 0" class="ranked-section">
          <div class="ranked-header">
            <h2 class="ranked-title">Rankings</h2>
            <span class="ranked-count">{{ rankedResumes.length }} resume{{ rankedResumes.length !== 1 ? 's' : '' }}</span>
          </div>

          <div class="ranked-list">
            <div
              v-for="(resume, idx) in rankedResumes"
              :key="resume.id"
              class="rank-card"
              @click="openDetail(resume)"
            >
              <!-- Rank badge -->
              <div class="rank-num" :class="rankBadgeClass(idx)">{{ idx + 1 }}</div>

              <!-- Main body -->
              <div class="rank-body">
                <div class="rank-filename">{{ resume.filename }}</div>

                <!-- Mini score bars -->
                <div class="rank-bars">
                  <div class="rank-bar-row">
                    <span class="bar-label">Skills</span>
                    <div class="bar-track">
                      <div class="bar-fill skills" :style="{ width: resume.score_breakdown.skills + '%' }" />
                    </div>
                    <span class="bar-pct">{{ resume.score_breakdown.skills }}%</span>
                  </div>
                  <div class="rank-bar-row">
                    <span class="bar-label">Duties</span>
                    <div class="bar-track">
                      <div class="bar-fill duties" :style="{ width: resume.score_breakdown.responsibilities + '%' }" />
                    </div>
                    <span class="bar-pct">{{ resume.score_breakdown.responsibilities }}%</span>
                  </div>
                </div>

                <!-- Status badges -->
                <div class="rank-badges">
                  <span class="status-badge" :class="resume.score_breakdown.education_met ? 'ok' : 'no'">
                    {{ resume.score_breakdown.education_met ? '✓' : '✗' }} Education
                  </span>
                  <span class="status-badge" :class="resume.score_breakdown.experience_met ? 'ok' : 'no'">
                    {{ resume.score_breakdown.experience_met ? '✓' : '✗' }} Experience
                  </span>
                  <span v-if="resume.score_breakdown.certifications > 0" class="status-badge cert">
                    🏆 Cert {{ resume.score_breakdown.certifications }}%
                  </span>
                  <span v-if="resume.score_breakdown.projects > 0" class="status-badge proj">
                    📁 Projects {{ resume.score_breakdown.projects }}%
                  </span>
                </div>
              </div>

              <!-- Composite score -->
              <div class="rank-score-box" :class="scoreBoxClass(resume.rank_score)">
                <span class="rank-score-num">{{ resume.rank_score }}</span>
                <span class="rank-score-lbl">/ 100</span>
              </div>

              <span class="rank-arrow">›</span>
            </div>
          </div>
        </div>
      </template>
    </main>

    <!-- Detail panel -->
    <ResumeDetailPanel
      v-if="detailResume"
      :resume="detailResume"
      @close="detailResume = null"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { createJobSession, uploadResumeToSession } from '@/api/jobs'
import ResumeDetailPanel from '@/components/ResumeDetailPanel.vue'

const auth = useAuthStore()
const router = useRouter()

const jdFileInput = ref(null)
const resumeFileInput = ref(null)
const jdFile = ref(null)
const jdLoading = ref(false)
const jdDragging = ref(false)
const resumeDragging = ref(false)
const error = ref('')
const uploadError = ref('')

const session = ref(null)          // { id, title }
const rankedResumes = ref([])      // sorted by rank_score desc
const processingQueue = ref([])    // { id, name, status, error }
let queueCounter = 0
let draining = false

const detailResume = ref(null)

// ── helpers ────────────────────────────────────────────────────────────────

function fileSizeLabel(file) {
  const kb = file.size / 1024
  return kb > 1024 ? `${(kb / 1024).toFixed(1)} MB` : `${kb.toFixed(0)} KB`
}

function validateFile(file) {
  const ext = file.name.split('.').pop().toLowerCase()
  if (!['pdf', 'docx', 'doc'].includes(ext)) return 'Only PDF and DOCX files are supported.'
  if (file.size > 10 * 1024 * 1024) return 'File size must not exceed 10 MB.'
  return null
}

function rankBadgeClass(idx) {
  if (idx === 0) return 'gold'
  if (idx === 1) return 'silver'
  if (idx === 2) return 'bronze'
  return 'default'
}

function scoreBoxClass(score) {
  if (score >= 70) return 'high'
  if (score >= 45) return 'medium'
  return 'low'
}

// ── JD upload ──────────────────────────────────────────────────────────────

function onJdChange(e) {
  const file = e.target.files[0]
  if (file) startJdUpload(file)
}

function onJdDrop(e) {
  jdDragging.value = false
  const file = e.dataTransfer.files[0]
  if (file) startJdUpload(file)
}

async function startJdUpload(file) {
  const err = validateFile(file)
  if (err) { error.value = err; return }
  error.value = ''
  jdFile.value = file
  jdLoading.value = true
  try {
    const { data } = await createJobSession(file)
    session.value = { id: data.session_id, title: data.title }
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to analyze job description.'
    jdFile.value = null
  } finally {
    jdLoading.value = false
  }
}

function resetSession() {
  session.value = null
  jdFile.value = null
  rankedResumes.value = []
  processingQueue.value = []
  error.value = ''
  uploadError.value = ''
  if (jdFileInput.value) jdFileInput.value.value = ''
}

// ── Resume queue ───────────────────────────────────────────────────────────

function onResumeFilesChange(e) {
  enqueueFiles(Array.from(e.target.files))
  e.target.value = ''
}

function onResumeDrop(e) {
  resumeDragging.value = false
  enqueueFiles(Array.from(e.dataTransfer.files))
}

function enqueueFiles(files) {
  uploadError.value = ''
  for (const file of files) {
    const err = validateFile(file)
    if (err) { uploadError.value = err; continue }
    processingQueue.value.push({ id: ++queueCounter, name: file.name, file, status: 'pending', error: '' })
  }
  drainQueue()
}

async function drainQueue() {
  if (draining) return
  draining = true
  while (true) {
    const next = processingQueue.value.find(i => i.status === 'pending')
    if (!next) break
    next.status = 'processing'
    try {
      const { data } = await uploadResumeToSession(session.value.id, next.file)
      rankedResumes.value.push(data)
      rankedResumes.value.sort((a, b) => b.rank_score - a.rank_score)
      processingQueue.value = processingQueue.value.filter(i => i.id !== next.id)
    } catch (e) {
      next.status = 'error'
      next.error = e.response?.data?.detail || 'Analysis failed'
    }
  }
  draining = false
}

// ── Detail panel ───────────────────────────────────────────────────────────

function openDetail(resume) {
  detailResume.value = resume
}

// ── Auth ───────────────────────────────────────────────────────────────────

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

/* ── Navbar ──────────────────────────────────────────────────────────────── */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: #fff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  position: sticky;
  top: 0;
  z-index: 100;
}
.brand { font-weight: 800; font-size: 1.35rem; color: #4f46e5; letter-spacing: -0.02em; }
.nav-links { display: flex; align-items: center; gap: 1.5rem; }
.nav-links a { color: #6b7280; text-decoration: none; font-weight: 500; font-size: 0.95rem; transition: color 0.15s; }
.nav-links a:hover { color: #4f46e5; }
.btn-logout {
  padding: 0.5rem 1.25rem; background: transparent; color: #4f46e5;
  border: 1.5px solid #4f46e5; border-radius: 8px; cursor: pointer;
  font-size: 0.9rem; font-weight: 600; transition: all 0.2s;
}
.btn-logout:hover { background: #4f46e5; color: #fff; }

/* ── Main content ─────────────────────────────────────────────────────────── */
.content { max-width: 860px; margin: 0 auto; padding: 3rem 1.5rem; }

h1 { margin: 0 0 0.4rem; font-size: 1.85rem; font-weight: 800; color: #1e1b4b; letter-spacing: -0.02em; }
.subtitle { color: #6b7280; font-size: 1rem; margin: 0 0 2.5rem; }

/* ── Setup card (phase 1) ─────────────────────────────────────────────────── */
.setup-card {
  background: #fff;
  border-radius: 20px;
  padding: 2.5rem;
  box-shadow: 0 4px 24px rgba(79,70,229,0.08);
  border: 1px solid #e0e7ff;
  text-align: center;
  max-width: 520px;
  margin: 0 auto;
}
.setup-icon { font-size: 3rem; margin-bottom: 0.75rem; }
.setup-title { font-size: 1.25rem; font-weight: 700; color: #1e1b4b; margin: 0 0 0.4rem; }
.setup-hint { color: #9ca3af; font-size: 0.9rem; margin: 0 0 1.5rem; }

.upload-zone {
  border: 2px dashed #c7d2fe;
  border-radius: 14px;
  padding: 2.5rem 1rem;
  cursor: pointer;
  transition: all 0.25s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  min-height: 140px;
  justify-content: center;
}
.upload-zone:hover { border-color: #a5b4fc; background: #f5f7ff; }
.upload-zone.dragging { border-color: #4f46e5; background: #eef2ff; transform: scale(1.01); }
.upload-zone.loading { cursor: default; opacity: 0.85; }

.upload-emoji { font-size: 2.5rem; }
.upload-cta { margin: 0; color: #6b7280; font-size: 0.95rem; }
.upload-filename { font-weight: 600; color: #1f2937; margin: 0; word-break: break-all; }
.upload-size { color: #9ca3af; font-size: 0.85rem; margin: 0; }
.upload-status { color: #6b7280; font-size: 0.95rem; margin: 0; }
.file-emoji { font-size: 2.5rem; }

.link { color: #4f46e5; font-weight: 600; text-decoration: underline; text-underline-offset: 2px; cursor: pointer; }
.hidden { display: none; }

.error {
  margin-top: 1rem; color: #dc2626; font-size: 0.9rem;
  padding: 0.75rem 1rem; background: #fef2f2;
  border-radius: 10px; border-left: 3px solid #dc2626;
}

/* ── Screening header ────────────────────────────────────────────────────── */
.screening-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.75rem;
}
.jd-chip {
  display: inline-block; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.06em;
  text-transform: uppercase; padding: 0.2rem 0.6rem; background: #eef2ff;
  color: #4f46e5; border-radius: 20px; margin-bottom: 0.4rem;
}
.screening-title { margin: 0; font-size: 1.5rem; font-weight: 800; color: #1e1b4b; }
.btn-outline {
  padding: 0.5rem 1.1rem; background: transparent; color: #4f46e5;
  border: 1.5px solid #c7d2fe; border-radius: 8px; cursor: pointer;
  font-size: 0.85rem; font-weight: 600; transition: all 0.2s; white-space: nowrap; flex-shrink: 0;
}
.btn-outline:hover { border-color: #4f46e5; background: #eef2ff; }

/* ── Upload bar ──────────────────────────────────────────────────────────── */
.upload-bar { margin-bottom: 1.25rem; }
.upload-bar-zone {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.85rem 1.25rem;
  border: 2px dashed #c7d2fe; border-radius: 12px;
  background: #fff; cursor: pointer; transition: all 0.2s;
}
.upload-bar-zone:hover { border-color: #a5b4fc; background: #f5f7ff; }
.upload-bar-zone.dragging { border-color: #4f46e5; background: #eef2ff; }
.upload-bar-icon { font-size: 1.4rem; }
.upload-bar-text { color: #6b7280; font-size: 0.9rem; }

/* ── Processing queue ────────────────────────────────────────────────────── */
.queue-list { display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 1.25rem; }
.queue-item {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.6rem 1rem; background: #fff;
  border-radius: 8px; border: 1px solid #e5e7eb; font-size: 0.875rem;
}
.queue-item.processing { border-color: #c7d2fe; background: #f5f7ff; }
.queue-item.error { border-color: #fecaca; background: #fef2f2; }
.queue-filename { flex: 1; font-weight: 500; color: #1f2937; }
.queue-label { font-size: 0.8rem; color: #6b7280; }
.queue-item.error .queue-label { color: #dc2626; }
.queue-icon-err { color: #ef4444; font-weight: 700; }
.queue-icon-wait { color: #9ca3af; }

/* ── Empty state ─────────────────────────────────────────────────────────── */
.empty-state { text-align: center; padding: 4rem 1rem; }
.empty-icon { font-size: 3rem; margin-bottom: 1rem; }
.empty-title { font-size: 1.1rem; font-weight: 600; color: #1f2937; margin: 0 0 0.4rem; }
.empty-hint { color: #9ca3af; font-size: 0.9rem; margin: 0; }

/* ── Ranked list ─────────────────────────────────────────────────────────── */
.ranked-section { margin-top: 0.5rem; }
.ranked-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 1rem;
}
.ranked-title { font-size: 1.2rem; font-weight: 700; color: #1e1b4b; margin: 0; }
.ranked-count {
  font-size: 0.8rem; font-weight: 600; padding: 0.2rem 0.75rem;
  background: #eef2ff; color: #4f46e5; border-radius: 20px;
}

.ranked-list { display: flex; flex-direction: column; gap: 0.75rem; }

.rank-card {
  display: flex; align-items: center; gap: 1rem;
  background: #fff; border-radius: 14px; padding: 1rem 1.25rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1.5px solid #f3f4f6;
  cursor: pointer; transition: all 0.2s;
}
.rank-card:hover {
  border-color: #c7d2fe;
  box-shadow: 0 6px 24px rgba(79,70,229,0.1);
  transform: translateY(-2px);
}

/* rank number badge */
.rank-num {
  width: 38px; height: 38px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 1rem; font-weight: 800; flex-shrink: 0;
}
.rank-num.gold   { background: linear-gradient(135deg,#f59e0b,#fbbf24); color:#fff; }
.rank-num.silver { background: linear-gradient(135deg,#6b7280,#9ca3af); color:#fff; }
.rank-num.bronze { background: linear-gradient(135deg,#b45309,#d97706); color:#fff; }
.rank-num.default{ background: #f3f4f6; color: #6b7280; }

.rank-body { flex: 1; min-width: 0; }
.rank-filename {
  font-weight: 600; color: #1f2937; font-size: 0.95rem;
  margin-bottom: 0.5rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

/* mini score bars */
.rank-bars { display: flex; flex-direction: column; gap: 0.3rem; margin-bottom: 0.5rem; }
.rank-bar-row { display: flex; align-items: center; gap: 0.4rem; }
.bar-label { font-size: 0.7rem; color: #9ca3af; font-weight: 600; width: 34px; flex-shrink: 0; }
.bar-track {
  flex: 1; height: 5px; background: #e5e7eb; border-radius: 3px; overflow: hidden;
}
.bar-fill { height: 100%; border-radius: 3px; transition: width 0.6s ease-out; }
.bar-fill.skills { background: linear-gradient(90deg, #4f46e5, #818cf8); }
.bar-fill.duties { background: linear-gradient(90deg, #0ea5e9, #38bdf8); }
.bar-pct { font-size: 0.7rem; font-weight: 600; color: #6b7280; width: 30px; text-align: right; flex-shrink: 0; }

/* status badges */
.rank-badges { display: flex; flex-wrap: wrap; gap: 0.35rem; }
.status-badge {
  font-size: 0.7rem; font-weight: 600; padding: 0.18rem 0.55rem; border-radius: 12px;
}
.status-badge.ok   { background: #d1fae5; color: #065f46; }
.status-badge.no   { background: #fee2e2; color: #991b1b; }
.status-badge.cert { background: #fef3c7; color: #92400e; }
.status-badge.proj { background: #e0f2fe; color: #0369a1; }

/* composite score box */
.rank-score-box {
  display: flex; flex-direction: column; align-items: center;
  padding: 0.6rem 0.85rem; border-radius: 10px; flex-shrink: 0; min-width: 64px;
}
.rank-score-box.high   { background: linear-gradient(135deg,#d1fae5,#a7f3d0); }
.rank-score-box.medium { background: linear-gradient(135deg,#fef3c7,#fde68a); }
.rank-score-box.low    { background: linear-gradient(135deg,#fee2e2,#fecaca); }
.rank-score-num { font-size: 1.35rem; font-weight: 800; color: #1e1b4b; line-height: 1; }
.rank-score-lbl { font-size: 0.65rem; color: #6b7280; font-weight: 600; }

.rank-arrow { font-size: 1.4rem; color: #c7d2fe; flex-shrink: 0; transition: all 0.2s; }
.rank-card:hover .rank-arrow { color: #4f46e5; transform: translateX(3px); }

/* ── Spinners ─────────────────────────────────────────────────────────────── */
.spinner-lg {
  width: 36px; height: 36px; border: 3px solid #e0e7ff; border-top-color: #4f46e5;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
.spinner-sm {
  width: 14px; height: 14px; border: 2px solid #e0e7ff; border-top-color: #4f46e5;
  border-radius: 50%; animation: spin 0.7s linear infinite; flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
