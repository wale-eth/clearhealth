"""ClearHealth — Analyse health and education documents for accessibility.

ClearHealth helps writers, healthcare professionals, and developers make
health-related text more accessible. It detects medical jargon, scores
readability with domain awareness, and suggests plain-English alternatives.

Quick start:
    >>> import clearhealth
    >>> report = clearhealth.analyse("The patient presented with acute myocardial infarction.")
    >>> print(report.grade)
    'D'
    >>> print(report.jargon_found)
    [JargonMatch(term='acute myocardial infarction', suggestion='heart attack', ...)]
"""

from clearhealth.analyzer import analyse, analyze, ClearHealthAnalyzer
from clearhealth.readability import ReadabilityScorer
from clearhealth.jargon import JargonDetector
from clearhealth.report import AccessibilityReport

__version__ = "0.1.0"
__all__ = [
    "analyse",
    "analyze",
    "ClearHealthAnalyzer",
    "ReadabilityScorer",
    "JargonDetector",
    "AccessibilityReport",
]
