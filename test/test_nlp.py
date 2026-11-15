"""
test/test_nlp.py — NLP Service Tests (TF-IDF + Cosine Similarity)
AI Chatbot for University Help Desk | KIET Group of Institutions
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "backend"))


class TestPreprocessing:
    """Tests for the text preprocessing pipeline."""

    def test_tokenise_basic(self):
        from services.nlp_service import preprocess
        tokens = preprocess("What is KIET?")
        assert isinstance(tokens, list)
        assert len(tokens) > 0

    def test_stopwords_removed(self):
        from services.nlp_service import preprocess
        tokens = preprocess("What is the location of KIET?")
        stopwords = {"what", "is", "the", "of"}
        for token in tokens:
            assert token not in stopwords

    def test_lowercasing(self):
        from services.nlp_service import preprocess
        tokens = preprocess("KIET GHAZIABAD ADMISSION")
        for token in tokens:
            assert token == token.lower()

    def test_empty_string(self):
        from services.nlp_service import preprocess
        tokens = preprocess("")
        assert tokens == []

    def test_none_input(self):
        from services.nlp_service import preprocess
        tokens = preprocess(None)
        assert tokens == []

    def test_special_chars_removed(self):
        from services.nlp_service import preprocess
        tokens = preprocess("KIET!!! @#$ admission???")
        for token in tokens:
            assert token.isalpha() or token.isalnum()


class TestTFIDFEngine:
    """Tests for the TFIDFEngine class."""

    def test_fit_builds_index(self):
        from services.nlp_service import TFIDFEngine
        engine = TFIDFEngine()
        questions = ["What is KIET?", "Where is KIET located?", "How to get admission?"]
        engine.fit(questions)
        assert engine.is_fitted
        assert engine.corpus_size == 3

    def test_query_returns_results(self):
        from services.nlp_service import TFIDFEngine
        engine = TFIDFEngine()
        engine.fit(["What is KIET?", "Where is KIET located?", "How to get admission?"])
        results = engine.query("KIET location", k=3)
        assert isinstance(results, list)
        assert len(results) > 0

    def test_query_returns_tuples(self):
        from services.nlp_service import TFIDFEngine
        engine = TFIDFEngine()
        engine.fit(["KIET is a college in Ghaziabad."])
        results = engine.query("college Ghaziabad")
        for item in results:
            assert isinstance(item, tuple)
            assert len(item) == 2

    def test_similar_query_has_high_score(self):
        from services.nlp_service import TFIDFEngine
        engine = TFIDFEngine()
        engine.fit([
            "What is KIET Group of Institutions?",
            "How do I apply for admission?",
            "What is the contact number?",
        ])
        results = engine.query("KIET Group of Institutions information")
        best_idx, best_score = results[0]
        assert best_score > 0.0

    def test_unrelated_query_has_lower_score(self):
        from services.nlp_service import TFIDFEngine
        engine = TFIDFEngine()
        engine.fit([
            "What is KIET?",
            "Where is the library?",
            "How to pay fees?",
        ])
        results_related = engine.query("KIET institution college")
        results_unrelated = engine.query("xyznonsenseword")
        score_related = results_related[0][1] if results_related else 0
        score_unrelated = results_unrelated[0][1] if results_unrelated else 0
        assert score_related >= score_unrelated

    def test_scores_sorted_descending(self):
        from services.nlp_service import TFIDFEngine
        engine = TFIDFEngine()
        engine.fit([
            "KIET admission process",
            "Hostel facilities at KIET",
            "Contact number for KIET help desk",
        ])
        results = engine.query("KIET admission")
        scores = [score for _, score in results]
        assert scores == sorted(scores, reverse=True)

    def test_empty_corpus(self):
        from services.nlp_service import TFIDFEngine
        engine = TFIDFEngine()
        engine.fit([])
        results = engine.query("KIET")
        assert results == []

    def test_cosine_similarity_identical_vectors(self):
        from services.nlp_service import TFIDFEngine
        engine = TFIDFEngine()
        vec = {"kiet": 0.5, "admission": 0.3}
        score = engine._cosine_similarity(vec, vec)
        assert abs(score - 1.0) < 1e-9

    def test_cosine_similarity_zero_vector(self):
        from services.nlp_service import TFIDFEngine
        engine = TFIDFEngine()
        score = engine._cosine_similarity({}, {"kiet": 0.5})
        assert score == 0.0
