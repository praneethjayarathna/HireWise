<template>
  <div class="dashboard">

    <!-- Navbar -->
    <nav class="navbar">
      <div class="nav-brand">
        <img src="../assets/logo-new.png" alt="Logo" style="width: 50px; height: 50px; margin-top: 0%;" />
        <span class="brand-name">HireWise</span>
      </div>
      <div class="nav-right">
        <!-- <span v-if="auth.user" class="nav-user">{{ auth.user.username }}</span> -->
        <button class="btn-logout" @click="handleLogout">Sign out</button>
      </div>
    </nav>

    <main class="main">

      <!-- Hero -->
      <div class="hero">
        <div class="hero-text">
          <p class="hero-greeting">{{ greeting }},</p>
          <h1 class="hero-name">{{ auth.user?.username ?? 'Recruiter' }}</h1>
          <p class="hero-sub">What would you like to do today?</p>
        </div>
        <div class="hero-badge">AI-Powered</div>
      </div>

      <!-- Feature cards -->
      <div class="cards">

        <!-- Primary: Screening -->
        <RouterLink to="/jobs/screen" class="card card-primary">
          <div class="card-icon-wrap primary-icon">🏆</div>
          <div class="card-body">
            <span class="card-tag">Recommended</span>
            <h2 class="card-title">Resume Screening Dashboard</h2>
            <p class="card-desc">Upload a job description, then screen and rank multiple resumes in one session. Explainable scores for every candidate.</p>
            <div class="card-pills">
              <span class="pill">Multi-resume ranking</span>
              <span class="pill">Explainable AI</span>
              <!-- <span class="pill">Projects &amp; certs</span> -->
            </div>
          </div>
          <span class="card-arrow">→</span>
        </RouterLink>

        <!-- Secondary: Single matcher -->
        <RouterLink to="/resume/matcher" class="card card-secondary">
          <div class="card-icon-wrap secondary-icon">📊</div>
          <div class="card-body">
            <h2 class="card-title">Single Resume Matcher</h2>
            <p class="card-desc">Deep-dive analysis of one resume against a job description - sentence-level overview, skills, education, experience.</p>
            <!-- <div class="card-pills">
              <span class="pill">Skill gap analysis</span>
              <span class="pill">Education check</span>
            </div> -->
          </div>
          <span class="card-arrow">→</span>
        </RouterLink>

      </div>

      <!-- Info row -->
      <div class="info-row">
        <div class="info-chip">
          <span class="info-icon">⚡</span>
          <span>SBERT semantic matching - goes beyond keyword search</span>
        </div>
        <div class="info-chip">
          <span class="info-icon">🎯</span>
          <span>7-dimension scoring: skills, responsibilities, education, experience, certs, projects</span>
        </div>
        <div class="info-chip">
          <span class="info-icon">📄</span>
          <span>Supports PDF &amp; DOCX resumes and job descriptions</span>
        </div>
      </div>

    </main>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

onMounted(() => { if (!auth.user) auth.fetchUser() })

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return 'Good morning'
  if (h < 18) return 'Good afternoon'
  return 'Good evening'
})

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: var(--slate-50, #f8fafc);
}

/* ── Navbar ──────────────────────────────────────────────────────────────── */
.navbar {
  position: sticky; top: 0; z-index: 100;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 2rem; height: 60px;
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid #e2e8f0;
}

.nav-brand { display: flex; align-items: center; gap: 0.6rem; }
.logo-mark {
  width: 32px; height: 32px;
  background: linear-gradient(135deg, #4f46e5, #6366f1);
  border-radius: 8px; display: flex; align-items: center; justify-content: center;
  font-size: 1rem; font-weight: 900; color: #fff;
}
.brand-name { font-size: 1.15rem; font-weight: 800; color: #1e1b4b; letter-spacing: -0.02em; }

.nav-right { display: flex; align-items: center; gap: 1rem; }
.nav-user  { font-size: 0.875rem; font-weight: 500; color: #64748b; }

.btn-logout {
  padding: 0.4rem 1rem; background: transparent;
  color: #4f46e5; border: 1.5px solid #c7d2fe; border-radius: 8px;
  font-size: 0.85rem; font-weight: 600; cursor: pointer;
  transition: all 0.2s;
}
.btn-logout:hover { background: #eef2ff; border-color: #4f46e5; }

/* ── Main ────────────────────────────────────────────────────────────────── */
.main { max-width: 900px; margin: 0 auto; padding: 3rem 1.5rem 4rem; }

/* ── Hero ────────────────────────────────────────────────────────────────── */
.hero {
  display: flex; align-items: flex-start; justify-content: space-between;
  margin-bottom: 2.5rem;
  animation: fadeUp 0.5s cubic-bezier(0.16,1,0.3,1);
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}

.hero-greeting { font-size: 1rem; color: #64748b; font-weight: 500; margin: 0 0 0.1rem; }
.hero-name {
  font-size: 2.2rem; font-weight: 900; color: #0f172a;
  letter-spacing: -0.04em; margin: 0 0 0.4rem; line-height: 1.15;
}
.hero-sub { font-size: 1rem; color: #64748b; margin: 0; }

.hero-badge {
  padding: 0.35rem 0.9rem; border-radius: 999px;
  background: linear-gradient(135deg, #eef2ff, #e0e7ff);
  color: #4f46e5; font-size: 0.75rem; font-weight: 700;
  letter-spacing: 0.04em; border: 1px solid #c7d2fe;
  white-space: nowrap;
}

/* ── Cards ───────────────────────────────────────────────────────────────── */
.cards {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 2rem;
  animation: fadeUp 0.5s cubic-bezier(0.16,1,0.3,1) 0.1s both;
}

.card {
  display: flex; align-items: center; gap: 1.5rem;
  padding: 1.5rem 1.75rem;
  border-radius: 18px; text-decoration: none; color: inherit;
  border: 1.5px solid transparent;
  transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
  position: relative; overflow: hidden;
}

.card-primary {
  background: linear-gradient(135deg, #1e1b4b 0%, #312e81 60%, #4338ca 100%);
  border-color: #4338ca;
}
.card-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 20px 40px rgba(67,56,202,0.4);
}
.card-primary .card-title { color: #fff; }
.card-primary .card-desc  { color: #a5b4fc; }
.card-primary .card-tag   { background: rgba(255,255,255,0.15); color: #e0e7ff; }
.card-primary .pill       { background: rgba(255,255,255,0.12); color: #c7d2fe; border-color: rgba(255,255,255,0.2); }
.card-primary .card-arrow { color: #818cf8; }
.card-primary:hover .card-arrow { color: #fff; }

.card-secondary {
  background: #fff; border-color: #e2e8f0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.card-secondary:hover {
  transform: translateY(-3px); border-color: #c7d2fe;
  box-shadow: 0 12px 32px rgba(79,70,229,0.12);
}
.card-secondary .card-title { color: #0f172a; }
.card-secondary .card-desc  { color: #64748b; }
.card-secondary .pill       { background: #f1f5f9; color: #475569; border-color: #e2e8f0; }
.card-secondary .card-arrow { color: #c7d2fe; }
.card-secondary:hover .card-arrow { color: #4f46e5; }

.card-icon-wrap {
  width: 56px; height: 56px; border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.6rem; flex-shrink: 0;
}
.primary-icon   { background: rgba(255,255,255,0.15); }
.secondary-icon { background: linear-gradient(135deg, #eef2ff, #e0e7ff); }

.card-body   { flex: 1; min-width: 0; }
.card-tag    { display: inline-block; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; padding: 0.2rem 0.6rem; border-radius: 999px; margin-bottom: 0.4rem; }
.card-title  { font-size: 1.15rem; font-weight: 800; margin: 0 0 0.4rem; letter-spacing: -0.01em; }
.card-desc   { font-size: 0.875rem; line-height: 1.55; margin: 0 0 0.75rem; }
.card-pills  { display: flex; flex-wrap: wrap; gap: 0.35rem; }
.pill        { font-size: 0.72rem; font-weight: 500; padding: 0.2rem 0.65rem; border-radius: 999px; border: 1px solid; }
.card-arrow  { font-size: 1.5rem; font-weight: 700; flex-shrink: 0; transition: all 0.25s; }
.card:hover .card-arrow { transform: translateX(4px); }

/* ── Info row ────────────────────────────────────────────────────────────── */
.info-row {
  display: flex; flex-wrap: wrap; gap: 0.75rem;
  animation: fadeUp 0.5s cubic-bezier(0.16,1,0.3,1) 0.2s both;
}

.info-chip {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.55rem 0.9rem; border-radius: 999px;
  background: #fff; border: 1px solid #e2e8f0;
  font-size: 0.8rem; color: #475569; font-weight: 500;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.info-icon { font-size: 0.9rem; }

@media (max-width: 640px) {
  .hero { flex-direction: column; gap: 0.75rem; }
  .card { flex-direction: column; align-items: flex-start; }
}
</style>
