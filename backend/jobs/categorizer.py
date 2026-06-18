"""
SBERT-based zero-shot sentence categorizer for job descriptions.

Strategy
--------
1. Split the raw text into sentences / short paragraphs, tracking section
   headers to provide context boosts.
2. Encode every sentence with SBERT (all-mpnet-base-v2 – higher accuracy).
3. Encode multiple diverse anchor phrases per category and use their mean
   embedding as the category vector.  Anchor embeddings are cached globally
   so they are computed only once per process.
4. Assign each sentence to the category with the highest cosine similarity,
   applying a small boost when the sentence falls under a matching header.
5. Apply a confidence threshold – sentences below it are dropped.
6. Multi-label: if a second category is within 0.05 of the best score and
   both exceed the threshold, add the sentence to both categories.
7. Return a dict with four lists of sentences.

Similarity scoring (compute_similarity)
----------------------------------------
For the *overview* category we use a coverage-weighted formula so that a
sparse but highly similar resume does not outscore a comprehensive one.

For all other categories we use a *JD-perspective* max-mean:
  For each JD sentence find the best-matching resume sentence, then average
  those per-JD scores.  This directly measures how many JD requirements are
  covered by the resume, rather than how well the resume's own sentences
  happen to match something in the JD.
"""

from __future__ import annotations

import re
import threading
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .model_loader import get_model as _get_model

CONFIDENCE_THRESHOLD = 0.25
MULTI_LABEL_MARGIN = 0.05
CONTEXT_BOOST = 0.15

# IT-domain anchor phrases per category for richer semantic coverage.
CATEGORY_ANCHORS: Dict[str, List[str]] = {
    "overview": [
        "company overview and introduction to the engineering team",
        "about us and what our software product does",
        "job summary for software engineer or developer position",
        "about the role on our technology or platform team",
        "our mission and engineering culture",
        "introduction to the team and the systems we build",
    ],
    "responsibilities": [
        "key responsibilities: design, develop, and deploy software systems",
        "what you will do: write code, build features, and review pull requests",
        "role expectations: implement backend services and APIs",
        "tasks: develop, test, and maintain scalable applications",
        "your day-to-day: coding, debugging, and collaborating with engineers",
        "core engineering duties: architect solutions and deliver software",
    ],
    "qualifications": [
        "required qualifications: degree in computer science or software engineering",
        "minimum years of software development or engineering experience",
        "bachelor's or master's degree in a technical field required",
        "preferred qualifications: prior experience in cloud or distributed systems",
        "academic credentials and professional software development background",
        "eligibility: strong programming foundation and problem-solving ability",
    ],
    "skills": [
        "technical skills: programming languages, frameworks, and databases",
        "tools and technologies: cloud platforms, DevOps, and CI/CD pipelines",
        "proficiency in backend or frontend frameworks and REST APIs",
        "knowledge of software development tools and version control",
        "core technical competencies: algorithms, data structures, system design",
        "expertise in software engineering practices and agile methodologies",
    ],
}

CATEGORIES = list(CATEGORY_ANCHORS.keys())

# Header keywords mapped to their corresponding category index.
_HEADER_KEYWORDS: List[Tuple[re.Pattern, int]] = [
    (re.compile(r"\b(overview|about us|about the (role|company|team)|who we are)\b", re.I), 0),
    (re.compile(r"\b(responsibilities|what you('ll| will) do|your role|duties)\b", re.I), 1),
    (re.compile(r"\b(requirements?|qualifications?|what we('re| are) looking for|who you are)\b", re.I), 2),
    (re.compile(r"\b(skills?|technologies|tools|competencies|expertise)\b", re.I), 3),
]

# ---------------------------------------------------------------------------
# Cached anchor embeddings — computed once per process
# ---------------------------------------------------------------------------
_anchor_embeddings: Optional[np.ndarray] = None
_anchor_lock = threading.Lock()


def _get_anchor_embeddings(model) -> np.ndarray:
    global _anchor_embeddings
    if _anchor_embeddings is None:
        with _anchor_lock:
            if _anchor_embeddings is None:
                _anchor_embeddings = _build_anchor_embeddings(model)
    return _anchor_embeddings


_HEADER_PATTERN = re.compile(
    r"\b(overview|summary|about us|about the (role|company|team|position|job)|"
    r"who we are|introduction|profile|objective|professional summary|"
    r"career summary|career objective|job description|position description|role description|"
    r"qualifications|requirements?|skills|technologies|education|experience|"
    r"responsibilities|duties|certifications|projects|publications|awards|"
    r"languages|additional information|references)\b", re.I
)


def _looks_like_header(text: str) -> bool:
    stripped = text.strip()
    if not stripped or len(stripped) > 80:
        return False
    ends_colon = stripped.endswith(":")
    is_allcaps = stripped.isupper() and len(stripped) > 2
    is_short = len(stripped) <= 60
    if ends_colon or is_allcaps:
        if _HEADER_PATTERN.search(stripped):
            return True
    if is_short and _HEADER_PATTERN.fullmatch(stripped.strip(":").strip()):
        return True
    return False


def _is_header(line: str) -> Optional[int]:
    """
    Return the category index if *line* looks like a section header,
    otherwise return None.
    """
    stripped = line.strip()
    if not stripped:
        return None

    is_short = len(stripped) <= 60
    ends_colon = stripped.endswith(":")
    is_allcaps = stripped.isupper() and len(stripped) > 2

    if is_short and (ends_colon or is_allcaps):
        for pattern, cat_idx in _HEADER_KEYWORDS:
            if pattern.search(stripped):
                return cat_idx

    for pattern, cat_idx in _HEADER_KEYWORDS:
        if pattern.search(stripped) and is_short:
            return cat_idx

    return None


def _split_sentences(text: str) -> List[Tuple[str, Optional[int]]]:
    """
    Split text into (sentence, context_category_index) pairs.

    context_category_index is the category inferred from the most recent
    section header, or None if no header has been seen yet.

    PDF word-wrapping means a single sentence is often spread across
    multiple lines.  We reconstruct paragraphs by buffering consecutive
    lines that do NOT end with a sentence terminator (.!?), then split
    the reconstructed paragraph at proper boundaries.  This prevents
    word-wrapped fragments like "passion for technology with my"  from
    being treated as independent sentences.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    raw_lines = [l.strip() for l in text.split("\n") if l.strip()]

    # --- Pass 1: reconstruct paragraphs ---
    # Lines ending with .!? close the current buffer (sentence complete).
    # Lines starting with a bullet marker (•, -, * …) are standalone items
    # and should never be joined with adjacent prose lines.
    _sent_end  = re.compile(r'[.!?]\s*$')
    _bullet    = re.compile(r'^[•\-*◦○●▸►→]')
    paragraphs: List[Tuple[str, Optional[int]]] = []
    current_context: Optional[int] = None
    buf: List[str] = []

    for line in raw_lines:
        header_cat = _is_header(line)
        if header_cat is not None:
            if buf:
                paragraphs.append((' '.join(buf), current_context))
                buf = []
            current_context = header_cat
            continue

        is_bullet = bool(_bullet.match(line))

        # Flush existing buffer before a bullet so bullets are never joined
        # with preceding prose lines.
        if is_bullet and buf:
            paragraphs.append((' '.join(buf), current_context))
            buf = []

        buf.append(line)

        # Close buffer on sentence terminator OR after a standalone bullet.
        if _sent_end.search(line) or is_bullet:
            paragraphs.append((' '.join(buf), current_context))
            buf = []

    if buf:
        paragraphs.append((' '.join(buf), current_context))

    # --- Pass 2: split each reconstructed paragraph into sentences ---
    result: List[Tuple[str, Optional[int]]] = []
    for para, ctx in paragraphs:
        parts = re.split(r'(?<=[.!?])\s+', para)
        for part in parts:
            part = part.strip()
            if len(part) > 10:
                result.append((part, ctx))

    return result


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Cosine similarity between each row of *a* and vector *b*."""
    a_norm = a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-10)
    b_norm = b / (np.linalg.norm(b) + 1e-10)
    return a_norm @ b_norm


def _build_anchor_embeddings(model) -> np.ndarray:
    """
    Encode all anchor phrases and return the per-category mean embeddings.
    Shape: (n_categories, embedding_dim)
    """
    anchors: List[np.ndarray] = []
    for cat in CATEGORIES:
        phrases = CATEGORY_ANCHORS[cat]
        phrase_embs = model.encode(phrases, convert_to_numpy=True, show_progress_bar=False)
        anchors.append(phrase_embs.mean(axis=0))
    return np.stack(anchors, axis=0)


def categorize(text: str) -> Dict[str, List[str]]:
    """
    Categorize sentences in *text* into overview / responsibilities /
    qualifications / skills using SBERT cosine similarity.

    Returns
    -------
    dict with keys: overview, responsibilities, qualifications, skills
    Each value is a list of sentence strings.
    Sentences below CONFIDENCE_THRESHOLD are silently dropped.
    """
    model = _get_model()

    sentence_pairs = _split_sentences(text)
    if not sentence_pairs:
        return {cat: [] for cat in CATEGORIES}

    sentences = [s for s, _ in sentence_pairs]
    contexts = [c for _, c in sentence_pairs]

    sentence_embeddings = model.encode(sentences, convert_to_numpy=True, show_progress_bar=False)
    anchor_embeddings = _get_anchor_embeddings(model)

    # sim_matrix shape: (n_sentences, n_categories)
    sim_matrix = np.stack(
        [_cosine_similarity(sentence_embeddings, anchor_embeddings[i]) for i in range(len(CATEGORIES))],
        axis=1,
    )

    # Apply context boost
    for idx, ctx in enumerate(contexts):
        if ctx is not None:
            sim_matrix[idx, ctx] += CONTEXT_BOOST

    result: Dict[str, List[str]] = {cat: [] for cat in CATEGORIES}

    for idx, sentence in enumerate(sentences):
        scores = sim_matrix[idx]
        best_idx = int(np.argmax(scores))
        best_score = scores[best_idx]

        if best_score < CONFIDENCE_THRESHOLD:
            continue

        result[CATEGORIES[best_idx]].append(sentence)

        # Multi-label: check if any other category is within the margin
        for cat_idx in range(len(CATEGORIES)):
            if cat_idx == best_idx:
                continue
            if scores[cat_idx] >= CONFIDENCE_THRESHOLD and (best_score - scores[cat_idx]) <= MULTI_LABEL_MARGIN:
                result[CATEGORIES[cat_idx]].append(sentence)

    return result


def _greedy_matches(
    jd_embeddings: np.ndarray,
    resume_embeddings: np.ndarray,
    threshold: float = 0.0,
) -> Tuple[List[Tuple[int, int, float]], float, float]:
    """
    Greedy one-to-one matching between JD and resume embeddings.

    Returns
    -------
    (matches, simpleAvg, coverageWeighted)
        matches: list of (jd_idx, resume_idx, similarity)
        simpleAvg: mean similarity of matched pairs
        coverageWeighted: simpleAvg × (matchedPairs / avgDocLength)
    """
    jd_norm = jd_embeddings / (np.linalg.norm(jd_embeddings, axis=1, keepdims=True) + 1e-10)
    resume_norm = resume_embeddings / (np.linalg.norm(resume_embeddings, axis=1, keepdims=True) + 1e-10)
    sim_matrix = jd_norm @ resume_norm.T

    n_jd = len(jd_embeddings)
    n_res = len(resume_embeddings)

    available = list(range(n_res))
    pairs: List[Tuple[int, int, float]] = []

    jd_best = [
        float(sim_matrix[i, available].max()) if available else 0.0
        for i in range(n_jd)
    ]
    jd_order = sorted(range(n_jd), key=lambda i: jd_best[i], reverse=True)

    for i in jd_order:
        if not available:
            break
        sub = sim_matrix[i, available]
        pos = int(np.argmax(sub))
        score = float(sub[pos])
        if score >= threshold:
            idx = available.pop(pos)
            pairs.append((i, idx, score))

    n_matched = len(pairs)
    simple_avg = float(np.mean([p[2] for p in pairs])) if pairs else 0.0
    avg_len = (n_jd + n_res) / 2.0
    coverage = n_matched / avg_len if avg_len > 0 else 0.0
    coverage_weighted = simple_avg * coverage

    return pairs, simple_avg, coverage_weighted


def compute_similarity(
    job_description: Dict[str, List[str]],
    resume: Dict[str, List[str]],
) -> Dict[str, float]:
    """
    Compute similarity scores between categorized job description and resume.

    For overview: coverage-weighted formula — simpleAvg × (matched / avgDocLength).

    For other categories: JD-perspective max-mean.
      For each JD sentence, find the best-matching resume sentence, then average
      those per-JD-sentence scores.  This directly measures how many JD
      requirements are satisfied by the resume (missing requirements drag the
      mean down), rather than how well the resume's own sentences happen to
      match something in the JD.

    Returns dict with per-category scores and 'overall' (weighted average).
    """
    model = _get_model()
    category_weights = {
        "overview": 0.10,
        "responsibilities": 0.30,
        "qualifications": 0.25,
        "skills": 0.35,
    }

    scores: Dict[str, float] = {}

    for cat in CATEGORIES:
        job_sentences = job_description.get(cat, [])
        resume_sentences = resume.get(cat, [])

        if not job_sentences or not resume_sentences:
            scores[cat] = 0.0
            continue

        job_embeddings = model.encode(job_sentences, convert_to_numpy=True, show_progress_bar=False)
        resume_embeddings = model.encode(resume_sentences, convert_to_numpy=True, show_progress_bar=False)

        if cat == "overview":
            _, simple_avg, coverage_weighted = _greedy_matches(
                job_embeddings, resume_embeddings, threshold=0.0,
            )
            scores[cat] = round(coverage_weighted, 4)
        else:
            # JD-perspective: shape (n_resume, n_job)
            r_norm = resume_embeddings / (np.linalg.norm(resume_embeddings, axis=1, keepdims=True) + 1e-10)
            j_norm = job_embeddings / (np.linalg.norm(job_embeddings, axis=1, keepdims=True) + 1e-10)
            sim_matrix = r_norm @ j_norm.T

            # For each JD sentence, best resume match
            max_per_jd = sim_matrix.max(axis=0)   # shape: (n_job,)
            scores[cat] = round(float(np.mean(max_per_jd)), 4)

    overall = sum(scores[cat] * category_weights[cat] for cat in CATEGORIES)
    scores["overall"] = overall

    return scores


def _filter_headers(sentences: List[str]) -> List[str]:
    """Remove header-like lines from a list of sentences."""
    return [s for s in sentences if not _looks_like_header(s)]


def compare_overviews(
    jd_sentences: List[str],
    resume_sentences: List[str],
    threshold: float = 0.40,
) -> List[Dict[str, Any]]:
    """
    Compare overview sentences from JD and resume using SBERT.

    Header-like lines are automatically filtered out before comparison.
    Very short lines (< 15 chars) are also removed as noise.

    Uses greedy one-to-one matching: each resume sentence can match at
    most one JD sentence, preventing a single resume sentence from being
    paired with multiple JD sentences.

    Returns
    -------
    list of dicts with keys: job_sentence, resume_sentence, similarity
    sorted descending by similarity (only pairs above *threshold*).
    """
    jd_sentences = _filter_headers(jd_sentences)
    resume_sentences = _filter_headers(resume_sentences)

    jd_sentences = [s for s in jd_sentences if len(s) >= 15]
    resume_sentences = [s for s in resume_sentences if len(s) >= 15]

    if not jd_sentences or not resume_sentences:
        return []

    model = _get_model()

    jd_embeddings = model.encode(jd_sentences, convert_to_numpy=True, show_progress_bar=False)
    resume_embeddings = model.encode(resume_sentences, convert_to_numpy=True, show_progress_bar=False)

    pairs, _, _ = _greedy_matches(jd_embeddings, resume_embeddings, threshold=threshold)

    return [
        {
            "job_sentence": jd_sentences[j],
            "resume_sentence": resume_sentences[r],
            "similarity": round(s, 4),
        }
        for j, r, s in pairs
    ]
