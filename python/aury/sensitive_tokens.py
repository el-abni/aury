from __future__ import annotations

import re

from .contracts import ProtectedToken

_PATHLIKE_RE = re.compile(r'(~|/|\\|\.[A-Za-z0-9_-]+$)')
_HOST_RE = re.compile(r'^[A-Za-z0-9._-]+\.[A-Za-z]{2,}$')
_ARCHIVE_RE = re.compile(r'\.(zip|7z|tar|tgz|gz|bz2|xz)$', re.IGNORECASE)


def token_sensitive_type(token: str) -> str | None:
    if not token:
        return None
    stripped = token.strip()
    if _ARCHIVE_RE.search(stripped):
        return 'archive'
    if _HOST_RE.match(stripped):
        return 'host'
    if _PATHLIKE_RE.search(stripped):
        return 'path'
    return None


def protect_sensitive_tokens(tokens: list[str]) -> tuple[list[str], list[ProtectedToken]]:
    protected: list[str] = []
    mapping: list[ProtectedToken] = []
    for token in tokens:
        token_type = token_sensitive_type(token)
        if token_type is None:
            protected.append(token)
            continue
        placeholder = f'__AURY_{token_type.upper()}_{len(mapping)+1}__'
        mapping.append(ProtectedToken(placeholder=placeholder, value=token, token_type=token_type))
        protected.append(placeholder)
    return protected, mapping


def restore_sensitive_tokens(tokens: list[str], protected_tokens: list[ProtectedToken]) -> list[str]:
    restored = list(tokens)
    for item in protected_tokens:
        restored = [item.value if token == item.placeholder else token for token in restored]
    return restored
