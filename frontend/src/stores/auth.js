import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL || 'https://hire-wise-ai.com/api'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('access') || null)
  const refreshToken = ref(localStorage.getItem('refresh') || null)
  const user = ref(null)

  const isAuthenticated = computed(() => !!accessToken.value)

  function setTokens(access, refresh) {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('access', access)
    localStorage.setItem('refresh', refresh)
  }

  function clearTokens() {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('access')
    localStorage.removeItem('refresh')
  }

  async function login(username, password) {
    const { data } = await axios.post(`${BASE}/auth/login/`, { username, password })
    setTokens(data.access, data.refresh)
    await fetchUser()
  }

  async function register(username, email, password, password2) {
    await axios.post(`${BASE}/auth/register/`, { username, email, password, password2 })
  }

  async function logout() {
    try {
      await axios.post(
        `${BASE}/auth/logout/`,
        { refresh: refreshToken.value },
        { headers: { Authorization: `Bearer ${accessToken.value}` } }
      )
    } finally {
      clearTokens()
    }
  }

  async function refresh() {
    const { data } = await axios.post(`${BASE}/auth/token/refresh/`, {
      refresh: refreshToken.value,
    })
    accessToken.value = data.access
    localStorage.setItem('access', data.access)
  }

  async function fetchUser() {
    const { data } = await axios.get(`${BASE}/auth/me/`, {
      headers: { Authorization: `Bearer ${accessToken.value}` },
    })
    user.value = data
  }

  return { accessToken, refreshToken, user, isAuthenticated, login, register, logout, refresh, fetchUser }
})
