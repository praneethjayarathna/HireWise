<template>
  <div class="dashboard">
    <nav class="navbar">
      <span class="brand">HireWise</span>
      <div class="user-info">
        <span v-if="auth.user">Hello, {{ auth.user.username }}</span>
        <button @click="handleLogout">Logout</button>
      </div>
    </nav>

    <main class="content">
      <h1>Dashboard</h1>
      <p class="subtitle">Welcome to HireWise!</p>

      <div class="cards">
        <!-- <RouterLink to="/jobs/analyze" class="feature-card">
          <span class="feature-icon">📄</span>
          <div>
            <h3>Job Description Analyzer</h3>
            <p>Upload a PDF or DOCX and extract overview, responsibilities, qualifications and skills.</p>
          </div>
          <span class="arrow">→</span>
        </RouterLink> -->

        <RouterLink to="/resume/matcher" class="feature-card">
          <span class="feature-icon">📊</span>
          <div>
            <h3>Resume Matcher</h3>
            <p>Upload your resume and compare it against a job description.</p>
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
.dashboard {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8fafc 0%, #f0f2f5 100%);
}

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

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info span {
  color: #6b7280;
  font-size: 0.9rem;
}

button {
  padding: 0.5rem 1.25rem;
  background: transparent;
  color: #4f46e5;
  border: 1.5px solid #4f46e5;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

button:hover {
  background: #4f46e5;
  color: #fff;
}

.content {
  max-width: 900px;
  margin: 0 auto;
  padding: 3rem 1.5rem;
}

h1 {
  margin: 0 0 0.4rem;
  font-size: 2rem;
  font-weight: 800;
  color: #1e1b4b;
  letter-spacing: -0.02em;
}

.subtitle {
  color: #6b7280;
  font-size: 1.05rem;
  margin: 0 0 2.5rem;
}

.cards {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.feature-card {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  background: #fff;
  border-radius: 16px;
  padding: 1.5rem 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  text-decoration: none;
  color: inherit;
  border: 2px solid transparent;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.feature-card:hover {
  border-color: #c7d2fe;
  box-shadow: 0 8px 30px rgba(79, 70, 229, 0.12);
  transform: translateY(-2px);
}

.feature-icon {
  font-size: 2.5rem;
  flex-shrink: 0;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%);
  border-radius: 14px;
}

.feature-card div {
  flex: 1;
}

.feature-card h3 {
  margin: 0 0 0.4rem;
  color: #1e1b4b;
  font-size: 1.1rem;
  font-weight: 700;
}

.feature-card p {
  margin: 0;
  color: #6b7280;
  font-size: 0.925rem;
  line-height: 1.5;
}

.arrow {
  font-size: 1.5rem;
  color: #a5b4fc;
  font-weight: 700;
  transition: transform 0.25s, color 0.25s;
}

.feature-card:hover .arrow {
  transform: translateX(4px);
  color: #4f46e5;
}
</style>
