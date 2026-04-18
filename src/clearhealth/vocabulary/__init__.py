"""Built-in vocabulary data for ClearHealth."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

_VOCAB_DIR = Path(__file__).parent
_CACHE: Dict[str, dict] = {}


def load_medical_terms() -> dict:
    """Load the medical jargon vocabulary.

    Returns:
        A dict mapping lowercase medical terms to
        ``{"plain": str, "category": str}``.
    """
    if "medical" not in _CACHE:
        path = _VOCAB_DIR / "medical_terms.json"
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        _CACHE["medical"] = data["terms"]
    return _CACHE["medical"]
