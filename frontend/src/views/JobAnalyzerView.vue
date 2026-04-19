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
.page { min-height: 100vh; background: #f0f2f5; }

/* Navbar */
.navbar {
  display: flex; justify-content: space-between; align-items: center;
  padding: 1rem 2rem; background: #fff;
  box-shadow: 0 1px 4px rgba(0,0,0,.08);
}
.brand { font-weight: 700; font-size: 1.2rem; color: #4f46e5; }
.nav-links { display: flex; align-items: center; gap: 1.5rem; }
.nav-links a { color: #4f46e5; text-decoration: none; font-weight: 500; }
.btn-logout {
  padding: .45rem 1rem; background: #4f46e5; color: #fff;
  border: none; border-radius: 6px; cursor: pointer; font-size: .9rem;
}

/* Content */
.content { max-width: 860px; margin: 0 auto; padding: 2rem 1rem; }
h1 { margin: 0 0 .4rem; font-size: 1.6rem; color: #1e1b4b; }
.subtitle { color: #6b7280; margin: 0 0 1.5rem; }

/* Upload card */
.upload-card {
  border: 2px dashed #c7d2fe; border-radius: 12px;
  background: #fff; transition: border-color .2s, background .2s;
  cursor: pointer;
}
.upload-card.dragging { border-color: #4f46e5; background: #eef2ff; }
.hidden-input { display: none; }

.upload-prompt {
  display: flex; flex-direction: column; align-items: center;
  padding: 2.5rem 1rem; gap: .5rem;
}
.upload-icon { font-size: 2.5rem; }
.upload-prompt p { margin: 0; color: #6b7280; }
.link { color: #4f46e5; font-weight: 600; cursor: pointer; }
.hint { font-size: .82rem; color: #9ca3af; }

.file-selected {
  display: flex; align-items: center; gap: 1rem;
  padding: 1rem 1.25rem;
}
.file-icon { font-size: 2rem; }
.file-info { flex: 1; display: flex; flex-direction: column; }
.file-name { font-weight: 600; color: #1f2937; word-break: break-all; }
.file-size { font-size: .82rem; color: #9ca3af; }
.btn-remove {
  background: none; border: none; font-size: 1.1rem;
  color: #9ca3af; cursor: pointer; padding: .25rem .5rem;
  border-radius: 4px; transition: color .15s;
}
.btn-remove:hover { color: #ef4444; }

/* Error */
.error { color: #dc2626; font-size: .9rem; margin: .75rem 0 0; }

/* Analyze button */
.btn-analyze {
  display: flex; align-items: center; gap: .6rem;
  margin-top: 1.25rem; padding: .75rem 2rem;
  background: #4f46e5; color: #fff; border: none;
  border-radius: 8px; font-size: 1rem; font-weight: 600;
  cursor: pointer; transition: background .2s;
}
.btn-analyze:hover:not(:disabled) { background: #4338ca; }
.btn-analyze:disabled { opacity: .55; cursor: not-allowed; }

/* Spinner */
.spinner {
  width: 16px; height: 16px; border: 2px solid rgba(255,255,255,.4);
  border-top-color: #fff; border-radius: 50%;
  animation: spin .7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Results */
.results {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 1.25rem;
  margin-top: 2rem;
}
</style>
