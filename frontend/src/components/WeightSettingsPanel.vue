<template>
  <div class="weight-panel">
    <button class="toggle-btn" @click="open = !open">
      <span class="toggle-icon">⚖️</span>
      Scoring Weights
      <span class="toggle-arrow">{{ open ? '▲' : '▼' }}</span>
      <span v-if="isCustom" class="custom-badge">Custom</span>
    </button>

    <div v-if="open" class="panel-body">
      <!-- Presets -->
      <div class="preset-row">
        <span class="preset-label">Presets:</span>
        <button
          v-for="p in presets"
          :key="p.name"
          class="preset-btn"
          :class="{ active: activePreset === p.name }"
          @click="applyPreset(p)"
        >{{ p.name }}</button>
      </div>

      <!-- Sliders -->
      <div class="sliders">
        <div v-for="dim in dims" :key="dim.key" class="slider-row">
          <span class="dim-icon">{{ dim.icon }}</span>
          <span class="dim-label">{{ dim.label }}</span>
          <input
            type="range"
            min="0"
            max="100"
            :value="local[dim.key]"
            class="slider"
            :style="{ accentColor: dim.color }"
            @input="onSlider(dim.key, $event.target.value)"
          />
          <input
            type="number"
            min="0"
            max="100"
            :value="local[dim.key]"
            class="num-input"
            @change="onSlider(dim.key, $event.target.value)"
          />
          <span class="pct-sign">%</span>
        </div>
      </div>

      <!-- Total indicator -->
      <div class="total-row">
        <span class="total-label">Total:</span>
        <span class="total-val" :class="totalClass">{{ total }}%</span>
        <span v-if="total !== 100" class="total-hint">
          {{ total < 100 ? `${100 - total}% unallocated` : `${total - 100}% over` }}
          — will be auto-normalised
        </span>
        <span v-else class="total-hint ok">Good to go</span>
      </div>

      <div class="action-row">
        <button class="btn-reset" @click="reset">Reset to Default</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Object, default: null },
})
const emit = defineEmits(['update:modelValue'])

const DEFAULTS = { skills: 35, responsibilities: 25, education: 13, experience: 10, certifications: 8, projects: 9 }

const presets = [
  { name: 'Default',     weights: { skills: 35, responsibilities: 25, education: 13, experience: 10, certifications: 8,  projects: 9  } },
  { name: 'Entry Level', weights: { skills: 35, responsibilities: 18, education: 15, experience: 5,  certifications: 5,  projects: 22 } },
  { name: 'Cert-Heavy',  weights: { skills: 31, responsibilities: 25, education: 12, experience: 10, certifications: 12, projects: 10 } },
]

const dims = [
  { key: 'skills',           label: 'Skills',           icon: '⚡', color: '#4f46e5' },
  { key: 'responsibilities', label: 'Responsibilities', icon: '📋', color: '#0ea5e9' },
  { key: 'certifications',   label: 'Certifications',   icon: '🏅', color: '#f59e0b' },
  { key: 'projects',         label: 'Projects',         icon: '🗂️', color: '#10b981' },
  { key: 'education',        label: 'Education',        icon: '🎓', color: '#8b5cf6' },
  { key: 'experience',       label: 'Experience',       icon: '💼', color: '#6366f1' },
]

const open = ref(false)
const local = ref({ ...DEFAULTS })
const activePreset = ref('Default')

const total = computed(() => Object.values(local.value).reduce((s, v) => s + Number(v), 0))
const totalClass = computed(() => total.value === 100 ? 'ok' : total.value > 100 ? 'over' : 'under')
const isCustom = computed(() => activePreset.value !== 'Default')

function onSlider(key, val) {
  local.value = { ...local.value, [key]: Math.max(0, Math.min(100, Number(val))) }
  activePreset.value = matchPreset() ?? 'Custom'
  emit('update:modelValue', { ...local.value })
}

function applyPreset(p) {
  local.value = { ...p.weights }
  activePreset.value = p.name
  emit('update:modelValue', { ...local.value })
}

function reset() {
  applyPreset(presets[0])
}

function matchPreset() {
  return presets.find(p =>
    Object.keys(p.weights).every(k => p.weights[k] === local.value[k])
  )?.name ?? null
}

// Sync if parent provides initial value
watch(() => props.modelValue, v => {
  if (v) local.value = { ...v }
}, { immediate: true })
</script>

<style scoped>
.weight-panel {
  border: 1.5px solid #e2e8f0;
  border-radius: 14px;
  background: #fff;
  overflow: hidden;
  margin-bottom: 1.5rem;
}

.toggle-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.85rem 1.25rem;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 700;
  color: #1e1b4b;
  text-align: left;
}
.toggle-btn:hover { background: #f8fafc; }
.toggle-icon { font-size: 1rem; }
.toggle-arrow { margin-left: auto; color: #94a3b8; font-size: 0.75rem; }

.custom-badge {
  font-size: 0.65rem;
  font-weight: 700;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  background: #eef2ff;
  color: #4f46e5;
  letter-spacing: 0.04em;
}

.panel-body {
  border-top: 1px solid #f1f5f9;
  padding: 1.25rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.preset-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.preset-label { font-size: 0.78rem; font-weight: 600; color: #64748b; }
.preset-btn {
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  border: 1.5px solid #e2e8f0;
  background: #fff;
  font-size: 0.78rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  transition: all 0.15s;
}
.preset-btn:hover { border-color: #a5b4fc; color: #4f46e5; }
.preset-btn.active { border-color: #4f46e5; background: #eef2ff; color: #4f46e5; }

.sliders { display: flex; flex-direction: column; gap: 0.6rem; }

.slider-row {
  display: grid;
  grid-template-columns: 1.2rem 9rem 1fr 3.2rem 1rem;
  align-items: center;
  gap: 0.65rem;
}
.dim-icon  { font-size: 0.9rem; text-align: center; }
.dim-label { font-size: 0.82rem; font-weight: 600; color: #334155; }
.slider    { width: 100%; height: 4px; cursor: pointer; }
.num-input {
  width: 100%;
  padding: 0.2rem 0.4rem;
  border: 1.5px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.82rem;
  font-weight: 700;
  text-align: right;
  color: #0f172a;
}
.num-input:focus { outline: none; border-color: #a5b4fc; }
.pct-sign { font-size: 0.78rem; color: #94a3b8; }

.total-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.6rem 0.75rem;
  border-radius: 8px;
  background: #f8fafc;
  font-size: 0.82rem;
}
.total-label { font-weight: 600; color: #475569; }
.total-val   { font-weight: 800; font-size: 0.9rem; }
.total-val.ok    { color: #16a34a; }
.total-val.over  { color: #dc2626; }
.total-val.under { color: #d97706; }
.total-hint    { color: #94a3b8; font-size: 0.78rem; }
.total-hint.ok { color: #16a34a; }

.action-row { display: flex; justify-content: flex-end; }
.btn-reset {
  padding: 0.4rem 1rem;
  border-radius: 8px;
  border: 1.5px solid #e2e8f0;
  background: #fff;
  font-size: 0.8rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-reset:hover { border-color: #cbd5e1; background: #f8fafc; }
</style>
