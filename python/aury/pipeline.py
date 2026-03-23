from __future__ import annotations

from collections.abc import Sequence

from .contracts import InputPhrase, PreparedAction
from .normalize import normalize_token, preprocess_text, strip_accents
from .sensitive_tokens import protect_sensitive_tokens, restore_sensitive_tokens

INTENTS = {'ajuda','reload','dev','atualizar','otimizar','status','procurar','instalar','remover','criar','copiar','mover','renomear','extrair','compactar','ping','ver','internet','velocidade'}
COMMAND_ALIASES = {
    'crie': 'criar',
    'copie': 'copiar',
    'copia': 'copiar',
    'compacte': 'compactar',
    'procure': 'procurar',
    'renomeie': 'renomear',
    'renomeia': 'renomear',
}


def _original_tokens_from_value(value: Sequence[str] | str) -> list[str]:
    if isinstance(value, str):
        text = value
    else:
        text = ' '.join(value)
    prepared_text = preprocess_text(text)
    return [part for part in prepared_text.split() if part.strip()]


def build_input_phrase(value: Sequence[str] | str) -> InputPhrase:
    original_tokens = _original_tokens_from_value(value)
    protected_tokens, mapping = protect_sensitive_tokens(original_tokens)
    placeholders = {item.placeholder for item in mapping}
    corrected_tokens = restore_sensitive_tokens(
        [token if token in placeholders else normalize_token(token) for token in protected_tokens],
        mapping,
    )
    normalized_display_tokens = list(corrected_tokens)
    normalized_tokens = [strip_accents(token).lower() for token in normalized_display_tokens]
    return InputPhrase(
        original_tokens=original_tokens,
        protected_tokens=mapping,
        corrected_tokens=corrected_tokens,
        normalized_tokens=normalized_tokens,
        normalized_display_tokens=normalized_display_tokens,
    )


def is_command_token(token: str) -> bool:
    normalized = normalize_token(token)
    return normalized in INTENTS or COMMAND_ALIASES.get(normalized, normalized) in INTENTS


def split_actions(tokens: list[str]) -> list[list[str]]:
    actions: list[list[str]] = []
    current: list[str] = []
    for index, token in enumerate(tokens):
        normalized = normalize_token(token)
        if current and normalized in {'depois'}:
            if current and normalize_token(current[-1]) == 'e':
                current.pop()
            actions.append(current)
            current = []
            continue
        if current and normalized == 'e':
            next_token = tokens[index + 1] if index + 1 < len(tokens) else ''
            if next_token and is_command_token(next_token):
                actions.append(current)
                current = []
                continue
        current.append(token)
    if current:
        actions.append(current)
    return actions or [tokens]


def prepare_action(index: int, tokens: list[str]) -> PreparedAction:
    phrase = build_input_phrase(tokens)
    return PreparedAction(
        index=index,
        original_tokens=phrase.original_tokens,
        corrected_tokens=phrase.corrected_tokens,
        normalized_tokens=phrase.normalized_tokens,
        normalized_display_tokens=phrase.normalized_display_tokens,
        original_action=' '.join(phrase.original_tokens).strip(),
    )


def prepare_actions(tokens: list[str]) -> tuple[InputPhrase, list[PreparedAction]]:
    phrase = build_input_phrase(tokens)
    actions = [prepare_action(i + 1, action) for i, action in enumerate(split_actions(phrase.original_tokens))]
    return phrase, actions


def prepare_text(text: str) -> tuple[InputPhrase, list[PreparedAction]]:
    phrase = build_input_phrase(text)
    actions = [prepare_action(i + 1, action) for i, action in enumerate(split_actions(phrase.original_tokens))]
    return phrase, actions
