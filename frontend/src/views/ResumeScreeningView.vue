<template>
  <div class="page">

    <!-- Navbar -->
    <nav class="navbar">
      <div class="nav-brand">
        <img src="../assets/logo-new.png" alt="Logo" style="width: 50px; height: 50px; margin-top: 0%;" />
        <span class="brand-name">HireWise</span>
      </div>
      <div class="nav-links">
        <RouterLink to="/dashboard">Dashboard</RouterLink>
        <button class="btn-logout" @click="handleLogout">Sign out</button>
      </div>
    </nav>

    <main class="content">

      <!-- ── Phase 1: Setup ──────────────────────────────────────────────── -->
      <Transition name="phase">
        <div v-if="!session" class="setup-phase" key="setup">
          <div class="setup-hero">
            <div class="setup-icon-ring">🏆</div>
            <h1 class="setup-title">Resume Screening Dashboard</h1>
            <p class="setup-sub">Upload a job description to create a screening session, then rank as many resumes as you need.</p>
          </div>

          <div
            class="jd-drop-zone"
            :class="{ dragging: jdDragging, loading: jdLoading }"
            @dragover.prevent="jdDragging = true"
            @dragleave.prevent="jdDragging = false"
            @drop.prevent="onJdDrop"
            @click="!jdLoading && jdFileInput.click()"
          >
            <input ref="jdFileInput" type="file" accept=".pdf,.docx,.doc" class="sr-only" @change="onJdChange" />

            <Transition name="fade" mode="out-in">
              <div v-if="jdLoading" key="loading" class="dz-state">
                <div class="dz-spinner" />
                <p class="dz-label">Analyzing job description…</p>
              </div>
              <div v-else-if="jdFile" key="file" class="dz-state">
                <span class="dz-file-icon">{{ jdFile.name.endsWith('.pdf') ? '📕' : '📘' }}</span>
                <p class="dz-filename">{{ jdFile.name }}</p>
                <p class="dz-size">{{ fileSizeLabel(jdFile) }}</p>
              </div>
              <div v-else key="empty" class="dz-state">
                <div class="dz-upload-icon">
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M12 12V4M8 8l4-4 4 4"/>
                  </svg>
                </div>
                <p class="dz-cta">Drop your job description here</p>
                <p class="dz-hint">or <span class="link">browse files</span> — PDF &amp; DOCX supported</p>
              </div>
            </Transition>
          </div>

          <Transition name="slide-down">
            <div v-if="error" class="alert alert-error">
              <span>⚠</span> {{ error }}
            </div>
          </Transition>

          <div class="setup-steps">
            <div class="step"><span class="step-num">1</span><span>Upload job description</span></div>
            <span class="step-divider">→</span>
            <div class="step step-muted"><span class="step-num">2</span><span>Upload resumes</span></div>
            <span class="step-divider">→</span>
            <div class="step step-muted"><span class="step-num">3</span><span>View ranked results</span></div>
          </div>
        </div>
      </Transition>

      <!-- ── Phase 2: Screening ──────────────────────────────────────────── -->
      <Transition name="phase">
        <div v-if="session" class="screening-phase" key="screening">

          <!-- Header -->
          <div class="screen-header">
            <div class="screen-jd">
              <span class="jd-label">Screening for</span>
              <h1 class="screen-title">{{ session.title }}</h1>
            </div>
            <button class="btn-ghost" @click="resetSession">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M19 12H5M12 5l-7 7 7 7"/>
              </svg>
              New session
            </button>
          </div>

          <!-- Upload bar -->
          <div
            class="upload-bar"
            :class="{ dragging: resumeDragging }"
            @dragover.prevent="resumeDragging = true"
            @dragleave.prevent="resumeDragging = false"
            @drop.prevent="onResumeDrop"
            @click="resumeFileInput.click()"
          >
            <input ref="resumeFileInput" type="file" accept=".pdf,.docx,.doc" multiple class="sr-only" @change="onResumeFilesChange" />
            <div class="upload-bar-inner">
              <div class="upload-bar-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 5v14M5 12l7-7 7 7"/><path d="M4 20h16"/>
                </svg>
              </div>
              <div>
                <p class="upload-bar-text">Drop resumes here or <span class="link">browse</span></p>
                <p class="upload-bar-hint">Multiple files supported · PDF &amp; DOCX</p>
              </div>
            </div>
          </div>

          <Transition name="slide-down">
            <div v-if="uploadError" class="alert alert-error">
              <span>⚠</span> {{ uploadError }}
            </div>
          </Transition>

          <!-- Processing queue -->
          <TransitionGroup name="queue" tag="div" class="queue-list">
            <div
              v-for="item in processingQueue"
              :key="item.id"
              class="queue-item"
              :class="item.status"
            >
              <div class="queue-status-icon">
                <span v-if="item.status === 'processing'" class="q-spinner" />
                <span v-else-if="item.status === 'error'" class="q-icon-err">✗</span>
                <span v-else class="q-icon-wait">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/>
                  </svg>
                </span>
              </div>
              <span class="queue-name">{{ item.name }}</span>
              <span class="queue-status-text">
                {{ item.status === 'processing' ? 'Analyzing…' : item.status === 'error' ? item.error : 'Queued' }}
              </span>
            </div>
          </TransitionGroup>

          <!-- Empty state -->
          <Transition name="fade">
            <div v-if="rankedResumes.length === 0 && processingQueue.length === 0" class="empty-state">
              <div class="empty-illustration">
                <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="#c7d2fe" stroke-width="1.2">
                  <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>
              </div>
              <p class="empty-title">No resumes screened yet</p>
              <p class="empty-hint">Upload resumes above to start ranking candidates</p>
            </div>
          </Transition>

          <!-- Rankings -->
          <div v-if="rankedResumes.length > 0" class="rankings">
            <div class="rankings-header">
              <h2 class="rankings-title">Candidate Rankings</h2>
              <span class="rankings-badge">{{ rankedResumes.length }} candidate{{ rankedResumes.length !== 1 ? 's' : '' }}</span>
            </div>

            <TransitionGroup name="card-list" tag="div" class="rank-list">
              <div
                v-for="(resume, idx) in rankedResumes"
                :key="resume.id"
                class="rank-card"
                @click="openDetail(resume)"
              >
                <!-- Medal badge -->
                <div class="medal" :class="medalClass(idx)">
                  <span class="medal-num">{{ idx + 1 }}</span>
                </div>

                <!-- Body -->
                <div class="rank-body">
                  <div class="rank-top">
                    <span class="rank-filename">{{ resume.filename }}</span>
                    <div class="rank-flags">
                      <span class="flag" :class="resume.score_breakdown.education_met ? 'flag-ok' : 'flag-no'">
                        {{ resume.score_breakdown.education_met ? '✓' : '✗' }} Edu
                      </span>
                      <span class="flag" :class="resume.score_breakdown.experience_met ? 'flag-ok' : 'flag-no'">
                        {{ resume.score_breakdown.experience_met ? '✓' : '✗' }} Exp
                      </span>
                      <span v-if="resume.score_breakdown.certifications > 0" class="flag flag-cert">
                        🏆 {{ resume.score_breakdown.certifications }}%
                      </span>
                    </div>
                  </div>

                  <div class="rank-bars">
                    <div class="bar-row">
                      <span class="bar-lbl">Skills</span>
                      <div class="bar-track">
                        <div class="bar-fill bar-skills" :style="{ width: resume.score_breakdown.skills + '%' }" />
                      </div>
                      <span class="bar-val">{{ resume.score_breakdown.skills }}%</span>
                    </div>
                    <div class="bar-row">
                      <span class="bar-lbl">Duties</span>
                      <div class="bar-track">
                        <div class="bar-fill bar-duties" :style="{ width: resume.score_breakdown.responsibilities + '%' }" />
                      </div>
                      <span class="bar-val">{{ resume.score_breakdown.responsibilities }}%</span>
                    </div>
                  </div>
                </div>

                <!-- Score -->
                <div class="rank-score" :class="scoreClass(resume.rank_score)">
                  <span class="score-num">{{ resume.rank_score }}</span>
                  <span class="score-denom">/100</span>
                </div>

                <!-- Chevron -->
                <div class="rank-chevron">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <path d="M9 18l6-6-6-6"/>
                  </svg>
                </div>
              </div>
            </TransitionGroup>
          </div>

        </div>
      </Transition>
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { createJobSession, uploadResumeToSession } from '@/api/jobs'
import ResumeDetailPanel from '@/components/ResumeDetailPanel.vue'

const auth   = useAuthStore()
const router = useRouter()

const jdFileInput    = ref(null)
const resumeFileInput = ref(null)
const jdFile         = ref(null)
const jdLoading      = ref(false)
const jdDragging     = ref(false)
const resumeDragging = ref(false)
const error          = ref('')
const uploadError    = ref('')
const session        = ref(null)
const rankedResumes  = ref([])
const processingQueue = ref([])
const detailResume   = ref(null)

let queueCounter = 0
let draining = false

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

function medalClass(idx) {
  if (idx === 0) return 'gold'
  if (idx === 1) return 'silver'
  if (idx === 2) return 'bronze'
  return 'plain'
}

function scoreClass(v) {
  if (v >= 70) return 'score-high'
  if (v >= 45) return 'score-mid'
  return 'score-low'
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
  session.value = null; jdFile.value = null
  rankedResumes.value = []; processingQueue.value = []
  error.value = ''; uploadError.value = ''
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

function openDetail(resume) { detailResume.value = resume }

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}
</script>

<style scoped>
/* ── Page shell ──────────────────────────────────────────────────────────── */
.page {
  min-height: 100vh;
  background: var(--slate-50, #f8fafc);
}

/* ── Navbar ──────────────────────────────────────────────────────────────── */
.navbar {
  position: sticky; top: 0; z-index: 100;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 2rem; height: 60px;
  background: rgba(255,255,255,0.88);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid #e2e8f0;
}
.nav-brand   { display: flex; align-items: center; gap: 0.6rem; }
.logo-mark   { width: 30px; height: 30px; background: linear-gradient(135deg,#4f46e5,#6366f1); border-radius: 7px; display:flex;align-items:center;justify-content:center; font-size:0.9rem; font-weight:900; color:#fff; }
.brand-name  { font-size: 1.1rem; font-weight: 800; color: #1e1b4b; letter-spacing: -0.02em; }
.nav-links   { display: flex; align-items: center; gap: 1.25rem; }
.nav-links a { color: #64748b; text-decoration: none; font-weight: 500; font-size: 0.9rem; transition: color 0.15s; }
.nav-links a:hover { color: #4f46e5; }
.btn-logout  { padding: 0.4rem 0.9rem; background: transparent; color: #4f46e5; border: 1.5px solid #c7d2fe; border-radius: 8px; font-size: 0.82rem; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.btn-logout:hover { background: #eef2ff; border-color: #4f46e5; }

/* ── Content ─────────────────────────────────────────────────────────────── */
.content { max-width: 860px; margin: 0 auto; padding: 3rem 1.5rem 5rem; }
.sr-only  { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0,0,0,0); }
.link     { color: #4f46e5; font-weight: 600; cursor: pointer; }

/* ── Phase transitions ───────────────────────────────────────────────────── */
.phase-enter-active { transition: all 0.4s cubic-bezier(0.16,1,0.3,1); }
.phase-leave-active { transition: all 0.25s ease; position: absolute; }
.phase-enter-from   { opacity: 0; transform: translateY(16px); }
.phase-leave-to     { opacity: 0; transform: translateY(-8px); }

/* ── Setup phase ─────────────────────────────────────────────────────────── */
.setup-phase { display: flex; flex-direction: column; align-items: center; gap: 2rem; }

.setup-hero { text-align: center; }
.setup-icon-ring {
  width: 72px; height: 72px; border-radius: 20px;
  background: linear-gradient(135deg, #eef2ff, #e0e7ff);
  border: 1.5px solid #c7d2fe;
  display: flex; align-items: center; justify-content: center;
  font-size: 2rem; margin: 0 auto 1.25rem;
}
.setup-title { font-size: 1.9rem; font-weight: 900; color: #0f172a; letter-spacing: -0.03em; margin: 0 0 0.5rem; }
.setup-sub   { color: #64748b; font-size: 1rem; margin: 0; max-width: 480px; line-height: 1.6; }

/* drop zone */
.jd-drop-zone {
  width: 100%; max-width: 520px;
  border: 2px dashed #c7d2fe; border-radius: 20px;
  background: #fff; cursor: pointer;
  transition: all 0.25s; min-height: 180px;
  display: flex; align-items: center; justify-content: center;
}
.jd-drop-zone:hover { border-color: #818cf8; background: #fafbff; box-shadow: 0 8px 32px rgba(79,70,229,0.08); }
.jd-drop-zone.dragging { border-color: #4f46e5; background: #eef2ff; transform: scale(1.01); }
.jd-drop-zone.loading  { cursor: default; }

.dz-state   { display: flex; flex-direction: column; align-items: center; gap: 0.5rem; padding: 2rem 1rem; }
.dz-spinner { width: 36px; height: 36px; border: 3px solid #e0e7ff; border-top-color: #4f46e5; border-radius: 50%; animation: spin 0.7s linear infinite; }
.dz-upload-icon { width: 52px; height: 52px; border-radius: 14px; background: #eef2ff; display: flex; align-items: center; justify-content: center; color: #4f46e5; margin-bottom: 0.25rem; }
.dz-cta     { font-size: 1rem; font-weight: 600; color: #0f172a; margin: 0; }
.dz-hint    { font-size: 0.875rem; color: #64748b; margin: 0; }
.dz-label   { font-size: 0.95rem; color: #64748b; margin: 0; }
.dz-file-icon { font-size: 2.5rem; }
.dz-filename  { font-weight: 600; color: #0f172a; margin: 0; word-break: break-all; text-align: center; }
.dz-size      { font-size: 0.85rem; color: #94a3b8; margin: 0; }

/* step indicators */
.setup-steps { display: flex; align-items: center; gap: 0.75rem; }
.step        { display: flex; align-items: center; gap: 0.45rem; font-size: 0.85rem; font-weight: 500; color: #334155; }
.step-muted  { color: #94a3b8; }
.step-num    { width: 22px; height: 22px; border-radius: 50%; background: #4f46e5; color: #fff; font-size: 0.7rem; font-weight: 700; display: flex; align-items: center; justify-content: center; }
.step-muted .step-num { background: #e2e8f0; color: #94a3b8; }
.step-divider { color: #cbd5e1; font-size: 1rem; }

/* ── Alert ───────────────────────────────────────────────────────────────── */
.alert { display: flex; align-items: center; gap: 0.6rem; padding: 0.75rem 1rem; border-radius: 10px; font-size: 0.875rem; font-weight: 500; width: 100%; max-width: 520px; }
.alert-error { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
.slide-down-enter-active, .slide-down-leave-active { transition: all 0.25s; }
.slide-down-enter-from, .slide-down-leave-to { opacity: 0; transform: translateY(-8px); }

/* ── Screening phase ─────────────────────────────────────────────────────── */
.screening-phase { display: flex; flex-direction: column; gap: 1.5rem; }

.screen-header {
  display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem;
}
.screen-jd { display: flex; flex-direction: column; gap: 0.25rem; }
.jd-label  { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; color: #4f46e5; }
.screen-title { font-size: 1.6rem; font-weight: 800; color: #0f172a; letter-spacing: -0.02em; margin: 0; line-height: 1.2; }

.btn-ghost {
  display: flex; align-items: center; gap: 0.4rem;
  padding: 0.45rem 0.9rem; background: transparent;
  color: #64748b; border: 1.5px solid #e2e8f0; border-radius: 8px;
  font-size: 0.82rem; font-weight: 600; cursor: pointer;
  transition: all 0.2s; white-space: nowrap; flex-shrink: 0;
}
.btn-ghost:hover { border-color: #cbd5e1; color: #334155; background: #f8fafc; }

/* upload bar */
.upload-bar {
  border: 2px dashed #c7d2fe; border-radius: 14px;
  background: #fff; cursor: pointer; transition: all 0.2s;
  padding: 1rem 1.5rem;
}
.upload-bar:hover  { border-color: #818cf8; background: #fafbff; }
.upload-bar.dragging { border-color: #4f46e5; background: #eef2ff; }
.upload-bar-inner { display: flex; align-items: center; gap: 1rem; }
.upload-bar-icon  { width: 40px; height: 40px; border-radius: 10px; background: #eef2ff; display: flex; align-items: center; justify-content: center; color: #4f46e5; flex-shrink: 0; }
.upload-bar-text  { font-size: 0.9rem; font-weight: 500; color: #334155; margin: 0; }
.upload-bar-hint  { font-size: 0.78rem; color: #94a3b8; margin: 0; margin-top: 0.15rem; }

/* queue */
.queue-list { display: flex; flex-direction: column; gap: 0.4rem; }
.queue-item { display: flex; align-items: center; gap: 0.75rem; padding: 0.6rem 1rem; background: #fff; border-radius: 10px; border: 1px solid #e2e8f0; font-size: 0.875rem; transition: all 0.3s; }
.queue-item.processing { border-color: #c7d2fe; background: #f5f7ff; }
.queue-item.error      { border-color: #fecaca; background: #fef2f2; }
.queue-status-icon     { flex-shrink: 0; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; }
.q-spinner { width: 14px; height: 14px; border: 2px solid #c7d2fe; border-top-color: #4f46e5; border-radius: 50%; animation: spin 0.7s linear infinite; }
.q-icon-err { color: #ef4444; font-weight: 700; }
.q-icon-wait { color: #94a3b8; }
.queue-name { flex: 1; font-weight: 500; color: #1e293b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.queue-status-text { font-size: 0.8rem; color: #64748b; flex-shrink: 0; }
.queue-item.error .queue-status-text { color: #dc2626; }

.queue-enter-active, .queue-leave-active { transition: all 0.3s; }
.queue-enter-from { opacity: 0; transform: translateX(-12px); }
.queue-leave-to   { opacity: 0; transform: translateX(12px); }

/* empty state */
.empty-state { text-align: center; padding: 4rem 1rem; }
.empty-illustration { margin-bottom: 1rem; }
.empty-title { font-size: 1rem; font-weight: 600; color: #334155; margin: 0 0 0.35rem; }
.empty-hint  { font-size: 0.875rem; color: #94a3b8; margin: 0; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* ── Rankings ────────────────────────────────────────────────────────────── */
.rankings { display: flex; flex-direction: column; gap: 1rem; }
.rankings-header { display: flex; align-items: center; justify-content: space-between; }
.rankings-title  { font-size: 1.1rem; font-weight: 700; color: #0f172a; margin: 0; }
.rankings-badge  { font-size: 0.75rem; font-weight: 600; padding: 0.25rem 0.75rem; background: #eef2ff; color: #4f46e5; border-radius: 999px; }

.rank-list { display: flex; flex-direction: column; gap: 0.65rem; }

.rank-card {
  display: flex; align-items: center; gap: 1.1rem;
  background: #fff; border-radius: 16px; padding: 1rem 1.25rem;
  border: 1.5px solid #e2e8f0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  cursor: pointer; transition: all 0.22s cubic-bezier(0.4,0,0.2,1);
}
.rank-card:hover {
  border-color: #c7d2fe;
  box-shadow: 0 8px 28px rgba(79,70,229,0.1);
  transform: translateY(-2px);
}

/* medals */
.medal {
  width: 40px; height: 40px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; font-size: 0.95rem; font-weight: 900;
}
.medal.gold   { background: linear-gradient(135deg,#f59e0b,#fbbf24); color: #fff; box-shadow: 0 3px 10px rgba(245,158,11,0.4); }
.medal.silver { background: linear-gradient(135deg,#6b7280,#9ca3af); color: #fff; box-shadow: 0 3px 10px rgba(107,114,128,0.3); }
.medal.bronze { background: linear-gradient(135deg,#b45309,#d97706); color: #fff; box-shadow: 0 3px 10px rgba(180,83,9,0.3); }
.medal.plain  { background: #f1f5f9; color: #64748b; }
.medal-num { line-height: 1; }

/* rank card body */
.rank-body { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 0.4rem; }
.rank-top  { display: flex; align-items: center; gap: 0.6rem; flex-wrap: wrap; }
.rank-filename { font-weight: 600; color: #0f172a; font-size: 0.9rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 280px; }

.rank-flags { display: flex; flex-wrap: wrap; gap: 0.3rem; }
.flag { font-size: 0.68rem; font-weight: 600; padding: 0.15rem 0.5rem; border-radius: 999px; }
.flag-ok   { background: #dcfce7; color: #15803d; }
.flag-no   { background: #fee2e2; color: #b91c1c; }
.flag-cert { background: #fef3c7; color: #92400e; }

/* mini bars */
.rank-bars { display: flex; flex-direction: column; gap: 0.28rem; }
.bar-row   { display: flex; align-items: center; gap: 0.4rem; }
.bar-lbl   { font-size: 0.68rem; color: #94a3b8; font-weight: 600; width: 32px; flex-shrink: 0; }
.bar-track { flex: 1; height: 4px; background: #f1f5f9; border-radius: 2px; overflow: hidden; }
.bar-fill  { height: 100%; border-radius: 2px; transition: width 0.7s cubic-bezier(0.4,0,0.2,1); }
.bar-skills { background: linear-gradient(90deg, #4f46e5, #818cf8); }
.bar-duties { background: linear-gradient(90deg, #0ea5e9, #38bdf8); }
.bar-val   { font-size: 0.68rem; font-weight: 600; color: #64748b; width: 28px; text-align: right; flex-shrink: 0; }

/* composite score */
.rank-score {
  display: flex; align-items: baseline; flex-shrink: 0;
  padding: 0.5rem 0.75rem; border-radius: 10px; min-width: 68px; justify-content: center;
}
.score-high { background: linear-gradient(135deg,#dcfce7,#bbf7d0); }
.score-mid  { background: linear-gradient(135deg,#fef3c7,#fde68a); }
.score-low  { background: linear-gradient(135deg,#fee2e2,#fecaca); }
.score-num  { font-size: 1.35rem; font-weight: 900; color: #0f172a; line-height: 1; }
.score-denom{ font-size: 0.7rem; color: #64748b; font-weight: 600; margin-left: 1px; }

.rank-chevron { color: #cbd5e1; flex-shrink: 0; transition: all 0.2s; }
.rank-card:hover .rank-chevron { color: #4f46e5; transform: translateX(3px); }

/* card-list transition */
.card-list-enter-active { transition: all 0.4s cubic-bezier(0.16,1,0.3,1); }
.card-list-enter-from   { opacity: 0; transform: translateX(-16px) scale(0.98); }
.card-list-move         { transition: transform 0.4s cubic-bezier(0.4,0,0.2,1); }

@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 600px) {
  .screen-header { flex-direction: column; }
  .rank-filename { max-width: 160px; }
  .rank-score { min-width: 56px; }
}

.brand-name { font-size: 1.15rem; font-weight: 800; color: #1e1b4b; letter-spacing: -0.02em; }
</style>
