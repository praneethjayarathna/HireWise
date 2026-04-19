<template>
  <div class="dashboard">
    <nav class="navbar">
      <span class="brand">MyApp</span>
      <div class="user-info">
        <span v-if="auth.user">Hello, {{ auth.user.username }}</span>
        <button @click="handleLogout">Logout</button>
      </div>
    </nav>
    <main class="content">
      <h1>Dashboard</h1>
      <p>You are authenticated. Build your app here.</p>
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

onMounted(() => { if (!auth.user) auth.fetchUser() })

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.dashboard { min-height: 100vh; background: #f0f2f5; }
.navbar { display: flex; justify-content: space-between; align-items: center; padding: 1rem 2rem; background: #fff; box-shadow: 0 1px 4px rgba(0,0,0,.1); }
.brand { font-weight: 700; font-size: 1.2rem; color: #4f46e5; }
.user-info { display: flex; align-items: center; gap: 1rem; }
button { padding: .5rem 1rem; background: #4f46e5; color: #fff; border: none; border-radius: 6px; cursor: pointer; }
.content { padding: 2rem; }
</style>
