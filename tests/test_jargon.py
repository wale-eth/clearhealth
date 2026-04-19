"""Tests for the jargon detection engine."""

import pytest

from clearhealth.jargon import JargonDetector, JargonMatch, JargonSummary


@pytest.fixture
def detector():
    return JargonDetector()


class TestJargonDetection:
    """Test medical jargon detection."""

    def test_single_word_detection(self, detector):
        result = detector.detect("The patient has hypertension.")
        assert result.total_jargon_count >= 1
        terms = [m.term.lower() for m in result.matches]
        assert "hypertension" in terms

    def test_multi_word_detection(self, detector):
        result = detector.detect("Diagnosed with myocardial infarction.")
        terms = [m.term.lower() for m in result.matches]
        assert "myocardial infarction" in terms

    def test_plain_english_suggestion(self, detector):
        result = detector.detect("The patient has hypertension.")
        match = next(m for m in result.matches if m.term.lower() == "hypertension")
        assert "high blood pressure" in match.plain.lower()

    def test_no_jargon_in_simple_text(self, detector):
        result = detector.detect("The dog ran across the park and jumped over the fence.")
        assert result.total_jargon_count == 0

    def test_multiple_terms(self, detector):
        text = "Patient has hypertension, tachycardia, and dyspnoea."
        result = detector.detect(text)
        assert result.total_jargon_count >= 3
        assert result.unique_terms >= 3

    def test_case_insensitive(self, detector):
        result = detector.detect("HYPERTENSION was noted.")
        assert result.total_jargon_count >= 1

    def test_multi_word_priority_over_single(self, detector):
        """Multi-word terms should be matched before their components."""
        result = detector.detect("Patient had myocardial infarction.")
        terms = [m.term.lower() for m in result.matches]
        # Should match "myocardial infarction" as one term, not "myocardial" separately
        assert "myocardial infarction" in terms

    def test_no_overlapping_matches(self, detector):
        """Matches should not overlap."""
        result = detector.detect("Acute myocardial infarction detected.")
        ranges = [(m.start, m.end) for m in result.matches]
        for i, (s1, e1) in enumerate(ranges):
            for j, (s2, e2) in enumerate(ranges):
                if i != j:
                    assert not (s1 < e2 and s2 < e1), f"Overlap: {ranges[i]} and {ranges[j]}"


class TestJargonSummary:
    """Test aggregate statistics."""

    def test_jargon_density(self, detector):
        text = "hypertension tachycardia dyspnoea normal normal normal normal normal normal normal"
        result = detector.detect(text)
        # 3 jargon terms in 10 words = 30 per 100
        assert result.jargon_density > 0

    def test_categories(self, detector):
        text = "Patient has hypertension and was given an analgesic."
        result = detector.detect(text)
        assert "condition" in result.categories or "medication" in result.categories

    def test_to_dict(self, detector):
        result = detector.detect("The patient has hypertension.")
        d = result.to_dict()
        assert "total_jargon_count" in d
        assert "matches" in d
        assert isinstance(d["matches"], list)


class TestCustomVocabulary:
    """Test adding custom terms."""

    def test_extra_terms(self):
        detector = JargonDetector(
            extra_terms={"stat": {"plain": "immediately", "category": "abbreviation"}}
        )
        result = detector.detect("Give medication stat.")
        terms = [m.term.lower() for m in result.matches]
        assert "stat" in terms

    def test_vocabulary_size(self):
        base = JargonDetector()
        custom = JargonDetector(extra_terms={"xyzterm": {"plain": "test", "category": "test"}})
        assert custom.vocabulary_size == base.vocabulary_size + 1


class TestSuggest:
    """Test single-term lookup."""

    def test_known_term(self, detector):
        assert detector.suggest("hypertension") is not None
        assert "blood pressure" in detector.suggest("hypertension").lower()

    def test_unknown_term(self, detector):
        assert detector.suggest("flibbertigibbet") is None

    def test_case_insensitive(self, detector):
        assert detector.suggest("Hypertension") == detector.suggest("hypertension")
