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
  background: #fff; border-radius: 10px;
  box-shadow: 0 1px 6px rgba(0,0,0,.07);
  overflow: hidden;
}
.card-header {
  display: flex; align-items: center; gap: .6rem;
  padding: .9rem 1.1rem;
  border-left: 4px solid #4f46e5;
  background: #fafafa;
}
.card-icon { font-size: 1.2rem; }
.card-title { flex: 1; margin: 0; font-size: 1rem; font-weight: 700; color: #1e1b4b; }
.badge {
  background: #e0e7ff; color: #4f46e5;
  font-size: .75rem; font-weight: 700;
  padding: .15rem .55rem; border-radius: 999px;
}
.card-body { padding: .75rem 1.1rem 1rem; }
ul { margin: 0; padding-left: 1.2rem; }
li {
  color: #374151; font-size: .9rem; line-height: 1.6;
  padding: .15rem 0;
  border-bottom: 1px solid #f3f4f6;
}
li:last-child { border-bottom: none; }
.empty { padding: 1rem 1.1rem; color: #9ca3af; font-size: .9rem; }
</style>
