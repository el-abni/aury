from __future__ import annotations

MARKER = "💜"


def polish_public_text(text: str) -> str:
    normalized = text.strip()
    if not normalized:
        return normalized
    first = normalized[:1]
    if first.isalpha():
        return first.upper() + normalized[1:]
    return normalized


def format_public_message(icon: str, text: str) -> str:
    return f"{icon} | {MARKER} {polish_public_text(text)}"


def success(text: str) -> str:
    return format_public_message("✅", text)


def failure(text: str) -> str:
    return format_public_message("❌", text)


def info(text: str) -> str:
    return format_public_message("ℹ️", text)


def blocked(text: str) -> str:
    normalized = text.strip()
    if normalized.lower().startswith("bloqueado"):
        return failure(normalized)
    return failure(f"Bloqueado {normalized}")
