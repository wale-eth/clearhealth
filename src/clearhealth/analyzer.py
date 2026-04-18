"""Main entry point for ClearHealth analysis.

Provides both a functional API (``analyse()``) and a class-based API
(``ClearHealthAnalyzer``) for analysing health documents.
"""

from __future__ import annotations

from typing import Dict, Optional

from clearhealth.readability import ReadabilityScorer
from clearhealth.jargon import JargonDetector
from clearhealth.report import (
    AccessibilityReport,
    compute_grade,
    generate_recommendations,
)


class ClearHealthAnalyzer:
    """Analyse health and education text for accessibility.

    Combines readability scoring, jargon detection, and actionable
    recommendations into a single analysis pipeline.

    Usage:
        >>> analyzer = ClearHealthAnalyzer()
        >>> report = analyzer.analyse("The patient presented with dyspnoea and tachycardia.")
        >>> print(report.grade)
        'D'
        >>> print(report.summary())

    You can customise the jargon vocabulary and complexity thresholds:
        >>> analyzer = ClearHealthAnalyzer(
        ...     extra_terms={"stat": {"plain": "immediately", "category": "abbreviation"}},
        ...     complex_sentence_threshold=10.0,
        ... )
    """

    def __init__(
        self,
        extra_terms: Optional[Dict[str, dict]] = None,
        complex_sentence_threshold: float = 12.0,
        use_spacy: bool = False,
    ):
        self._scorer = ReadabilityScorer(
            complex_sentence_threshold=complex_sentence_threshold,
        )
        self._detector = JargonDetector(
            extra_terms=extra_terms,
            use_spacy=use_spacy,
        )
        self._threshold = complex_sentence_threshold

    @property
    def vocabulary_size(self) -> int:
        """Number of terms in the jargon vocabulary."""
        return self._detector.vocabulary_size

    def analyse(self, text: str) -> AccessibilityReport:
        """Analyse text and return a full accessibility report.

        Args:
            text: The health or education document text to analyse.

        Returns:
            An AccessibilityReport with grade, scores, jargon, and recommendations.
        """
        if not text or not text.strip():
            raise ValueError("Cannot analyse empty text.")

        # Compute readability
        scores = self._scorer.score(text)
        sentences = self._scorer.score_sentences(text)

        # Detect jargon
        jargon = self._detector.detect(text, word_count=scores.word_count)

        # Find complex sentences
        complex_sentences = [s for s in sentences if s.is_complex]

        # Compute overall grade
        grade, explanation = compute_grade(scores, jargon)

        # Generate recommendations
        recommendations = generate_recommendations(scores, jargon, complex_sentences)

        return AccessibilityReport(
            grade=grade,
            grade_explanation=explanation,
            readability=scores,
            jargon=jargon,
            complex_sentences=complex_sentences,
            recommendations=recommendations,
            text_length=len(text),
        )

    # Alias for American English spelling
    analyze = analyse


def analyse(text: str, **kwargs) -> AccessibilityReport:
    """Analyse text for health-literacy accessibility.

    This is a convenience function that creates a default analyzer and
    runs the analysis. For repeated use, prefer creating a
    ``ClearHealthAnalyzer`` instance.

    Args:
        text: The text to analyse.
        **kwargs: Passed to ``ClearHealthAnalyzer.__init__``.

    Returns:
        An AccessibilityReport.

    Example:
        >>> import clearhealth
        >>> report = clearhealth.analyse("Take two tablets by mouth every eight hours.")
        >>> print(report.grade)
        'A'
    """
    analyzer = ClearHealthAnalyzer(**kwargs)
    return analyzer.analyse(text)


# American English alias
analyze = analyse
