<template>
  <div class="auth-page">

    <!-- Left brand panel -->
    <div class="brand-panel">
      <div class="brand-content">
        <div class="brand-logo">
          <!-- <span class="logo-mark">H</span> -->
           <img src="../assets/logo-new.png" alt="Logo" style="width: 50px; height: 50px; margin-top: 0%;" />
          <span class="logo-name">HireWise</span>
        </div>
        <h1 class="brand-headline">Hire smarter with AI-powered screening</h1>
        <p class="brand-sub">Match resumes to job descriptions semantically - not just by keywords.</p>
        <ul class="brand-features">
          <li><span class="feat-dot" />Semantic skill &amp; responsibility matching</li>
          <li><span class="feat-dot" />Rank multiple resumes in one session</li>
          <li><span class="feat-dot" />Explainable evidence for every score</li>
          <li><span class="feat-dot" />Projects &amp; certifications considered</li>
        </ul>
      </div>
      <div class="brand-orb brand-orb-1" />
      <div class="brand-orb brand-orb-2" />
      <div class="brand-orb brand-orb-3" />
    </div>

    <!-- Right form panel -->
    <div class="form-panel">
      <form class="auth-form" @submit.prevent="handleLogin" novalidate>
        <div class="form-header">
          <h2>Welcome back</h2>
          <p>Sign in to your HireWise account</p>
        </div>

        <Transition name="alert">
          <div v-if="error" class="alert alert-error" role="alert">
            <span class="alert-icon">⚠</span>{{ error }}
          </div>
        </Transition>

        <div class="field-group">
          <label class="field-label" for="username">Username</label>
          <div class="field-wrap">
            <span class="field-icon">👤</span>
            <input
              id="username"
              v-model="form.username"
              type="text"
              class="field-input"
              placeholder="Enter your username"
              autocomplete="username"
              required
            />
          </div>
        </div>

        <div class="field-group">
          <label class="field-label" for="password">Password</label>
          <div class="field-wrap">
            <span class="field-icon">🔒</span>
            <input
              id="password"
              v-model="form.password"
              :type="showPwd ? 'text' : 'password'"
              class="field-input"
              placeholder="Enter your password"
              autocomplete="current-password"
              required
            />
            <button type="button" class="pwd-toggle" @click="showPwd = !showPwd">
              {{ showPwd ? '🙈' : '👁' }}
            </button>
          </div>
        </div>

        <button type="submit" class="btn-primary" :disabled="loading">
          <span v-if="loading" class="btn-spinner" />
          <span>{{ loading ? 'Signing in…' : 'Sign In' }}</span>
          <span v-if="!loading" class="btn-arrow">→</span>
        </button>

        <p class="form-footer">
          Don't have an account?
          <RouterLink to="/register">Create one free</RouterLink>
        </p>
      </form>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const form = ref({ username: '', password: '' })
const error = ref('')
const loading = ref(false)
const showPwd = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(form.value.username, form.value.password)
    router.push('/dashboard')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Login failed. Check your credentials.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* ── Layout ──────────────────────────────────────────────────────────────── */
.auth-page {
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: 100vh;
}

@media (max-width: 768px) {
  .auth-page { grid-template-columns: 1fr; }
  .brand-panel { display: none; }
}

/* ── Brand panel ─────────────────────────────────────────────────────────── */
.brand-panel {
  position: relative;
  background: linear-gradient(145deg, #1e1b4b 0%, #312e81 40%, #4338ca 100%);
  padding: 3rem;
  display: flex;
  align-items: center;
  overflow: hidden;
}

.brand-content { position: relative; z-index: 2; }

.brand-logo {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 2.5rem;
}

.logo-mark {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #818cf8, #a5b4fc);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  font-weight: 900;
  color: #1e1b4b;
}

.logo-name {
  font-size: 1.4rem;
  font-weight: 800;
  color: #fff;
  letter-spacing: -0.02em;
}

.brand-headline {
  font-size: 2rem;
  font-weight: 800;
  color: #fff;
  line-height: 1.25;
  margin: 0 0 1rem;
  letter-spacing: -0.03em;
}

.brand-sub {
  color: #a5b4fc;
  font-size: 1rem;
  line-height: 1.6;
  margin: 0 0 2rem;
  max-width: 340px;
}

.brand-features {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.brand-features li {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  color: #c7d2fe;
  font-size: 0.9rem;
  font-weight: 500;
}

.feat-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #818cf8;
  flex-shrink: 0;
}

/* decorative orbs */
.brand-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.25;
  pointer-events: none;
}
.brand-orb-1 { width: 320px; height: 320px; background: #6366f1; top: -80px; right: -80px; }
.brand-orb-2 { width: 200px; height: 200px; background: #a855f7; bottom: 80px; left: -40px; }
.brand-orb-3 { width: 150px; height: 150px; background: #3b82f6; bottom: -30px; right: 100px; }

/* ── Form panel ──────────────────────────────────────────────────────────── */
.form-panel {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1.5rem;
}

.auth-form {
  width: 100%;
  max-width: 400px;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  animation: slideUp 0.4s cubic-bezier(0.16,1,0.3,1);
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}

.form-header { text-align: center; margin-bottom: 0.25rem; }
.form-header h2 {
  font-size: 1.8rem; font-weight: 800; color: #0f172a;
  letter-spacing: -0.03em; margin: 0 0 0.35rem;
}
.form-header p { color: #64748b; font-size: 0.9rem; margin: 0; }

/* ── Alert ───────────────────────────────────────────────────────────────── */
.alert {
  display: flex; align-items: center; gap: 0.6rem;
  padding: 0.75rem 1rem; border-radius: var(--radius);
  font-size: 0.875rem; font-weight: 500;
}
.alert-error  { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
.alert-icon   { font-size: 1rem; flex-shrink: 0; }

.alert-enter-active, .alert-leave-active { transition: all 0.25s; }
.alert-enter-from, .alert-leave-to { opacity: 0; transform: translateY(-8px); }

/* ── Fields ──────────────────────────────────────────────────────────────── */
.field-group { display: flex; flex-direction: column; gap: 0.4rem; }
.field-label { font-size: 0.875rem; font-weight: 600; color: #374151; }

.field-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.field-icon {
  position: absolute;
  left: 0.9rem;
  font-size: 1rem;
  pointer-events: none;
  z-index: 1;
}

.field-input {
  width: 100%;
  padding: 0.8rem 1rem 0.8rem 2.6rem;
  border: 1.5px solid #e2e8f0;
  border-radius: var(--radius);
  font-size: 0.95rem;
  font-family: inherit;
  background: #f8fafc;
  color: #0f172a;
  transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;
}
.field-input::placeholder { color: #94a3b8; }
.field-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(79,70,229,0.12);
  background: #fff;
}

.pwd-toggle {
  position: absolute; right: 0.75rem;
  background: none; border: none; cursor: pointer;
  font-size: 1rem; padding: 0.25rem; border-radius: 6px;
  opacity: 0.6; transition: opacity 0.15s;
}
.pwd-toggle:hover { opacity: 1; }

/* ── Primary button ──────────────────────────────────────────────────────── */
.btn-primary {
  display: flex; align-items: center; justify-content: center; gap: 0.5rem;
  width: 100%;
  padding: 0.85rem;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  color: #fff;
  border: none; border-radius: var(--radius);
  font-size: 0.95rem; font-weight: 700; font-family: inherit;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.2s;
  margin-top: 0.25rem;
  letter-spacing: 0.01em;
}
.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-primary);
}
.btn-primary:active:not(:disabled) { transform: translateY(0); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-arrow { font-size: 1.1rem; transition: transform 0.2s; }
.btn-primary:hover:not(:disabled) .btn-arrow { transform: translateX(3px); }

.btn-spinner {
  width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,0.4); border-top-color: #fff;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Footer ──────────────────────────────────────────────────────────────── */
.form-footer {
  text-align: center; color: #64748b; font-size: 0.875rem; margin: 0;
}
.form-footer a {
  color: var(--primary); font-weight: 600; text-decoration: none;
  transition: color 0.15s;
}
.form-footer a:hover { color: var(--primary-dark); text-decoration: underline; }
</style>
