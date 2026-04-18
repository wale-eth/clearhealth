"""Tests for the main analyzer and report generation."""

import pytest

from clearhealth.analyzer import analyse, analyze, ClearHealthAnalyzer
from clearhealth.report import AccessibilityReport


@pytest.fixture
def analyzer():
    return ClearHealthAnalyzer()


class TestAnalyser:
    """Test the main analysis pipeline."""

    def test_analyse_returns_report(self, analyzer):
        report = analyzer.analyse("Take two tablets by mouth every day.")
        assert isinstance(report, AccessibilityReport)

    def test_simple_text_gets_good_grade(self, analyzer):
        text = (
            "Take your medicine every morning with food. "
            "Drink a full glass of water. "
            "Call your doctor if you feel sick."
        )
        report = analyzer.analyse(text)
        assert report.grade in ("A", "B")

    def test_complex_text_gets_poor_grade(self, analyzer):
        text = (
            "The patient presented with acute myocardial infarction secondary "
            "to atherosclerotic cardiovascular disease. Percutaneous coronary "
            "intervention was performed with concurrent anticoagulant therapy. "
            "Postoperative echocardiogram revealed reduced ventricular function "
            "with bilateral pulmonary oedema requiring intravenous diuretic "
            "administration and continuous haemodynamic monitoring."
        )
        report = analyzer.analyse(text)
        assert report.grade in ("D", "F")

    def test_jargon_detected_in_report(self, analyzer):
        report = analyzer.analyse("The patient has hypertension and dyspnoea.")
        assert report.jargon.total_jargon_count >= 2

    def test_recommendations_generated(self, analyzer):
        report = analyzer.analyse(
            "The bilateral cerebrovascular atherosclerotic pathology "
            "necessitated comprehensive neurological intervention."
        )
        assert len(report.recommendations) > 0

    def test_empty_text_raises(self, analyzer):
        with pytest.raises(ValueError, match="empty"):
            analyzer.analyse("")

    def test_whitespace_only_raises(self, analyzer):
        with pytest.raises(ValueError, match="empty"):
            analyzer.analyse("   \n\t  ")


class TestReportOutput:
    """Test report serialisation."""

    def test_to_dict(self, analyzer):
        report = analyzer.analyse("Simple health advice here.")
        d = report.to_dict()
        assert "grade" in d
        assert "readability" in d
        assert "jargon" in d
        assert "recommendations" in d

    def test_summary_is_string(self, analyzer):
        report = analyzer.analyse("Take your medicine daily.")
        summary = report.summary()
        assert isinstance(summary, str)
        assert "Accessibility Grade" in summary

    def test_summary_includes_jargon_suggestions(self, analyzer):
        report = analyzer.analyse("The patient has hypertension.")
        summary = report.summary()
        assert "hypertension" in summary.lower()
        assert "blood pressure" in summary.lower()


class TestConvenienceFunction:
    """Test the module-level analyse/analyze functions."""

    def test_analyse_function(self):
        report = analyse("Take your medicine with water.")
        assert isinstance(report, AccessibilityReport)

    def test_analyze_alias(self):
        report = analyze("Take your medicine with water.")
        assert isinstance(report, AccessibilityReport)


class TestCustomConfiguration:
    """Test custom analyzer configuration."""

    def test_custom_threshold(self):
        # Very low threshold should flag more sentences as complex
        strict = ClearHealthAnalyzer(complex_sentence_threshold=5.0)
        lenient = ClearHealthAnalyzer(complex_sentence_threshold=20.0)

        text = "This is a moderately complex sentence about health topics and wellness."
        strict_report = strict.analyse(text)
        lenient_report = lenient.analyse(text)

        assert len(strict_report.complex_sentences) >= len(lenient_report.complex_sentences)

    def test_extra_terms(self):
        analyzer = ClearHealthAnalyzer(
            extra_terms={"prn": {"plain": "as needed", "category": "abbreviation"}}
        )
        report = analyzer.analyse("Take medication prn for pain.")
        terms = [m.term.lower() for m in report.jargon.matches]
        assert "prn" in terms
