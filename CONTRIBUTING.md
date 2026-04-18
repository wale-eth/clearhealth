# Contributing to ClearHealth

Thank you for your interest in contributing to ClearHealth! This project aims to make health and education documents more accessible, and every contribution helps.

## Getting started

### 1. Fork and clone

```bash
git clone https://github.com/wale-eth/clearhealth.git
cd clearhealth
```

### 2. Set up your development environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### 3. Run the tests

```bash
pytest
```

All tests should pass before you start making changes.

## How to contribute

### Reporting bugs

Open an issue using the **Bug Report** template. Include:
- What you expected to happen
- What actually happened
- A minimal code example that reproduces the issue
- Your Python version and OS

### Suggesting features

Open an issue using the **Feature Request** template. Describe:
- The problem you're trying to solve
- Your proposed solution
- Any alternatives you've considered

### Adding medical terms to the vocabulary

One of the easiest ways to contribute is expanding the medical jargon vocabulary in `src/clearhealth/vocabulary/medical_terms.json`.

Each entry needs:
- **Key**: The medical term in lowercase
- **plain**: A plain-English explanation (written for a general adult audience)
- **category**: One of: `anatomy`, `condition`, `procedure`, `medication`, `lab_value`, `general_medical`, `abbreviation`

```json
"term_here": {
    "plain": "simple explanation here",
    "category": "condition"
}
```

**Guidelines for plain-English alternatives:**
- Write as if explaining to a friend who isn't in healthcare
- Keep it under 15 words
- Avoid using other medical jargon in the explanation
- Use British English spelling (this is a UK-focused project)

### Submitting code changes

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and add tests. We aim for 80%+ test coverage.

3. Run the full test suite:
   ```bash
   pytest --cov=clearhealth
   ```

4. Run linting:
   ```bash
   ruff check src/ tests/
   ```

5. Commit with a clear message:
   ```bash
   git commit -m "Add support for dental terminology"
   ```

6. Push and open a pull request against `main`.

## Code style

- **Python**: Follow PEP 8. We use [Ruff](https://docs.astral.sh/ruff/) for linting.
- **Line length**: 99 characters max.
- **Type hints**: Use them for all public functions and methods.
- **Docstrings**: Google style. All public classes and functions need docstrings.
- **Tests**: Use pytest. One test file per module, mirroring the `src/` structure.

## Pull request checklist

- [ ] Tests pass (`pytest`)
- [ ] Linting passes (`ruff check src/ tests/`)
- [ ] New code has tests
- [ ] Public functions have docstrings
- [ ] PR description explains what changed and why

## Code of conduct

Be kind, be constructive, be inclusive. This project exists to make health information accessible to everyone -- that spirit extends to how we work together.

## Questions?

Open a discussion or reach out. No question is too small.
