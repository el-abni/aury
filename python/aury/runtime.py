from __future__ import annotations

import json
import os
import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .analyzer import prepare_analyses
from .contracts import ActionExecutionPlan, Analysis, SequenceExecutionPlan, SupportedRuntimeRoute
from .host import (
    PackageExecutionPlan,
    build_package_execution_plan,
    package_no_results_message,
    package_noop_message,
    package_state_probe_missing_message,
    package_state_confirmation_message,
    package_success_message,
    resolve_package_action_policy,
)

UNSUPPORTED_EXIT = 120
_PYTHON_RUNTIME_BACKEND = "runtime Python"
RouteHandler = Callable[[Analysis, ActionExecutionPlan], int]
_PACKAGE_ROUTE_NAMES = {"package_search", "package_install", "package_remove"}
_PACKAGE_NO_RESULTS_MARKERS = (
    "no packages found",
    "no matches found",
    "no matching items found",
    "nenhum pacote encontrado",
    "nenhuma correspondencia encontrada",
    "nenhum item correspondente encontrado",
)


def _run(args: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True)


def _backend_missing(name: str) -> int:
    print(f"❌ backend '{name}' não está disponível")
    return 1


def _state_probe_missing(backend_label: str, probe_label: str) -> int:
    print(package_state_probe_missing_message(backend_label, probe_label))
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
        return f"a ação {index} é atendida pelo adaptador Fish nesta linha."

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
    output = proc.stdout.rstrip()
    if output:
        print(output)
    return 0


def _package_search_no_results(proc: subprocess.CompletedProcess[str]) -> bool:
    if proc.returncode not in {0, 1, 104}:
        return False

    combined_output = "\n".join(part.strip().lower() for part in (proc.stdout, proc.stderr) if part.strip())
    if not combined_output:
        return True

    return any(marker in combined_output for marker in _PACKAGE_NO_RESULTS_MARKERS)


def _probe_package_state(execution_plan: PackageExecutionPlan) -> bool | None:
    if not execution_plan.state_probe_command:
        return None

    proc = _run(execution_plan.state_probe_command)
    if execution_plan.policy.intent == "instalar":
        return proc.returncode == 0
    return proc.returncode != 0


def _run_package_search(execution_plan: PackageExecutionPlan) -> int:
    proc = _run(execution_plan.command)
    no_results = _package_search_no_results(proc)
    if proc.returncode != 0 and not no_results:
        return _backend_failed(execution_plan.policy.backend_label)

    if no_results:
        print(package_no_results_message(execution_plan.package_target, execution_plan.policy.backend_label))
        return 0

    output = proc.stdout.rstrip()
    if output:
        print(output)
        return 0

    print(package_no_results_message(execution_plan.package_target, execution_plan.policy.backend_label))
    return 0


def _run_package_mutation(execution_plan: PackageExecutionPlan) -> int:
    target = execution_plan.package_target
    intent = execution_plan.policy.intent
    backend_label = execution_plan.policy.backend_label

    initial_state = _probe_package_state(execution_plan)
    if initial_state is True:
        print(package_noop_message(intent, target))
        return 0

    proc = _run(execution_plan.command)
    if proc.returncode != 0:
        return _backend_failed(backend_label)

    final_state = _probe_package_state(execution_plan)
    if final_state is False:
        print(package_state_confirmation_message(intent, target, backend_label))
        return 1

    output = proc.stdout.rstrip()
    if output:
        print(output)
        return 0

    print(package_success_message(intent, target))
    return 0


def _execute_package_operation(intent: str, analysis: Analysis) -> int:
    execution_plan = build_package_execution_plan(intent, analysis.entities.get("alvo_principal", ""))
    if execution_plan.policy.block_message is not None:
        print(execution_plan.policy.block_message)
        return 1

    if intent == "procurar":
        return _run_package_search(execution_plan)

    return _run_package_mutation(execution_plan)


def _file_kind_label(kind: str) -> str:
    if kind == "pasta":
        return "a pasta"
    return "o arquivo"


def _created_path_success(kind: str, target: str) -> int:
    print(f"✅ Pronto, eu criei {_file_kind_label(kind)} '{target}'.")
    return 0


def _created_path_failure(kind: str, target: str) -> int:
    print(f"❌ não consegui criar {_file_kind_label(kind)} '{target}'")
    return 1


def _handle_file_create(analysis: Analysis, _action_plan: ActionExecutionPlan) -> int:
    target = _analysis_target(analysis)
    if not target or target == "-":
        return UNSUPPORTED_EXIT

    path = Path(target)
    try:
        parent = path.parent
        if str(parent) not in {"", "."}:
            parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            os.utime(path, None)
        else:
            path.touch()
    except OSError:
        return _created_path_failure("arquivo", target)

    return _created_path_success("arquivo", target)


def _handle_folder_create(analysis: Analysis, _action_plan: ActionExecutionPlan) -> int:
    target = _analysis_target(analysis)
    if not target or target == "-":
        return UNSUPPORTED_EXIT

    try:
        Path(target).mkdir(parents=True, exist_ok=True)
    except OSError:
        return _created_path_failure("pasta", target)

    return _created_path_success("pasta", target)


def _handle_package_search(analysis: Analysis, action_plan: ActionExecutionPlan) -> int:
    return _execute_package_operation("procurar", analysis)


def _handle_package_install(analysis: Analysis, _action_plan: ActionExecutionPlan) -> int:
    return _execute_package_operation("instalar", analysis)


def _handle_package_remove(analysis: Analysis, _action_plan: ActionExecutionPlan) -> int:
    return _execute_package_operation("remover", analysis)


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
    entity_type: str | None = None
    target: str | None = None
    requires_target: bool = False
    requires_backend: bool = True

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

        if self.entity_type is not None and analysis.entities.get("tipo") != self.entity_type:
            return False

        action_target = _analysis_target(analysis)
        if self.requires_target and (not action_target or action_target == "-"):
            return False

        if self.target is not None and action_target != self.target:
            return False

        return True

    def matches_plan(self, action_plan: ActionExecutionPlan) -> bool:
        return action_plan.route == self.supported_runtime_route.route

    def build_action_plan(self) -> ActionExecutionPlan:
        return ActionExecutionPlan.supported_now(
            self.supported_runtime_route,
            reason="runtime Python já conhece uma rota explícita e segura para essa ação.",
        )


_PLANNED_RUNTIME_ROUTE_SPECS = (
    _RuntimeRouteSpec(
        supported_runtime_route=SupportedRuntimeRoute(route="file_create", backend=_PYTHON_RUNTIME_BACKEND),
        handler=_handle_file_create,
        domain="arquivo",
        intent="criar",
        entity_type="arquivo",
        requires_target=True,
        requires_backend=False,
    ),
    _RuntimeRouteSpec(
        supported_runtime_route=SupportedRuntimeRoute(route="folder_create", backend=_PYTHON_RUNTIME_BACKEND),
        handler=_handle_folder_create,
        domain="arquivo",
        intent="criar",
        entity_type="pasta",
        requires_target=True,
        requires_backend=False,
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

_RUNTIME_ROUTE_SPECS = _PLANNED_RUNTIME_ROUTE_SPECS + (
    _RuntimeRouteSpec(
        supported_runtime_route=SupportedRuntimeRoute(route="package_search", backend="-"),
        handler=_handle_package_search,
        domain="pacote",
        intent="procurar",
        requires_target=True,
        requires_backend=False,
    ),
    _RuntimeRouteSpec(
        supported_runtime_route=SupportedRuntimeRoute(route="package_install", backend="-"),
        handler=_handle_package_install,
        domain="pacote",
        intent="instalar",
        requires_target=True,
        requires_backend=False,
    ),
    _RuntimeRouteSpec(
        supported_runtime_route=SupportedRuntimeRoute(route="package_remove", backend="-"),
        handler=_handle_package_remove,
        domain="pacote",
        intent="remover",
        requires_target=True,
        requires_backend=False,
    ),
)


def _route_spec_for_analysis(analysis: Analysis) -> _RuntimeRouteSpec | None:
    for route_spec in _PLANNED_RUNTIME_ROUTE_SPECS:
        if route_spec.matches_analysis(analysis):
            return route_spec
    return None


def _route_spec_for_plan(action_plan: ActionExecutionPlan) -> _RuntimeRouteSpec | None:
    for route_spec in _RUNTIME_ROUTE_SPECS:
        if route_spec.matches_plan(action_plan):
            return route_spec
    return None


def plan_action_execution(analysis: Analysis) -> ActionExecutionPlan:
    if analysis.status == "CONSISTENTE" and analysis.domain == "pacote" and analysis.intent in {"procurar", "instalar", "remover"}:
        package_policy = resolve_package_action_policy(analysis.intent)
        supported_runtime_route = SupportedRuntimeRoute(route=package_policy.route, backend=package_policy.backend_label)
        if package_policy.status == "SUPPORTED_WITH_POLICY_BLOCK":
            return ActionExecutionPlan.supported_with_policy_block(
                supported_runtime_route,
                reason=package_policy.reason,
            )
        return ActionExecutionPlan.supported_now(
            supported_runtime_route,
            reason=package_policy.reason,
        )

    route_spec = _route_spec_for_analysis(analysis)
    if route_spec is not None:
        return route_spec.build_action_plan()

    if analysis.status == "CONSISTENTE":
        return ActionExecutionPlan.future_migration_candidate(
            reason="a análise fechou com segurança, e essa ação é atendida pelo adaptador Fish nesta linha.",
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

    if any(action_plan.status == "SUPPORTED_WITH_POLICY_BLOCK" for action_plan in action_plans):
        return SequenceExecutionPlan(
            action_plans=action_plans,
            decision="EXECUTE_IN_PYTHON",
            reason="todas as ações ficam dentro do runtime Python atual, inclusive os bloqueios honestos exigidos pela política de host.",
        )

    return SequenceExecutionPlan(
        action_plans=action_plans,
        decision="EXECUTE_IN_PYTHON",
        reason="todas as ações têm rota explícita no runtime Python atual.",
    )


def _ensure_route_backend(route_spec: _RuntimeRouteSpec) -> int:
    if not route_spec.requires_backend:
        return 0
    if shutil.which(route_spec.backend) is None:
        return _backend_missing(route_spec.backend)
    return 0


def _ensure_package_backends(analysis: Analysis) -> int:
    execution_plan = build_package_execution_plan(analysis.intent, _analysis_target(analysis))
    if execution_plan.policy.block_message is not None:
        return 0
    for required_command in execution_plan.required_commands:
        if shutil.which(required_command) is None:
            return _backend_missing(required_command)
    for required_command in execution_plan.state_probe_required_commands:
        if shutil.which(required_command) is None:
            return _state_probe_missing(execution_plan.policy.backend_label, execution_plan.state_probe_label or required_command)
    return 0


def _ensure_analysis_backend(analysis: Analysis, route_spec: _RuntimeRouteSpec, action_plan: ActionExecutionPlan) -> int:
    if action_plan.route in _PACKAGE_ROUTE_NAMES:
        return _ensure_package_backends(analysis)
    return _ensure_route_backend(route_spec)


def _execute_supported_analysis(analysis: Analysis, action_plan: ActionExecutionPlan | None = None) -> int:
    resolved_plan = action_plan or plan_action_execution(analysis)
    if not resolved_plan.executes_in_python or resolved_plan.route is None:
        return UNSUPPORTED_EXIT

    route_spec = _route_spec_for_plan(resolved_plan)
    if route_spec is None:
        return UNSUPPORTED_EXIT

    backend_status = _ensure_analysis_backend(analysis, route_spec, resolved_plan)
    if backend_status != 0:
        return backend_status

    return route_spec.handler(analysis, resolved_plan)


def _can_execute_multi_action(sequence_plan: SequenceExecutionPlan) -> bool:
    return len(sequence_plan.action_plans) > 1 and sequence_plan.executes_in_python


def _preflight_multi_action(analyses: list[Analysis], sequence_plan: SequenceExecutionPlan) -> int:
    if not sequence_plan.executes_in_python:
        return UNSUPPORTED_EXIT

    for analysis, action_plan in zip(analyses, sequence_plan.action_plans):
        route_spec = _route_spec_for_plan(action_plan)
        if route_spec is None:
            return UNSUPPORTED_EXIT
        status = _ensure_analysis_backend(analysis, route_spec, action_plan)
        if status != 0:
            return status
    return 0


def _execute_multi_action(analyses: list[Analysis], sequence_plan: SequenceExecutionPlan) -> int:
    if not _can_execute_multi_action(sequence_plan):
        return UNSUPPORTED_EXIT

    preflight_status = _preflight_multi_action(analyses, sequence_plan)
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
