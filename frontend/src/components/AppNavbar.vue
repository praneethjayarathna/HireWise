<template>
  <nav class="app-navbar">
    <div class="nav-brand">
      <img src="@/assets/logo-new.png" alt="HireWise Logo" class="nav-logo" />
      <span class="brand-name">HireWise</span>
    </div>
    <div class="nav-right">
      <slot />
      <button class="btn-logout" @click="$emit('logout')">Sign out</button>
    </div>
  </nav>
</template>

<script setup>
defineEmits(['logout'])
</script>

<style scoped>
.app-navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  height: 60px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid #e2e8f0;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.nav-logo {
  width: 40px;
  height: 40px;
  object-fit: contain;
}

.brand-name {
  font-size: 1.15rem;
  font-weight: 800;
  color: #1e1b4b;
  letter-spacing: -0.02em;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

/* Nav links passed via slot */
.nav-right :deep(a) {
  color: #64748b;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.9rem;
  transition: color 0.15s;
}

.nav-right :deep(a:hover),
.nav-right :deep(a.router-link-active) {
  color: #4f46e5;
}

.btn-logout {
  padding: 0.4rem 1rem;
  background: transparent;
  color: #4f46e5;
  border: 1.5px solid #c7d2fe;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-logout:hover {
  background: #eef2ff;
  border-color: #4f46e5;
}
</style>
