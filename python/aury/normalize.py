from __future__ import annotations

import re
import unicodedata

_CORRECTIONS = {
    "vc": "você",
    "vcs": "vocês",
    "ce": "você",
    "cê": "você",
    "q": "que",
    "ta": "está",
    "tá": "está",
    "tb": "também",
    "tbm": "também",
    "mosta": "mostrar",
    "mosra": "mostrar",
    "ve": "ver",
    "vee": "ver",
    "instalaa": "instalar",
}

_VOCATIVES = {"aury", "ay"}


def strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")


def normalize_token(token: str) -> str:
    lowered = token.strip().strip(",.;:!?").lower()
    lowered = _CORRECTIONS.get(lowered, lowered)
    return lowered


def preprocess_text(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text.replace("\n", " ")).strip()
    cleaned = re.sub(r"^[Aa]ury\s*,\s*", "", cleaned)
    cleaned = re.sub(r"^[Aa]y\s*,\s*", "", cleaned)
    return cleaned.strip()


def tokenize(text: str) -> list[str]:
    text = preprocess_text(text)
    return [normalize_token(part) for part in text.split() if part.strip()]


def normalized_text(text: str) -> str:
    return " ".join(tokenize(text))


def first_token(text: str) -> str:
    tokens = tokenize(text)
    return tokens[0] if tokens else ""
