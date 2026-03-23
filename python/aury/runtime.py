from __future__ import annotations

import json
import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from typing import Sequence

from .analyzer import prepare_analyses
from .contracts import ActionExecutionPlan, Analysis, SequenceExecutionPlan, SupportedRuntimeRoute

UNSUPPORTED_EXIT = 120
RouteHandler = Callable[[Analysis, ActionExecutionPlan], int]


def _run(args: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True)


def _backend_missing(name: str) -> int:
    print(f"❌ backend '{name}' não está disponível")
    return 1


def _backend_failed(name: str) -> int:
    print(f"❌ backend '{name}' retornou erro operacional")
    return 1


def _analysis_target(analysis: Analysis) -> str:
    return analysis.entities.get("alvo_principal", "")


def _analysis_gap(analysis: Analysis) -> str:
    return analysis.entities.get("lacuna", "").strip()


def _fish_fallback_reason(analysis: Analysis) -> str:
    gap = _analysis_gap(analysis)
    if analysis.status == "BLOQUEADA":
        if gap:
            return f"a análise ficou bloqueada por lacuna explícita: {gap}."
        return "a análise ficou bloqueada antes da execução direta no runtime Python."
    if analysis.status == "NAO_ENQUADRADA":
        return "a ação ficou fora do recorte reconhecido com segurança para execução direta no runtime Python."
    return "a análise não fechou com segurança para execução direta no runtime Python."


def _sequence_return_reason(index: int, analysis: Analysis, action_plan: ActionExecutionPlan) -> str:
    if action_plan.status == "FUTURE_MIGRATION_CANDIDATE":
        return f"a ação {index} ainda depende do adaptador Fish."

    gap = _analysis_gap(analysis)
    if analysis.status == "BLOQUEADA":
        if gap:
            return f"a ação {index} ficou bloqueada por lacuna explícita: {gap}."
        return f"a ação {index} ficou bloqueada antes da execução direta no runtime Python."
    if analysis.status == "NAO_ENQUADRADA":
        return f"a ação {index} ficou fora do recorte reconhecido com segurança."
    return f"a ação {index} não fechou com segurança no runtime Python."


def _run_and_print(backend: str, args: Sequence[str]) -> int:
    proc = _run(args)
    if proc.returncode != 0:
        return _backend_failed(backend)
    print(proc.stdout.rstrip())
    return 0


def _handle_package_search(analysis: Analysis, action_plan: ActionExecutionPlan) -> int:
    if action_plan.backend is None:
        return UNSUPPORTED_EXIT
    target = analysis.entities.get("alvo_principal", "")
    return _run_and_print(action_plan.backend, [action_plan.backend, "-Ss", "--", target])


def _handle_network_ip(_analysis: Analysis, action_plan: ActionExecutionPlan) -> int:
    if action_plan.backend is None:
        return UNSUPPORTED_EXIT
    return _run_and_print(action_plan.backend, [action_plan.backend, "-brief", "address"])


def _handle_network_ping(_analysis: Analysis, action_plan: ActionExecutionPlan) -> int:
    if action_plan.backend is None:
        return UNSUPPORTED_EXIT
    return _run_and_print(action_plan.backend, [action_plan.backend, "-c", "2", "--", "8.8.8.8"])


def _handle_network_speedtest(_analysis: Analysis, action_plan: ActionExecutionPlan) -> int:
    if action_plan.backend is None:
        return UNSUPPORTED_EXIT
    proc = _run([action_plan.backend, "--json"])
    if proc.returncode != 0:
        return _backend_failed(action_plan.backend)
    try:
        payload = json.loads(proc.stdout)
        if isinstance(payload, list):
            payload = payload[0]
        ping = payload["ping"]
        download = payload["download"]
        upload = payload["upload"]
        jitter = payload["jitter"]
    except Exception:
        print("❌ não consegui ler o retorno do librespeed-cli com confiança")
        return 1
    print("✅ velocidade da internet")
    print(f"ping: {ping} ms")
    print(f"download: {download} Mbps")
    print(f"upload: {upload} Mbps")
    print(f"jitter: {jitter} ms")
    return 0


def _handle_system_cpu(_analysis: Analysis, action_plan: ActionExecutionPlan) -> int:
    if action_plan.backend is None:
        return UNSUPPORTED_EXIT
    return _run_and_print(action_plan.backend, [action_plan.backend])


def _handle_system_memory(_analysis: Analysis, action_plan: ActionExecutionPlan) -> int:
    if action_plan.backend is None:
        return UNSUPPORTED_EXIT
    return _run_and_print(action_plan.backend, [action_plan.backend, "-h"])


def _handle_system_disk(_analysis: Analysis, action_plan: ActionExecutionPlan) -> int:
    if action_plan.backend is None:
        return UNSUPPORTED_EXIT
    return _run_and_print(action_plan.backend, [action_plan.backend, "-h"])


def _handle_system_status(_analysis: Analysis, action_plan: ActionExecutionPlan) -> int:
    if action_plan.backend is None:
        return UNSUPPORTED_EXIT
    return _run_and_print(action_plan.backend, [action_plan.backend])


def _handle_system_gpu(_analysis: Analysis, action_plan: ActionExecutionPlan) -> int:
    if action_plan.backend is None:
        return UNSUPPORTED_EXIT
    proc = _run([action_plan.backend])
    if proc.returncode != 0:
        return _backend_failed(action_plan.backend)
    lines = [line for line in proc.stdout.splitlines() if "VGA" in line or "3D controller" in line]
    print("\n".join(lines).rstrip())
    return 0


@dataclass(frozen=True)
class _RuntimeRouteSpec:
    supported_runtime_route: SupportedRuntimeRoute
    handler: RouteHandler
    domain: str
    intent: str | None = None
    target: str | None = None
    requires_target: bool = False

    @property
    def route(self) -> str:
        return self.supported_runtime_route.route

    @property
    def backend(self) -> str:
        return self.supported_runtime_route.backend

    def matches_analysis(self, analysis: Analysis) -> bool:
        if analysis.status != "CONSISTENTE":
            return False

        if analysis.domain != self.domain:
            return False

        if self.intent is not None and analysis.intent != self.intent:
            return False

        action_target = _analysis_target(analysis)
        if self.requires_target and (not action_target or action_target == "-"):
            return False

        if self.target is not None and action_target != self.target:
            return False

        return True

    def matches_plan(self, action_plan: ActionExecutionPlan) -> bool:
        return action_plan.matches_supported_runtime_route(self.supported_runtime_route)

    def build_action_plan(self) -> ActionExecutionPlan:
        return ActionExecutionPlan.supported_now(
            self.supported_runtime_route,
            reason="runtime Python já conhece uma rota explícita e segura para essa ação.",
        )


_RUNTIME_ROUTE_SPECS = (
    _RuntimeRouteSpec(
        supported_runtime_route=SupportedRuntimeRoute(route="package_search", backend="pacman"),
        handler=_handle_package_search,
        domain="pacote",
        intent="procurar",
        requires_target=True,
    ),
    _RuntimeRouteSpec(
        supported_runtime_route=SupportedRuntimeRoute(route="network_ip", backend="ip"),
        handler=_handle_network_ip,
        domain="rede",
        target="ip",
    ),
    _RuntimeRouteSpec(
        supported_runtime_route=SupportedRuntimeRoute(route="network_ping", backend="ping"),
        handler=_handle_network_ping,
        domain="rede",
        target="internet",
    ),
    _RuntimeRouteSpec(
        supported_runtime_route=SupportedRuntimeRoute(route="network_speedtest", backend="librespeed-cli"),
        handler=_handle_network_speedtest,
        domain="rede",
        target="velocidade da internet",
    ),
    _RuntimeRouteSpec(
        supported_runtime_route=SupportedRuntimeRoute(route="system_cpu", backend="lscpu"),
        handler=_handle_system_cpu,
        domain="sistema",
        target="cpu",
    ),
    _RuntimeRouteSpec(
        supported_runtime_route=SupportedRuntimeRoute(route="system_memory", backend="free"),
        handler=_handle_system_memory,
        domain="sistema",
        target="memória",
    ),
    _RuntimeRouteSpec(
        supported_runtime_route=SupportedRuntimeRoute(route="system_disk", backend="df"),
        handler=_handle_system_disk,
        domain="sistema",
        target="disco",
    ),
    _RuntimeRouteSpec(
        supported_runtime_route=SupportedRuntimeRoute(route="system_status", backend="uptime"),
        handler=_handle_system_status,
        domain="sistema",
        target="status do sistema",
    ),
    _RuntimeRouteSpec(
        supported_runtime_route=SupportedRuntimeRoute(route="system_gpu", backend="lspci"),
        handler=_handle_system_gpu,
        domain="sistema",
        target="gpu",
    ),
)


def _route_spec_for_analysis(analysis: Analysis) -> _RuntimeRouteSpec | None:
    for route_spec in _RUNTIME_ROUTE_SPECS:
        if route_spec.matches_analysis(analysis):
            return route_spec
    return None


def _route_spec_for_plan(action_plan: ActionExecutionPlan) -> _RuntimeRouteSpec | None:
    for route_spec in _RUNTIME_ROUTE_SPECS:
        if route_spec.matches_plan(action_plan):
            return route_spec
    return None


def plan_action_execution(analysis: Analysis) -> ActionExecutionPlan:
    route_spec = _route_spec_for_analysis(analysis)
    if route_spec is not None:
        return route_spec.build_action_plan()

    if analysis.status == "CONSISTENTE":
        return ActionExecutionPlan.future_migration_candidate(
            reason="a análise fechou com segurança, mas essa ação ainda depende do adaptador Fish.",
        )

    return ActionExecutionPlan.fish_fallback(
        reason=_fish_fallback_reason(analysis),
    )


def plan_sequence_execution(analyses: list[Analysis]) -> SequenceExecutionPlan:
    action_plans = tuple(plan_action_execution(analysis) for analysis in analyses)
    if not action_plans:
        return SequenceExecutionPlan(reason="não há ações preparadas para executar.")

    for index, (analysis, action_plan) in enumerate(zip(analyses, action_plans), start=1):
        if action_plan.executes_in_python:
            continue
        return SequenceExecutionPlan(
            action_plans=action_plans,
            decision="RETURN_TO_FISH",
            reason=_sequence_return_reason(index, analysis, action_plan),
        )

    return SequenceExecutionPlan(
        action_plans=action_plans,
        decision="EXECUTE_IN_PYTHON",
        reason="todas as ações têm rota explícita no runtime Python atual.",
    )


def _ensure_route_backend(route_spec: _RuntimeRouteSpec) -> int:
    if shutil.which(route_spec.backend) is None:
        return _backend_missing(route_spec.backend)
    return 0


def _execute_supported_analysis(analysis: Analysis, action_plan: ActionExecutionPlan | None = None) -> int:
    resolved_plan = action_plan or plan_action_execution(analysis)
    if not resolved_plan.executes_in_python or resolved_plan.route is None:
        return UNSUPPORTED_EXIT

    route_spec = _route_spec_for_plan(resolved_plan)
    if route_spec is None:
        return UNSUPPORTED_EXIT

    backend_status = _ensure_route_backend(route_spec)
    if backend_status != 0:
        return backend_status

    return route_spec.handler(analysis, resolved_plan)


def _can_execute_multi_action(sequence_plan: SequenceExecutionPlan) -> bool:
    return len(sequence_plan.action_plans) > 1 and sequence_plan.executes_in_python


def _preflight_multi_action(sequence_plan: SequenceExecutionPlan) -> int:
    if not sequence_plan.executes_in_python:
        return UNSUPPORTED_EXIT

    for action_plan in sequence_plan.action_plans:
        route_spec = _route_spec_for_plan(action_plan)
        if route_spec is None:
            return UNSUPPORTED_EXIT
        status = _ensure_route_backend(route_spec)
        if status != 0:
            return status
    return 0


def _execute_multi_action(analyses: list[Analysis], sequence_plan: SequenceExecutionPlan) -> int:
    if not _can_execute_multi_action(sequence_plan):
        return UNSUPPORTED_EXIT

    preflight_status = _preflight_multi_action(sequence_plan)
    if preflight_status != 0:
        return preflight_status

    for analysis, action_plan in zip(analyses, sequence_plan.action_plans):
        status = _execute_supported_analysis(analysis, action_plan)
        if status != 0:
            return status
    return 0


def execute(text: str) -> int:
    _phrase, _actions, analyses = prepare_analyses(text)
    sequence_plan = plan_sequence_execution(analyses)

    if not sequence_plan.action_plans:
        return UNSUPPORTED_EXIT

    if len(analyses) == 1:
        return _execute_supported_analysis(analyses[0], sequence_plan.action_plans[0])

    return _execute_multi_action(analyses, sequence_plan)
