"""
SBERT-based zero-shot sentence categorizer for job descriptions.

Strategy
--------
1. Split the raw text into sentences / short paragraphs.
2. Encode every sentence with SBERT (all-MiniLM-L6-v2 – fast & accurate).
3. Encode four category anchor phrases.
4. Assign each sentence to the category whose anchor has the highest
   cosine similarity.
5. Return a dict with four lists of sentences.

The model is loaded once at module level (lazy singleton) so it is not
re-loaded on every request.
"""

from __future__ import annotations

import re
import threading
from typing import Dict, List

import numpy as np

_model = None
_lock = threading.Lock()

CATEGORY_ANCHORS: Dict[str, str] = {
    "overview": (
        "company overview, job summary, about the role, position description, "
        "about us, who we are, introduction to the job"
    ),
    "responsibilities": (
        "job duties, responsibilities, what you will do, day-to-day tasks, "
        "key responsibilities, role expectations, accountabilities"
    ),
    "qualifications": (
        "required qualifications, education requirements, years of experience, "
        "degree required, minimum requirements, preferred qualifications, "
        "certifications needed"
    ),
    "skills": (
        "technical skills, soft skills, tools and technologies, programming languages, "
        "competencies, proficiency in, knowledge of, ability to"
    ),
}

CATEGORIES = list(CATEGORY_ANCHORS.keys())


def _get_model():
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                from sentence_transformers import SentenceTransformer
                _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _split_sentences(text: str) -> List[str]:
    """Split text into meaningful chunks (sentences or bullet points)."""
    # Normalise line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Split on newlines first (preserves bullet structure)
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    sentences: List[str] = []
    for line in lines:
        # Further split long lines on sentence boundaries
        parts = re.split(r"(?<=[.!?])\s+", line)
        sentences.extend(p.strip() for p in parts if len(p.strip()) > 10)
    return sentences


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Compute cosine similarity between a matrix and a vector."""
    a_norm = a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-10)
    b_norm = b / (np.linalg.norm(b) + 1e-10)
    return a_norm @ b_norm


def categorize(text: str) -> Dict[str, List[str]]:
    """
    Categorize sentences in *text* into overview / responsibilities /
    qualifications / skills using SBERT cosine similarity.

    Returns
    -------
    dict with keys: overview, responsibilities, qualifications, skills
    Each value is a list of sentence strings.
    """
    model = _get_model()

    sentences = _split_sentences(text)
    if not sentences:
        return {cat: [] for cat in CATEGORIES}

    # Encode sentences and anchors
    sentence_embeddings = model.encode(sentences, convert_to_numpy=True, show_progress_bar=False)
    anchor_embeddings = model.encode(
        list(CATEGORY_ANCHORS.values()),
        convert_to_numpy=True,
        show_progress_bar=False,
    )

    # similarity matrix: (n_sentences, n_categories)
    sim_matrix = np.stack(
        [_cosine_similarity(sentence_embeddings, anchor_embeddings[i]) for i in range(len(CATEGORIES))],
        axis=1,
    )

    assigned = np.argmax(sim_matrix, axis=1)

    result: Dict[str, List[str]] = {cat: [] for cat in CATEGORIES}
    for idx, cat_idx in enumerate(assigned):
        result[CATEGORIES[cat_idx]].append(sentences[idx])

    return result
