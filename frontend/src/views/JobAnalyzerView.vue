<template>
  <div class="page">
    <!-- Header -->
    <nav class="navbar">
      <span class="brand">MyApp</span>
      <div class="nav-links">
        <RouterLink to="/dashboard">Dashboard</RouterLink>
        <button class="btn-logout" @click="handleLogout">Logout</button>
      </div>
    </nav>

    <main class="content">
      <h1>Job Description Analyzer</h1>
      <p class="subtitle">Upload a PDF or DOCX file to extract and categorize the job description.</p>

      <!-- Upload card -->
      <div
        class="upload-card"
        :class="{ dragging }"
        @dragover.prevent="dragging = true"
        @dragleave.prevent="dragging = false"
        @drop.prevent="onDrop"
      >
        <input
          ref="fileInput"
          type="file"
          accept=".pdf,.docx,.doc"
          class="hidden-input"
          @change="onFileChange"
        />

        <div v-if="!selectedFile" class="upload-prompt" @click="fileInput.click()">
          <span class="upload-icon">📄</span>
          <p>Drag & drop your file here or <span class="link">browse</span></p>
          <p class="hint">Supports PDF and DOCX · Max 10 MB</p>
        </div>

        <div v-else class="file-selected">
          <span class="file-icon">{{ fileIcon }}</span>
          <div class="file-info">
            <span class="file-name">{{ selectedFile.name }}</span>
            <span class="file-size">{{ fileSizeLabel }}</span>
          </div>
          <button class="btn-remove" title="Remove" @click.stop="clearFile">✕</button>
        </div>
      </div>

      <!-- Error -->
      <p v-if="error" class="error">{{ error }}</p>

      <!-- Analyze button -->
      <button
        class="btn-analyze"
        :disabled="!selectedFile || loading"
        @click="analyze"
      >
        <span v-if="loading" class="spinner" />
        {{ loading ? 'Analyzing…' : 'Analyze Job Description' }}
      </button>

      <!-- Results -->
      <section v-if="result" class="results">
        <CategoryCard
          v-for="cat in categories"
          :key="cat.key"
          :title="cat.label"
          :icon="cat.icon"
          :color="cat.color"
          :items="result[cat.key]"
        />
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { analyzeJobDescription } from '@/api/jobs'
import CategoryCard from '@/components/CategoryCard.vue'

const auth = useAuthStore()
const router = useRouter()

const fileInput = ref(null)
const selectedFile = ref(null)
const loading = ref(false)
const error = ref('')
const result = ref(null)
const dragging = ref(false)

const categories = [
  { key: 'overview',         label: 'Overview',         icon: '🏢', color: '#6366f1' },
  { key: 'responsibilities', label: 'Responsibilities', icon: '📋', color: '#0ea5e9' },
  { key: 'qualifications',   label: 'Qualifications',   icon: '🎓', color: '#10b981' },
  { key: 'skills',           label: 'Skills',           icon: '⚡', color: '#f59e0b' },
]

const fileIcon = computed(() => {
  if (!selectedFile.value) return ''
  return selectedFile.value.name.endsWith('.pdf') ? '📕' : '📘'
})

const fileSizeLabel = computed(() => {
  if (!selectedFile.value) return ''
  const kb = selectedFile.value.size / 1024
  return kb > 1024 ? `${(kb / 1024).toFixed(1)} MB` : `${kb.toFixed(0)} KB`
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

function onFileChange(e) {
  const file = e.target.files[0]
  if (file && validateFile(file)) {
    selectedFile.value = file
    error.value = ''
    result.value = null
  }
}

function onDrop(e) {
  dragging.value = false
  const file = e.dataTransfer.files[0]
  if (file && validateFile(file)) {
    selectedFile.value = file
    error.value = ''
    result.value = null
  }
}

function clearFile() {
  selectedFile.value = null
  result.value = null
  error.value = ''
  if (fileInput.value) fileInput.value.value = ''
}

async function analyze() {
  if (!selectedFile.value) return
  loading.value = true
  error.value = ''
  result.value = null
  try {
    const { data } = await analyzeJobDescription(selectedFile.value)
    result.value = data
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

/* Navbar */
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

/* Content */
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

/* Upload card */
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

/* Error */
.error {
  color: #dc2626;
  font-size: 0.9rem;
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  background: #fef2f2;
  border-radius: 10px;
  border-left: 3px solid #dc2626;
}

/* Analyze button */
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

.btn-analyze:active:not(:disabled) {
  transform: translateY(0);
}

.btn-analyze:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

/* Spinner */
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

/* Results */
.results {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
  margin-top: 2.5rem;
}
</style>
