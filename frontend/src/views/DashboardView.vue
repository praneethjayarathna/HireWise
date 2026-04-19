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
      <p class="subtitle">What would you like to do today?</p>

      <div class="cards">
        <RouterLink to="/jobs/analyze" class="feature-card">
          <span class="feature-icon">📄</span>
          <div>
            <h3>Job Description Analyzer</h3>
            <p>Upload a PDF or DOCX and extract overview, responsibilities, qualifications and skills.</p>
          </div>
          <span class="arrow">→</span>
        </RouterLink>
      </div>
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
.navbar {
  display: flex; justify-content: space-between; align-items: center;
  padding: 1rem 2rem; background: #fff;
  box-shadow: 0 1px 4px rgba(0,0,0,.08);
}
.brand { font-weight: 700; font-size: 1.2rem; color: #4f46e5; }
.user-info { display: flex; align-items: center; gap: 1rem; }
button {
  padding: .5rem 1rem; background: #4f46e5; color: #fff;
  border: none; border-radius: 6px; cursor: pointer;
}
.content { max-width: 860px; margin: 0 auto; padding: 2rem 1rem; }
h1 { margin: 0 0 .3rem; color: #1e1b4b; }
.subtitle { color: #6b7280; margin: 0 0 2rem; }

.cards { display: flex; flex-direction: column; gap: 1rem; }

.feature-card {
  display: flex; align-items: center; gap: 1.25rem;
  background: #fff; border-radius: 12px; padding: 1.25rem 1.5rem;
  box-shadow: 0 1px 6px rgba(0,0,0,.07);
  text-decoration: none; color: inherit;
  border: 2px solid transparent;
  transition: border-color .2s, box-shadow .2s;
}
.feature-card:hover { border-color: #4f46e5; box-shadow: 0 4px 16px rgba(79,70,229,.12); }
.feature-icon { font-size: 2.2rem; flex-shrink: 0; }
.feature-card div { flex: 1; }
.feature-card h3 { margin: 0 0 .3rem; color: #1e1b4b; font-size: 1rem; }
.feature-card p { margin: 0; color: #6b7280; font-size: .88rem; }
.arrow { font-size: 1.3rem; color: #4f46e5; font-weight: 700; }
</style>
