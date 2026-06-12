"""
Shared SBERT model singleton.

Both categorizer.py and skills_extractor.py import _get_model from here
so the sentence-transformers model is loaded exactly once per process.
"""

import threading
from typing import Optional

_model = None
_lock = threading.Lock()


def get_model():
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                from dotenv import load_dotenv
                load_dotenv()
                from sentence_transformers import SentenceTransformer
                _model = SentenceTransformer("all-mpnet-base-v2")
    return _model
