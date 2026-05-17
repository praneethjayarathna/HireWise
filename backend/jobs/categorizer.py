"""
SBERT-based zero-shot sentence categorizer for job descriptions.

Strategy
--------
1. Split the raw text into sentences / short paragraphs, tracking section
   headers to provide context boosts.
2. Encode every sentence with SBERT (all-mpnet-base-v2 – higher accuracy).
3. Encode multiple diverse anchor phrases per category and use their mean
   embedding as the category vector.
4. Assign each sentence to the category with the highest cosine similarity,
   applying a small boost when the sentence falls under a matching header.
5. Apply a confidence threshold – sentences below it are dropped.
6. Multi-label: if a second category is within 0.05 of the best score and
   both exceed the threshold, add the sentence to both categories.
7. Return a dict with four lists of sentences.

The model is loaded once (lazy singleton) so it is not re-loaded per request.
"""

from __future__ import annotations

import re
import threading
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

_model = None
_lock = threading.Lock()

CONFIDENCE_THRESHOLD = 0.25
MULTI_LABEL_MARGIN = 0.05
CONTEXT_BOOST = 0.15

# Multiple diverse anchor phrases per category for richer semantic coverage.
CATEGORY_ANCHORS: Dict[str, List[str]] = {
    "overview": [
        "company overview and introduction",
        "about us and who we are",
        "job summary and position description",
        "about the role and what we do",
        "our mission and company culture",
        "introduction to the team and organisation",
    ],
    "responsibilities": [
        "key responsibilities and job duties",
        "what you will do day to day",
        "role expectations and accountabilities",
        "tasks and deliverables you will own",
        "your day-to-day activities and projects",
        "core functions and primary duties of the role",
    ],
    "qualifications": [
        "required qualifications and education requirements",
        "minimum years of experience needed",
        "degree or certification required",
        "preferred qualifications and background",
        "academic credentials and professional experience",
        "eligibility criteria and mandatory requirements",
    ],
    "skills": [
        "technical skills and programming languages",
        "tools and technologies you should know",
        "soft skills and interpersonal competencies",
        "proficiency in frameworks and platforms",
        "knowledge of and ability to use specific software",
        "core competencies and areas of expertise",
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


def _get_model():
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                from dotenv import load_dotenv
                load_dotenv()
                from sentence_transformers import SentenceTransformer
                _model = SentenceTransformer("all-mpnet-base-v2")
    return _model


_HEADER_PATTERN = re.compile(
    r"\b(overview|summary|about us|about the (role|company|team|position|job)|"
    r"who we are|introduction|profile|objective|professional summary|"
    r"career summary|job description|position description|role description|"
    r" qualifications|requirements?)\b", re.I
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

    A header is: short (<= 60 chars), ends with ':', is ALL-CAPS, or
    matches one of the known header keyword patterns.
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

    # Keyword match regardless of formatting
    for pattern, cat_idx in _HEADER_KEYWORDS:
        if pattern.search(stripped) and is_short:
            return cat_idx

    return None


def _split_sentences(text: str) -> List[Tuple[str, Optional[int]]]:
    """
    Split text into (sentence, context_category_index) pairs.

    context_category_index is the category inferred from the most recent
    section header, or None if no header has been seen yet.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    result: List[Tuple[str, Optional[int]]] = []
    current_context: Optional[int] = None

    for line in lines:
        header_cat = _is_header(line)
        if header_cat is not None:
            current_context = header_cat
            # Don't emit the header line itself as a sentence to classify
            continue

        parts = re.split(r"(?<=[.!?])\s+", line)
        for part in parts:
            part = part.strip()
            if len(part) > 10:
                result.append((part, current_context))

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
    anchor_embeddings = _build_anchor_embeddings(model)

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
            continue  # drop low-confidence sentences

        result[CATEGORIES[best_idx]].append(sentence)

        # Multi-label: check if any other category is within the margin
        for cat_idx in range(len(CATEGORIES)):
            if cat_idx == best_idx:
                continue
            if scores[cat_idx] >= CONFIDENCE_THRESHOLD and (best_score - scores[cat_idx]) <= MULTI_LABEL_MARGIN:
                result[CATEGORIES[cat_idx]].append(sentence)

    return result


def compute_similarity(
    job_description: Dict[str, List[str]],
    resume: Dict[str, List[str]],
) -> Dict[str, float]:
    """
    Compute similarity scores between categorized job description and resume.

    For each category:
    - Encode all sentences from both job description and resume
    - Compute pairwise cosine similarity
    - Use maximum similarity per resume sentence, then average

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

        sim_matrix = np.stack(
            [_cosine_similarity(resume_embeddings, job_embeddings[i]) for i in range(len(job_sentences))],
            axis=1,
        )

        if sim_matrix.size == 0:
            scores[cat] = 0.0
            continue

        max_sims = sim_matrix.max(axis=1)
        scores[cat] = float(np.mean(max_sims))

    overall = sum(scores[cat] * category_weights[cat] for cat in CATEGORIES)
    scores["overall"] = overall

    return scores


def _filter_headers(sentences: List[str]) -> List[str]:
    """Remove header-like lines from a list of sentences."""
    return [s for s in sentences if not _looks_like_header(s)]


def compare_overviews(
    jd_sentences: List[str],
    resume_sentences: List[str],
    threshold: float = 0.30,
) -> List[Dict[str, Any]]:
    """
    Compare overview sentences from JD and resume using SBERT.

    Header-like lines are automatically filtered out before comparison.

    For each JD overview sentence, finds the best matching resume overview
    sentence via pairwise cosine similarity. Returns all pairs sorted by
    similarity descending (only pairs above *threshold*).

    Returns
    -------
    list of dicts with keys: job_sentence, resume_sentence, similarity
    """
    jd_sentences = _filter_headers(jd_sentences)
    resume_sentences = _filter_headers(resume_sentences)

    if not jd_sentences or not resume_sentences:
        return []

    model = _get_model()

    jd_embeddings = model.encode(jd_sentences, convert_to_numpy=True, show_progress_bar=False)
    resume_embeddings = model.encode(resume_sentences, convert_to_numpy=True, show_progress_bar=False)

    jd_norm = jd_embeddings / (np.linalg.norm(jd_embeddings, axis=1, keepdims=True) + 1e-10)
    resume_norm = resume_embeddings / (np.linalg.norm(resume_embeddings, axis=1, keepdims=True) + 1e-10)

    sim_matrix = jd_norm @ resume_norm.T

    matches: List[Dict[str, Any]] = []
    for i, jd_sent in enumerate(jd_sentences):
        best_idx = int(np.argmax(sim_matrix[i]))
        best_score = float(sim_matrix[i][best_idx])
        if best_score >= threshold:
            matches.append({
                "job_sentence": jd_sent,
                "resume_sentence": resume_sentences[best_idx],
                "similarity": round(best_score, 4),
            })

    matches.sort(key=lambda x: x["similarity"], reverse=True)
    return matches
