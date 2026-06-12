<template>
  <Teleport to="body">
    <Transition name="overlay">
      <div v-if="resume" class="overlay" @click.self="$emit('close')" />
    </Transition>
    <Transition name="panel">
      <div v-if="resume" class="panel" role="dialog" aria-modal="true">

        <!-- ── Panel header ─────────────────────────────────────────────── -->
        <div class="panel-header">
          <div class="panel-title-group">
            <span class="panel-filename">{{ resume.filename }}</span>
            <div class="panel-score-row">
              <span class="panel-composite" :class="scoreClass(resume.rank_score)">
                {{ resume.rank_score }} / 100
              </span>
              <span class="panel-composite-label">Composite Score</span>
            </div>
          </div>
          <button class="panel-close" @click="$emit('close')" title="Close">✕</button>
        </div>

        <!-- ── Score breakdown strip ───────────────────────────────────── -->
        <div class="breakdown-strip">
          <div class="breakdown-item">
            <span class="bd-label">Skills</span>
            <div class="bd-track"><div class="bd-fill skills" :style="{ width: resume.score_breakdown.skills + '%' }" /></div>
            <span class="bd-pct">{{ resume.score_breakdown.skills }}%</span>
          </div>
          <div class="breakdown-item">
            <span class="bd-label">Duties</span>
            <div class="bd-track"><div class="bd-fill duties" :style="{ width: resume.score_breakdown.responsibilities + '%' }" /></div>
            <span class="bd-pct">{{ resume.score_breakdown.responsibilities }}%</span>
          </div>
          <div class="breakdown-item">
            <span class="bd-label">Cert</span>
            <div class="bd-track"><div class="bd-fill cert" :style="{ width: resume.score_breakdown.certifications + '%' }" /></div>
            <span class="bd-pct">{{ resume.score_breakdown.certifications }}%</span>
          </div>
          <div class="breakdown-item">
            <span class="bd-label">Projects</span>
            <div class="bd-track"><div class="bd-fill proj" :style="{ width: resume.score_breakdown.projects + '%' }" /></div>
            <span class="bd-pct">{{ resume.score_breakdown.projects }}%</span>
          </div>
          <div class="breakdown-badges">
            <span class="bd-badge" :class="resume.score_breakdown.education_met ? 'ok' : 'no'">
              {{ resume.score_breakdown.education_met ? '✓' : '✗' }} Education
            </span>
            <span class="bd-badge" :class="resume.score_breakdown.experience_met ? 'ok' : 'no'">
              {{ resume.score_breakdown.experience_met ? '✓' : '✗' }} Experience
            </span>
          </div>
        </div>

        <!-- ── Scrollable analysis body ────────────────────────────────── -->
        <div class="panel-body">

          <!-- Category similarity scores -->
          <section v-if="sim" class="section">
            <h3 class="section-title">Category Match Scores</h3>
            <div class="cat-bars">
              <div v-for="cat in categories" :key="cat.key" class="cat-bar-card">
                <div class="cat-bar-header">
                  <span class="cat-icon">{{ cat.icon }}</span>
                  <span class="cat-label">{{ cat.label }}</span>
                  <span class="cat-score">{{ (catScore(cat.key) * 100).toFixed(0) }}%</span>
                </div>
                <div class="bar-track-lg">
                  <div class="bar-fill-lg" :style="{ width: catScore(cat.key) * 100 + '%', background: cat.color }" />
                </div>
              </div>
            </div>
          </section>

          <!-- Overview comparison -->
          <section v-if="overviewMatches !== null" class="section">
            <h3 class="section-title">Overview Comparison</h3>
            <p class="section-hint">Semantic matches between JD overview and resume summary</p>
            <div class="overview-stats">
              <div class="stat-pill">
                <span class="stat-val">{{ overviewMatches.length }}</span>
                <span class="stat-lbl">Matched Pairs</span>
              </div>
              <div class="stat-pill highlight">
                <span class="stat-val">{{ overviewAvgScore }}%</span>
                <span class="stat-lbl">Avg Similarity</span>
              </div>
            </div>
            <div v-if="overviewMatches.length" class="overview-list">
              <div
                v-for="(m, i) in overviewMatches" :key="i"
                class="overview-item" :class="matchTier(m.similarity)"
              >
                <div class="overview-pair">
                  <div class="ov-side job">
                    <span class="ov-lbl">Job Description</span>
                    <p class="ov-text">{{ m.job_sentence }}</p>
                  </div>
                  <div class="ov-conn">
                    <span>↔</span>
                    <span class="ov-sim">{{ (m.similarity * 100).toFixed(0) }}%</span>
                  </div>
                  <div class="ov-side resume">
                    <span class="ov-lbl">Resume</span>
                    <p class="ov-text">{{ m.resume_sentence }}</p>
                  </div>
                </div>
                <div class="thin-track">
                  <div class="thin-fill" :style="{ width: m.similarity * 100 + '%', background: matchColor(m.similarity) }" />
                </div>
              </div>
            </div>
            <p v-else class="empty-note">No matching overview sentences found.</p>
          </section>

          <!-- Skills -->
          <section v-if="skill" class="section">
            <h3 class="section-title">Skills Analysis</h3>
            <div class="three-stats">
              <div class="stat-pill">
                <span class="stat-val">{{ skill.job_skills_count }}</span>
                <span class="stat-lbl">Job Required</span>
              </div>
              <div class="stat-pill">
                <span class="stat-val">{{ skill.resume_skills_count }}</span>
                <span class="stat-lbl">Resume Skills</span>
              </div>
              <div class="stat-pill highlight">
                <span class="stat-val">{{ skill.effective_match_rate ?? skill.match_rate }}%</span>
                <span class="stat-lbl">Effective Match</span>
              </div>
            </div>

            <div class="skills-grid">
              <div class="skill-card match">
                <h4 class="skill-card-title"><span class="sck-icon ok-icon">✓</span> Matching Skills</h4>
                <div v-if="skill.matching_skills?.length" class="tag-list">
                  <span v-for="s in skill.matching_skills" :key="s" class="tag match">{{ s }}</span>
                </div>
                <p v-else class="empty-note">No direct matches found.</p>
              </div>
              <div class="skill-card miss">
                <h4 class="skill-card-title"><span class="sck-icon no-icon">✗</span> Missing Skills</h4>
                <div v-if="skill.missing_skills?.length" class="tag-list">
                  <span v-for="s in skill.missing_skills" :key="s" class="tag miss">{{ s }}</span>
                </div>
                <p v-else class="empty-note">All required skills found!</p>
              </div>
            </div>

            <div v-if="skill.skills_from_projects?.length" class="enriched-card proj-enrich">
              <h4 class="enriched-title">📁 Skills via Projects</h4>
              <div class="tag-list">
                <span v-for="s in skill.skills_from_projects" :key="s" class="tag proj-tag">{{ s }}</span>
              </div>
            </div>

            <div v-if="skill.skills_from_certifications?.length" class="enriched-card cert-enrich">
              <h4 class="enriched-title">🏆 Skills via Certifications</h4>
              <div class="tag-list">
                <span v-for="s in skill.skills_from_certifications" :key="s" class="tag cert-tag">{{ s }}</span>
              </div>
            </div>

            <div v-if="skill.skill_variations && Object.keys(skill.skill_variations).length" class="enriched-card var-enrich">
              <h4 class="enriched-title">≈ Semantic Matches</h4>
              <div class="var-list">
                <div v-for="(v, k) in skill.skill_variations" :key="k" class="var-row">
                  <span class="var-job">{{ k }}</span>
                  <span class="var-arrow">→</span>
                  <span class="var-res">{{ v }}</span>
                </div>
              </div>
            </div>
          </section>

          <!-- Education -->
          <section v-if="edu" class="section">
            <h3 class="section-title">Education Qualification</h3>
            <div class="two-col">
              <div class="info-card">
                <h4 class="info-card-title"><span>📋</span> Job Requirement</h4>
                <div v-if="edu.job_highest" class="edu-details">
                  <span class="level-badge" :class="levelClass(edu.job_highest.level_value)">{{ edu.job_highest.level }}</span>
                  <div v-if="edu.job_highest.major" class="kv"><span class="kv-key">Major</span><span class="kv-val">{{ edu.job_highest.major }}</span></div>
                  <div class="tag-list" style="margin-top:0.5rem">
                    <span v-for="m in edu.job_majors" :key="m" class="tag job-major">{{ m }}</span>
                  </div>
                </div>
                <p v-else class="empty-note">No specific requirement.</p>
              </div>
              <div class="info-card">
                <h4 class="info-card-title"><span>📄</span> Resume Qualification</h4>
                <div v-if="edu.resume_highest" class="edu-details">
                  <span class="level-badge" :class="levelClass(edu.resume_highest.level_value)">{{ edu.resume_highest.level }}</span>
                  <div v-if="edu.resume_highest.major" class="kv"><span class="kv-key">Major</span><span class="kv-val">{{ edu.resume_highest.major }}</span></div>
                  <div class="tag-list" style="margin-top:0.5rem">
                    <span v-for="m in edu.resume_majors" :key="m" class="tag res-major">{{ m }}</span>
                  </div>
                </div>
                <p v-else class="empty-note">No education found.</p>
              </div>
            </div>
            <div class="result-msg" :class="edu.meets_requirement ? 'ok-msg' : 'warn-msg'">
              <span class="msg-icon">{{ edu.meets_requirement ? '✓' : '!' }}</span>
              {{ edu.meets_requirement_message }}
            </div>
          </section>

          <!-- Experience -->
          <section v-if="exp" class="section">
            <h3 class="section-title">Work Experience</h3>
            <div class="two-col">
              <div class="info-card">
                <h4 class="info-card-title"><span>📋</span> Job Requirement</h4>
                <div v-if="exp.job_experience?.level">
                  <span class="exp-badge" :class="expClass(exp.job_experience.level_value)">{{ exp.job_experience.level }}</span>
                  <p v-if="exp.job_experience.context" class="context-quote">"{{ exp.job_experience.context }}"</p>
                </div>
                <p v-else class="empty-note">No specific requirement.</p>
              </div>
              <div class="info-card">
                <h4 class="info-card-title"><span>💼</span> Resume Experience</h4>
                <div v-if="exp.resume_experience?.level">
                  <span class="exp-badge" :class="expClass(exp.resume_experience.level_value)">{{ exp.resume_experience.level }}</span>
                  <p v-if="exp.resume_experience.context" class="context-quote">"{{ exp.resume_experience.context }}"</p>
                </div>
                <p v-else class="empty-note">No experience found.</p>
              </div>
            </div>
            <div class="result-msg" :class="exp.meets_requirement ? 'ok-msg' : 'warn-msg'">
              <span class="msg-icon">{{ exp.meets_requirement ? '✓' : '!' }}</span>
              {{ exp.meets_message }}
            </div>
          </section>

          <!-- Responsibilities -->
          <section v-if="resp" class="section">
            <h3 class="section-title">Responsibilities vs Experience</h3>
            <div class="resp-score-row">
              <div class="resp-score-badge" :class="respTier(resp.score)">
                <span class="resp-score-num">{{ resp.effective_score ?? resp.score }}%</span>
                <span class="resp-score-sub">Duties Match</span>
              </div>
              <p class="resp-explanation">{{ resp.explanation }}</p>
            </div>

            <div v-if="resp.matched_duties?.length">
              <h4 class="sub-heading">Matched Duties</h4>
              <div class="duty-list">
                <div v-for="(d, i) in resp.matched_duties" :key="i" class="duty-item">
                  <div class="duty-pair">
                    <span class="duty-job">{{ d.job_duty }}</span>
                    <span class="duty-sep">↔</span>
                    <span class="duty-res">{{ d.experience_duty }}</span>
                  </div>
                  <span class="duty-sim">{{ (d.similarity * 100).toFixed(0) }}% match</span>
                </div>
              </div>
            </div>

            <div v-if="resp.matched_via_projects?.length" class="proj-duties">
              <h4 class="sub-heading">Covered via Projects</h4>
              <div class="duty-list">
                <div v-for="(d, i) in resp.matched_via_projects" :key="i" class="duty-item proj-duty">
                  <div class="duty-pair">
                    <span class="duty-job">{{ d.matched_responsibility }}</span>
                    <span class="duty-sep">↔</span>
                    <span class="duty-res">{{ d.project_title }}</span>
                  </div>
                  <span class="duty-sim">{{ (d.similarity * 100).toFixed(0) }}% match</span>
                </div>
              </div>
            </div>

            <div v-if="resp.unmatched_responsibilities?.length">
              <h4 class="sub-heading">Not Covered</h4>
              <div class="tag-list">
                <span v-for="d in resp.unmatched_responsibilities" :key="d" class="tag miss">{{ d }}</span>
              </div>
            </div>
          </section>

          <!-- Certifications -->
          <section v-if="cert" class="section">
            <h3 class="section-title">Certifications</h3>
            <p class="section-hint">{{ cert.summary }}</p>

            <div v-if="cert.qualification_matches?.length" class="qual-matches">
              <h4 class="sub-heading">Satisfies Job Requirements</h4>
              <div v-for="(q, i) in cert.qualification_matches" :key="i" class="qual-item">
                <span class="qual-cert">{{ q.certification }}</span>
                <span class="qual-sep">→</span>
                <span class="qual-req">{{ q.matched_requirement }}</span>
                <span class="qual-sim">{{ (q.similarity * 100).toFixed(0) }}%</span>
              </div>
            </div>

            <div v-if="cert.certification_skills_map?.length" class="cert-list">
              <div v-for="(c, i) in cert.certification_skills_map" :key="i" class="cert-item">
                <div class="cert-item-header">
                  <span class="cert-icon">🏆</span>
                  <span class="cert-name">{{ c.certification }}</span>
                  <span class="tag" :class="c.has_relevance ? 'match' : 'miss'" style="font-size:0.7rem">
                    {{ c.has_relevance ? 'Related to job' : 'Not required' }}
                  </span>
                </div>
                <div v-if="c.related_skills?.length" class="tag-list" style="margin-top:0.4rem">
                  <span v-for="s in c.related_skills.slice(0,8)" :key="s.skill" class="tag cert-tag">
                    {{ s.skill }}
                  </span>
                  <span v-if="c.related_skills.length > 8" class="tag-more">+{{ c.related_skills.length - 8 }}</span>
                </div>
              </div>
            </div>

            <div class="relevance-bar">
              <div class="rel-header">
                <span class="rel-label">Overall Certification Relevance</span>
                <span class="rel-val" :class="scoreClass(cert.overall_match_score)">{{ cert.overall_match_score }}%</span>
              </div>
              <div class="bar-track-lg">
                <div class="bar-fill-lg" :style="{ width: cert.overall_match_score + '%', background: barColor(cert.overall_match_score) }" />
              </div>
            </div>
          </section>

          <!-- Projects -->
          <section v-if="proj" class="section">
            <h3 class="section-title">Projects</h3>
            <p class="section-hint">{{ proj.summary }}</p>

            <div v-if="proj.responsibility_matches?.length" class="qual-matches">
              <h4 class="sub-heading">Addresses Job Responsibilities</h4>
              <div v-for="(r, i) in proj.responsibility_matches" :key="i" class="qual-item">
                <span class="qual-cert">{{ r.project_title }}</span>
                <span class="qual-sep">→</span>
                <span class="qual-req">{{ r.matched_responsibility }}</span>
                <span class="qual-sim">{{ (r.similarity * 100).toFixed(0) }}%</span>
              </div>
            </div>

            <div v-if="proj.projects_skills_map?.length" class="cert-list">
              <div v-for="(p, i) in proj.projects_skills_map" :key="i" class="cert-item proj-item">
                <div class="cert-item-header">
                  <span class="cert-icon">📁</span>
                  <span class="cert-name">{{ p.project_title }}</span>
                  <span class="tag" :class="p.has_relevance ? 'match' : 'miss'" style="font-size:0.7rem">
                    {{ p.has_relevance ? 'Related to job' : 'Not relevant' }}
                  </span>
                </div>
                <p v-if="p.description" class="proj-desc">{{ p.description }}</p>
                <div v-if="p.related_skills?.length" class="tag-list" style="margin-top:0.4rem">
                  <span v-for="s in p.related_skills.slice(0,8)" :key="s" class="tag proj-tag">{{ s }}</span>
                  <span v-if="p.related_skills.length > 8" class="tag-more">+{{ p.related_skills.length - 8 }}</span>
                </div>
              </div>
            </div>

            <div class="relevance-bar">
              <div class="rel-header">
                <span class="rel-label">Overall Project Relevance</span>
                <span class="rel-val" :class="scoreClass(proj.overall_match_score)">{{ proj.overall_match_score }}%</span>
              </div>
              <div class="bar-track-lg">
                <div class="bar-fill-lg" :style="{ width: proj.overall_match_score + '%', background: barColor(proj.overall_match_score) }" />
              </div>
            </div>
          </section>

        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  resume: { type: Object, default: null },
})
defineEmits(['close'])

const analysis = computed(() => props.resume?.analysis ?? {})
const sim      = computed(() => analysis.value.similarity_scores)
const skill    = computed(() => analysis.value.skill_analysis)
const edu      = computed(() => analysis.value.education_analysis)
const exp      = computed(() => analysis.value.experience_analysis)
const resp     = computed(() => analysis.value.responsibility_analysis)
const cert     = computed(() => analysis.value.certification_analysis)
const proj     = computed(() => analysis.value.project_analysis)
const overviewMatches = computed(() => analysis.value.overview_matches ?? null)

const categories = [
  { key: 'skills',          label: 'Skills',           icon: '⚡', color: '#4f46e5' },
  { key: 'responsibilities',label: 'Responsibilities',  icon: '📋', color: '#0ea5e9' },
  { key: 'qualifications',  label: 'Qualifications',   icon: '🎓', color: '#8b5cf6' },
  { key: 'overview',        label: 'Overview',         icon: '🏢', color: '#6366f1' },
]

const overviewAvgScore = computed(() => {
  if (!overviewMatches.value?.length) return 0
  const sum = overviewMatches.value.reduce((a, m) => a + m.similarity, 0)
  return ((sum / overviewMatches.value.length) * 100).toFixed(0)
})

function catScore(key) {
  if (!sim.value) return 0
  if (key === 'skills' && skill.value)
    return (skill.value.effective_match_rate ?? skill.value.match_rate) / 100
  if (key === 'responsibilities' && resp.value)
    return (resp.value.effective_score ?? resp.value.score) / 100
  return sim.value[key] ?? 0
}

function scoreClass(v) {
  if (v >= 70) return 'high'
  if (v >= 45) return 'medium'
  return 'low'
}

function matchTier(s) {
  if (s >= 0.7) return 'tier-high'
  if (s >= 0.4) return 'tier-med'
  return 'tier-low'
}

function matchColor(s) {
  if (s >= 0.7) return '#10b981'
  if (s >= 0.4) return '#f59e0b'
  return '#ef4444'
}

function levelClass(v) {
  if (!v) return ''
  if (v >= 5) return 'phd'
  if (v >= 4) return 'master'
  if (v >= 3) return 'bachelor'
  if (v >= 2) return 'associate'
  return 'certificate'
}

function expClass(v) {
  if (!v) return ''
  if (v >= 7) return 'expert'
  if (v >= 5) return 'lead'
  if (v >= 4) return 'senior'
  if (v >= 3) return 'mid'
  return 'entry'
}

function respTier(s) {
  if (s >= 80) return 'resp-high'
  if (s >= 50) return 'resp-med'
  return 'resp-low'
}

function barColor(v) {
  if (v >= 70) return '#10b981'
  if (v >= 45) return '#f59e0b'
  return '#ef4444'
}
</script>

<style scoped>
/* ── Transitions ─────────────────────────────────────────────────────────── */
.overlay-enter-active, .overlay-leave-active { transition: opacity 0.25s; }
.overlay-enter-from,  .overlay-leave-to      { opacity: 0; }

.panel-enter-active, .panel-leave-active { transition: transform 0.3s cubic-bezier(0.4,0,0.2,1); }
.panel-enter-from,   .panel-leave-to     { transform: translateX(100%); }

/* ── Overlay + panel shell ───────────────────────────────────────────────── */
.overlay {
  position: fixed; inset: 0; z-index: 200;
  background: rgba(0,0,0,0.4); backdrop-filter: blur(2px);
}
.panel {
  position: fixed; top: 0; right: 0; bottom: 0; z-index: 201;
  width: min(700px, 100vw);
  background: #fff;
  display: flex; flex-direction: column;
  box-shadow: -8px 0 40px rgba(0,0,0,0.15);
}

/* ── Header ──────────────────────────────────────────────────────────────── */
.panel-header {
  display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem;
  padding: 1.25rem 1.5rem 1rem;
  border-bottom: 1px solid #e5e7eb;
  background: #fafbff;
  flex-shrink: 0;
}
.panel-title-group { display: flex; flex-direction: column; gap: 0.4rem; min-width: 0; }
.panel-filename {
  font-size: 1rem; font-weight: 700; color: #1e1b4b;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 500px;
}
.panel-score-row { display: flex; align-items: baseline; gap: 0.5rem; }
.panel-composite {
  font-size: 1.5rem; font-weight: 800; padding: 0.15rem 0.6rem;
  border-radius: 8px; line-height: 1;
}
.panel-composite.high   { background: #d1fae5; color: #065f46; }
.panel-composite.medium { background: #fef3c7; color: #92400e; }
.panel-composite.low    { background: #fee2e2; color: #991b1b; }
.panel-composite-label  { font-size: 0.8rem; color: #9ca3af; font-weight: 500; }

.panel-close {
  flex-shrink: 0; background: #f3f4f6; border: none; border-radius: 8px;
  width: 34px; height: 34px; font-size: 1rem; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.15s; color: #6b7280;
}
.panel-close:hover { background: #fee2e2; color: #dc2626; }

/* ── Breakdown strip ─────────────────────────────────────────────────────── */
.breakdown-strip {
  padding: 0.85rem 1.5rem;
  background: #f8f9ff;
  border-bottom: 1px solid #e5e7eb;
  display: flex; flex-wrap: wrap; gap: 0.6rem 1.25rem; align-items: center;
  flex-shrink: 0;
}
.breakdown-item { display: flex; align-items: center; gap: 0.35rem; }
.bd-label { font-size: 0.7rem; font-weight: 600; color: #9ca3af; width: 42px; }
.bd-track { width: 70px; height: 5px; background: #e5e7eb; border-radius: 3px; overflow: hidden; }
.bd-fill { height: 100%; border-radius: 3px; transition: width 0.5s; }
.bd-fill.skills { background: linear-gradient(90deg,#4f46e5,#818cf8); }
.bd-fill.duties { background: linear-gradient(90deg,#0ea5e9,#38bdf8); }
.bd-fill.cert   { background: linear-gradient(90deg,#f59e0b,#fbbf24); }
.bd-fill.proj   { background: linear-gradient(90deg,#10b981,#34d399); }
.bd-pct { font-size: 0.7rem; font-weight: 600; color: #6b7280; }

.breakdown-badges { display: flex; gap: 0.35rem; }
.bd-badge { font-size: 0.7rem; font-weight: 600; padding: 0.2rem 0.55rem; border-radius: 12px; }
.bd-badge.ok { background: #d1fae5; color: #065f46; }
.bd-badge.no { background: #fee2e2; color: #991b1b; }

/* ── Panel body (scrollable) ─────────────────────────────────────────────── */
.panel-body { flex: 1; overflow-y: auto; padding: 1.25rem 1.5rem; display: flex; flex-direction: column; gap: 2rem; }

/* ── Common section ──────────────────────────────────────────────────────── */
.section {}
.section-title { font-size: 1.05rem; font-weight: 700; color: #1e1b4b; margin: 0 0 0.4rem; }
.section-hint  { font-size: 0.85rem; color: #9ca3af; margin: 0 0 0.85rem; }
.sub-heading   { font-size: 0.9rem; font-weight: 600; color: #374151; margin: 1rem 0 0.5rem; }
.empty-note    { color: #9ca3af; font-size: 0.85rem; font-style: italic; margin: 0; }

/* ── Category score bars ─────────────────────────────────────────────────── */
.cat-bars { display: flex; flex-direction: column; gap: 0.6rem; }
.cat-bar-card { background: #f9fafb; border-radius: 8px; padding: 0.65rem 0.85rem; }
.cat-bar-header { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.4rem; }
.cat-icon  { font-size: 1rem; }
.cat-label { flex: 1; font-weight: 500; color: #374151; font-size: 0.9rem; }
.cat-score { font-weight: 700; color: #1e1b4b; font-size: 0.9rem; }
.bar-track-lg  { height: 8px; background: #e5e7eb; border-radius: 4px; overflow: hidden; }
.bar-fill-lg   { height: 100%; border-radius: 4px; transition: width 0.6s ease-out; }

/* ── Stats pills ─────────────────────────────────────────────────────────── */
.overview-stats, .three-stats {
  display: flex; gap: 0.75rem; margin-bottom: 1rem; flex-wrap: wrap;
}
.stat-pill {
  display: flex; flex-direction: column; align-items: center;
  padding: 0.55rem 1rem; background: #fff; border-radius: 10px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05); border: 1px solid #e5e7eb;
}
.stat-pill.highlight { background: linear-gradient(135deg,#4f46e5,#6366f1); border: none; }
.stat-pill.highlight .stat-val, .stat-pill.highlight .stat-lbl { color: #fff; }
.stat-val { font-size: 1.1rem; font-weight: 700; color: #1e1b4b; }
.stat-lbl { font-size: 0.7rem; color: #6b7280; font-weight: 500; }

/* ── Overview pairs ──────────────────────────────────────────────────────── */
.overview-list { display: flex; flex-direction: column; gap: 0.75rem; }
.overview-item {
  background: #fff; border-radius: 10px; padding: 0.85rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05); border-left: 4px solid #e5e7eb;
}
.overview-item.tier-high { border-left-color: #10b981; }
.overview-item.tier-med  { border-left-color: #f59e0b; }
.overview-item.tier-low  { border-left-color: #ef4444; }
.overview-pair { display: flex; align-items: flex-start; gap: 0.75rem; margin-bottom: 0.5rem; }
.ov-side { flex: 1; min-width: 0; }
.ov-lbl  { font-size: 0.65rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; display: block; margin-bottom: 0.25rem; }
.ov-side.job .ov-lbl    { color: #7c3aed; }
.ov-side.resume .ov-lbl { color: #059669; }
.ov-text { margin: 0; font-size: 0.82rem; color: #374151; line-height: 1.5; }
.ov-conn { display: flex; flex-direction: column; align-items: center; gap: 0.15rem; padding-top: 1rem; flex-shrink: 0; }
.ov-sim  { font-size: 0.72rem; font-weight: 700; color: #6b7280; }
.thin-track { height: 3px; background: #e5e7eb; border-radius: 2px; overflow: hidden; }
.thin-fill  { height: 100%; border-radius: 2px; transition: width 0.5s; }

/* ── Skills ──────────────────────────────────────────────────────────────── */
.skills-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-bottom: 0.75rem; }
@media (max-width: 540px) { .skills-grid { grid-template-columns: 1fr; } }
.skill-card { background: #fff; border-radius: 10px; padding: 0.85rem; box-shadow: 0 1px 4px rgba(0,0,0,0.05); }
.skill-card.match { border-left: 4px solid #10b981; }
.skill-card.miss  { border-left: 4px solid #ef4444; }
.skill-card-title { display: flex; align-items: center; gap: 0.4rem; font-size: 0.9rem; font-weight: 600; margin: 0 0 0.6rem; color: #1f2937; }
.sck-icon { display: flex; align-items: center; justify-content: center; width: 20px; height: 20px; border-radius: 50%; font-size: 0.75rem; font-weight: 700; }
.ok-icon { background: #d1fae5; color: #10b981; }
.no-icon { background: #fee2e2; color: #ef4444; }

/* ── Tags ────────────────────────────────────────────────────────────────── */
.tag-list { display: flex; flex-wrap: wrap; gap: 0.35rem; }
.tag { display: inline-block; padding: 0.25rem 0.6rem; border-radius: 16px; font-size: 0.8rem; font-weight: 500; }
.tag.match    { background: #d1fae5; color: #065f46; }
.tag.miss     { background: #fee2e2; color: #991b1b; }
.tag.proj-tag { background: #e0f2fe; color: #0369a1; }
.tag.cert-tag { background: #fef3c7; color: #92400e; }
.tag.job-major{ background: #ede9fe; color: #7c3aed; }
.tag.res-major{ background: #d1fae5; color: #065f46; }
.tag-more { font-size: 0.75rem; color: #9ca3af; padding: 0.25rem 0.4rem; }

/* ── Enriched skill cards ────────────────────────────────────────────────── */
.enriched-card { margin-top: 0.6rem; background: #f9fafb; border-radius: 10px; padding: 0.75rem; }
.proj-enrich { border-left: 4px solid #0ea5e9; }
.cert-enrich { border-left: 4px solid #f59e0b; }
.var-enrich  { border-left: 4px solid #8b5cf6; }
.enriched-title { font-size: 0.85rem; font-weight: 600; color: #374151; margin: 0 0 0.5rem; }
.var-list { display: flex; flex-direction: column; gap: 0.3rem; }
.var-row  { display: flex; align-items: center; gap: 0.5rem; padding: 0.3rem 0.5rem; background: #fff; border-radius: 6px; }
.var-job  { font-weight: 500; color: #1f2937; font-size: 0.82rem; }
.var-arrow{ color: #9ca3af; }
.var-res  { font-weight: 500; color: #059669; font-size: 0.82rem; }

/* ── Two-col layout ──────────────────────────────────────────────────────── */
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-bottom: 0.75rem; }
@media (max-width: 540px) { .two-col { grid-template-columns: 1fr; } }
.info-card { background: #fff; border-radius: 10px; padding: 0.85rem; box-shadow: 0 1px 4px rgba(0,0,0,0.05); }
.info-card-title { display: flex; align-items: center; gap: 0.4rem; font-size: 0.9rem; font-weight: 600; margin: 0 0 0.75rem; color: #1f2937; }
.edu-details { display: flex; flex-direction: column; gap: 0.5rem; }
.kv { display: flex; flex-direction: column; gap: 0.15rem; }
.kv-key { font-size: 0.7rem; color: #9ca3af; font-weight: 500; text-transform: uppercase; }
.kv-val { font-size: 0.85rem; color: #1f2937; font-weight: 500; }

/* ── Level / exp badges ──────────────────────────────────────────────────── */
.level-badge, .exp-badge {
  display: inline-block; padding: 0.35rem 0.75rem; border-radius: 6px;
  font-size: 0.9rem; font-weight: 700; color: #fff; width: fit-content;
}
.level-badge.phd      { background: linear-gradient(135deg,#7c3aed,#a855f7); }
.level-badge.master   { background: linear-gradient(135deg,#2563eb,#3b82f6); }
.level-badge.bachelor { background: linear-gradient(135deg,#059669,#10b981); }
.level-badge.associate{ background: linear-gradient(135deg,#d97706,#f59e0b); }
.level-badge.certificate{ background: linear-gradient(135deg,#6b7280,#9ca3af); }
.exp-badge.expert { background: linear-gradient(135deg,#7c3aed,#a855f7); }
.exp-badge.lead   { background: linear-gradient(135deg,#ea580c,#f97316); }
.exp-badge.senior { background: linear-gradient(135deg,#ca8a04,#eab308); }
.exp-badge.mid    { background: linear-gradient(135deg,#16a34a,#22c55e); }
.exp-badge.entry  { background: linear-gradient(135deg,#6b7280,#9ca3af); }

.context-quote { font-size: 0.8rem; color: #6b7280; font-style: italic; margin: 0.5rem 0 0; padding: 0.4rem; background: #f9fafb; border-radius: 6px; }

/* ── Result messages ─────────────────────────────────────────────────────── */
.result-msg { display: flex; align-items: center; gap: 0.6rem; padding: 0.75rem 1rem; border-radius: 8px; font-size: 0.9rem; font-weight: 500; }
.result-msg.ok-msg   { background: #d1fae5; color: #065f46; }
.result-msg.warn-msg { background: #fef3c7; color: #92400e; }
.msg-icon { display: flex; align-items: center; justify-content: center; width: 24px; height: 24px; border-radius: 50%; font-size: 0.85rem; font-weight: 700; flex-shrink: 0; }
.ok-msg   .msg-icon { background: #10b981; color: #fff; }
.warn-msg .msg-icon { background: #f59e0b; color: #fff; }

/* ── Responsibilities ────────────────────────────────────────────────────── */
.resp-score-row { display: flex; align-items: flex-start; gap: 1rem; margin-bottom: 1rem; }
.resp-score-badge {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 0.75rem 1rem; border-radius: 10px; flex-shrink: 0; min-width: 80px;
}
.resp-score-badge.resp-high { background: linear-gradient(135deg,#059669,#10b981); color:#fff; }
.resp-score-badge.resp-med  { background: linear-gradient(135deg,#d97706,#f59e0b); color:#fff; }
.resp-score-badge.resp-low  { background: linear-gradient(135deg,#dc2626,#ef4444); color:#fff; }
.resp-score-num { font-size: 1.5rem; font-weight: 800; }
.resp-score-sub { font-size: 0.72rem; font-weight: 500; }
.resp-explanation { flex: 1; font-size: 0.85rem; color: #4b5563; line-height: 1.5; padding: 0.6rem 0.75rem; background: #f9fafb; border-radius: 8px; border-left: 3px solid #6366f1; margin: 0; }

.duty-list { display: flex; flex-direction: column; gap: 0.5rem; }
.duty-item {
  display: flex; flex-direction: column; gap: 0.25rem;
  padding: 0.6rem 0.75rem; background: #f0fdf4; border-radius: 8px; border-left: 3px solid #10b981;
}
.duty-item.proj-duty { background: #f0f9ff; border-left-color: #0ea5e9; }
.duty-pair { display: flex; gap: 0.4rem; align-items: flex-start; flex-wrap: wrap; }
.duty-job { flex: 1; font-size: 0.8rem; color: #7c3aed; font-weight: 500; }
.duty-sep { color: #9ca3af; flex-shrink: 0; }
.duty-res { flex: 1; font-size: 0.8rem; color: #059669; font-weight: 500; }
.duty-sim { font-size: 0.72rem; color: #6b7280; font-weight: 600; }
.proj-duties { margin-top: 0.5rem; }

/* ── Certifications / Projects ───────────────────────────────────────────── */
.qual-matches { margin-bottom: 0.75rem; }
.qual-item { display: flex; align-items: flex-start; gap: 0.5rem; padding: 0.5rem 0.6rem; background: #fffbeb; border-radius: 6px; margin-bottom: 0.35rem; flex-wrap: wrap; }
.qual-cert { font-weight: 600; font-size: 0.82rem; color: #1f2937; }
.qual-sep  { color: #9ca3af; }
.qual-req  { flex: 1; font-size: 0.8rem; color: #6b7280; min-width: 0; }
.qual-sim  { font-size: 0.72rem; font-weight: 700; color: #92400e; background: #fef3c7; padding: 0.1rem 0.4rem; border-radius: 6px; flex-shrink: 0; }

.cert-list { display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 0.75rem; }
.cert-item { padding: 0.65rem 0.85rem; background: #f9fafb; border-radius: 8px; border-left: 4px solid #8b5cf6; }
.proj-item { border-left-color: #0ea5e9; }
.cert-item-header { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.35rem; }
.cert-icon { font-size: 1rem; }
.cert-name { flex: 1; font-weight: 600; font-size: 0.88rem; color: #1f2937; }
.proj-desc { font-size: 0.8rem; color: #6b7280; font-style: italic; margin: 0 0 0.4rem; padding: 0.4rem; background: #f3f4f6; border-radius: 4px; }

.relevance-bar { margin-top: 0.5rem; padding: 0.85rem 1rem; background: #f9fafb; border-radius: 10px; border: 1px solid #e5e7eb; }
.rel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem; }
.rel-label  { font-weight: 600; color: #1f2937; font-size: 0.9rem; }
.rel-val    { font-size: 1.1rem; font-weight: 800; padding: 0.2rem 0.6rem; border-radius: 6px; }
.rel-val.high   { background: #d1fae5; color: #065f46; }
.rel-val.medium { background: #fef3c7; color: #92400e; }
.rel-val.low    { background: #fee2e2; color: #991b1b; }
</style>
