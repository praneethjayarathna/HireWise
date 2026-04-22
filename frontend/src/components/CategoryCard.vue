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
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  overflow: hidden;
  transition: transform 0.25s, box-shadow 0.25s;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.1rem 1.25rem;
  border-left: 4px solid v-bind(color);
  background: linear-gradient(90deg, rgba(0, 0, 0, 0.02) 0%, transparent 100%);
}

.card-icon {
  font-size: 1.35rem;
}

.card-title {
  flex: 1;
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
  color: #1e1b4b;
}

.badge {
  background: v-bind(color);
  color: #fff;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
}

.card-body {
  padding: 0.5rem 1.25rem 1.25rem;
}

ul {
  margin: 0;
  padding-left: 1.3rem;
}

li {
  color: #374151;
  font-size: 0.925rem;
  line-height: 1.65;
  padding: 0.4rem 0;
  border-bottom: 1px solid #f3f4f6;
}

li:last-child {
  border-bottom: none;
}

.empty {
  padding: 1.25rem 1.25rem;
  color: #9ca3af;
  font-size: 0.9rem;
  font-style: italic;
}
</style>
