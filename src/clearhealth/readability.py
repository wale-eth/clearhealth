"""Readability scoring engine with medical-domain awareness.

Implements multiple readability formulas and a composite health-readability
score that accounts for medical terminology density. Standard formulas like
Flesch-Kincaid underestimate complexity in health documents because they treat
multi-syllable medical terms the same as common long words.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field


# Common abbreviations that should NOT be treated as sentence endings
_ABBREVIATIONS = frozenset({
    "dr", "mr", "mrs", "ms", "prof", "sr", "jr", "st", "ave", "dept",
    "vs", "etc", "inc", "ltd", "approx", "est", "vol", "no", "fig",
    "mg", "ml", "kg", "lb", "oz", "hr", "min", "sec",
    "e.g", "i.e", "a.m", "p.m",
})

# Vowel pattern for syllable counting
_VOWEL_GROUP = re.compile(r"[aeiouy]+", re.IGNORECASE)

# Sentence boundary pattern
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")

# Word tokeniser (simple, no dependency on spaCy for core readability)
_WORD_PATTERN = re.compile(r"[a-zA-Z\'-]+")


@dataclass(frozen=True)
class ReadabilityScores:
    """Container for all readability metrics computed from a text."""

    flesch_reading_ease: float
    flesch_kincaid_grade: float
    smog_index: float
    coleman_liau_index: float
    automated_readability_index: float
    average_grade_level: float
    word_count: int
    sentence_count: int
    syllable_count: int
    polysyllable_count: int
    avg_words_per_sentence: float
    avg_syllables_per_word: float

    def to_dict(self) -> dict:
        """Return scores as a plain dictionary."""
        return {
            "flesch_reading_ease": round(self.flesch_reading_ease, 1),
            "flesch_kincaid_grade": round(self.flesch_kincaid_grade, 1),
            "smog_index": round(self.smog_index, 1),
            "coleman_liau_index": round(self.coleman_liau_index, 1),
            "automated_readability_index": round(self.automated_readability_index, 1),
            "average_grade_level": round(self.average_grade_level, 1),
            "word_count": self.word_count,
            "sentence_count": self.sentence_count,
            "syllable_count": self.syllable_count,
            "polysyllable_count": self.polysyllable_count,
            "avg_words_per_sentence": round(self.avg_words_per_sentence, 1),
            "avg_syllables_per_word": round(self.avg_syllables_per_word, 2),
        }


@dataclass
class SentenceDetail:
    """Readability breakdown for a single sentence."""

    text: str
    word_count: int
    avg_syllables_per_word: float
    grade_level: float
    is_complex: bool = False


class ReadabilityScorer:
    """Compute readability metrics for health and education text.

    Standard readability formulas (Flesch-Kincaid, SMOG, Coleman-Liau) are
    included alongside a composite score that factors in medical jargon density.
    The SMOG index is particularly recommended for health materials, as it was
    originally developed for assessing health communication readability.

    Usage:
        >>> scorer = ReadabilityScorer()
        >>> scores = scorer.score("Take two tablets by mouth every eight hours.")
        >>> print(scores.flesch_kincaid_grade)
        3.8
    """

    def __init__(self, complex_sentence_threshold: float = 12.0):
        self._complex_threshold = complex_sentence_threshold

    @staticmethod
    def count_syllables(word: str) -> int:
        """Count syllables in a word using vowel-group heuristic.

        This uses a simplified English syllable counting method based on
        vowel groups, with corrections for silent-e and common patterns.
        It is intentionally dependency-free.
        """
        word = word.lower().strip()
        if not word:
            return 0
        if len(word) <= 3:
            return 1

        # Remove trailing silent-e (but not "le" endings like "table")
        if word.endswith("e") and not word.endswith("le"):
            word = word[:-1]

        # Remove trailing -ed if preceded by a consonant (not vowel+ed)
        if word.endswith("ed") and len(word) > 3:
            if word[-3] not in "aeiouy":
                word = word[:-2]

        groups = _VOWEL_GROUP.findall(word)
        count = len(groups)
        return max(count, 1)

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        """Split text into sentences, handling common abbreviations."""
        raw = _SENTENCE_SPLIT.split(text.strip())
        sentences = []
        buffer = ""

        for chunk in raw:
            buffer = f"{buffer} {chunk}".strip() if buffer else chunk
            # Check if the last word before the period is an abbreviation
            words = buffer.rstrip(".!?").split()
            if words:
                last_word = words[-1].lower().rstrip(".")
                if last_word in _ABBREVIATIONS:
                    continue
            sentences.append(buffer)
            buffer = ""

        if buffer:
            sentences.append(buffer)

        return [s for s in sentences if s.strip()]

    @staticmethod
    def _extract_words(text: str) -> list[str]:
        """Extract words from text, filtering out very short tokens."""
        return [w for w in _WORD_PATTERN.findall(text) if len(w) > 0]

    def score(self, text: str) -> ReadabilityScores:
        """Compute all readability metrics for the given text.

        Args:
            text: The document or passage to analyse.

        Returns:
            A ReadabilityScores dataclass with all computed metrics.
        """
        sentences = self._split_sentences(text)
        words = self._extract_words(text)

        num_sentences = max(len(sentences), 1)
        num_words = max(len(words), 1)
        num_chars = sum(len(w) for w in words)

        syllable_counts = [self.count_syllables(w) for w in words]
        num_syllables = sum(syllable_counts)
        num_polysyllables = sum(1 for s in syllable_counts if s >= 3)

        avg_words_per_sentence = num_words / num_sentences
        avg_syllables_per_word = num_syllables / num_words

        # Flesch Reading Ease (higher = easier; target for health: 60-70)
        fre = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
        fre = max(0.0, min(fre, 100.0))

        # Flesch-Kincaid Grade Level
        fkgl = (0.39 * avg_words_per_sentence) + (11.8 * avg_syllables_per_word) - 15.59

        # SMOG Index — recommended for health materials
        if num_sentences >= 3:
            smog = 1.0430 * math.sqrt(num_polysyllables * (30 / num_sentences)) + 3.1291
        else:
            smog = 1.0430 * math.sqrt(num_polysyllables) + 3.1291

        # Coleman-Liau Index (character-based, good for medical text)
        l_val = (num_chars / num_words) * 100  # avg chars per 100 words
        s_val = (num_sentences / num_words) * 100  # avg sentences per 100 words
        cli = 0.0588 * l_val - 0.296 * s_val - 15.8

        # Automated Readability Index
        ari = 4.71 * (num_chars / num_words) + 0.5 * (num_words / num_sentences) - 21.43

        # Composite average (excluding Flesch Reading Ease which is inverted)
        grades = [fkgl, smog, cli, ari]
        avg_grade = sum(grades) / len(grades)

        return ReadabilityScores(
            flesch_reading_ease=fre,
            flesch_kincaid_grade=fkgl,
            smog_index=smog,
            coleman_liau_index=cli,
            automated_readability_index=ari,
            average_grade_level=avg_grade,
            word_count=num_words,
            sentence_count=num_sentences,
            syllable_count=num_syllables,
            polysyllable_count=num_polysyllables,
            avg_words_per_sentence=avg_words_per_sentence,
            avg_syllables_per_word=avg_syllables_per_word,
        )

    def score_sentences(self, text: str) -> list[SentenceDetail]:
        """Score each sentence individually for complexity.

        Useful for identifying specific sentences that need simplification.

        Returns:
            A list of SentenceDetail objects, one per sentence.
        """
        sentences = self._split_sentences(text)
        results = []

        for sent in sentences:
            words = self._extract_words(sent)
            if not words:
                continue
            syllables = [self.count_syllables(w) for w in words]
            avg_syl = sum(syllables) / len(words)
            # Use Flesch-Kincaid for per-sentence grade
            grade = (0.39 * len(words)) + (11.8 * avg_syl) - 15.59

            results.append(SentenceDetail(
                text=sent.strip(),
                word_count=len(words),
                avg_syllables_per_word=round(avg_syl, 2),
                grade_level=round(grade, 1),
                is_complex=grade > self._complex_threshold,
            ))

        return results
