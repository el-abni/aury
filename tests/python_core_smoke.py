#!/usr/bin/env python3
from __future__ import annotations

import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from aury.analyzer import prepare_analyses, prepare_analysis
from aury.contracts import ActionExecutionPlan, SupportedRuntimeRoute
from aury.pipeline import prepare_text
from aury.runtime import plan_action_execution, plan_sequence_execution
from aury.sensitive_tokens import protect_sensitive_tokens, restore_sensitive_tokens

ENV = os.environ.copy()
ENV["PYTHONPATH"] = str(ROOT / "python")
ENV["AURY_SHARE_DIR"] = str(ROOT)


def run(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged_env = ENV.copy()
    if env:
        merged_env.update(env)
    return subprocess.run([sys.executable, "-m", "aury", *args], cwd=ROOT, env=merged_env, text=True, capture_output=True)


def assert_in(output: str, expected: str) -> None:
    if expected not in output:
        raise AssertionError(f"esperava encontrar {expected!r} em:\n{output}")


def write_stub(bin_dir: Path, name: str, body: str) -> None:
    path = bin_dir / name
    path.write_text(body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def test_help() -> None:
    proc = run("ajuda")
    assert proc.returncode == 0
    assert_in(proc.stdout, "💜 Aury")


def test_version() -> None:
    proc = run("--version")
    assert proc.returncode == 0
    assert_in(proc.stdout, "💜 Aury")


def test_dev_remove_pkg() -> None:
    proc = run("dev", "remover", "vlc")
    assert proc.returncode == 0
    assert_in(proc.stdout, "domínio:")
    assert_in(proc.stdout, "pacote")
    assert_in(proc.stdout, "Remover 'vlc'.")


def test_dev_chain() -> None:
    phrase = "copie a pasta Aury que fica em Documentos para Downloads e renomeie ela para Aury-backup"
    proc = run("dev", *phrase.split())
    assert proc.returncode == 0
    assert_in(proc.stdout, "origem:")
    assert_in(proc.stdout, "Documentos/Aury")
    assert_in(proc.stdout, "novo nome:")
    assert_in(proc.stdout, "Downloads/Aury-backup")


def test_runtime_speedtest() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        bin_dir = Path(tmp)
        write_stub(
            bin_dir,
            "librespeed-cli",
            "#!/usr/bin/env bash\nprintf '%s\\n' '{\"ping\":12.3,\"download\":245.67,\"upload\":58.9,\"jitter\":0.45}'\n",
        )
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}"}
        proc = run("velocidade", "da", "internet", env=env)
        assert proc.returncode == 0
        assert_in(proc.stdout, "download: 245.67 Mbps")


def test_runtime_ping() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        bin_dir = Path(tmp)
        write_stub(bin_dir, "ping", "#!/usr/bin/env bash\necho 'PING_STUB -c 2 -- 8.8.8.8'\n")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}"}
        proc = run("testar", "internet", env=env)
        assert proc.returncode == 0
        assert_in(proc.stdout, "PING_STUB")


def test_runtime_package_search() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        bin_dir = Path(tmp)
        write_stub(bin_dir, "pacman", "#!/usr/bin/env bash\necho 'PACMAN_SEARCH_STUB -Ss -- steam'\n")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}"}
        proc = run("procurar", "steam", env=env)
        assert proc.returncode == 0
        assert_in(proc.stdout, "PACMAN_SEARCH_STUB")


def test_runtime_gpu() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        bin_dir = Path(tmp)
        write_stub(
            bin_dir,
            "lspci",
            "#!/usr/bin/env bash\nprintf '%s\\n' '00:02.0 VGA compatible controller: GPU STUB' '00:14.0 USB controller: USB STUB'\n",
        )
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}"}
        proc = run("ver", "gpu", env=env)
        assert proc.returncode == 0
        assert_in(proc.stdout, "GPU STUB")
        if "USB STUB" in proc.stdout:
            raise AssertionError("handler de GPU não deveria imprimir linhas fora do filtro esperado")


def test_runtime_multi_action_supported() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        bin_dir = Path(tmp)
        write_stub(bin_dir, "ip", "#!/usr/bin/env bash\necho 'IP_MULTI_STUB -brief address'\n")
        write_stub(bin_dir, "uptime", "#!/usr/bin/env bash\necho 'UPTIME_MULTI_STUB'\n")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}"}
        proc = run("ver", "ip", "e", "status", env=env)
        assert proc.returncode == 0
        assert_in(proc.stdout, "IP_MULTI_STUB")
        assert_in(proc.stdout, "UPTIME_MULTI_STUB")


def test_runtime_multi_action_unsupported_no_partial() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        bin_dir = Path(tmp)
        write_stub(bin_dir, "pacman", "#!/usr/bin/env bash\necho 'PACMAN_MULTI_STUB'\n")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}"}
        proc = run("procurar", "steam", "e", "remover", "vlc", env=env)
        assert proc.returncode == 120
        if "PACMAN_MULTI_STUB" in proc.stdout:
            raise AssertionError("runtime multi-ação executou parcialmente uma sequência que deveria cair em fallback")


def test_sensitive_tokens_contract() -> None:
    original = ["teste.tar.gz", "Downloads/token", "google.com"]
    protected, mapping = protect_sensitive_tokens(original)
    if [item.token_type for item in mapping] != ["archive", "path", "host"]:
        raise AssertionError(f"tipagem inesperada: {[item.token_type for item in mapping]!r}")
    if restore_sensitive_tokens(protected, mapping) != original:
        raise AssertionError("restauração de tokens sensíveis não retornou a sequência original")


def test_pipeline_prepare_text() -> None:
    phrase, actions = prepare_text("Aury, procurar steam e remover vlc")
    if phrase.original_text != "procurar steam e remover vlc":
        raise AssertionError(f"frase original inesperada: {phrase.original_text!r}")
    if phrase.normalized_text != "procurar steam e remover vlc":
        raise AssertionError(f"frase normalizada inesperada: {phrase.normalized_text!r}")
    if [action.original_action for action in actions] != ["procurar steam", "remover vlc"]:
        raise AssertionError(f"split inesperado: {[action.original_action for action in actions]!r}")

    protected_phrase, _ = prepare_text("extraia teste.tar.gz para Downloads/token 123")
    if [item.token_type for item in protected_phrase.protected_tokens] != ["archive", "path"]:
        raise AssertionError(
            f"tokens protegidos inesperados: {[item.token_type for item in protected_phrase.protected_tokens]!r}"
        )
    assert_in(protected_phrase.normalized_text, "teste.tar.gz")
    assert_in(protected_phrase.normalized_text, "Downloads/token")


def test_prepare_analysis_uses_prepared_action() -> None:
    phrase, action, analysis = prepare_analysis("Aury, remover vlc")
    if phrase.original_text != "remover vlc":
        raise AssertionError(f"frase preparada inesperada: {phrase.original_text!r}")
    if action.original_action != "remover vlc":
        raise AssertionError(f"ação preparada inesperada: {action.original_action!r}")
    if analysis.original_text != action.original_action:
        raise AssertionError("a análise não está partindo do trecho original da ação preparada")
    if analysis.normalized_text != action.normalized_action:
        raise AssertionError("a análise não está partindo do trecho normalizado da ação preparada")
    if analysis.summary != "Remover 'vlc'.":
        raise AssertionError(f"resumo inesperado: {analysis.summary!r}")


def test_prepare_analyses_multiple_actions() -> None:
    phrase, actions, analyses = prepare_analyses("Aury, procurar steam e remover vlc")
    if phrase.original_text != "procurar steam e remover vlc":
        raise AssertionError(f"frase preparada inesperada: {phrase.original_text!r}")
    if [action.original_action for action in actions] != ["procurar steam", "remover vlc"]:
        raise AssertionError(f"ações preparadas inesperadas: {[action.original_action for action in actions]!r}")
    if [analysis.summary for analysis in analyses] != ["Procurar 'steam'.", "Remover 'vlc'."]:
        raise AssertionError(f"análises inesperadas: {[analysis.summary for analysis in analyses]!r}")


def test_action_execution_plan_supported_now() -> None:
    _phrase, _action, analysis = prepare_analysis("ver ip")
    action_plan = plan_action_execution(analysis)
    if action_plan.status != "SUPPORTED_NOW":
        raise AssertionError(f"classificação inesperada: {action_plan.status!r}")
    if action_plan.route != "network_ip":
        raise AssertionError(f"rota inesperada: {action_plan.route!r}")
    if action_plan.backend != "ip":
        raise AssertionError(f"backend inesperado: {action_plan.backend!r}")
    if not action_plan.executes_in_python:
        raise AssertionError("a ação suportada deveria executar no runtime Python")


def test_action_execution_plan_supported_runtime_route_contract() -> None:
    supported_runtime_route = SupportedRuntimeRoute(route="network_ip", backend="ip")
    action_plan = ActionExecutionPlan.supported_now(
        supported_runtime_route,
        reason="runtime Python já conhece uma rota explícita e segura para essa ação.",
    )
    if action_plan.route != "network_ip":
        raise AssertionError(f"rota inesperada: {action_plan.route!r}")
    if action_plan.backend != "ip":
        raise AssertionError(f"backend inesperado: {action_plan.backend!r}")
    if not action_plan.matches_supported_runtime_route(supported_runtime_route):
        raise AssertionError("o plano suportado não reconheceu a rota compartilhada")


def test_action_execution_plan_future_migration_candidate() -> None:
    _phrase, _action, analysis = prepare_analysis("remover vlc")
    action_plan = plan_action_execution(analysis)
    if action_plan.status != "FUTURE_MIGRATION_CANDIDATE":
        raise AssertionError(f"classificação inesperada: {action_plan.status!r}")
    if action_plan.route is not None:
        raise AssertionError(f"rota não deveria existir: {action_plan.route!r}")
    if action_plan.backend is not None:
        raise AssertionError(f"backend não deveria existir: {action_plan.backend!r}")
    if action_plan.executes_in_python:
        raise AssertionError("a ação candidata a migração futura ainda deve voltar ao Fish")


def test_sequence_execution_plan_supported_now() -> None:
    _phrase, _actions, analyses = prepare_analyses("ver ip e status")
    sequence_plan = plan_sequence_execution(analyses)
    if sequence_plan.decision != "EXECUTE_IN_PYTHON":
        raise AssertionError(f"decisão inesperada: {sequence_plan.decision!r}")
    if len(sequence_plan.action_plans) != 2:
        raise AssertionError(f"plano de sequência inesperado: {len(sequence_plan.action_plans)!r}")


def test_sequence_execution_plan_returns_to_fish() -> None:
    _phrase, _actions, analyses = prepare_analyses("procurar steam e remover vlc")
    sequence_plan = plan_sequence_execution(analyses)
    if sequence_plan.decision != "RETURN_TO_FISH":
        raise AssertionError(f"decisão inesperada: {sequence_plan.decision!r}")
    if sequence_plan.action_plans[1].status != "FUTURE_MIGRATION_CANDIDATE":
        raise AssertionError(f"classificação inesperada: {sequence_plan.action_plans[1].status!r}")


def test_dev_multiple_actions() -> None:
    phrase = "procurar steam e remover vlc"
    proc = run("dev", *phrase.split())
    assert proc.returncode == 0
    assert_in(proc.stdout, "Plano da sequência")
    assert_in(proc.stdout, "Ação 1")
    assert_in(proc.stdout, "Ação 2")
    assert_in(proc.stdout, "candidata a migração futura")
    assert_in(proc.stdout, "voltar ao Fish")
    assert_in(proc.stdout, "resumo:                        Procurar 'steam'.")
    assert_in(proc.stdout, "resumo:                        Remover 'vlc'.")


def main() -> int:
    tests = [
        test_help,
        test_version,
        test_dev_remove_pkg,
        test_dev_chain,
        test_runtime_speedtest,
        test_runtime_ping,
        test_runtime_package_search,
        test_runtime_gpu,
        test_runtime_multi_action_supported,
        test_runtime_multi_action_unsupported_no_partial,
        test_sensitive_tokens_contract,
        test_pipeline_prepare_text,
        test_prepare_analysis_uses_prepared_action,
        test_prepare_analyses_multiple_actions,
        test_action_execution_plan_supported_now,
        test_action_execution_plan_supported_runtime_route_contract,
        test_action_execution_plan_future_migration_candidate,
        test_sequence_execution_plan_supported_now,
        test_sequence_execution_plan_returns_to_fish,
        test_dev_multiple_actions,
    ]
    for test in tests:
        test()
    print(f"python_core_smoke: ok ({len(tests)} testes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
