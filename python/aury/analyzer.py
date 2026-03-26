from __future__ import annotations

import re

from .contracts import Analysis, InputPhrase, PreparedAction
from .normalize import strip_accents
from .pipeline import prepare_text
from .sensitive_tokens import token_sensitive_type


_EXTRACTION_INTENT_TOKENS = {
    "extrair",
    "extraia",
    "extrai",
    "extraira",
    "extrairá",
    "descompactar",
    "descompacte",
    "descompacta",
    "descomprima",
    "descomprimir",
    "desarquivar",
}
_COMPRESSION_INTENT_TOKENS = {"compactar", "compacte"}
_COPY_INTENT_TOKENS = {"copiar", "copie", "copia"}
_MOVE_INTENT_TOKENS = {"mover", "move", "mova"}
_RENAME_INTENT_TOKENS = {"renomear", "renomeie", "renomeia", "renomea"}
_EXTRACTION_CONNECTOR_TOKENS = {"para"}
_COMPRESSION_CONNECTOR_TOKENS = {"para"}
_EXTRACTION_LEADING_TYPE_TOKENS = {"arquivo", "pacote", "pasta"}
_EXTRACTION_DESTINATION_NOISE_TOKENS = {
    "a",
    "as",
    "o",
    "os",
    "um",
    "uma",
    "uns",
    "umas",
    "pasta",
    "caminho",
    "local",
    "destino",
    "lugar",
    "que",
    "fica",
    "ficar",
    "esta",
    "em",
    "no",
    "na",
    "nos",
    "nas",
}
_CREATE_LOCATION_BASE_NOISE_TOKENS = {
    "a",
    "as",
    "o",
    "os",
    "um",
    "uma",
    "uns",
    "umas",
    "pasta",
    "arquivo",
    "caminho",
    "local",
    "destino",
    "lugar",
    "diretorio",
    "diretório",
}
_PACKAGE_DOMAIN_NOISE_TOKENS = {"pacote", "pacotes", "app", "aplicativo", "aplicativos", "programa", "programas"}


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


def _package_target(action: PreparedAction) -> str:
    start = 1
    while start < len(action.normalized_tokens):
        token = action.normalized_tokens[start]
        if token not in _PACKAGE_DOMAIN_NOISE_TOKENS:
            break
        start += 1
    target = " ".join(action.original_tokens[start:]).strip()
    return target or "-"


def _normalized_action_text(action: PreparedAction) -> str:
    return " ".join(action.normalized_tokens).strip()


def _join_tokens(tokens: list[str]) -> str:
    return " ".join(tokens).strip()


def _semantic_token(token: str) -> str:
    return token.rstrip(",.;:!?")


def _semantic_original_tokens(tokens: list[str]) -> list[str]:
    return [_semantic_token(token) for token in tokens]


def _normalized_intent_token(token: str) -> str:
    if token in {"criar", "crie"}:
        return "criar"
    if token in {"procurar", "procure"}:
        return "procurar"
    if token in {"atualizar", "atualiza", "atualize", "update", "upgrade", "sincronizar", "atualizara"}:
        return "atualizar"
    if token in {"otimizar", "otimiza", "otimize", "limpar", "limpa", "melhorar", "acelerar"}:
        return "otimizar"
    if token in {"remover", "remova", "apagar", "apague", "apaga"}:
        return "remover"
    if token in _COPY_INTENT_TOKENS:
        return "copiar"
    if token in _MOVE_INTENT_TOKENS:
        return "mover"
    if token in _RENAME_INTENT_TOKENS:
        return "renomear"
    if token in _EXTRACTION_INTENT_TOKENS:
        return "extrair"
    if token in _COMPRESSION_INTENT_TOKENS:
        return "compactar"
    return token


def _has_explicit_target(action: PreparedAction) -> bool:
    return _action_target(action) != "-"


def _is_probably_path(value: str) -> bool:
    if not value:
        return False
    return bool(
        re.match(r"^(~/|/|\./|\.\./)", value)
        or re.search(r".+/$", value)
        or re.search(r".+/.+", value)
    )


def _is_probably_filename(value: str) -> bool:
    if not value:
        return False
    return bool(
        _is_probably_path(value)
        or re.match(r"^\.[^/]+$", value)
        or re.match(r"^[^\s/]+\.[A-Za-z0-9][A-Za-z0-9._-]*$", value)
    )


def _is_probably_directory_hint(value: str) -> bool:
    if not value:
        return False
    return bool(re.search(r"/$", value))


def _parent_directory_or_empty(path: str) -> str:
    if not path or "/" not in path:
        return ""
    parent, _, _name = path.rpartition("/")
    return parent


def _join_base_and_name(base: str, name: str) -> str:
    if not base:
        return name
    if not name:
        return base
    if _is_probably_path(name):
        return name
    return f"{base}/{name}" if not base.endswith("/") else f"{base}{name}"


def _join_location_base_and_name(base: str, name: str) -> str:
    if not base:
        return name
    if not name:
        return base
    if name.endswith("/"):
        trimmed_name = name[:-1]
        if trimmed_name and not re.match(r"^(~/|/|\./|\.\./)", trimmed_name) and "/" not in trimmed_name:
            return f"{base}/{name}" if not base.endswith("/") else f"{base}{name}"
    return _join_base_and_name(base, name)


def _basename(path: str) -> str:
    if not path:
        return ""
    return path.rsplit("/", 1)[-1]


def _resolve_rename_target(source: str, requested_newname: str) -> str:
    if not requested_newname:
        return requested_newname
    rename_base = _parent_directory_or_empty(source)
    return _join_base_and_name(rename_base, requested_newname)


def _effective_transfer_destination(source_type: str, source: str, requested_destination: str) -> str:
    if source_type != "pasta":
        return requested_destination
    return _join_base_and_name(requested_destination, _basename(source))


def _detect_archive_type(path: str) -> str:
    lower = path.lower()
    if lower.endswith(".tar.gz") or lower.endswith(".tgz"):
        return "tar.gz"
    if lower.endswith(".tar"):
        return "tar"
    if lower.endswith(".zip"):
        return "zip"
    if lower.endswith(".7z"):
        return "7z"
    return ""


def _detect_compact_output_type(path: str) -> str:
    lower = path.lower()
    if lower.endswith(".tar.gz"):
        return "tar.gz"
    if lower.endswith(".zip"):
        return "zip"
    return ""


def _archive_default_destination(archive_path: str) -> str:
    base = archive_path.rsplit("/", 1)[-1]
    lower = base.lower()
    name = base

    if lower.endswith(".tar.gz"):
        name = base[:-7]
    elif lower.endswith(".tgz"):
        name = base[:-4]
    elif lower.endswith(".tar"):
        name = base[:-4]
    elif lower.endswith(".zip"):
        name = base[:-4]
    elif lower.endswith(".7z"):
        name = base[:-3]

    if not name:
        name = "extracted"

    parent = _parent_directory_or_empty(archive_path)
    if not parent or parent == ".":
        return f"./{name}"
    return f"{parent}/{name}"


def _extract_destination_phrase(
    original_tokens: list[str],
    normalized_tokens: list[str],
) -> tuple[str, bool]:
    start = 0
    while start < len(normalized_tokens):
        if token_sensitive_type(original_tokens[start]) is not None:
            break
        if normalized_tokens[start] not in _EXTRACTION_DESTINATION_NOISE_TOKENS:
            break
        start += 1

    skipped_tokens = normalized_tokens[:start]
    destination = _join_tokens(original_tokens[start:])
    used_simple_location = (
        "que" in skipped_tokens
        and any(token in {"fica", "esta"} for token in skipped_tokens)
        and any(token in {"em", "no", "na", "nos", "nas"} for token in skipped_tokens)
    )
    return destination, used_simple_location


def _blocked_compact_action(
    action: PreparedAction,
    *,
    source_type: str,
    source: str = "",
    output: str = "",
    lacuna: str,
    reason: str,
    summary: str,
    observations: list[str] | None = None,
) -> Analysis:
    entities = {"tipo_de_origem": source_type, "lacuna": lacuna}
    if source:
        entities["origem"] = source
        entities["alvo_principal"] = source
    if output:
        entities["saida"] = output
    return _analysis(
        action,
        intent="compactar",
        domain="arquivo",
        status="BLOQUEADA",
        reason=reason,
        summary=summary,
        entities=entities,
        observations=observations or [],
    )


def _match_compact_action(action: PreparedAction) -> Analysis | None:
    normalized_tokens = action.normalized_tokens
    original_tokens = action.original_tokens

    if len(normalized_tokens) < 2:
        return None

    first_token = _normalized_intent_token(normalized_tokens[0])
    if first_token != "compactar":
        return None

    if normalized_tokens[1] not in {"arquivo", "pasta"}:
        return None

    source_type = normalized_tokens[1]
    source_start = 2

    if source_start >= len(original_tokens):
        return _blocked_compact_action(
            action,
            source_type=source_type,
            lacuna="origem",
            reason="o pedido de compactação foi reconhecido, mas faltou a origem explícita.",
            summary="Compactação sem origem válida; leitura bloqueada.",
            observations=["a compactação mínima da v1.7 exige um único arquivo ou uma única pasta como origem"],
        )

    connector_idx = next(
        (index for index in range(source_start, len(normalized_tokens)) if normalized_tokens[index] in _COMPRESSION_CONNECTOR_TOKENS),
        None,
    )

    if connector_idx is None:
        source = _join_tokens(original_tokens[source_start:])
        if not source:
            return _blocked_compact_action(
                action,
                source_type=source_type,
                lacuna="origem",
                reason="o pedido de compactação foi reconhecido, mas faltou a origem explícita.",
                summary="Compactação sem origem válida; leitura bloqueada.",
                observations=["a compactação mínima da v1.7 exige um único arquivo ou uma única pasta como origem"],
            )
        return _blocked_compact_action(
            action,
            source_type=source_type,
            source=source,
            lacuna="saída explícita obrigatória",
            reason="o pedido de compactação foi reconhecido, mas ainda falta a saída explícita obrigatória.",
            summary="Compactação sem saída explícita; leitura bloqueada.",
            observations=["o primeiro corte da compactação exige o conector 'para' com um arquivo de saída explícito"],
        )

    source = _join_tokens(original_tokens[source_start:connector_idx])
    output = _join_tokens(original_tokens[connector_idx + 1 :])

    if not source:
        return _blocked_compact_action(
            action,
            source_type=source_type,
            output=output,
            lacuna="origem",
            reason="o pedido de compactação foi reconhecido, mas faltou a origem explícita.",
            summary="Compactação sem origem válida; leitura bloqueada.",
            observations=["a compactação mínima da v1.7 exige um único arquivo ou uma única pasta como origem"],
        )

    if not output:
        return _blocked_compact_action(
            action,
            source_type=source_type,
            source=source,
            lacuna="saída explícita obrigatória",
            reason="o pedido de compactação foi reconhecido, mas ainda falta a saída explícita obrigatória.",
            summary="Compactação sem saída explícita; leitura bloqueada.",
            observations=["o primeiro corte da compactação exige o conector 'para' com um arquivo de saída explícito"],
        )

    output_type = _detect_compact_output_type(output)
    if not output_type:
        return _blocked_compact_action(
            action,
            source_type=source_type,
            source=source,
            output=output,
            lacuna="saída .zip ou .tar.gz",
            reason="o pedido de compactação foi reconhecido, mas a saída ficou fora do recorte mínimo de formatos.",
            summary="Saída fora do recorte da compactação; leitura bloqueada.",
            observations=["nesta v1.7, a compactação mínima aceita apenas '.zip' e '.tar.gz'"],
        )

    return _analysis(
        action,
        intent="compactar",
        domain="arquivo",
        status="CONSISTENTE",
        reason=f"pedido de compactação de {source_type} com saída explícita reconhecido.",
        summary=f"Compactar '{source}' em '{output}'.",
        entities={
            "tipo": output_type,
            "tipo_de_origem": source_type,
            "alvo_principal": source,
            "origem": source,
            "saida": output,
        },
        observations=[
            f"formato inferido exclusivamente pelo sufixo da saída '{output}'",
            "execução normal atual continua no adaptador Fish",
        ],
    )


def _match_extract_action(action: PreparedAction) -> Analysis | None:
    normalized_tokens = action.normalized_tokens
    original_tokens = action.original_tokens

    if len(normalized_tokens) < 2:
        return None

    first_token = _normalized_intent_token(normalized_tokens[0])
    if first_token != "extrair":
        return None

    source_start = 1
    while source_start < len(normalized_tokens) and normalized_tokens[source_start] in _EXTRACTION_LEADING_TYPE_TOKENS:
        source_start += 1

    if source_start >= len(original_tokens):
        return None

    connector_idx = next(
        (index for index in range(source_start, len(normalized_tokens)) if normalized_tokens[index] in _EXTRACTION_CONNECTOR_TOKENS),
        None,
    )

    if connector_idx is None:
        source = _join_tokens(original_tokens[source_start:])
        destination = ""
        used_simple_location = False
        used_explicit_path_destination = False
    else:
        source = _join_tokens(original_tokens[source_start:connector_idx])
        destination, used_simple_location = _extract_destination_phrase(
            original_tokens[connector_idx + 1 :],
            normalized_tokens[connector_idx + 1 :],
        )
        used_explicit_path_destination = _is_probably_path(destination)
        if not destination or (not used_simple_location and not used_explicit_path_destination):
            return None

    if not source:
        return None

    archive_type = _detect_archive_type(source)
    if not archive_type:
        return None

    observations = ["execução normal atual continua no adaptador Fish"]
    reason = "pedido de extração de arquivo compactado reconhecido."

    if not destination:
        destination = _archive_default_destination(source)
        reason = (
            "pedido de extração de arquivo compactado reconhecido; "
            "o destino padrão pode ser derivado com segurança a partir do nome do arquivo."
        )
        observations.insert(0, f"destino padrão de extração derivado como '{destination}'")
    elif used_simple_location:
        reason = (
            "pedido de extração de arquivo compactado com destino em localização "
            "conversacional simples reconhecido."
        )
        observations.insert(0, f"localização conversacional simples usada para fechar o destino '{destination}'")
    else:
        reason = "pedido de extração de arquivo compactado com destino explícito em caminho real reconhecido."
        observations.insert(0, f"destino explícito em caminho real preservado como '{destination}'")

    entities = {
        "tipo": archive_type,
        "arquivo_compactado": source,
        "alvo_principal": source,
        "destino": destination,
    }
    if used_simple_location:
        entities["localizacao_conversacional"] = f"destino simples: {destination}"

    domain = "pasta" if "pasta" in normalized_tokens else "arquivo"
    return _analysis(
        action,
        intent="extrair",
        domain=domain,
        status="CONSISTENTE",
        reason=reason,
        summary=f"Extrair '{source}' para '{destination}'.",
        entities=entities,
        observations=observations,
    )


def _has_out_of_scope_location(tokens: list[str]) -> bool:
    return any(token in {"em", "no", "na", "nos", "nas", "para"} for token in tokens)


def _explicit_file_type(tokens: list[str]) -> tuple[str, int] | None:
    if len(tokens) < 3:
        return None

    if tokens[1] in {"arquivo", "pasta"}:
        return tokens[1], 1

    if len(tokens) >= 4 and tokens[1] in {"o", "a"} and tokens[2] in {"arquivo", "pasta"}:
        return tokens[2], 2

    return None


def _conversational_location_bounds(tokens: list[str]) -> tuple[int, int] | None:
    for index in range(len(tokens) - 2):
        if tokens[index] != "que":
            continue
        if tokens[index + 1] not in {"fica", "esta"}:
            continue
        if tokens[index + 2] not in {"em", "no", "na", "nos", "nas"}:
            continue
        return index, index + 3
    return None


def _resolve_located_target(original_tokens: list[str], normalized_tokens: list[str], *, start: int) -> tuple[str, str] | None:
    location_bounds = _conversational_location_bounds(normalized_tokens[start:])
    if location_bounds is None:
        return None

    name_end, base_start = location_bounds
    target_name = _join_tokens(original_tokens[start : start + name_end])
    target_base = _join_tokens(original_tokens[start + base_start :])
    if not target_name or not target_base:
        return None

    return _join_base_and_name(target_base, target_name), target_base


def _strip_leading_location_base_noise(
    original_tokens: list[str],
    normalized_tokens: list[str],
) -> tuple[list[str], list[str]]:
    start = 0
    while start < len(normalized_tokens):
        if token_sensitive_type(original_tokens[start]) is not None:
            break
        if normalized_tokens[start] in _CREATE_LOCATION_BASE_NOISE_TOKENS:
            start += 1
            continue
        break
    return original_tokens[start:], normalized_tokens[start:]


def _resolve_simple_create_target(
    original_tokens: list[str],
    normalized_tokens: list[str],
    *,
    start: int,
) -> tuple[str, str, str] | None:
    connector_idx = next(
        (index for index in range(start, len(normalized_tokens) - 1) if normalized_tokens[index] == "em"),
        None,
    )
    if connector_idx is None:
        return None

    target_name = _join_tokens(original_tokens[start:connector_idx])
    base_original_tokens, base_normalized_tokens = _strip_leading_location_base_noise(
        original_tokens[connector_idx + 1 :],
        normalized_tokens[connector_idx + 1 :],
    )
    target_base = _join_tokens(base_original_tokens)
    if not target_name or not target_base:
        return None
    if "e" in base_normalized_tokens:
        return None

    return _join_location_base_and_name(target_base, target_name), target_name, target_base


def _is_local_reference_token(token: str) -> bool:
    return token in {"ele", "ela", "isso"}


def _resolved_local_reference(previous_analysis: Analysis, token: str) -> tuple[str, str] | None:
    if previous_analysis.intent != "remover":
        return None
    if previous_analysis.domain != "arquivo":
        return None
    if previous_analysis.status != "CONSISTENTE":
        return None

    reference_path = previous_analysis.entities.get("origem") or previous_analysis.entities.get("alvo_principal", "")
    reference_type = previous_analysis.entities.get("tipo", "")
    if not reference_path or not reference_type:
        return None

    if token == "ele" and reference_type != "arquivo":
        return None
    if token == "ela" and reference_type != "pasta":
        return None

    return reference_path, reference_type


def _resolved_copy_followup_local_reference(previous_analysis: Analysis, token: str) -> tuple[str, str] | None:
    if previous_analysis.intent != "copiar":
        return None
    if previous_analysis.domain != "arquivo":
        return None
    if previous_analysis.status != "CONSISTENTE":
        return None

    reference_path = previous_analysis.entities.get("destino") or previous_analysis.entities.get("alvo_principal", "")
    reference_type = previous_analysis.entities.get("tipo", "")
    if not reference_path or not reference_type:
        return None

    if token == "ele" and reference_type != "arquivo":
        return None
    if token == "ela" and reference_type != "pasta":
        return None

    return reference_path, reference_type


def _resolved_move_or_copy_followup_local_reference(previous_analysis: Analysis, token: str) -> tuple[str, str] | None:
    resolved_reference = _resolved_copy_followup_local_reference(previous_analysis, token)
    if resolved_reference is not None:
        return resolved_reference

    if previous_analysis.intent != "mover":
        return None
    if previous_analysis.domain != "arquivo":
        return None
    if previous_analysis.status != "CONSISTENTE":
        return None

    reference_path = previous_analysis.entities.get("destino") or previous_analysis.entities.get("alvo_principal", "")
    reference_type = previous_analysis.entities.get("tipo", "")
    if not reference_path or not reference_type:
        return None
    if reference_type == "arquivo" and not _is_probably_filename(reference_path):
        return None

    if token == "ele" and reference_type != "arquivo":
        return None
    if token == "ela" and reference_type != "pasta":
        return None

    return reference_path, reference_type


def _previous_analysis_context(previous_analysis: Analysis) -> str:
    items = [
        f"intenção '{previous_analysis.intent}'",
        f"domínio '{previous_analysis.domain}'",
        f"estado '{previous_analysis.status}'",
    ]
    previous_type = previous_analysis.entities.get("tipo", "")
    previous_target = previous_analysis.entities.get("origem") or previous_analysis.entities.get("alvo_principal", "")
    if previous_type:
        items.append(f"tipo '{previous_type}'")
    if previous_target:
        items.append(f"alvo '{previous_target}'")
    return ", ".join(items)


def _match_isolated_destructive_local_reference(action: PreparedAction) -> Analysis | None:
    if len(action.normalized_tokens) != 2:
        return None

    first_token = _normalized_intent_token(action.normalized_tokens[0])
    if first_token != "remover":
        return None

    local_reference_token = action.normalized_tokens[1]
    if not _is_local_reference_token(local_reference_token):
        return None

    return _analysis(
        action,
        intent="remover",
        domain="arquivo",
        status="BLOQUEADA",
        reason=(
            f"a referência local '{local_reference_token}' não foi resolvida com segurança "
            "porque não há antecedente seguro nesta ação destrutiva isolada."
        ),
        summary="Remoção sem alvo seguro; leitura bloqueada.",
        entities={"referencia_local": f"{local_reference_token} (não resolvida)"},
        observations=[
            f"anáfora destrutiva isolada com '{local_reference_token}' não fornece alvo seguro",
            "modo normal atual bloqueia remoção destrutiva sem alvo explícito no adaptador Fish",
        ],
    )


def _match_basic_file_action(action: PreparedAction) -> Analysis | None:
    normalized_tokens = action.normalized_tokens
    original_tokens = action.original_tokens

    if len(normalized_tokens) < 2:
        return None

    first_token = _normalized_intent_token(normalized_tokens[0])
    second_token = normalized_tokens[1]

    if first_token == "criar":
        target_type = ""
        target_start = 0
        if second_token in {"arquivo", "pasta"}:
            target_type = second_token
            target_start = 2
        elif len(normalized_tokens) >= 4 and second_token in {"o", "a", "um", "uma"} and normalized_tokens[2] in {"arquivo", "pasta"}:
            target_type = normalized_tokens[2]
            target_start = 3
        elif _is_probably_directory_hint(original_tokens[1]):
            target_type = "pasta"
            target_start = 1
        elif _is_probably_filename(original_tokens[1]):
            target_type = "arquivo"
            target_start = 1
        if not target_type:
            return None
        located_target = _resolve_simple_create_target(original_tokens, normalized_tokens, start=target_start)
        if located_target is not None:
            target, target_name, target_base = located_target
            return _analysis(
                action,
                intent="criar",
                domain="arquivo",
                status="CONSISTENTE",
                reason=f"pedido de criação de {target_type} com localização conversacional simples reconhecido.",
                summary=f"Criar '{target}'.",
                entities={
                    "tipo": target_type,
                    "alvo_principal": target,
                    "destino": target_base,
                    "localizacao_conversacional": f"nome: {target_name} | base: {target_base} | conector: em",
                },
                observations=[
                    f"localização conversacional simples usada para recompor a base '{target_base}'",
                    "execução normal atual já pode seguir no runtime Python",
                ],
            )
        if _has_out_of_scope_location(normalized_tokens[target_start:]):
            return None
        target = _join_tokens(original_tokens[target_start:])
        if not target:
            return None
        return _analysis(
            action,
            intent="criar",
            domain="arquivo",
            status="CONSISTENTE",
            reason=f"pedido básico de criação de {target_type} reconhecido.",
            summary=f"Criar '{target}'.",
            entities={"tipo": target_type, "alvo_principal": target},
            observations=["execução normal atual já pode seguir no runtime Python"],
        )

    if first_token == "remover" and len(normalized_tokens) == 2:
        target = original_tokens[1]
        target_type = ""
        reason = ""
        if _is_probably_directory_hint(target):
            target_type = "pasta"
            reason = "pedido curto de remoção de pasta reconhecido."
        elif _is_probably_filename(target):
            target_type = "arquivo"
            reason = "pedido curto de remoção de arquivo reconhecido."
        if not target_type:
            return None
        return _analysis(
            action,
            intent="remover",
            domain="arquivo",
            status="CONSISTENTE",
            reason=reason,
            summary=f"Remover '{target}'.",
            entities={"tipo": target_type, "alvo_principal": target},
            observations=[
                "remoção destrutiva continua com confirmação no adaptador Fish",
            ],
        )

    if len(normalized_tokens) < 3:
        return None

    explicit_type = _explicit_file_type(normalized_tokens)
    if first_token in {"copiar", "mover"} and explicit_type is not None:
        target_type, type_idx = explicit_type
        if target_type != "arquivo":
            return None
        target_start = type_idx + 1
        try:
            connector_idx = normalized_tokens.index("para", target_start)
        except ValueError:
            return None
        source_slice = normalized_tokens[target_start:connector_idx]
        if not source_slice or _conversational_location_bounds(source_slice) is not None:
            return None
        source = _join_tokens(original_tokens[target_start:connector_idx])
        destination = _join_tokens(original_tokens[connector_idx + 1 :])
        if not source or not destination:
            return None
        summary_verb = "Copiar" if first_token == "copiar" else "Mover"
        reason = "pedido básico de cópia de arquivo reconhecido." if first_token == "copiar" else "pedido básico de mover arquivo reconhecido."
        return _analysis(
            action,
            intent=first_token,
            domain="arquivo",
            status="CONSISTENTE",
            reason=reason,
            summary=f"{summary_verb} '{source}' para '{destination}'.",
            entities={
                "tipo": "arquivo",
                "alvo_principal": source,
                "origem": source,
                "destino": destination,
            },
            observations=["execução normal atual continua no adaptador Fish"],
        )

    if first_token == "renomear" and explicit_type is not None:
        target_type, type_idx = explicit_type
        if target_type != "arquivo":
            return None
        target_start = type_idx + 1
        try:
            connector_idx = normalized_tokens.index("para", target_start)
        except ValueError:
            return None
        source_slice = normalized_tokens[target_start:connector_idx]
        if not source_slice or _conversational_location_bounds(source_slice) is not None:
            return None
        source = _join_tokens(original_tokens[target_start:connector_idx])
        requested_newname = _join_tokens(original_tokens[connector_idx + 1 :])
        if not source or not requested_newname:
            return None
        final_target = _resolve_rename_target(source, requested_newname)
        return _analysis(
            action,
            intent="renomear",
            domain="arquivo",
            status="CONSISTENTE",
            reason="pedido básico de renomear arquivo reconhecido.",
            summary=f"Renomear '{source}' para '{final_target}'.",
            entities={
                "tipo": "arquivo",
                "alvo_principal": source,
                "origem": source,
                "destino": final_target,
                "novo_nome": requested_newname,
            },
            observations=["execução normal atual continua no adaptador Fish"],
        )

    if first_token == "remover":
        explicit_type = _explicit_file_type(normalized_tokens)
        target_type = ""
        target_start = 0
        implicit_file_requires_location = False
        if explicit_type is not None:
            target_type, type_idx = explicit_type
            target_start = type_idx + 1
        elif _is_probably_directory_hint(original_tokens[1]):
            target_type = "pasta"
            target_start = 1
        elif _is_probably_filename(original_tokens[1]):
            target_type = "arquivo"
            target_start = 1
            implicit_file_requires_location = True
        if not target_type:
            return None
        located_target = _resolve_located_target(original_tokens, normalized_tokens, start=target_start)
        if located_target is not None:
            target, target_base = located_target
            return _analysis(
                action,
                intent="remover",
                domain="arquivo",
                status="CONSISTENTE",
                reason=f"pedido explícito de remoção de {target_type} com localização conversacional reconhecido.",
                summary=f"Remover '{target}'.",
                entities={
                    "tipo": target_type,
                    "alvo_principal": target,
                    "origem": target,
                },
                observations=[
                    f"localização conversacional usada para recompor a base '{target_base}'",
                    "remoção explícita continua com confirmação destrutiva no adaptador Fish",
                ],
            )
        simple_located_target = _resolve_simple_create_target(original_tokens, normalized_tokens, start=target_start)
        if simple_located_target is not None:
            target, _target_name, target_base = simple_located_target
            return _analysis(
                action,
                intent="remover",
                domain="arquivo",
                status="CONSISTENTE",
                reason=f"pedido de remoção de {target_type} com localização conversacional simples reconhecido.",
                summary=f"Remover '{target}'.",
                entities={
                    "tipo": target_type,
                    "alvo_principal": target,
                    "origem": target,
                },
                observations=[
                    f"localização conversacional simples usada para recompor a base '{target_base}'",
                    "remoção destrutiva continua com confirmação no adaptador Fish",
                ],
            )
        if implicit_file_requires_location:
            return None
        if _has_out_of_scope_location(normalized_tokens[target_start:]):
            return None
        target = _join_tokens(original_tokens[target_start:])
        if not target:
            return None
        return _analysis(
            action,
            intent="remover",
            domain="arquivo",
            status="CONSISTENTE",
            reason=f"pedido explícito de remoção de {target_type} reconhecido.",
            summary=f"Remover '{target}'.",
            entities={"tipo": target_type, "alvo_principal": target},
            observations=[
                "remoção explícita continua com confirmação destrutiva no adaptador Fish",
            ],
        )

    return None


def _match_located_copy_action(action: PreparedAction) -> Analysis | None:
    normalized_tokens = action.normalized_tokens
    original_tokens = action.original_tokens
    semantic_original_tokens = _semantic_original_tokens(original_tokens)

    if len(normalized_tokens) < 6:
        return None

    first_token = _normalized_intent_token(normalized_tokens[0])
    if first_token != "copiar":
        return None

    explicit_type = _explicit_file_type(normalized_tokens)
    if explicit_type is None:
        return None
    target_type, type_idx = explicit_type

    target_start = type_idx + 1
    try:
        connector_idx = normalized_tokens.index("para", target_start)
    except ValueError:
        return None

    located_source = _resolve_located_target(
        semantic_original_tokens[:connector_idx],
        normalized_tokens[:connector_idx],
        start=target_start,
    )
    if located_source is None:
        return None

    source, source_base = located_source
    requested_destination = _join_tokens(semantic_original_tokens[connector_idx + 1 :])
    if not requested_destination:
        return None

    effective_destination = _effective_transfer_destination(target_type, source, requested_destination)

    return _analysis(
        action,
        intent="copiar",
        domain="arquivo",
        status="CONSISTENTE",
        reason=f"pedido de cópia de {target_type} com localização conversacional reconhecido.",
        summary=f"Copiar '{source}' para '{effective_destination}'.",
        entities={
            "tipo": target_type,
            "alvo_principal": source,
            "origem": source,
            "destino": effective_destination,
        },
        observations=[
            f"localização conversacional usada para recompor a base '{source_base}'",
            f"destino efetivo recomposto como '{effective_destination}' para continuidade local",
            "execução normal atual continua no adaptador Fish",
        ],
    )


def _match_folder_transfer_action(action: PreparedAction) -> Analysis | None:
    normalized_tokens = action.normalized_tokens
    original_tokens = action.original_tokens
    semantic_original_tokens = _semantic_original_tokens(original_tokens)

    if len(normalized_tokens) < 5:
        return None

    first_token = _normalized_intent_token(normalized_tokens[0])
    if first_token not in {"copiar", "mover"}:
        return None

    explicit_type = _explicit_file_type(normalized_tokens)
    if explicit_type is None:
        return None
    target_type, type_idx = explicit_type
    if target_type != "pasta":
        return None

    target_start = type_idx + 1
    try:
        connector_idx = normalized_tokens.index("para", target_start)
    except ValueError:
        return None

    source_slice = normalized_tokens[target_start:connector_idx]
    if not source_slice or _conversational_location_bounds(source_slice) is not None:
        return None

    source = _join_tokens(semantic_original_tokens[target_start:connector_idx])
    requested_destination = _join_tokens(semantic_original_tokens[connector_idx + 1 :])
    if not source or not requested_destination:
        return None

    effective_destination = _effective_transfer_destination(target_type, source, requested_destination)
    summary_verb = "Copiar" if first_token == "copiar" else "Mover"
    reason = "pedido básico de cópia de pasta reconhecido." if first_token == "copiar" else "pedido básico de mover pasta reconhecido."
    return _analysis(
        action,
        intent=first_token,
        domain="arquivo",
        status="CONSISTENTE",
        reason=reason,
        summary=f"{summary_verb} '{source}' para '{effective_destination}'.",
        entities={
            "tipo": target_type,
            "alvo_principal": source,
            "origem": source,
            "destino": effective_destination,
        },
        observations=[
            f"destino efetivo recomposto como '{effective_destination}' para continuidade local",
            "execução normal atual continua no adaptador Fish",
        ],
    )


def _match_destructive_followup_with_local_reference(
    action: PreparedAction,
    previous_analysis: Analysis | None,
) -> Analysis | None:
    if previous_analysis is None:
        return None
    if len(action.normalized_tokens) != 2:
        return None

    first_token = _normalized_intent_token(action.normalized_tokens[0])
    if first_token != "remover":
        return None

    local_reference_token = action.normalized_tokens[1]
    if not _is_local_reference_token(local_reference_token):
        return None

    resolved_reference = _resolved_local_reference(previous_analysis, local_reference_token)
    if resolved_reference is None:
        previous_context = _previous_analysis_context(previous_analysis)
        return _analysis(
            action,
            intent="remover",
            domain="arquivo",
            status="BLOQUEADA",
            reason=(
                f"a referência local '{local_reference_token}' tentou reaproveitar o contexto anterior, "
                "mas ele não fornece antecedente seguro para remoção destrutiva."
            ),
            summary="Remoção sem alvo seguro; leitura bloqueada.",
            entities={"referencia_local": local_reference_token},
            observations=[
                f"contexto anterior insuficiente ou incompatível: {previous_context}",
                "modo normal atual bloqueia remoção destrutiva sem alvo explícito no adaptador Fish",
            ],
        )

    reference_path, reference_type = resolved_reference
    return _analysis(
        action,
        intent="remover",
        domain="arquivo",
        status="BLOQUEADA",
        reason=(
            f"a referência local '{local_reference_token}' foi resolvida com segurança como '{reference_path}', "
            "mas a continuação destrutiva ainda não está alinhada ao runtime legado atual."
        ),
        summary=f"Remoção de '{reference_path}' reconhecida, mas bloqueada no estado atual.",
        entities={
            "tipo": reference_type,
            "alvo_principal": reference_path,
            "origem": reference_path,
            "referencia_local": reference_path,
            "lacuna": "alinhamento com runtime atual",
        },
        observations=[
            f"referência local '{local_reference_token}' resolvida com segurança como '{reference_path}'",
            "antecedente imediato anterior permaneceu específico o bastante para reaproveitamento diagnóstico",
            "runtime legado atual ainda bloqueia continuação destrutiva anafórica equivalente",
        ],
    )


def _match_rename_followup_with_local_reference(
    action: PreparedAction,
    previous_analysis: Analysis | None,
) -> Analysis | None:
    if previous_analysis is None:
        return None
    if len(action.normalized_tokens) < 4:
        return None

    first_token = _normalized_intent_token(action.normalized_tokens[0])
    if first_token != "renomear":
        return None

    local_reference_token = action.normalized_tokens[1]
    if not _is_local_reference_token(local_reference_token):
        return None

    try:
        connector_idx = action.normalized_tokens.index("para", 2)
    except ValueError:
        return None

    semantic_original_tokens = _semantic_original_tokens(action.original_tokens)
    requested_newname = _join_tokens(semantic_original_tokens[connector_idx + 1 :])
    if not requested_newname:
        return None

    resolved_reference = _resolved_move_or_copy_followup_local_reference(previous_analysis, local_reference_token)
    if resolved_reference is None:
        return None

    reference_path, reference_type = resolved_reference
    final_target = _resolve_rename_target(reference_path, requested_newname)
    antecedent_phrase = "da cópia anterior" if previous_analysis.intent == "copiar" else "da ação anterior de mover"
    return _analysis(
        action,
        intent="renomear",
        domain="arquivo",
        status="CONSISTENTE",
        reason=(
            f"a referência local '{local_reference_token}' foi resolvida com segurança "
            f"a partir do resultado {antecedent_phrase} como '{reference_path}'."
        ),
        summary=f"Renomear '{reference_path}' para '{final_target}'.",
        entities={
            "tipo": reference_type,
            "alvo_principal": reference_path,
            "origem": reference_path,
            "destino": final_target,
            "novo_nome": requested_newname,
            "referencia_local": reference_path,
        },
        observations=[
            f"referência local '{local_reference_token}' resolvida com segurança como '{reference_path}'",
            "resultado da ação anterior permaneceu específico o bastante para continuidade local",
            "execução normal atual continua no adaptador Fish",
        ],
    )


def _match_move_followup_with_local_reference(
    action: PreparedAction,
    previous_analysis: Analysis | None,
) -> Analysis | None:
    if previous_analysis is None:
        return None
    if len(action.normalized_tokens) < 4:
        return None

    first_token = _normalized_intent_token(action.normalized_tokens[0])
    if first_token != "mover":
        return None

    local_reference_token = action.normalized_tokens[1]
    if not _is_local_reference_token(local_reference_token):
        return None

    try:
        connector_idx = action.normalized_tokens.index("para", 2)
    except ValueError:
        return None

    semantic_original_tokens = _semantic_original_tokens(action.original_tokens)
    requested_destination = _join_tokens(semantic_original_tokens[connector_idx + 1 :])
    if not requested_destination:
        return None

    resolved_reference = _resolved_copy_followup_local_reference(previous_analysis, local_reference_token)
    if resolved_reference is None:
        return None

    reference_path, reference_type = resolved_reference
    effective_destination = _effective_transfer_destination(reference_type, reference_path, requested_destination)
    return _analysis(
        action,
        intent="mover",
        domain="arquivo",
        status="CONSISTENTE",
        reason=(
            f"a referência local '{local_reference_token}' foi resolvida com segurança "
            f"a partir do resultado da cópia anterior como '{reference_path}'."
        ),
        summary=f"Mover '{reference_path}' para '{effective_destination}'.",
        entities={
            "tipo": reference_type,
            "alvo_principal": reference_path,
            "origem": reference_path,
            "destino": effective_destination,
            "referencia_local": reference_path,
        },
        observations=[
            f"referência local '{local_reference_token}' resolvida com segurança como '{reference_path}'",
            f"destino efetivo recomposto como '{effective_destination}' para continuidade local",
            "resultado da cópia anterior permaneceu específico o bastante para continuidade local",
            "execução normal atual continua no adaptador Fish",
        ],
    )


def _match_located_rename_action(action: PreparedAction) -> Analysis | None:
    normalized_tokens = action.normalized_tokens
    original_tokens = action.original_tokens
    semantic_original_tokens = _semantic_original_tokens(original_tokens)

    if len(normalized_tokens) < 6:
        return None

    first_token = _normalized_intent_token(normalized_tokens[0])
    if first_token != "renomear":
        return None

    explicit_type = _explicit_file_type(normalized_tokens)
    if explicit_type is None:
        return None
    target_type, type_idx = explicit_type

    target_start = type_idx + 1
    try:
        connector_idx = normalized_tokens.index("para", target_start)
    except ValueError:
        return None

    located_source = _resolve_located_target(
        semantic_original_tokens[:connector_idx],
        normalized_tokens[:connector_idx],
        start=target_start,
    )
    if located_source is None:
        return None

    source, source_base = located_source
    requested_newname = _join_tokens(semantic_original_tokens[connector_idx + 1 :])
    if not requested_newname:
        return None

    final_target = _resolve_rename_target(source, requested_newname)
    return _analysis(
        action,
        intent="renomear",
        domain="arquivo",
        status="CONSISTENTE",
        reason=f"pedido de renomear {target_type} com localização conversacional reconhecido.",
        summary=f"Renomear '{source}' para '{final_target}'.",
        entities={
            "tipo": target_type,
            "alvo_principal": source,
            "origem": source,
            "destino": final_target,
            "novo_nome": requested_newname,
        },
        observations=[
            f"localização conversacional usada para recompor a base '{source_base}'",
            "execução normal atual continua no adaptador Fish",
        ],
    )


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
    first_token = _normalized_intent_token(action.normalized_tokens[0]) if action.normalized_tokens else ""

    chain = _match_copy_rename(action)
    if chain is not None:
        return chain

    compact_action = _match_compact_action(action)
    if compact_action is not None:
        return compact_action

    basic_file_action = _match_basic_file_action(action)
    if basic_file_action is not None:
        return basic_file_action

    located_copy_action = _match_located_copy_action(action)
    if located_copy_action is not None:
        return located_copy_action

    folder_transfer_action = _match_folder_transfer_action(action)
    if folder_transfer_action is not None:
        return folder_transfer_action

    located_rename_action = _match_located_rename_action(action)
    if located_rename_action is not None:
        return located_rename_action

    extract_action = _match_extract_action(action)
    if extract_action is not None:
        return extract_action

    if first_token == "remover":
        target = _package_target(action)
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

    if first_token in {"instalar", "instala", "instale"} and _has_explicit_target(action):
        target = _package_target(action)
        return _analysis(
            action,
            intent="instalar",
            domain="pacote",
            status="CONSISTENTE",
            reason="pedido de instalação de pacote reconhecido.",
            summary=f"Instalar '{target}'.",
            entities={"alvo_principal": target},
            observations=["política de pacote agora depende do perfil mínimo do host Linux"],
        )

    if first_token == "atualizar":
        return _analysis(
            action,
            intent="atualizar",
            domain="sistema",
            status="CONSISTENTE",
            reason="pedido de manutenção do host reconhecido.",
            summary="Manutenção do host: atualizar o host local.",
            entities={"alvo_principal": "host local"},
            observations=[
                "manutenção do host continua local ao adaptador Fish nesta linha",
                "não há equivalência multi-distro prometida para esta ação",
            ],
        )

    if first_token == "otimizar":
        return _analysis(
            action,
            intent="otimizar",
            domain="sistema",
            status="CONSISTENTE",
            reason="pedido de manutenção do host reconhecido.",
            summary="Manutenção do host: otimizar o host local.",
            entities={"alvo_principal": "host local"},
            observations=[
                "manutenção do host continua local ao adaptador Fish nesta linha",
                "não há equivalência multi-distro prometida para esta ação",
            ],
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

    if "velocidade" in action.normalized_tokens and "rede" in action.normalized_tokens:
        return _analysis(
            action,
            intent="velocidade",
            domain="rede",
            status="CONSISTENTE",
            reason="leitura de rede fechada como pedido de medição de velocidade.",
            summary="Medir a velocidade da rede.",
            entities={"alvo_principal": "velocidade da rede"},
            observations=[
                "modo normal atual fecha isso como speedtest via adaptador Fish",
                "backend esperado: librespeed-cli",
            ],
        )

    if first_token in {"procurar", "buscar"}:
        target = _package_target(action)
        return _analysis(
            action,
            intent="procurar",
            domain="pacote",
            status="CONSISTENTE",
            reason="pedido de busca de pacote reconhecido.",
            summary=f"Procurar '{target}'.",
            entities={"alvo_principal": target},
            observations=["política de pacote agora depende do perfil mínimo do host Linux"],
        )

    if first_token == "ping" and _has_explicit_target(action):
        target = _action_target(action)
        return _analysis(
            action,
            intent="ping",
            domain="rede",
            status="CONSISTENTE",
            reason="pedido de ping com host explícito reconhecido.",
            summary=f"Pingar '{target}'.",
            entities={"alvo_principal": target},
            observations=["execução normal atual preserva o host explícito no adaptador Fish"],
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
    analyses: list[Analysis] = []
    previous_analysis: Analysis | None = None
    for action in actions:
        move_followup = _match_move_followup_with_local_reference(action, previous_analysis)
        rename_followup = _match_rename_followup_with_local_reference(action, previous_analysis)
        followup = _match_destructive_followup_with_local_reference(action, previous_analysis)
        isolated = _match_isolated_destructive_local_reference(action) if previous_analysis is None else None
        analysis = move_followup or rename_followup or followup or isolated or analyze_prepared_action(action)
        analyses.append(analysis)
        previous_analysis = analysis
    return analyses


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
