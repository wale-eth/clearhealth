"""Accessibility report generation.

Combines readability scores, jargon detection, and sentence-level analysis
into a single accessibility report with an overall grade.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from clearhealth.readability import ReadabilityScores, SentenceDetail
from clearhealth.jargon import JargonSummary


# Grade thresholds based on average grade level + jargon density
# Target for health materials: Grade 6-8 reading level (CDC recommendation)
_GRADE_THRESHOLDS = {
    "A": {"max_grade": 6.0, "max_jargon_density": 1.0},
    "B": {"max_grade": 8.0, "max_jargon_density": 3.0},
    "C": {"max_grade": 10.0, "max_jargon_density": 5.0},
    "D": {"max_grade": 13.0, "max_jargon_density": 8.0},
}
# Anything above D thresholds = F


@dataclass(frozen=True)
class AccessibilityReport:
    """Complete accessibility analysis of a health document.

    Attributes:
        grade: Overall accessibility grade from A (most accessible) to F.
        grade_explanation: Human-readable explanation of what the grade means.
        readability: Detailed readability metrics.
        jargon: Jargon detection results with suggestions.
        complex_sentences: Sentences flagged as difficult to read.
        recommendations: Actionable suggestions for improvement.
        text_length: Character count of the analysed text.
    """

    grade: str
    grade_explanation: str
    readability: ReadabilityScores
    jargon: JargonSummary
    complex_sentences: list[SentenceDetail]
    recommendations: list[str]
    text_length: int

    def to_dict(self) -> dict:
        """Serialise the full report to a dictionary."""
        return {
            "grade": self.grade,
            "grade_explanation": self.grade_explanation,
            "readability": self.readability.to_dict(),
            "jargon": self.jargon.to_dict(),
            "complex_sentences": [
                {
                    "text": s.text,
                    "word_count": s.word_count,
                    "grade_level": s.grade_level,
                }
                for s in self.complex_sentences
            ],
            "recommendations": self.recommendations,
            "text_length": self.text_length,
        }

    def summary(self) -> str:
        """Return a concise human-readable summary of the report."""
        lines = [
            f"Accessibility Grade: {self.grade}",
            f"  {self.grade_explanation}",
            "",
            f"Reading Level: Grade {self.readability.average_grade_level:.1f}",
            f"  Flesch Reading Ease: {self.readability.flesch_reading_ease:.1f}/100",
            f"  SMOG Index: {self.readability.smog_index:.1f}",
            "",
            f"Medical Jargon: {self.jargon.total_jargon_count} terms found "
            f"({self.jargon.unique_terms} unique)",
            f"  Jargon Density: {self.jargon.jargon_density:.1f} per 100 words",
            "",
            f"Complex Sentences: {len(self.complex_sentences)} of "
            f"{self.readability.sentence_count}",
            "",
            f"Word Count: {self.readability.word_count}",
            f"Sentence Count: {self.readability.sentence_count}",
        ]

        if self.jargon.matches:
            lines.append("")
            lines.append("Jargon Found (with suggestions):")
            seen = set()
            for match in self.jargon.matches:
                key = match.term.lower()
                if key not in seen:
                    lines.append(f'  "{match.term}" -> {match.plain}')
                    seen.add(key)

        if self.recommendations:
            lines.append("")
            lines.append("Recommendations:")
            for i, rec in enumerate(self.recommendations, 1):
                lines.append(f"  {i}. {rec}")

        return "\n".join(lines)


def compute_grade(
    readability: ReadabilityScores,
    jargon: JargonSummary,
) -> tuple[str, str]:
    """Compute the overall accessibility grade.

    The grade is determined by the combination of reading level and
    jargon density. A document can be brought down by either factor.

    Returns:
        A tuple of (grade_letter, explanation).
    """
    avg_grade = readability.average_grade_level
    density = jargon.jargon_density

    for letter, thresholds in _GRADE_THRESHOLDS.items():
        if avg_grade <= thresholds["max_grade"] and density <= thresholds["max_jargon_density"]:
            break
    else:
        letter = "F"

    explanations = {
        "A": (
            "Excellent accessibility. This text is written at a level most adults "
            "can easily understand, with minimal medical jargon."
        ),
        "B": (
            "Good accessibility. The text is readable for most adults but contains "
            "some medical terminology that could be simplified."
        ),
        "C": (
            "Fair accessibility. The reading level and jargon usage may be "
            "challenging for adults with lower health literacy."
        ),
        "D": (
            "Poor accessibility. The text is written at a level that many adults "
            "would struggle with. Significant simplification is recommended."
        ),
        "F": (
            "Very poor accessibility. The text is highly technical and would be "
            "inaccessible to most general readers. Major rewriting is needed."
        ),
    }

    return letter, explanations[letter]


def generate_recommendations(
    readability: ReadabilityScores,
    jargon: JargonSummary,
    complex_sentences: list[SentenceDetail],
) -> list[str]:
    """Generate actionable recommendations based on the analysis.

    Returns:
        A list of plain-English recommendations for improving accessibility.
    """
    recs: list[str] = []

    # Reading level recommendations
    if readability.average_grade_level > 8.0:
        recs.append(
            f"Reduce the reading level from grade {readability.average_grade_level:.1f} "
            f"to grade 6-8. The CDC recommends health materials be written at "
            f"a 6th-8th grade reading level."
        )

    if readability.avg_words_per_sentence > 20:
        recs.append(
            f"Shorten sentences. The average is {readability.avg_words_per_sentence:.0f} "
            f"words per sentence; aim for 15-20 words."
        )

    if readability.avg_syllables_per_word > 1.6:
        recs.append(
            "Use shorter, simpler words where possible. The average word "
            "complexity is high for general-audience health materials."
        )

    # Jargon recommendations
    if jargon.total_jargon_count > 0:
        top_categories = sorted(
            jargon.categories.items(), key=lambda x: x[1], reverse=True
        )
        cat_str = ", ".join(f"{cat} ({n})" for cat, n in top_categories[:3])
        recs.append(
            f"Replace {jargon.total_jargon_count} medical jargon terms with "
            f"plain-English alternatives. Most common categories: {cat_str}."
        )

    if jargon.jargon_density > 5.0:
        recs.append(
            f"Jargon density is {jargon.jargon_density:.1f} terms per 100 words, "
            f"which is very high. Consider rewriting sections with the highest "
            f"concentration of medical terminology."
        )

    # Complex sentence recommendations
    if complex_sentences:
        recs.append(
            f"{len(complex_sentences)} sentence(s) are flagged as complex "
            f"(above grade 12 reading level). Consider breaking these into "
            f"shorter sentences or using simpler vocabulary."
        )

    if not recs:
        recs.append(
            "This text meets accessibility guidelines. No changes recommended."
        )

    return recs
