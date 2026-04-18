# ClearHealth

**Analyse health and education documents for accessibility.**

[![CI](https://github.com/wale-eth/clearhealth/actions/workflows/ci.yml/badge.svg)](https://github.com/wale-eth/clearhealth/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/clearhealth.svg)](https://pypi.org/project/clearhealth/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

---

43% of working-age adults in England struggle to understand health information written at a typical reading level. ClearHealth helps writers, healthcare professionals, and developers make health-related text more accessible.

It detects medical jargon, scores readability with domain awareness, and suggests plain-English alternatives — all in a single Python library.

## What it does

```python
import clearhealth

report = clearhealth.analyse("""
    The patient presented with acute myocardial infarction secondary to
    atherosclerotic cardiovascular disease. Percutaneous coronary intervention
    was performed with concurrent anticoagulant therapy.
""")

print(report.grade)
# 'F'

print(report.summary())
# Accessibility Grade: F
#   Very poor accessibility. The text is highly technical and would be
#   inaccessible to most general readers. Major rewriting is needed.
#
# Reading Level: Grade 18.2
#   Flesch Reading Ease: 0.0/100
#   SMOG Index: 19.4
#
# Medical Jargon: 7 terms found (7 unique)
#   Jargon Density: 29.17 per 100 words
#
# Jargon Found (with suggestions):
#   "acute" -> sudden, short-term
#   "myocardial infarction" -> heart attack
#   "atherosclerotic" -> ...
#   "cardiovascular" -> related to the heart and blood vessels
#   "percutaneous" -> through the skin
#   "anticoagulant" -> blood thinner
#
# Recommendations:
#   1. Reduce the reading level from grade 18.2 to grade 6-8.
#   2. Replace 7 medical jargon terms with plain-English alternatives.
#   3. 2 sentence(s) are flagged as complex...
```

## Features

- **Readability scoring** — Flesch-Kincaid, SMOG, Coleman-Liau, Automated Readability Index, plus a composite average. SMOG is recommended for health materials.
- **Medical jargon detection** — 140+ medical terms with plain-English alternatives, covering anatomy, conditions, procedures, medications, and lab values.
- **Accessibility grading** — A-F grade based on both reading level and jargon density. Target for health materials: Grade B or above.
- **Sentence-level analysis** — Identifies specific sentences that are too complex, so you know exactly what to fix.
- **Actionable recommendations** — Concrete suggestions based on CDC Clear Communication guidelines.
- **CLI tool** — Analyse documents from the command line.
- **Extensible vocabulary** — Add your own domain-specific terms.
- **No heavy dependencies** — Core analysis works without spaCy. Optional spaCy integration for advanced NER.

## Installation

```bash
pip install clearhealth
```

For development:

```bash
git clone https://github.com/wale-eth/clearhealth.git
cd clearhealth
pip install -e ".[dev]"
```

## Quick start

### Python API

```python
import clearhealth

# Analyse any health-related text
report = clearhealth.analyse("Take two tablets by mouth every eight hours with food.")

print(report.grade)          # 'A'
print(report.readability.flesch_kincaid_grade)  # 3.8
print(report.jargon.total_jargon_count)         # 0
```

### With jargon detection

```python
report = clearhealth.analyse("The patient has hypertension and bilateral oedema.")

for match in report.jargon.matches:
    print(f'  "{match.term}" → {match.plain}')
# "hypertension" → high blood pressure
# "bilateral" → on both sides
# "oedema" → swelling caused by fluid build-up
```

### Sentence-level analysis

```python
report = clearhealth.analyse("""
    Drink plenty of water. The acute exacerbation of chronic obstructive
    pulmonary disease necessitated bronchodilator therapy.
""")

for sentence in report.complex_sentences:
    print(f"  Grade {sentence.grade_level}: {sentence.text[:60]}...")
```

### Custom vocabulary

```python
analyzer = clearhealth.ClearHealthAnalyzer(
    extra_terms={
        "prn": {"plain": "as needed", "category": "abbreviation"},
        "tid": {"plain": "three times a day", "category": "abbreviation"},
        "npo": {"plain": "do not eat or drink", "category": "abbreviation"},
    }
)
report = analyzer.analyse("Give paracetamol prn for pain.")
```

### Command line

```bash
# Analyse a document
clearhealth analyse patient_leaflet.txt

# JSON output for integration
clearhealth analyse discharge_summary.txt --format json

# Pipe from stdin
echo "The patient has hypertension" | clearhealth analyse -
```

### JSON output

```python
import json
report = clearhealth.analyse("Your text here.")
print(json.dumps(report.to_dict(), indent=2))
```

## Grading scale

| Grade | Reading Level | Jargon Density | Meaning |
|-------|--------------|----------------|---------|
| **A** | ≤ Grade 6 | ≤ 1 per 100 words | Accessible to most adults |
| **B** | ≤ Grade 8 | ≤ 3 per 100 words | Good for general health materials |
| **C** | ≤ Grade 10 | ≤ 5 per 100 words | May challenge lower-literacy readers |
| **D** | ≤ Grade 13 | ≤ 8 per 100 words | Difficult for general audiences |
| **F** | > Grade 13 | > 8 per 100 words | Inaccessible to most readers |

The CDC recommends health materials be written at a **6th–8th grade reading level** (Grade A–B).

## Why this matters

Health literacy is a public health issue. When people can't understand their medical information, they miss medications, skip follow-ups, and have worse health outcomes. This isn't about intelligence — it's about whether the text meets the reader where they are.

ClearHealth gives writers and developers a tool to measure and improve the accessibility of health content before it reaches patients.

## Roadmap

- [ ] spaCy pipeline component integration
- [ ] NHS-specific vocabulary module
- [ ] Multi-language support
- [ ] LLM-powered rewriting suggestions
- [ ] Streamlit demo app
- [ ] Benchmark dataset with human-annotated accessibility scores

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Good first issues are labelled [`good first issue`](https://github.com/wale-eth/clearhealth/labels/good%20first%20issue).

## Vocabulary sources

The built-in medical vocabulary draws from publicly available sources:

- [MedlinePlus Health Topics](https://medlineplus.gov/) (U.S. National Library of Medicine)
- [NHS Health A to Z](https://www.nhs.uk/conditions/)
- [CDC Clear Communication Index](https://www.cdc.gov/healthliteracy/developmaterials/guidancestandards.html)

## License

MIT — see [LICENSE](LICENSE).
