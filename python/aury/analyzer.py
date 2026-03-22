from __future__ import annotations

import re

from .contracts import Analysis, InputPhrase, PreparedAction
from .normalize import strip_accents
from .pipeline import prepare_text


def _unsupported(action: PreparedAction) -> Analysis:
    return Analysis(
        original_text=action.original_action,
        normalized_text=action.normalized_action,
        intent="não identificada",
        domain="desconhecido",
        status="NAO_ENQUADRADA",
        reason="não consegui enquadrar esse pedido com segurança no recorte atual.",
        summary="Sem ação prevista.",
        observations=["fallback honesto deve assumir o pedido"],
    )


def _analysis(
    action: PreparedAction,
    *,
    intent: str,
    domain: str,
    status: str,
    reason: str,
    summary: str,
    entities: dict[str, str] | None = None,
    observations: list[str] | None = None,
) -> Analysis:
    return Analysis(
        original_text=action.original_action,
        normalized_text=action.normalized_action,
        intent=intent,
        domain=domain,
        status=status,
        reason=reason,
        summary=summary,
        entities=entities or {},
        observations=observations or [],
    )


def _first_action(actions: list[PreparedAction]) -> PreparedAction:
    return actions[0] if actions else PreparedAction(index=1)


def _action_target(action: PreparedAction) -> str:
    target = " ".join(action.original_tokens[1:]).strip()
    return target or "-"


def _normalized_action_text(action: PreparedAction) -> str:
    return " ".join(action.normalized_tokens).strip()


def _match_copy_rename(action: PreparedAction) -> Analysis | None:
    original_clean = action.original_action
    ascii_original = strip_accents(original_clean)
    pattern = re.compile(
        r"copie a pasta (?P<name>[^ ]+) que fica em (?P<base>[^ ]+) para (?P<dest>[^ ]+) e renomeie ela para (?P<new>[^ ]+)",
        re.IGNORECASE,
    )
    m = pattern.search(ascii_original)
    if not m:
        return None
    name = m.group("name")
    base = m.group("base")
    dest_base = m.group("dest")
    new_name = m.group("new")
    source = f"{base}/{name}"
    copied = f"{dest_base}/{name}"
    final = f"{dest_base}/{new_name}"
    return _analysis(
        action,
        intent="renomear",
        domain="arquivo",
        status="CONSISTENTE",
        reason="intenção, domínio e entidades mínimas convergem para uma leitura única.",
        summary=f"Renomear '{copied}' para '{final}'.",
        entities={
            "tipo": "pasta",
            "origem": source,
            "destino": copied,
            "novo_nome": final,
        },
        observations=["encadeamento local preservado"],
    )


def analyze_prepared_action(action: PreparedAction) -> Analysis:
    if not action.original_tokens:
        return Analysis(
            original_text="",
            normalized_text="",
            intent="não identificada",
            domain="desconhecido",
            status="BLOQUEADA",
            reason="faltou a frase para inspecionar.",
            summary="Sem ação prevista.",
            observations=["forneça uma frase depois de 'aury dev'"],
        )

    normalized_text = _normalized_action_text(action)
    first_token = action.normalized_tokens[0] if action.normalized_tokens else ""

    chain = _match_copy_rename(action)
    if chain is not None:
        return chain

    if first_token in {"remover", "remova"}:
        target = _action_target(action)
        return _analysis(
            action,
            intent="remover",
            domain="pacote",
            status="CONSISTENTE",
            reason="política canônica de remoção sem colisão explícita favorece pacote.",
            summary=f"Remover '{target}'.",
            entities={"alvo_principal": target},
            observations=["forma explícita de arquivo continua tratada pelo runtime legado"],
        )

    if "velocidade" in action.normalized_tokens and "internet" in action.normalized_tokens:
        return _analysis(
            action,
            intent="velocidade",
            domain="rede",
            status="CONSISTENTE",
            reason="leitura de rede fechada com alvo explícito de velocidade.",
            summary="Medir a velocidade da internet.",
            entities={"alvo_principal": "velocidade da internet"},
            observations=["backend esperado: librespeed-cli"],
        )

    if first_token in {"procurar", "buscar"}:
        target = _action_target(action)
        return _analysis(
            action,
            intent="procurar",
            domain="pacote",
            status="CONSISTENTE",
            reason="pedido de busca de pacote reconhecido.",
            summary=f"Procurar '{target}'.",
            entities={"alvo_principal": target},
        )

    if normalized_text in {"ver ip", "mostrar ip", "ip"}:
        return _analysis(
            action,
            intent="ver",
            domain="rede",
            status="CONSISTENTE",
            reason="pedido de rede reconhecido.",
            summary="Mostrar o IP local.",
            entities={"alvo_principal": "ip"},
        )

    if normalized_text in {"testar internet", "verificar internet", "internet"}:
        return _analysis(
            action,
            intent="testar",
            domain="rede",
            status="CONSISTENTE",
            reason="pedido de conectividade reconhecido.",
            summary="Testar a conectividade com a internet.",
            entities={"alvo_principal": "internet"},
        )

    if "cpu" in action.normalized_tokens:
        return _analysis(
            action,
            intent="ver",
            domain="sistema",
            status="CONSISTENTE",
            reason="pedido de sistema reconhecido.",
            summary="Mostrar informações de CPU.",
            entities={"alvo_principal": "cpu"},
        )

    if "memoria" in action.normalized_tokens:
        return _analysis(
            action,
            intent="ver",
            domain="sistema",
            status="CONSISTENTE",
            reason="pedido de sistema reconhecido.",
            summary="Mostrar informações de memória.",
            entities={"alvo_principal": "memória"},
        )

    if "disco" in action.normalized_tokens:
        return _analysis(
            action,
            intent="ver",
            domain="sistema",
            status="CONSISTENTE",
            reason="pedido de sistema reconhecido.",
            summary="Mostrar informações de disco.",
            entities={"alvo_principal": "disco"},
        )

    if "gpu" in action.normalized_tokens:
        return _analysis(
            action,
            intent="ver",
            domain="sistema",
            status="CONSISTENTE",
            reason="pedido de sistema reconhecido.",
            summary="Mostrar informações de GPU.",
            entities={"alvo_principal": "gpu"},
        )

    if normalized_text == "status" or "status do sistema" in normalized_text:
        return _analysis(
            action,
            intent="status",
            domain="sistema",
            status="CONSISTENTE",
            reason="pedido de status reconhecido.",
            summary="Mostrar o status do sistema.",
            entities={"alvo_principal": "status do sistema"},
        )

    return _unsupported(action)


def analyze_prepared_actions(actions: list[PreparedAction]) -> list[Analysis]:
    if not actions:
        return [analyze_prepared_action(PreparedAction(index=1))]
    return [analyze_prepared_action(action) for action in actions]


def prepare_analyses(text: str) -> tuple[InputPhrase, list[PreparedAction], list[Analysis]]:
    phrase, actions = prepare_text(text)
    prepared_actions = actions or [PreparedAction(index=1)]
    return phrase, prepared_actions, analyze_prepared_actions(prepared_actions)


def prepare_analysis(text: str) -> tuple[InputPhrase, PreparedAction, Analysis]:
    phrase, actions, analyses = prepare_analyses(text)
    action = _first_action(actions)
    analysis = analyses[0] if analyses else analyze_prepared_action(action)
    return phrase, action, analysis


def analyze_phrase(text: str) -> Analysis:
    # O runtime atual continua ancorado na primeira ação preparada.
    _phrase, _actions, analyses = prepare_analyses(text)
    return analyses[0]
