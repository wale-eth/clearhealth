"""Medical jargon detection and plain-English suggestion engine.

Detects medical terminology in text and suggests accessible alternatives.
Uses a curated vocabulary of medical terms mapped to plain-English
explanations, with optional spaCy NER integration for broader coverage.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional

from clearhealth.vocabulary import load_medical_terms


@dataclass(frozen=True)
class JargonMatch:
    """A single detected jargon term with its plain-English alternative."""

    term: str
    plain: str
    category: str
    start: int
    end: int
    sentence_index: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "term": self.term,
            "plain": self.plain,
            "category": self.category,
            "start": self.start,
            "end": self.end,
            "sentence_index": self.sentence_index,
        }


@dataclass(frozen=True)
class JargonSummary:
    """Aggregated jargon detection results for a document."""

    matches: list[JargonMatch]
    total_jargon_count: int
    unique_terms: int
    jargon_density: float  # jargon terms per 100 words
    categories: dict[str, int]  # count by category

    def to_dict(self) -> dict:
        return {
            "total_jargon_count": self.total_jargon_count,
            "unique_terms": self.unique_terms,
            "jargon_density": round(self.jargon_density, 2),
            "categories": self.categories,
            "matches": [m.to_dict() for m in self.matches],
        }


class JargonDetector:
    """Detect medical jargon and suggest plain-English alternatives.

    The detector uses a curated vocabulary of medical terms. Multi-word
    terms (e.g., "myocardial infarction") are matched before single-word
    terms to avoid partial matches.

    Usage:
        >>> detector = JargonDetector()
        >>> result = detector.detect("The patient has acute myocardial infarction.")
        >>> for match in result.matches:
        ...     print(f"{match.term} -> {match.plain}")
        acute -> sudden, short-term
        myocardial infarction -> heart attack

    You can also supply additional custom terms:
        >>> detector = JargonDetector(extra_terms={"stat": {"plain": "immediately", "category": "abbreviation"}})
    """

    def __init__(
        self,
        extra_terms: Optional[Dict[str, dict]] = None,
        use_spacy: bool = False,
    ):
        self._terms = dict(load_medical_terms())
        if extra_terms:
            self._terms.update(extra_terms)
        self._use_spacy = use_spacy

        # Separate multi-word and single-word terms for matching priority
        self._multi_word: Dict[str, dict] = {}
        self._single_word: Dict[str, dict] = {}
        for term, info in self._terms.items():
            if " " in term:
                self._multi_word[term] = info
            else:
                self._single_word[term] = info

        # Pre-compile multi-word patterns (longest first for greedy matching)
        sorted_multi = sorted(self._multi_word.keys(), key=len, reverse=True)
        self._multi_patterns: list[tuple[re.Pattern, str]] = [
            (re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE), term)
            for term in sorted_multi
        ]

        # Pre-compile single-word pattern
        if self._single_word:
            escaped = "|".join(re.escape(t) for t in self._single_word)
            self._single_pattern = re.compile(
                rf"\b({escaped})\b", re.IGNORECASE
            )
        else:
            self._single_pattern = None

    @property
    def vocabulary_size(self) -> int:
        """Number of terms in the loaded vocabulary."""
        return len(self._terms)

    def detect(self, text: str, word_count: Optional[int] = None) -> JargonSummary:
        """Detect medical jargon in the given text.

        Args:
            text: The text to analyse.
            word_count: Pre-computed word count (for efficiency if already known).

        Returns:
            A JargonSummary with all matches and aggregate statistics.
        """
        if word_count is None:
            word_count = len(re.findall(r"[a-zA-Z'-]+", text))

        matches: list[JargonMatch] = []
        # Track matched character ranges to avoid overlaps
        matched_ranges: list[tuple[int, int]] = []

        # Phase 1: multi-word terms (higher priority)
        for pattern, term_key in self._multi_patterns:
            for m in pattern.finditer(text):
                start, end = m.start(), m.end()
                if not self._overlaps(start, end, matched_ranges):
                    info = self._multi_word[term_key]
                    matches.append(JargonMatch(
                        term=m.group(),
                        plain=info["plain"],
                        category=info["category"],
                        start=start,
                        end=end,
                    ))
                    matched_ranges.append((start, end))

        # Phase 2: single-word terms
        if self._single_pattern:
            for m in self._single_pattern.finditer(text):
                start, end = m.start(), m.end()
                if not self._overlaps(start, end, matched_ranges):
                    term_lower = m.group().lower()
                    if term_lower in self._single_word:
                        info = self._single_word[term_lower]
                        matches.append(JargonMatch(
                            term=m.group(),
                            plain=info["plain"],
                            category=info["category"],
                            start=start,
                            end=end,
                        ))
                        matched_ranges.append((start, end))

        # Sort by position in text
        matches.sort(key=lambda m: m.start)

        # Aggregate stats
        unique_terms = len({m.term.lower() for m in matches})
        categories: dict[str, int] = {}
        for m in matches:
            categories[m.category] = categories.get(m.category, 0) + 1

        density = (len(matches) / max(word_count, 1)) * 100

        return JargonSummary(
            matches=matches,
            total_jargon_count=len(matches),
            unique_terms=unique_terms,
            jargon_density=density,
            categories=categories,
        )

    @staticmethod
    def _overlaps(start: int, end: int, ranges: list[tuple[int, int]]) -> bool:
        """Check if a character range overlaps with any existing range."""
        for rs, re_ in ranges:
            if start < re_ and end > rs:
                return True
        return False

    def suggest(self, term: str) -> Optional[str]:
        """Look up the plain-English alternative for a single term.

        Args:
            term: The medical term to look up (case-insensitive).

        Returns:
            The plain-English suggestion, or None if not found.
        """
        info = self._terms.get(term.lower())
        return info["plain"] if info else None
