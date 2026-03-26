#!/usr/bin/env python3
from __future__ import annotations

import os
import stat
import subprocess
import sys
import tempfile
from contextlib import contextmanager
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


def write_os_release(
    root: Path,
    *,
    distro_id: str,
    distro_like: str = "",
    variant_id: str = "",
    name: str = "",
) -> Path:
    path = root / "os-release"
    lines = [f"ID={distro_id}"]
    if distro_like:
        lines.append(f'ID_LIKE="{distro_like}"')
    if variant_id:
        lines.append(f'VARIANT_ID="{variant_id}"')
    if name:
        lines.append(f'NAME="{name}"')
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


@contextmanager
def temporary_env(overrides: dict[str, str]):
    sentinel = object()
    previous: dict[str, object] = {}
    for key, value in overrides.items():
        previous[key] = os.environ.get(key, sentinel)
        os.environ[key] = value
    try:
        yield
    finally:
        for key, old_value in previous.items():
            if old_value is sentinel:
                os.environ.pop(key, None)
            else:
                os.environ[key] = str(old_value)


def dev_executor(phrase: str, *, env: dict[str, str] | None = None) -> tuple[str, str]:
    _phrase, _actions, analyses = prepare_analyses(phrase)
    env_overrides = env or {}
    with temporary_env(env_overrides):
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


def assert_executor(phrase: str, expected_executor: str, *, env: dict[str, str] | None = None) -> str:
    actual_executor, route = dev_executor(phrase, env=env)
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
        os_release = write_os_release(Path(tmp), distro_id="cachyos", distro_like="arch", name="CachyOS")
        path_env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}

        route = assert_executor("procurar steam", "python", env=path_env)
        output = run_fish(["procurar", "steam"], env=path_env)
        if "PACMAN_STUB -Ss -- steam" not in output:
            fail("modo normal não observou a rota Python esperada para procurar pacote")
        ok(f"procurar steam alinhado em Python ({route})")

        route = assert_executor("ver ip", "python", env=path_env)
        output = run_fish(["ver", "ip"], env=path_env)
        if "IP_STUB -brief address" not in output:
            fail("modo normal não observou a rota Python esperada para ver ip")
        ok(f"ver ip alinhado em Python ({route})")

        route = assert_executor("testar internet", "python", env=path_env)
        output = run_fish(["testar", "internet"], env=path_env)
        if "PING_STUB -c 2 -- 8.8.8.8" not in output:
            fail("modo normal não observou a rota Python esperada para testar internet")
        ok(f"testar internet alinhado em Python ({route})")

        route = assert_executor("velocidade da internet", "python", env=path_env)
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
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "paru", "#!/usr/bin/env bash\nprintf 'PARU_UPDATE_STUB %s\\n' \"$*\"\n")
        write_stub(bin_dir, "pacman", "#!/usr/bin/env bash\nprintf 'PACMAN_UNUSED %s\\n' \"$*\"\n")
        write_stub(bin_dir, "sudo", "#!/usr/bin/env bash\n\"$@\"\n")
        write_stub(bin_dir, "journalctl", "#!/usr/bin/env bash\nprintf 'JOURNALCTL_STUB %s\\n' \"$*\"\n")
        write_stub(bin_dir, "paccache", "#!/usr/bin/env bash\nprintf 'PACCACHE_STUB %s\\n' \"$*\"\n")
        os_release = write_os_release(root, distro_id="cachyos", distro_like="arch", name="CachyOS")
        path_env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}

        route = assert_executor("atualizar sistema", "fish", env=path_env)
        if route != "-":
            fail("manutenção local em Arch não deve fingir rota Python suportada")
        dev_output = run_fish(["dev", "atualizar", "sistema"], env=path_env)
        if "manutenção local do host" not in dev_output or "compatibilidade:               manutenção local do host" not in dev_output:
            fail("aury dev precisa enquadrar atualizar sistema como manutenção local do host em Arch")
        output = run_fish(["atualizar", "sistema"], env=path_env)
        if "PARU_UPDATE_STUB -Syu" not in output:
            fail("modo normal não observou a rota local esperada para atualizar sistema em Arch")
        ok("atualizar sistema permanece local e honestamente enquadrado em Arch")

        assert_executor("otimizar sistema", "fish", env=path_env)
        dev_output = run_fish(["dev", "otimizar", "sistema"], env=path_env)
        if "manutenção local do host" not in dev_output or "compatibilidade:               manutenção local do host" not in dev_output:
            fail("aury dev precisa enquadrar otimizar sistema como manutenção local do host em Arch")
        output = run_fish(["otimizar", "sistema"], env=path_env)
        if "PACCACHE_STUB -rk2" not in output or "JOURNALCTL_STUB --vacuum-time=7d" not in output:
            fail("modo normal não observou a rota local esperada para otimizar sistema em Arch")
        ok("otimizar sistema permanece local e honestamente enquadrado em Arch")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        os_release = write_os_release(root, distro_id="ubuntu", distro_like="debian", name="Ubuntu")
        path_env = {"PATH": os.environ["PATH"], "AURY_OS_RELEASE_PATH": str(os_release)}

        route = assert_executor("atualizar sistema", "python", env=path_env)
        if route != "host_maintenance_policy_gate":
            fail("manutenção fora do recorte em Debian precisa subir pelo gate honesto do runtime Python")
        dev_output = run_fish(["dev", "atualizar", "sistema"], env=path_env)
        if "compatibilidade:               fora do recorte" not in dev_output:
            fail("aury dev não pode descrever atualizar sistema em Debian como se fosse portátil")
        output = run_fish_public_error(["atualizar", "sistema"], env=path_env)
        if "manutenção do host" not in output or "fora do recorte equivalente" not in output:
            fail("modo normal precisa bloquear atualizar sistema em Debian com leitura honesta de manutenção do host")
        ok("atualizar sistema sai como fora do recorte em Debian")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "dnf", "#!/usr/bin/env bash\nprintf 'DNF_SHOULD_NOT_RUN %s\\n' \"$*\"\n")
        os_release = write_os_release(root, distro_id="bazzite", distro_like="fedora", name="Bazzite")
        path_env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}

        route = assert_executor("otimizar sistema", "python", env=path_env)
        if route != "host_maintenance_policy_gate":
            fail("host Atomic precisa subir pelo gate honesto de manutenção do host")
        dev_output = run_fish(["dev", "otimizar", "sistema"], env=path_env)
        if "compatibilidade:               bloqueado por política" not in dev_output:
            fail("aury dev precisa explicitar bloqueio por política para otimizar sistema em host Atomic")
        output = run_fish_public_error(["otimizar", "sistema"], env=path_env)
        if "bloqueado por política" not in output or "DNF_SHOULD_NOT_RUN" in output:
            fail("modo normal não pode tratar manutenção em host Atomic como backend simplesmente executável")
        ok("otimizar sistema permanece bloqueado por política em host Atomic")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "sudo", "#!/usr/bin/env bash\n\"$@\"\n")
        write_stub(
            bin_dir,
            "pacman",
            "#!/usr/bin/env bash\n"
            f"firefox_state={root / 'firefox.installed'!s}\n"
            f"vlc_state={root / 'vlc.removed'!s}\n"
            "if [ \"$1\" = \"-Q\" ] && [ \"$3\" = \"firefox\" ]; then\n"
            "  if [ -f \"$firefox_state\" ]; then\n"
            "    exit 0\n"
            "  fi\n"
            "  touch \"$firefox_state\"\n"
            "  exit 1\n"
            "fi\n"
            "if [ \"$1\" = \"-Q\" ] && [ \"$3\" = \"vlc\" ]; then\n"
            "  if [ -f \"$vlc_state\" ]; then\n"
            "    exit 1\n"
            "  fi\n"
            "  touch \"$vlc_state\"\n"
            "  exit 0\n"
            "fi\n"
            "printf 'PACMAN_FALLBACK %s\\n' \"$*\"\n",
        )
        write_stub(
            bin_dir,
            "paru",
            "#!/usr/bin/env bash\nprintf 'PARU_FALLBACK %s\\n' \"$*\"\n",
        )
        os_release = write_os_release(root, distro_id="cachyos", distro_like="arch", name="CachyOS")
        path_env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}

        assert_executor("instalar firefox", "python", env=path_env)
        output = run_fish(["instalar", "firefox"], env=path_env)
        if "PARU_FALLBACK -S --needed -- firefox" not in output:
            fail("modo normal não observou a rota Python esperada para instalar firefox")
        ok("instalar firefox alinhado em Python")

        assert_executor("remover vlc", "python", env=path_env)
        output = run_fish(["remover", "vlc"], env=path_env)
        if "PACMAN_FALLBACK -Rns -- vlc" not in output:
            fail("modo normal não observou a rota Python esperada para remover vlc")
        ok("remover vlc alinhado em Python")

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
