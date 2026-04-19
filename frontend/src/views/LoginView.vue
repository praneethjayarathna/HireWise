<template>
  <div class="auth-container">
    <form class="auth-card" @submit.prevent="handleLogin">
      <h2>Sign In</h2>
      <p v-if="error" class="error">{{ error }}</p>

      <label>Username</label>
      <input v-model="form.username" type="text" autocomplete="username" required />

      <label>Password</label>
      <input v-model="form.password" type="password" autocomplete="current-password" required />

      <button type="submit" :disabled="loading">{{ loading ? 'Signing in…' : 'Sign In' }}</button>
      <p>No account? <RouterLink to="/register">Register</RouterLink></p>
    </form>
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
.auth-container { display: flex; justify-content: center; align-items: center; min-height: 100vh; background: #f0f2f5; }
.auth-card { background: #fff; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,.1); width: 100%; max-width: 380px; display: flex; flex-direction: column; gap: .75rem; }
h2 { margin: 0 0 .5rem; text-align: center; }
input { padding: .6rem .8rem; border: 1px solid #ccc; border-radius: 6px; font-size: 1rem; }
button { padding: .7rem; background: #4f46e5; color: #fff; border: none; border-radius: 6px; font-size: 1rem; cursor: pointer; }
button:disabled { opacity: .6; cursor: not-allowed; }
.error { color: #dc2626; font-size: .9rem; }
</style>
