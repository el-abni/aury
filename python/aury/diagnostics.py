from __future__ import annotations

from .analyzer import prepare_analyses
from .contracts import ActionExecutionPlan, Analysis, PreparedAction, SequenceExecutionPlan
from .host import detect_host_profile, resolve_host_maintenance_action_policy, resolve_package_action_policy
from .runtime import plan_action_execution, plan_sequence_execution

_FIELD_WIDTH = 30


def _field(label: str, value: str | None) -> str:
    if not value:
        value = "-"
    return f"{label + ':':<{_FIELD_WIDTH}} {value}"


def _action_plan_status_label(
    action_plan: ActionExecutionPlan,
    analysis: Analysis | None = None,
) -> str:
    if analysis is not None and analysis.domain == "sistema" and analysis.intent in {"atualizar", "otimizar"}:
        maintenance_policy = resolve_host_maintenance_action_policy(analysis.intent)
        if maintenance_policy.status == "FUTURE_MIGRATION_CANDIDATE":
            return "manutenção local do host"
    if action_plan.status == "SUPPORTED_NOW":
        return "suportada agora"
    if action_plan.status == "SUPPORTED_WITH_POLICY_BLOCK":
        return "bloqueio honesto agora"
    if action_plan.status == "FUTURE_MIGRATION_CANDIDATE":
        return "atendida pelo adaptador Fish"
    return "fora do recorte do núcleo Python"


def _action_plan_decision(action_plan: ActionExecutionPlan) -> str:
    if action_plan.executes_in_python:
        return "executar no Python"
    return "voltar ao Fish"


def _sequence_plan_status_label(sequence_plan: SequenceExecutionPlan) -> str:
    if any(action_plan.status == "SUPPORTED_WITH_POLICY_BLOCK" for action_plan in sequence_plan.action_plans):
        return "bloqueio honesto agora"
    if sequence_plan.executes_in_python:
        return "suportada agora"
    if any(action_plan.status == "FUTURE_MIGRATION_CANDIDATE" for action_plan in sequence_plan.action_plans):
        return "atendida pelo adaptador Fish"
    return "fora do recorte do núcleo Python"


def _sequence_plan_decision(sequence_plan: SequenceExecutionPlan) -> str:
    if sequence_plan.executes_in_python:
        return "executar no Python"
    return "voltar ao Fish"


def _render_sequence_plan(sequence_plan: SequenceExecutionPlan) -> list[str]:
    return [
        "Plano da sequência",
        _field("classificação", _sequence_plan_status_label(sequence_plan)),
        _field("decisão", _sequence_plan_decision(sequence_plan)),
        _field("motivo", sequence_plan.reason),
    ]


def _needs_host_profile(analyses: list[Analysis]) -> bool:
    return any(
        analysis.domain == "pacote"
        or (analysis.domain == "sistema" and analysis.intent in {"atualizar", "otimizar"})
        for analysis in analyses
    )


def _render_host_profile() -> list[str]:
    host_profile = detect_host_profile()
    return [
        "Perfil do host",
        _field("família linux", host_profile.linux_family_label),
        _field("mutabilidade", host_profile.mutability_label),
        _field("tier de suporte", host_profile.support_tier_label),
        _field("fronteira", host_profile.compatibility_frontier_label),
        _field("backends de pacote", host_profile.package_backends_label),
    ]


def _lacunas_label(analysis: Analysis) -> str:
    explicit_gap = analysis.entities.get("lacuna")
    if explicit_gap:
        return explicit_gap
    if analysis.status == "CONSISTENTE":
        return "-"
    if analysis.reason == "faltou a frase para inspecionar.":
        return "frase ausente"
    if analysis.status == "BLOQUEADA":
        return "alvo seguro"
    return "pedido fora do recorte"


def _render_action_report(action: PreparedAction, analysis: Analysis, action_plan: ActionExecutionPlan) -> list[str]:
    entities = analysis.entities
    package_policy = None
    maintenance_policy = None
    if analysis.domain == "pacote" and analysis.intent in {"procurar", "instalar", "remover"}:
        package_policy = resolve_package_action_policy(analysis.intent)
    if analysis.domain == "sistema" and analysis.intent in {"atualizar", "otimizar"}:
        maintenance_policy = resolve_host_maintenance_action_policy(analysis.intent)
    compatibility_label = "-"
    route_label = action_plan.route
    backend_label = action_plan.backend
    if package_policy is not None:
        compatibility_label = package_policy.compatibility_frontier_label
    if maintenance_policy is not None:
        compatibility_label = maintenance_policy.compatibility_frontier_label
        route_label = route_label or maintenance_policy.route
        backend_label = backend_label or maintenance_policy.backend_label
    lines = [
        f"Ação {action.index}",
        "Entrada",
        _field("trecho original", action.original_action),
        _field("trecho normalizado", action.normalized_action),
        "Enquadramento",
        _field("intenção", analysis.intent),
        _field("domínio", analysis.domain),
        "Entidades",
        _field("tipo", entities.get("tipo", "-")),
        _field("tipo de origem", entities.get("tipo_de_origem", "-")),
        _field("alvo principal", entities.get("alvo_principal", entities.get("destino", "-"))),
    ]
    if entities.get("arquivo_compactado"):
        lines.append(_field("arquivo compactado", entities["arquivo_compactado"]))
    if entities.get("origem"):
        lines.append(_field("origem", entities["origem"]))
    if entities.get("saida"):
        lines.append(_field("saída", entities["saida"]))
    if entities.get("referencia_local"):
        lines.append(_field("referência local", entities["referencia_local"]))
    if entities.get("destino"):
        lines.append(_field("destino", entities["destino"]))
    if entities.get("novo_nome"):
        lines.append(_field("novo nome", entities["novo_nome"]))
    if entities.get("localizacao_conversacional"):
        lines.append(_field("localização conversacional", entities["localizacao_conversacional"]))
    lines.extend(
        [
            "Diagnostico",
            _field("estado", analysis.status),
            _field("motivo", analysis.reason),
            _field("lacunas", _lacunas_label(analysis)),
            "Acao prevista",
            _field("resumo", analysis.summary),
            "Plano de execução",
            _field("classificação", _action_plan_status_label(action_plan, analysis)),
            _field("compatibilidade", compatibility_label),
            _field("rota suportada", route_label),
            _field("backend necessário", backend_label),
            _field("decisão", _action_plan_decision(action_plan)),
            _field("motivo do plano", action_plan.reason),
            "Observacoes",
            _field("itens", "; ".join(analysis.observations) if analysis.observations else "-"),
        ]
    )
    return lines


def render_dev_report(text: str) -> str:
    _phrase, actions, analyses = prepare_analyses(text)
    sequence_plan = plan_sequence_execution(analyses)
    action_plans = [plan_action_execution(analysis) for analysis in analyses]
    lines = [""]
    lines.extend(_render_sequence_plan(sequence_plan))
    if _needs_host_profile(analyses):
        lines.append("")
        lines.extend(_render_host_profile())
    if actions:
        lines.append("")
    for index, (action, analysis, action_plan) in enumerate(zip(actions, analyses, action_plans)):
        if index > 0:
            lines.append("")
        lines.extend(_render_action_report(action, analysis, action_plan))
    return "\n".join(lines)
