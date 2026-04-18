# I Built an Open-Source Tool to Make Health Documents More Accessible. Here Is Why

*Draft for Towards Data Science / Medium*

---

A few months ago, I was helping a family member understand a hospital discharge letter. It read like this.

> "The patient was diagnosed with acute myocardial infarction secondary to atherosclerotic cardiovascular disease. Percutaneous coronary intervention was performed with concurrent anticoagulant therapy."

My family member, an intelligent and capable adult, had no idea what had happened to them. They had a heart attack. A stent was placed. They were on blood thinners. But the letter did not say any of that.

This experience stuck with me. As a data scientist who works with text every day, I kept thinking about it. This is a solvable problem. We have the tools. Why has nobody built this?

## The scale of the problem

It turns out this is not a niche issue. According to NHS data, **43% of working-age adults in England** cannot understand health information written at a typical reading level. That is not because they lack intelligence. It is because health materials are written for clinicians, not patients.

The CDC recommends health materials be written at a **6th to 8th grade reading level**. Most patient leaflets, discharge summaries, and consent forms are written at grade 12 or above. That gap has real consequences. Missed medications. Skipped follow-ups. Worse health outcomes.

There are readability tools out there like Flesch-Kincaid, SMOG, and the Hemingway Editor. But none of them understand medical language. They will tell you a sentence is "hard to read" but they will not tell you *why* or *what to change*. They treat "cardiovascular" the same as any other long word.

## So I built ClearHealth

**ClearHealth** is a Python library that analyses health and education documents for accessibility. It does three things.

1. **Scores readability** with medical-domain awareness, going beyond basic Flesch-Kincaid to account for the unique complexity of health vocabulary.
2. **Detects medical jargon**, flagging terms like "hypertension," "myocardial infarction," and "anticoagulant" that most readers will not understand.
3. **Suggests plain-English alternatives** so writers know exactly how to fix the problem, not just that a problem exists.

Here is what it looks like in practice.

```python
import clearhealth

report = clearhealth.analyse("""
    The patient presented with acute myocardial infarction secondary to
    atherosclerotic cardiovascular disease. Percutaneous coronary intervention
    was performed with concurrent anticoagulant therapy.
""")

print(report.grade)  # 'F'

for match in report.jargon.matches:
    print(f'  "{match.term}" → {match.plain}')
# "acute" → sudden, short-term
# "myocardial infarction" → heart attack
# "cardiovascular" → related to the heart and blood vessels
# "percutaneous" → through the skin
# "anticoagulant" → blood thinner
```

The output includes an **accessibility grade (A to F)**, a full readability breakdown, a list of every jargon term with its suggestion, and actionable recommendations for improvement.

## How it works under the hood

### Readability scoring

ClearHealth computes four standard readability indices. Flesch-Kincaid, SMOG, Coleman-Liau, and the Automated Readability Index. It then averages them into a composite grade level. I chose SMOG as the primary reference because it was originally developed for assessing health communication materials.

The scoring engine is dependency-free. It uses a vowel-group heuristic for syllable counting with corrections for silent-e and common English patterns. It is not perfect (English is messy), but it is fast and does not require loading a spaCy model just to count syllables.

### Jargon detection

The jargon detector uses a curated vocabulary of 140+ medical terms mapped to plain-English alternatives. Terms are categorised by type, covering anatomy, conditions, procedures, medications, lab values, and general medical language.

Multi-word terms like "myocardial infarction" or "deep vein thrombosis" are matched before single-word terms to avoid partial matches. The detector uses pre-compiled regex patterns sorted by length for greedy matching, with overlap prevention.

The vocabulary is stored as a JSON file. That makes it easy for anyone to contribute new terms without needing to change any code.

### Accessibility grading

The overall A to F grade is determined by two factors. Reading level and jargon density. A document can be dragged down by either one. A text written in simple sentences but packed with unexplained jargon will still get a poor grade, and vice versa.

The thresholds are based on the CDC's Clear Communication Index guidelines, adapted for the UK context.

## What I learned building this

**Medical vocabulary is harder than it looks.** Writing "plain English" alternatives for medical terms is an exercise in humility. How do you explain "percutaneous" in under ten words? ("Through the skin.") What about "idiopathic"? ("Of unknown cause.") Every term requires you to think about what a reader actually needs to know.

**Existing readability tools have a blind spot.** Flesch-Kincaid will tell you that "Take your medicine" and "Administer the pharmaceutical agent" are both relatively simple sentences because they are both short with moderate syllable counts. But one is accessible and the other is not. Domain-aware analysis matters.

**Syllable counting in English is surprisingly hard.** There is no reliable rule-based method that handles all cases. "Area" has three syllables. "Idea" has three. "Queue" has one. I settled on a vowel-group heuristic with specific corrections, accepting plus or minus one syllable tolerance on edge cases. For readability scoring, this is accurate enough.

## Who is this for?

- **Health communicators** writing patient leaflets, discharge letters, or consent forms
- **NHS digital teams** building patient-facing content
- **EdTech developers** working with health education content
- **Researchers** studying health literacy
- **Any developer** who processes health-related text and wants to flag accessibility issues

## What is next

This is v0.1.0. The vocabulary is intentionally focused (140+ terms covering the most common medical jargon) rather than trying to be exhaustive. Here is what is planned.

- **spaCy pipeline component** so you can drop ClearHealth into any existing spaCy workflow
- **NHS-specific vocabulary module** with terms and abbreviations specific to UK healthcare
- **Multi-language support** because health literacy challenges are amplified for non-native English speakers
- **LLM-powered rewriting suggestions** as an optional feature for users with API access
- **Streamlit demo** giving non-technical users a web interface

## Try it

```bash
pip install clearhealth
```

Or clone the repo.

```bash
git clone https://github.com/wale-eth/clearhealth.git
cd clearhealth
pip install -e ".[dev]"
pytest  # everything should pass
```

The vocabulary is in `src/clearhealth/vocabulary/medical_terms.json`. If you know a medical term that is missing a plain-English alternative, PRs are welcome.

**GitHub** [github.com/wale-eth/clearhealth](https://github.com/wale-eth/clearhealth)

---

*I am a data scientist working with NLP in the UK. If you work in health communication or health literacy, I would love to hear whether this is useful and what is missing. The best tools come from the people who need them.*
