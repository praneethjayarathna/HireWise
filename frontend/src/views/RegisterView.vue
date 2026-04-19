<template>
  <div class="auth-container">
    <form class="auth-card" @submit.prevent="handleRegister">
      <h2>Create Account</h2>
      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="success" class="success">{{ success }}</p>

      <label>Username</label>
      <input v-model="form.username" type="text" autocomplete="username" required />

      <label>Email</label>
      <input v-model="form.email" type="email" autocomplete="email" required />

      <label>Password</label>
      <input v-model="form.password" type="password" autocomplete="new-password" required />

      <label>Confirm Password</label>
      <input v-model="form.password2" type="password" autocomplete="new-password" required />

      <button type="submit" :disabled="loading">{{ loading ? 'Creating…' : 'Register' }}</button>
      <p>Already have an account? <RouterLink to="/login">Sign in</RouterLink></p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const form = ref({ username: '', email: '', password: '', password2: '' })
const error = ref('')
const success = ref('')
const loading = ref(false)

async function handleRegister() {
  error.value = ''
  success.value = ''
  if (form.value.password !== form.value.password2) {
    error.value = 'Passwords do not match.'
    return
  }
  loading.value = true
  try {
    await auth.register(form.value.username, form.value.email, form.value.password, form.value.password2)
    success.value = 'Account created! You can now sign in.'
    form.value = { username: '', email: '', password: '', password2: '' }
  } catch (e) {
    const data = e.response?.data
    error.value = data ? Object.values(data).flat().join(' ') : 'Registration failed.'
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
.success { color: #16a34a; font-size: .9rem; }
</style>
