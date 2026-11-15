"""
services/nlp_service.py — Pure Python NLP Engine
AI Chatbot for University Help Desk | KIET Group of Institutions

Implements:
    - Text normalisation & preprocessing
    - Tokenisation with stopword removal and stemming heuristics
    - TF-IDF vectorisation (from scratch — no external dependencies)
    - Cosine similarity
    - FAQ matching with configurable confidence threshold

This module is intentionally written without scikit-learn so the application
runs on any standard Python 3.x installation.

Algorithm reference:
    TF(t, d)  = (count of term t in doc d) / (total terms in d)
    IDF(t, D) = log((|D| + 1) / (df(t) + 1)) + 1   [smoothed]
    TF-IDF    = TF * IDF
    Similarity = cos(θ) = (A · B) / (|A| × |B|)
"""

import re
import math
from collections import Counter


# ──────────────────────────────────────────────
# Stopwords — common English words ignored during vectorisation
# ──────────────────────────────────────────────

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "dare", "ought",
    "of", "in", "to", "for", "on", "at", "by", "from", "with", "about",
    "into", "through", "during", "before", "after", "above", "below",
    "and", "or", "but", "not", "so", "yet", "both", "either", "neither",
    "this", "that", "these", "those", "such", "own", "same",
    "i", "me", "my", "myself", "we", "our", "ours", "you", "your",
    "it", "its", "itself", "they", "them", "their", "what", "which",
    "who", "whom", "how", "when", "where", "why", "all", "any", "few",
    "more", "most", "other", "some", "than", "too", "very", "just",
    "also", "get", "got", "let", "much", "many", "want", "know",
    "tell", "help", "please", "hi", "hello", "hey", "sir", "madam",
}


# ──────────────────────────────────────────────
# Lightweight suffix-stripping (poor man's stemmer)
# ──────────────────────────────────────────────

def _strip_suffix(word: str) -> str:
    """Remove common English suffixes to normalise word forms."""
    for suffix in ("tion", "ing", "ness", "ment", "ity", "ly", "ed", "er", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


# ──────────────────────────────────────────────
# Text preprocessing
# ──────────────────────────────────────────────

def preprocess(text: str) -> list[str]:
    """
    Normalise and tokenise text into a list of meaningful stems.

    Steps:
        1. Lowercase
        2. Expand common contractions
        3. Remove punctuation / special characters
        4. Split into tokens
        5. Remove stopwords and very short tokens
        6. Apply suffix-stripping
    """
    if not text or not isinstance(text, str):
        return []

    # Lowercase
    text = text.lower()

    # Expand contractions
    contractions = {
        "what's": "what is", "where's": "where is", "when's": "when is",
        "how's": "how is", "who's": "who is", "it's": "it is",
        "don't": "do not", "doesn't": "does not", "didn't": "did not",
        "won't": "will not", "can't": "cannot", "i'm": "i am",
        "i've": "i have", "i'll": "i will", "you're": "you are",
        "they're": "they are", "we're": "we are", "isn't": "is not",
        "aren't": "are not", "wasn't": "was not", "weren't": "were not",
    }
    for contraction, expansion in contractions.items():
        text = text.replace(contraction, expansion)

    # Remove punctuation (keep only letters, digits, spaces)
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Tokenise
    tokens = text.split()

    # Remove stopwords, single-character tokens, and pure-digit tokens
    tokens = [
        t for t in tokens
        if t not in STOPWORDS and len(t) > 1 and not t.isdigit()
    ]

    # Strip common suffixes (stemming heuristic)
    tokens = [_strip_suffix(t) for t in tokens]

    # Remove duplicates while preserving order
    seen = set()
    unique = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            unique.append(t)

    return unique


# ──────────────────────────────────────────────
# TF-IDF engine
# ──────────────────────────────────────────────

class TFIDFEngine:
    """
    Builds and maintains a TF-IDF index over a corpus of FAQ questions.

    Usage:
        engine = TFIDFEngine()
        engine.fit(questions_list)       # build the index
        results = engine.query(text, k=3)  # retrieve top-k matches
    """

    def __init__(self):
        self._corpus_tokens: list[list[str]] = []
        self._idf: dict[str, float] = {}
        self._tfidf_vectors: list[dict[str, float]] = []
        self._fitted = False

    # ── Build ──────────────────────────────────

    def _compute_tf(self, tokens: list[str]) -> dict[str, float]:
        """Term frequency: count(t, d) / len(d)."""
        if not tokens:
            return {}
        counts = Counter(tokens)
        total = len(tokens)
        return {word: count / total for word, count in counts.items()}

    def _compute_idf(self) -> dict[str, float]:
        """
        Smoothed IDF:
            idf(t) = log((N + 1) / (df(t) + 1)) + 1
        where N = number of documents and df(t) = documents containing t.
        """
        n = len(self._corpus_tokens)
        all_words: set[str] = set(w for doc in self._corpus_tokens for w in doc)
        idf = {}
        for word in all_words:
            df = sum(1 for doc in self._corpus_tokens if word in doc)
            idf[word] = math.log((n + 1) / (df + 1)) + 1.0
        return idf

    def fit(self, questions: list[str]) -> None:
        """
        Build TF-IDF index from a list of question strings.
        Call this whenever the FAQ corpus changes.
        """
        self._corpus_tokens = [preprocess(q) for q in questions]
        self._idf = self._compute_idf()

        self._tfidf_vectors = []
        for tokens in self._corpus_tokens:
            tf = self._compute_tf(tokens)
            vec = {word: tf_val * self._idf.get(word, 1.0)
                   for word, tf_val in tf.items()}
            self._tfidf_vectors.append(vec)

        self._fitted = True

    # ── Query ─────────────────────────────────

    @staticmethod
    def _cosine_similarity(vec_a: dict[str, float],
                           vec_b: dict[str, float]) -> float:
        """
        Cosine similarity between two sparse TF-IDF vectors.
        Returns 0.0 if either vector is the zero vector.
        """
        # Dot product over the intersection of keys (rest contribute 0)
        common_keys = set(vec_a.keys()) & set(vec_b.keys())
        if not common_keys:
            return 0.0

        dot = sum(vec_a[k] * vec_b[k] for k in common_keys)
        mag_a = math.sqrt(sum(v * v for v in vec_a.values()))
        mag_b = math.sqrt(sum(v * v for v in vec_b.values()))

        if mag_a == 0.0 or mag_b == 0.0:
            return 0.0

        return dot / (mag_a * mag_b)

    def _vectorise_query(self, query: str) -> dict[str, float]:
        """Convert a raw query string into a TF-IDF vector using the fitted IDF."""
        tokens = preprocess(query)
        if not tokens:
            return {}
        tf = self._compute_tf(tokens)
        return {word: tf_val * self._idf.get(word, 1.0)
                for word, tf_val in tf.items()}

    def query(self, text: str, k: int = 3) -> list[tuple[int, float]]:
        """
        Retrieve the top-k most similar FAQ indices for the given query.

        Returns:
            List of (index, similarity_score) tuples, sorted descending by score.
            Index corresponds to the position in the original questions list.
        """
        if not self._fitted or not self._tfidf_vectors:
            return []

        query_vec = self._vectorise_query(text)
        if not query_vec:
            return []

        scores = [
            (i, self._cosine_similarity(query_vec, faq_vec))
            for i, faq_vec in enumerate(self._tfidf_vectors)
        ]

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:k]

    @property
    def is_fitted(self) -> bool:
        return self._fitted

    @property
    def corpus_size(self) -> int:
        return len(self._corpus_tokens)


# ──────────────────────────────────────────────
# Module-level singleton (lazy initialisation)
# ──────────────────────────────────────────────

_engine: TFIDFEngine = TFIDFEngine()


def get_engine() -> TFIDFEngine:
    """Return the shared TFIDFEngine instance."""
    return _engine


def rebuild_index(questions: list[str]) -> None:
    """Re-fit the shared engine on an updated list of questions."""
    global _engine
    _engine.fit(questions)
