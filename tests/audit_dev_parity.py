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

from aury.analyzer import prepare_analyses
from aury.runtime import plan_sequence_execution


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def ok(message: str) -> None:
    print(f"OK: {message}")


def write_stub(bin_dir: Path, name: str, body: str) -> None:
    path = bin_dir / name
    path.write_text(body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def dev_executor(phrase: str) -> tuple[str, str]:
    _phrase, _actions, analyses = prepare_analyses(phrase)
    sequence_plan = plan_sequence_execution(analyses)
    action_plan = sequence_plan.action_plans[0]
    executor = "python" if sequence_plan.executes_in_python else "fish"
    route = action_plan.route or "-"
    return executor, route


def run_fish(args: list[str], *, env: dict[str, str] | None = None, cwd: Path | None = None) -> str:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    proc = subprocess.run(
        ["fish", "-c", f"source '{ROOT / 'bin' / 'aury.fish'}'; aury $argv", "--", *args],
        cwd=cwd or ROOT,
        env=merged_env,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        fail(f"execução Fish falhou para {args!r}: {proc.stderr or proc.stdout}")
    return proc.stdout


def run_fish_result(
    args: list[str],
    *,
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    proc = subprocess.run(
        ["fish", "-c", f"source '{ROOT / 'bin' / 'aury.fish'}'; aury $argv", "--", *args],
        cwd=cwd or ROOT,
        env=merged_env,
        text=True,
        capture_output=True,
        check=False,
    )
    return proc


def run_fish_public_error(args: list[str], *, env: dict[str, str] | None = None, cwd: Path | None = None) -> str:
    proc = run_fish_result(args, env=env, cwd=cwd)
    if proc.returncode != 0:
        return proc.stdout
    fail(f"execução Fish deveria falhar publicamente para {args!r}, mas saiu com 0")


def assert_executor(phrase: str, expected_executor: str) -> str:
    actual_executor, route = dev_executor(phrase)
    if actual_executor != expected_executor:
        fail(f"plano de 'aury dev' para {phrase!r} deveria usar {expected_executor}, mas retornou {actual_executor}")
    return route


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        bin_dir = Path(tmp) / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)

        write_stub(bin_dir, "pacman", "#!/usr/bin/env bash\nprintf 'PACMAN_STUB %s\\n' \"$*\"\n")
        write_stub(bin_dir, "ip", "#!/usr/bin/env bash\nprintf 'IP_STUB %s\\n' \"$*\"\n")
        write_stub(bin_dir, "ping", "#!/usr/bin/env bash\nprintf 'PING_STUB %s\\n' \"$*\"\n")
        write_stub(
            bin_dir,
            "librespeed-cli",
            "#!/usr/bin/env bash\nprintf '{\"ping\":11.2,\"download\":123.4,\"upload\":56.7,\"jitter\":1.8}'\n",
        )
        path_env = {"PATH": f"{bin_dir}:{os.environ['PATH']}"}

        route = assert_executor("procurar steam", "python")
        output = run_fish(["procurar", "steam"], env=path_env)
        if "PACMAN_STUB -Ss -- steam" not in output:
            fail("modo normal não observou a rota Python esperada para procurar pacote")
        ok(f"procurar steam alinhado em Python ({route})")

        route = assert_executor("ver ip", "python")
        output = run_fish(["ver", "ip"], env=path_env)
        if "IP_STUB -brief address" not in output:
            fail("modo normal não observou a rota Python esperada para ver ip")
        ok(f"ver ip alinhado em Python ({route})")

        route = assert_executor("testar internet", "python")
        output = run_fish(["testar", "internet"], env=path_env)
        if "PING_STUB -c 2 -- 8.8.8.8" not in output:
            fail("modo normal não observou a rota Python esperada para testar internet")
        ok(f"testar internet alinhado em Python ({route})")

        route = assert_executor("velocidade da internet", "python")
        output = run_fish(["velocidade", "da", "internet"], env=path_env)
        if "download: 123.4 Mbps" not in output:
            fail("modo normal não observou a rota Python esperada para velocidade da internet")
        ok(f"velocidade da internet alinhada em Python ({route})")

        assert_executor("abra o arquivo relatorio.pdf", "fish")
        output = run_fish_public_error(["abra", "o", "arquivo", "relatorio.pdf"], env=path_env)
        if "não consegui entender esse pedido com segurança" not in output:
            fail("modo normal não preservou o fallback honesto para pedido fora do recorte")
        ok("abra o arquivo relatorio.pdf alinhado em Fish")

        assert_executor("remover ela", "fish")
        output = run_fish_public_error(["remover", "ela"], env=path_env)
        if "não vou remover nada sem um alvo explícito." not in output:
            fail("modo normal não preservou o bloqueio destrutivo explícito")
        ok("remover ela alinhado em Fish")

    with tempfile.TemporaryDirectory() as tmp:
        bin_dir = Path(tmp) / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "sudo", "#!/usr/bin/env bash\n\"$@\"\n")
        write_stub(
            bin_dir,
            "pacman",
            "#!/usr/bin/env bash\nif [ \"$1\" = \"-Si\" ]; then\n  exit 1\nfi\nprintf 'PACMAN_FALLBACK %s\\n' \"$*\"\n",
        )
        write_stub(
            bin_dir,
            "paru",
            "#!/usr/bin/env bash\nif [ \"$1\" = \"-Si\" ]; then\n  exit 0\nfi\nprintf 'PARU_FALLBACK %s\\n' \"$*\"\n",
        )
        path_env = {"PATH": f"{bin_dir}:{os.environ['PATH']}"}

        assert_executor("instalar firefox", "fish")
        output = run_fish(["instalar", "firefox"], env=path_env)
        if "PARU_FALLBACK -S --needed -- firefox" not in output:
            fail("modo normal não caiu no adaptador Fish para instalar firefox")
        ok("instalar firefox alinhado em Fish")

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        assert_executor("criar arquivo teste.txt", "python")
        output = run_fish(["criar", "arquivo", "teste.txt"], cwd=workdir)
        if "eu criei o arquivo 'teste.txt'" not in output or not (workdir / "teste.txt").is_file():
            fail("modo normal não observou a rota Python esperada para criar arquivo")
        ok("criar arquivo teste.txt alinhado em Python")

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        (workdir / "Downloads").mkdir(parents=True, exist_ok=True)
        assert_executor("criar pasta Relatorios em Downloads", "python")
        output = run_fish(["criar", "pasta", "Relatorios", "em", "Downloads"], cwd=workdir)
        if "eu criei a pasta 'Downloads/Relatorios'" not in output or not (workdir / "Downloads" / "Relatorios").is_dir():
            fail("modo normal não observou a rota Python esperada para criar pasta localizada")
        ok("criar pasta Relatorios em Downloads alinhado em Python")

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        bin_dir = workdir / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        (workdir / "teste.txt").write_text("ok\n", encoding="utf-8")
        write_stub(
            bin_dir,
            "zip",
            "#!/usr/bin/env bash\narchive=\"$2\"\n: > \"$archive\"\n",
        )
        path_env = {"PATH": f"{bin_dir}:{os.environ['PATH']}"}

        assert_executor("compactar arquivo teste.txt para saida.zip", "fish")
        output = run_fish(["compactar", "arquivo", "teste.txt", "para", "saida.zip"], env=path_env, cwd=workdir)
        if "eu compactei 'teste.txt' em 'saida.zip'" not in output or not (workdir / "saida.zip").is_file():
            fail("modo normal não caiu no adaptador Fish para compactar arquivo em zip")
        ok("compactar arquivo teste.txt para saida.zip alinhado em Fish")

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        bin_dir = workdir / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        (workdir / "projetos").mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "tar", "#!/usr/bin/env bash\narchive=\"$2\"\n: > \"$archive\"\n")
        path_env = {"PATH": f"{bin_dir}:{os.environ['PATH']}"}

        assert_executor("compactar pasta projetos/ para saida.tar.gz", "fish")
        output = run_fish(["compactar", "pasta", "projetos/", "para", "saida.tar.gz"], env=path_env, cwd=workdir)
        if "eu compactei 'projetos/' em 'saida.tar.gz'" not in output or not (workdir / "saida.tar.gz").is_file():
            fail("modo normal não caiu no adaptador Fish para compactar pasta em tar.gz")
        ok("compactar pasta projetos/ para saida.tar.gz alinhado em Fish")

    print("audit_dev_parity: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
