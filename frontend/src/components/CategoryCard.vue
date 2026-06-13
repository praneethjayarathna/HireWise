<template>
  <div class="card">
    <div class="card-header" :style="{ borderLeftColor: color }">
      <span class="card-icon">{{ icon }}</span>
      <h2 class="card-title">{{ title }}</h2>
      <span class="badge">{{ items.length }}</span>
    </div>

    <div v-if="items.length" class="card-body">
      <ul>
        <li v-for="(item, i) in items" :key="i">{{ item }}</li>
      </ul>
    </div>
    <div v-else class="empty">No items detected.</div>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  icon:  String,
  color: String,
  items: { type: Array, default: () => [] },
})
</script>

<style scoped>
.card {
  background: #fff;
  border-radius: 16px;
  border: 1.5px solid #e2e8f0;
  overflow: hidden;
  transition: transform 0.22s cubic-bezier(0.4,0,0.2,1), box-shadow 0.22s, border-color 0.22s;
}

.card:hover {
  transform: translateY(-3px);
  border-color: #c7d2fe;
  box-shadow: 0 10px 28px rgba(79,70,229,0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-left: 4px solid v-bind(color);
  background: linear-gradient(90deg, rgba(79,70,229,0.03) 0%, transparent 100%);
}

.card-icon {
  font-size: 1.25rem;
}

.card-title {
  flex: 1;
  margin: 0;
  font-size: 0.975rem;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.01em;
}

.badge {
  background: v-bind(color);
  color: #fff;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
}

.card-body {
  padding: 0.4rem 1.25rem 1.1rem;
}

ul {
  margin: 0;
  padding-left: 1.2rem;
}

li {
  color: #334155;
  font-size: 0.9rem;
  line-height: 1.65;
  padding: 0.35rem 0;
  border-bottom: 1px solid #f1f5f9;
}

li:last-child {
  border-bottom: none;
}

.empty {
  padding: 1.1rem 1.25rem;
  color: #94a3b8;
  font-size: 0.875rem;
  font-style: italic;
}
</style>
