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
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #f0f2f5 0%, #eef0f5 100%);
  padding: 1rem;
}

.auth-card {
  background: #fff;
  padding: 2.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
  width: 100%;
  max-width: 400px;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

h2 {
  margin: 0 0 0.5rem;
  text-align: center;
  font-size: 1.75rem;
  font-weight: 700;
  color: #1e1b4b;
}

label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.25rem;
  display: block;
}

input {
  width: 100%;
  padding: 0.875rem 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  font-size: 1rem;
  transition: border-color 0.2s, box-shadow 0.2s;
  background: #fafafa;
  box-sizing: border-box;
}

input:focus {
  outline: none;
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
  background: #fff;
}

input::placeholder {
  color: #9ca3af;
}

button {
  width: 100%;
  padding: 0.9rem;
  background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.2s;
  margin-top: 0.5rem;
}

button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.35);
}

button:active:not(:disabled) {
  transform: translateY(0);
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  color: #dc2626;
  font-size: 0.875rem;
  padding: 0.75rem 1rem;
  background: #fef2f2;
  border-radius: 8px;
  border-left: 3px solid #dc2626;
}

.success {
  color: #16a34a;
  font-size: 0.875rem;
  padding: 0.75rem 1rem;
  background: #f0fdf4;
  border-radius: 8px;
  border-left: 3px solid #16a34a;
}

.auth-card p {
  text-align: center;
  color: #6b7280;
  font-size: 0.9rem;
  margin: 0;
}

.auth-card a {
  color: #4f46e5;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.15s;
}

.auth-card a:hover {
  color: #3730a3;
  text-decoration: underline;
}
</style>
