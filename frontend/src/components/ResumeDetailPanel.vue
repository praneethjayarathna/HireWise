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

          <!-- Score breakdown -->
          <section v-if="resume.score_breakdown" class="section">
            <h3 class="section-title">Score Breakdown</h3>
            <div class="cat-bars">
              <div v-for="dim in breakdownDims" :key="dim.key" class="cat-bar-card">
                <div class="cat-bar-header">
                  <span class="cat-icon">{{ dim.icon }}</span>
                  <span class="cat-label">{{ dim.label }}</span>
                  <span v-if="dim.na" class="met-badge met-na">N/A</span>
                  <span v-else-if="dim.met !== undefined" :class="['met-badge', dim.met ? 'met-yes' : 'met-no']">
                    {{ dim.met ? 'Yes' : 'No' }}
                  </span>
                  <span v-else class="cat-score">{{ dim.value }}%</span>
                </div>
                <div v-if="!dim.na && dim.met === undefined" class="bar-track-lg">
                  <div class="bar-fill-lg" :style="{ width: dim.value + '%', background: dim.color }" />
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
                <span class="stat-lbl">F1 Score</span>
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
                  <p v-if="edu.resume_highest.context" class="edu-degree-name">{{ edu.resume_highest.context }}</p>
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
              <div class="resp-score-badge" :class="respTier(respScorePct)">
                <span class="resp-score-num">{{ respScorePct }}%</span>
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

            <div v-if="(cert.total_certifications ?? 0) > 0" class="relevance-bar">
              <div class="rel-header">
                <span class="rel-label">Certification Match Score</span>
                <span class="rel-val" :class="scoreClass(certQualityPct)">{{ certQualityPct }}%</span>
              </div>
              <div class="bar-track-lg">
                <div class="bar-fill-lg" :style="{ width: certQualityPct + '%', background: barColor(certQualityPct) }" />
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
                <span class="rel-label">Project Match Score</span>
                <span class="rel-val" :class="scoreClass(projQualityPct)">{{ projQualityPct }}%</span>
              </div>
              <div class="bar-track-lg">
                <div class="bar-fill-lg" :style="{ width: projQualityPct + '%', background: barColor(projQualityPct) }" />
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
const certQualityPct = computed(() => Math.round((cert.value?.quality_score ?? 0) * 100))
const projQualityPct = computed(() => Math.round((proj.value?.quality_score ?? 0) * 100))
const respScorePct   = computed(() => Math.round((resp.value?.mean_similarity ?? 0) * 100))
const overviewMatches  = computed(() => analysis.value.overview_matches ?? null)
const overviewF1Score  = computed(() => analysis.value.overview_f1_score ?? null)

const overviewAvgScore = computed(() => {
  if (overviewF1Score.value != null) return (overviewF1Score.value * 100).toFixed(0)
  if (!overviewMatches.value?.length) return 0
  const sum = overviewMatches.value.reduce((a, m) => a + m.similarity, 0)
  return ((sum / overviewMatches.value.length) * 100).toFixed(0)
})

const breakdownDims = computed(() => {
  const bd = props.resume?.score_breakdown ?? {}
  const noCerts = (cert.value?.total_certifications ?? 0) === 0
  return [
    { key: 'skills',           label: 'Skills',           icon: '⚡', color: '#4f46e5', value: bd.skills           ?? 0 },
    { key: 'responsibilities', label: 'Responsibilities', icon: '📋', color: '#0ea5e9', value: bd.responsibilities  ?? 0 },
    { key: 'certifications',   label: 'Certifications',   icon: '🏅', color: '#f59e0b', value: bd.certifications    ?? 0, na: noCerts },
    { key: 'projects',         label: 'Projects',         icon: '🗂️', color: '#10b981', value: bd.projects          ?? 0 },
    { key: 'education',  label: 'Education',  icon: '🎓', color: '#8b5cf6', value: bd.education  ?? 0, met: bd.education_met },
    { key: 'experience', label: 'Experience', icon: '💼', color: '#6366f1', value: bd.experience ?? 0, met: bd.experience_met },
    { key: 'overview',         label: 'Overview (F1)',    icon: '🏢', color: '#06b6d4', value: Number(overviewAvgScore.value) },
  ]
})

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
.overlay-enter-active, .overlay-leave-active { transition: opacity 0.3s; }
.overlay-enter-from,  .overlay-leave-to      { opacity: 0; }

.panel-enter-active  { transition: transform 0.35s cubic-bezier(0.16,1,0.3,1); }
.panel-leave-active  { transition: transform 0.25s cubic-bezier(0.4,0,0.2,1); }
.panel-enter-from,   .panel-leave-to     { transform: translateX(100%); }

/* ── Overlay + panel shell ───────────────────────────────────────────────── */
.overlay {
  position: fixed; inset: 0; z-index: 200;
  background: rgba(15,23,42,0.45); backdrop-filter: blur(3px);
}
.panel {
  position: fixed; top: 0; right: 0; bottom: 0; z-index: 201;
  width: min(720px, 100vw);
  background: #f8fafc;
  display: flex; flex-direction: column;
  box-shadow: -12px 0 60px rgba(0,0,0,0.18);
}

/* ── Header ──────────────────────────────────────────────────────────────── */
.panel-header {
  display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem;
  padding: 1.25rem 1.5rem 1rem;
  border-bottom: 1px solid #e2e8f0;
  background: linear-gradient(135deg, #1e1b4b 0%, #312e81 60%, #4338ca 100%);
  flex-shrink: 0;
}
.panel-title-group { display: flex; flex-direction: column; gap: 0.4rem; min-width: 0; }
.panel-filename {
  font-size: 0.95rem; font-weight: 700; color: #e0e7ff;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 500px;
}
.panel-score-row { display: flex; align-items: baseline; gap: 0.5rem; }
.panel-composite {
  font-size: 1.6rem; font-weight: 900; padding: 0.15rem 0.7rem;
  border-radius: 10px; line-height: 1;
}
.panel-composite.high   { background: #dcfce7; color: #14532d; }
.panel-composite.medium { background: #fef3c7; color: #78350f; }
.panel-composite.low    { background: #fee2e2; color: #7f1d1d; }
.panel-composite-label  { font-size: 0.8rem; color: #a5b4fc; font-weight: 500; }

.panel-close {
  flex-shrink: 0; background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.2);
  border-radius: 8px; width: 34px; height: 34px; font-size: 0.9rem; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.15s; color: #c7d2fe;
}
.panel-close:hover { background: rgba(239,68,68,0.25); color: #fca5a5; border-color: rgba(239,68,68,0.4); }

/* ── Breakdown strip ─────────────────────────────────────────────────────── */
.breakdown-strip {
  padding: 0.85rem 1.5rem;
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
  display: flex; flex-wrap: wrap; gap: 0.6rem 1.5rem; align-items: center;
  flex-shrink: 0;
}
.breakdown-item { display: flex; align-items: center; gap: 0.4rem; }
.bd-label { font-size: 0.68rem; font-weight: 700; color: #94a3b8; width: 40px; letter-spacing: 0.02em; text-transform: uppercase; }
.bd-track { width: 80px; height: 5px; background: #f1f5f9; border-radius: 3px; overflow: hidden; }
.bd-fill { height: 100%; border-radius: 3px; transition: width 0.6s cubic-bezier(0.4,0,0.2,1); }
.bd-fill.skills { background: linear-gradient(90deg,#4f46e5,#818cf8); }
.bd-fill.duties { background: linear-gradient(90deg,#0ea5e9,#38bdf8); }
.bd-fill.cert   { background: linear-gradient(90deg,#f59e0b,#fbbf24); }
.bd-fill.proj   { background: linear-gradient(90deg,#10b981,#34d399); }
.bd-pct { font-size: 0.72rem; font-weight: 700; color: #475569; }

.breakdown-badges { display: flex; gap: 0.4rem; }
.bd-badge { font-size: 0.7rem; font-weight: 600; padding: 0.2rem 0.6rem; border-radius: 999px; }
.bd-badge.ok { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
.bd-badge.no { background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }

/* ── Panel body (scrollable) ─────────────────────────────────────────────── */
.panel-body { flex: 1; overflow-y: auto; padding: 1.5rem; display: flex; flex-direction: column; gap: 1.5rem; }

/* ── Common section ──────────────────────────────────────────────────────── */
.section {
  background: #fff; border-radius: 14px; padding: 1.1rem 1.25rem;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.section-title {
  font-size: 0.95rem; font-weight: 800; color: #0f172a;
  margin: 0 0 0.25rem; letter-spacing: -0.01em;
  padding-bottom: 0.6rem; border-bottom: 1.5px solid #f1f5f9;
  margin-bottom: 0.85rem;
}
.section-hint  { font-size: 0.82rem; color: #94a3b8; margin: -0.5rem 0 0.85rem; }
.sub-heading   { font-size: 0.82rem; font-weight: 700; color: #475569; margin: 1rem 0 0.45rem; text-transform: uppercase; letter-spacing: 0.05em; }
.empty-note    { color: #94a3b8; font-size: 0.83rem; font-style: italic; margin: 0; }

/* ── Category score bars ─────────────────────────────────────────────────── */
.cat-bars { display: flex; flex-direction: column; gap: 0.5rem; }
.cat-bar-card {
  background: #f8fafc; border-radius: 10px; padding: 0.6rem 0.85rem;
  border: 1px solid #f1f5f9;
}
.cat-bar-header { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.4rem; }
.cat-icon  { font-size: 0.95rem; }
.cat-label { flex: 1; font-weight: 500; color: #334155; font-size: 0.875rem; }
.cat-score { font-weight: 800; color: #0f172a; font-size: 0.875rem; }
.met-badge { font-size: 0.72rem; font-weight: 700; padding: 0.18rem 0.6rem; border-radius: 999px; }
.met-yes   { background: #dcfce7; color: #16a34a; }
.met-no    { background: #fee2e2; color: #dc2626; }
.met-na    { background: #f1f5f9; color: #64748b; }
.bar-track-lg  { height: 7px; background: #e2e8f0; border-radius: 4px; overflow: hidden; }
.bar-fill-lg   { height: 100%; border-radius: 4px; transition: width 0.65s cubic-bezier(0.4,0,0.2,1); }

/* ── Stats pills ─────────────────────────────────────────────────────────── */
.overview-stats, .three-stats {
  display: flex; gap: 0.6rem; margin-bottom: 1rem; flex-wrap: wrap;
}
.stat-pill {
  display: flex; flex-direction: column; align-items: center;
  padding: 0.55rem 1rem; background: #f8fafc; border-radius: 10px;
  border: 1px solid #e2e8f0;
}
.stat-pill.highlight { background: linear-gradient(135deg,#4f46e5,#6366f1); border: none; }
.stat-pill.highlight .stat-val, .stat-pill.highlight .stat-lbl { color: #fff; }
.stat-val { font-size: 1.1rem; font-weight: 800; color: #0f172a; }
.stat-lbl { font-size: 0.68rem; color: #64748b; font-weight: 600; letter-spacing: 0.02em; }

/* ── Overview pairs ──────────────────────────────────────────────────────── */
.overview-list { display: flex; flex-direction: column; gap: 0.65rem; }
.overview-item {
  background: #f8fafc; border-radius: 10px; padding: 0.85rem;
  border: 1px solid #e2e8f0; border-left: 4px solid #e2e8f0;
}
.overview-item.tier-high { border-left-color: #10b981; background: #f0fdf4; }
.overview-item.tier-med  { border-left-color: #f59e0b; background: #fffbeb; }
.overview-item.tier-low  { border-left-color: #ef4444; background: #fef2f2; }
.overview-pair { display: flex; align-items: flex-start; gap: 0.75rem; margin-bottom: 0.5rem; }
.ov-side { flex: 1; min-width: 0; }
.ov-lbl  { font-size: 0.62rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; display: block; margin-bottom: 0.25rem; }
.ov-side.job .ov-lbl    { color: #7c3aed; }
.ov-side.resume .ov-lbl { color: #059669; }
.ov-text { margin: 0; font-size: 0.82rem; color: #334155; line-height: 1.5; }
.ov-conn { display: flex; flex-direction: column; align-items: center; gap: 0.15rem; padding-top: 1rem; flex-shrink: 0; }
.ov-sim  { font-size: 0.7rem; font-weight: 700; color: #64748b; }
.thin-track { height: 3px; background: #e2e8f0; border-radius: 2px; overflow: hidden; }
.thin-fill  { height: 100%; border-radius: 2px; transition: width 0.5s; }

/* ── Skills ──────────────────────────────────────────────────────────────── */
.skills-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.65rem; margin-bottom: 0.75rem; }
@media (max-width: 540px) { .skills-grid { grid-template-columns: 1fr; } }
.skill-card {
  background: #f8fafc; border-radius: 10px; padding: 0.85rem;
  border: 1px solid #e2e8f0;
}
.skill-card.match { border-left: 4px solid #10b981; }
.skill-card.miss  { border-left: 4px solid #ef4444; }
.skill-card-title { display: flex; align-items: center; gap: 0.4rem; font-size: 0.875rem; font-weight: 700; margin: 0 0 0.6rem; color: #0f172a; }
.sck-icon { display: flex; align-items: center; justify-content: center; width: 20px; height: 20px; border-radius: 50%; font-size: 0.75rem; font-weight: 700; flex-shrink: 0; }
.ok-icon { background: #dcfce7; color: #15803d; }
.no-icon { background: #fee2e2; color: #dc2626; }

/* ── Tags ────────────────────────────────────────────────────────────────── */
.tag-list { display: flex; flex-wrap: wrap; gap: 0.35rem; }
.tag { display: inline-block; padding: 0.22rem 0.6rem; border-radius: 999px; font-size: 0.78rem; font-weight: 500; }
.tag.match    { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
.tag.miss     { background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }
.tag.proj-tag { background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; }
.tag.cert-tag { background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
.tag.job-major{ background: #ede9fe; color: #6d28d9; border: 1px solid #ddd6fe; }
.tag.res-major{ background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
.tag-more { font-size: 0.73rem; color: #94a3b8; padding: 0.22rem 0.4rem; }

/* ── Enriched skill cards ────────────────────────────────────────────────── */
.enriched-card { margin-top: 0.5rem; background: #f8fafc; border-radius: 10px; padding: 0.75rem 0.85rem; border: 1px solid #e2e8f0; }
.proj-enrich { border-left: 4px solid #0ea5e9; }
.cert-enrich { border-left: 4px solid #f59e0b; }
.var-enrich  { border-left: 4px solid #8b5cf6; }
.enriched-title { font-size: 0.8rem; font-weight: 700; color: #334155; margin: 0 0 0.5rem; }
.var-list { display: flex; flex-direction: column; gap: 0.3rem; }
.var-row  { display: flex; align-items: center; gap: 0.5rem; padding: 0.3rem 0.5rem; background: #fff; border-radius: 6px; border: 1px solid #f1f5f9; }
.var-job  { font-weight: 600; color: #0f172a; font-size: 0.82rem; }
.var-arrow{ color: #94a3b8; flex-shrink: 0; }
.var-res  { font-weight: 500; color: #059669; font-size: 0.82rem; }

/* ── Two-col layout ──────────────────────────────────────────────────────── */
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 0.65rem; margin-bottom: 0.75rem; }
@media (max-width: 540px) { .two-col { grid-template-columns: 1fr; } }
.info-card {
  background: #f8fafc; border-radius: 10px; padding: 0.85rem;
  border: 1px solid #e2e8f0;
}
.info-card-title { display: flex; align-items: center; gap: 0.4rem; font-size: 0.875rem; font-weight: 700; margin: 0 0 0.75rem; color: #0f172a; }
.edu-details { display: flex; flex-direction: column; gap: 0.5rem; }
.edu-degree-name { margin: 0; font-size: 0.8rem; color: #475569; line-height: 1.4; }
.kv { display: flex; flex-direction: column; gap: 0.15rem; }
.kv-key { font-size: 0.68rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }
.kv-val { font-size: 0.85rem; color: #0f172a; font-weight: 600; }

/* ── Level / exp badges ──────────────────────────────────────────────────── */
.level-badge, .exp-badge {
  display: inline-block; padding: 0.3rem 0.75rem; border-radius: 8px;
  font-size: 0.875rem; font-weight: 700; color: #fff; width: fit-content;
}
.level-badge.phd        { background: linear-gradient(135deg,#7c3aed,#a855f7); }
.level-badge.master     { background: linear-gradient(135deg,#2563eb,#3b82f6); }
.level-badge.bachelor   { background: linear-gradient(135deg,#059669,#10b981); }
.level-badge.associate  { background: linear-gradient(135deg,#d97706,#f59e0b); }
.level-badge.certificate{ background: linear-gradient(135deg,#64748b,#94a3b8); }
.exp-badge.expert { background: linear-gradient(135deg,#7c3aed,#a855f7); }
.exp-badge.lead   { background: linear-gradient(135deg,#ea580c,#f97316); }
.exp-badge.senior { background: linear-gradient(135deg,#ca8a04,#eab308); }
.exp-badge.mid    { background: linear-gradient(135deg,#16a34a,#22c55e); }
.exp-badge.entry  { background: linear-gradient(135deg,#64748b,#94a3b8); }

.context-quote {
  font-size: 0.8rem; color: #64748b; font-style: italic; margin: 0.5rem 0 0;
  padding: 0.4rem 0.6rem; background: #fff; border-radius: 6px;
  border-left: 3px solid #c7d2fe;
}

/* ── Result messages ─────────────────────────────────────────────────────── */
.result-msg { display: flex; align-items: center; gap: 0.6rem; padding: 0.75rem 1rem; border-radius: 10px; font-size: 0.875rem; font-weight: 500; }
.result-msg.ok-msg   { background: #f0fdf4; color: #14532d; border: 1px solid #bbf7d0; }
.result-msg.warn-msg { background: #fffbeb; color: #78350f; border: 1px solid #fde68a; }
.msg-icon { display: flex; align-items: center; justify-content: center; width: 24px; height: 24px; border-radius: 50%; font-size: 0.85rem; font-weight: 700; flex-shrink: 0; }
.ok-msg   .msg-icon { background: #10b981; color: #fff; }
.warn-msg .msg-icon { background: #f59e0b; color: #fff; }

/* ── Responsibilities ────────────────────────────────────────────────────── */
.resp-score-row { display: flex; align-items: flex-start; gap: 1rem; margin-bottom: 1rem; }
.resp-score-badge {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 0.75rem 1rem; border-radius: 12px; flex-shrink: 0; min-width: 84px;
}
.resp-score-badge.resp-high { background: linear-gradient(135deg,#059669,#10b981); color:#fff; }
.resp-score-badge.resp-med  { background: linear-gradient(135deg,#d97706,#f59e0b); color:#fff; }
.resp-score-badge.resp-low  { background: linear-gradient(135deg,#dc2626,#ef4444); color:#fff; }
.resp-score-num { font-size: 1.6rem; font-weight: 900; }
.resp-score-sub { font-size: 0.68rem; font-weight: 600; opacity: 0.85; }
.resp-explanation {
  flex: 1; font-size: 0.83rem; color: #334155; line-height: 1.55;
  padding: 0.6rem 0.8rem; background: #f8fafc; border-radius: 10px;
  border-left: 3px solid #c7d2fe; margin: 0;
}

.duty-list { display: flex; flex-direction: column; gap: 0.45rem; }
.duty-item {
  display: flex; flex-direction: column; gap: 0.25rem;
  padding: 0.6rem 0.75rem; background: #f0fdf4; border-radius: 8px; border-left: 3px solid #10b981;
}
.duty-item.proj-duty { background: #f0f9ff; border-left-color: #0ea5e9; }
.duty-pair { display: flex; gap: 0.4rem; align-items: flex-start; flex-wrap: wrap; }
.duty-job { flex: 1; font-size: 0.8rem; color: #7c3aed; font-weight: 500; }
.duty-sep { color: #94a3b8; flex-shrink: 0; }
.duty-res { flex: 1; font-size: 0.8rem; color: #059669; font-weight: 500; }
.duty-sim { font-size: 0.7rem; color: #64748b; font-weight: 700; }
.proj-duties { margin-top: 0.5rem; }

/* ── Certifications / Projects ───────────────────────────────────────────── */
.qual-matches { margin-bottom: 0.75rem; }
.qual-item {
  display: flex; align-items: flex-start; gap: 0.5rem;
  padding: 0.5rem 0.65rem; background: #fffbeb; border-radius: 8px;
  margin-bottom: 0.35rem; flex-wrap: wrap;
  border: 1px solid #fde68a;
}
.qual-cert { font-weight: 700; font-size: 0.82rem; color: #0f172a; }
.qual-sep  { color: #94a3b8; flex-shrink: 0; }
.qual-req  { flex: 1; font-size: 0.8rem; color: #64748b; min-width: 0; }
.qual-sim  { font-size: 0.7rem; font-weight: 700; color: #78350f; background: #fde68a; padding: 0.1rem 0.4rem; border-radius: 6px; flex-shrink: 0; }

.cert-list { display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 0.75rem; }
.cert-item { padding: 0.65rem 0.85rem; background: #f8fafc; border-radius: 10px; border: 1px solid #e2e8f0; border-left: 4px solid #8b5cf6; }
.proj-item { border-left-color: #0ea5e9; }
.cert-item-header { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.35rem; }
.cert-icon { font-size: 1rem; }
.cert-name { flex: 1; font-weight: 700; font-size: 0.875rem; color: #0f172a; }
.proj-desc { font-size: 0.8rem; color: #64748b; font-style: italic; margin: 0 0 0.4rem; padding: 0.4rem 0.6rem; background: #fff; border-radius: 6px; border-left: 2px solid #c7d2fe; }

.relevance-bar {
  margin-top: 0.5rem; padding: 0.9rem 1rem; background: #f8fafc;
  border-radius: 12px; border: 1px solid #e2e8f0;
}
.rel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.65rem; }
.rel-label  { font-weight: 700; color: #0f172a; font-size: 0.875rem; }
.rel-val    { font-size: 1rem; font-weight: 900; padding: 0.2rem 0.65rem; border-radius: 8px; }
.rel-val.high   { background: #dcfce7; color: #14532d; }
.rel-val.medium { background: #fef3c7; color: #78350f; }
.rel-val.low    { background: #fee2e2; color: #7f1d1d; }
</style>
