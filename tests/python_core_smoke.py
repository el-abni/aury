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

from aury.analyzer import prepare_analyses, prepare_analysis
from aury.contracts import ActionExecutionPlan, SupportedRuntimeRoute
from aury.host import build_package_execution_plan, detect_host_profile, resolve_package_action_policy
from aury.pipeline import prepare_text
from aury.runtime import plan_action_execution, plan_sequence_execution
from aury.sensitive_tokens import protect_sensitive_tokens, restore_sensitive_tokens

ENV = os.environ.copy()
ENV["PYTHONPATH"] = str(ROOT / "python")
ENV["AURY_SHARE_DIR"] = str(ROOT)
FISH_ROUTED_LABEL = "atendida pelo adaptador Fish"


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


def test_help() -> None:
    proc = run("ajuda")
    assert proc.returncode == 0
    assert_in(proc.stdout, "💜 Aury")


def test_version() -> None:
    proc = run("--version")
    assert proc.returncode == 0
    assert_in(proc.stdout, "💜 Aury")


def test_dev_remove_pkg() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "pacman", "#!/usr/bin/env bash\nexit 0\n")
        os_release = write_os_release(root, distro_id="cachyos", distro_like="arch", name="CachyOS")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}
        proc = run("dev", "remover", "vlc", env=env)
        assert proc.returncode == 0
        assert_in(proc.stdout, "domínio:                       pacote")
        assert_in(proc.stdout, "Remover 'vlc'.")
        assert_in(proc.stdout, "Perfil do host")
        assert_in(proc.stdout, "família linux:                 arch")
        assert_in(proc.stdout, "rota suportada:                package_remove")
        assert_in(proc.stdout, "backend necessário:            sudo + pacman")
        assert_in(proc.stdout, "decisão:                       executar no Python")


def test_dev_install_package_alignment() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "apt-cache", "#!/usr/bin/env bash\nexit 0\n")
        write_stub(bin_dir, "apt-get", "#!/usr/bin/env bash\nexit 0\n")
        write_stub(bin_dir, "sudo", "#!/usr/bin/env bash\nexit 0\n")
        os_release = write_os_release(root, distro_id="ubuntu", distro_like="debian", name="Ubuntu")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}
        proc = run("dev", "instalar", "firefox", env=env)
        assert proc.returncode == 0
        assert_in(proc.stdout, "intenção:                      instalar")
        assert_in(proc.stdout, "domínio:                       pacote")
        assert_in(proc.stdout, "alvo principal:                firefox")
        assert_in(proc.stdout, "resumo:                        Instalar 'firefox'.")
        assert_in(proc.stdout, "família linux:                 debian")
        assert_in(proc.stdout, "tier de suporte:               Tier 1 inicial")
        assert_in(proc.stdout, "suportada agora")
        assert_in(proc.stdout, "rota suportada:                package_install")
        assert_in(proc.stdout, "backend necessário:            sudo + apt-get")
        assert_in(proc.stdout, "decisão:                       executar no Python")


def test_dev_package_atomic_block_alignment() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "dnf", "#!/usr/bin/env bash\nexit 0\n")
        os_release = write_os_release(root, distro_id="bazzite", distro_like="fedora", name="Bazzite")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}
        proc = run("dev", "instalar", "firefox", env=env)
        assert proc.returncode == 0
        assert_in(proc.stdout, "Perfil do host")
        assert_in(proc.stdout, "família linux:                 fedora")
        assert_in(proc.stdout, "mutabilidade:                  Atomic")
        assert_in(proc.stdout, "tier de suporte:               suporte limitado")
        assert_in(proc.stdout, "fronteira:                     bloqueado por política")
        assert_in(proc.stdout, "classificação:                 bloqueio honesto agora")
        assert_in(proc.stdout, "compatibilidade:               bloqueado por política")
        assert_in(proc.stdout, "rota suportada:                package_install")
        assert_in(proc.stdout, "backend necessário:            -")
        assert_in(proc.stdout, "decisão:                       executar no Python")
        assert_in(proc.stdout, "detectado como Atomic/imutável")
        assert_in(proc.stdout, "mesmo quando há backend instalado")


def test_dev_package_opensuse_search_alignment() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "zypper", "#!/usr/bin/env bash\nexit 0\n")
        os_release = write_os_release(root, distro_id="opensuse-tumbleweed", distro_like="opensuse suse", name="openSUSE Tumbleweed")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}
        proc = run("dev", "procurar", "steam", env=env)
        assert proc.returncode == 0
        assert_in(proc.stdout, "intenção:                      procurar")
        assert_in(proc.stdout, "domínio:                       pacote")
        assert_in(proc.stdout, "alvo principal:                steam")
        assert_in(proc.stdout, "família linux:                 opensuse")
        assert_in(proc.stdout, "mutabilidade:                  mutável")
        assert_in(proc.stdout, "tier de suporte:               Tier 2 útil contido")
        assert_in(proc.stdout, "suportada agora")
        assert_in(proc.stdout, "rota suportada:                package_search")
        assert_in(proc.stdout, "backend necessário:            zypper")
        assert_in(proc.stdout, "recorte contido")
        assert_in(proc.stdout, "decisão:                       executar no Python")


def test_dev_package_opensuse_install_alignment() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "zypper", "#!/usr/bin/env bash\nexit 0\n")
        write_stub(bin_dir, "sudo", "#!/usr/bin/env bash\nexit 0\n")
        write_stub(bin_dir, "rpm", "#!/usr/bin/env bash\nexit 0\n")
        os_release = write_os_release(root, distro_id="opensuse-tumbleweed", distro_like="opensuse suse", name="openSUSE Tumbleweed")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}
        proc = run("dev", "instalar", "firefox", env=env)
        assert proc.returncode == 0
        assert_in(proc.stdout, "intenção:                      instalar")
        assert_in(proc.stdout, "domínio:                       pacote")
        assert_in(proc.stdout, "alvo principal:                firefox")
        assert_in(proc.stdout, "família linux:                 opensuse")
        assert_in(proc.stdout, "tier de suporte:               Tier 2 útil contido")
        assert_in(proc.stdout, "suportada agora")
        assert_in(proc.stdout, "rota suportada:                package_install")
        assert_in(proc.stdout, "backend necessário:            sudo + zypper")
        assert_in(proc.stdout, "decisão:                       executar no Python")


def test_dev_package_opensuse_remove_alignment() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "zypper", "#!/usr/bin/env bash\nexit 0\n")
        write_stub(bin_dir, "sudo", "#!/usr/bin/env bash\nexit 0\n")
        write_stub(bin_dir, "rpm", "#!/usr/bin/env bash\nexit 0\n")
        os_release = write_os_release(root, distro_id="opensuse-tumbleweed", distro_like="opensuse suse", name="openSUSE Tumbleweed")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}
        proc = run("dev", "remover", "vlc", env=env)
        assert proc.returncode == 0
        assert_in(proc.stdout, "intenção:                      remover")
        assert_in(proc.stdout, "domínio:                       pacote")
        assert_in(proc.stdout, "alvo principal:                vlc")
        assert_in(proc.stdout, "família linux:                 opensuse")
        assert_in(proc.stdout, "tier de suporte:               Tier 2 útil contido")
        assert_in(proc.stdout, "suportada agora")
        assert_in(proc.stdout, "rota suportada:                package_remove")
        assert_in(proc.stdout, "backend necessário:            sudo + zypper")
        assert_in(proc.stdout, "decisão:                       executar no Python")


def test_dev_ping_host_alignment() -> None:
    proc = run("dev", "ping", "google.com")
    assert proc.returncode == 0
    assert_in(proc.stdout, "intenção:                      ping")
    assert_in(proc.stdout, "domínio:                       rede")
    assert_in(proc.stdout, "alvo principal:                google.com")
    assert_in(proc.stdout, "resumo:                        Pingar 'google.com'.")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")


def test_dev_network_speed_rede_alignment() -> None:
    proc = run("dev", "velocidade", "da", "rede")
    assert proc.returncode == 0
    assert_in(proc.stdout, "intenção:                      velocidade")
    assert_in(proc.stdout, "domínio:                       rede")
    assert_in(proc.stdout, "alvo principal:                velocidade da rede")
    assert_in(proc.stdout, "resumo:                        Medir a velocidade da rede.")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")


def test_dev_create_file_alignment() -> None:
    proc = run("dev", "criar", "arquivo", "abc.txt")
    assert proc.returncode == 0
    assert_in(proc.stdout, "intenção:                      criar")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          arquivo")
    assert_in(proc.stdout, "alvo principal:                abc.txt")
    assert_in(proc.stdout, "resumo:                        Criar 'abc.txt'.")
    assert_in(proc.stdout, "suportada agora")
    assert_in(proc.stdout, "rota suportada:                file_create")
    assert_in(proc.stdout, "backend necessário:            runtime Python")
    assert_in(proc.stdout, "decisão:                       executar no Python")


def test_dev_create_folder_alignment() -> None:
    proc = run("dev", "criar", "pasta", "pasta_teste")
    assert proc.returncode == 0
    assert_in(proc.stdout, "intenção:                      criar")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          pasta")
    assert_in(proc.stdout, "alvo principal:                pasta_teste")
    assert_in(proc.stdout, "resumo:                        Criar 'pasta_teste'.")
    assert_in(proc.stdout, "suportada agora")
    assert_in(proc.stdout, "rota suportada:                folder_create")
    assert_in(proc.stdout, "backend necessário:            runtime Python")
    assert_in(proc.stdout, "decisão:                       executar no Python")


def test_dev_create_folder_inflected_alignment() -> None:
    proc = run("dev", "crie", "a", "pasta", "Aury")
    assert proc.returncode == 0
    assert_in(proc.stdout, "trecho original:               crie a pasta Aury")
    assert_in(proc.stdout, "trecho normalizado:            crie a pasta aury")
    assert_in(proc.stdout, "intenção:                      criar")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          pasta")
    assert_in(proc.stdout, "alvo principal:                Aury")
    assert_in(proc.stdout, "resumo:                        Criar 'Aury'.")
    assert_in(proc.stdout, "suportada agora")
    assert_in(proc.stdout, "decisão:                       executar no Python")


def test_dev_create_file_inflected_alignment() -> None:
    proc = run("dev", "crie", "um", "arquivo", "teste.txt")
    assert proc.returncode == 0
    assert_in(proc.stdout, "trecho original:               crie um arquivo teste.txt")
    assert_in(proc.stdout, "trecho normalizado:            crie um arquivo teste.txt")
    assert_in(proc.stdout, "intenção:                      criar")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          arquivo")
    assert_in(proc.stdout, "alvo principal:                teste.txt")
    assert_in(proc.stdout, "resumo:                        Criar 'teste.txt'.")
    assert_in(proc.stdout, "suportada agora")
    assert_in(proc.stdout, "decisão:                       executar no Python")


def test_dev_create_folder_located_alignment() -> None:
    proc = run("dev", "criar", "pasta", "Relatorios", "em", "Downloads")
    assert proc.returncode == 0
    assert_in(proc.stdout, "trecho original:               criar pasta Relatorios em Downloads")
    assert_in(proc.stdout, "intenção:                      criar")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          pasta")
    assert_in(proc.stdout, "alvo principal:                Downloads/Relatorios")
    assert_in(proc.stdout, "destino:                       Downloads")
    assert_in(proc.stdout, "localização conversacional:    nome: Relatorios | base: Downloads | conector: em")
    assert_in(proc.stdout, "resumo:                        Criar 'Downloads/Relatorios'.")
    assert_in(proc.stdout, "suportada agora")
    assert_in(proc.stdout, "decisão:                       executar no Python")
    assert_in(proc.stdout, "localização conversacional simples usada para recompor a base 'Downloads'")


def test_dev_create_folder_located_inflected_alignment() -> None:
    proc = run("dev", "crie", "a", "pasta", "Relatorios", "em", "Downloads")
    assert proc.returncode == 0
    assert_in(proc.stdout, "trecho original:               crie a pasta Relatorios em Downloads")
    assert_in(proc.stdout, "intenção:                      criar")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          pasta")
    assert_in(proc.stdout, "alvo principal:                Downloads/Relatorios")
    assert_in(proc.stdout, "destino:                       Downloads")
    assert_in(proc.stdout, "localização conversacional:    nome: Relatorios | base: Downloads | conector: em")
    assert_in(proc.stdout, "resumo:                        Criar 'Downloads/Relatorios'.")
    assert_in(proc.stdout, "suportada agora")
    assert_in(proc.stdout, "decisão:                       executar no Python")


def test_dev_create_file_located_alignment() -> None:
    proc = run("dev", "criar", "arquivo", "teste.txt", "em", "Downloads")
    assert proc.returncode == 0
    assert_in(proc.stdout, "trecho original:               criar arquivo teste.txt em Downloads")
    assert_in(proc.stdout, "intenção:                      criar")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          arquivo")
    assert_in(proc.stdout, "alvo principal:                Downloads/teste.txt")
    assert_in(proc.stdout, "destino:                       Downloads")
    assert_in(proc.stdout, "localização conversacional:    nome: teste.txt | base: Downloads | conector: em")
    assert_in(proc.stdout, "resumo:                        Criar 'Downloads/teste.txt'.")
    assert_in(proc.stdout, "suportada agora")
    assert_in(proc.stdout, "decisão:                       executar no Python")
    assert_in(proc.stdout, "localização conversacional simples usada para recompor a base 'Downloads'")


def test_dev_create_file_located_inflected_alignment() -> None:
    proc = run("dev", "crie", "um", "arquivo", "teste.txt", "em", "Downloads")
    assert proc.returncode == 0
    assert_in(proc.stdout, "trecho original:               crie um arquivo teste.txt em Downloads")
    assert_in(proc.stdout, "intenção:                      criar")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          arquivo")
    assert_in(proc.stdout, "alvo principal:                Downloads/teste.txt")
    assert_in(proc.stdout, "destino:                       Downloads")
    assert_in(proc.stdout, "localização conversacional:    nome: teste.txt | base: Downloads | conector: em")
    assert_in(proc.stdout, "resumo:                        Criar 'Downloads/teste.txt'.")
    assert_in(proc.stdout, "suportada agora")
    assert_in(proc.stdout, "decisão:                       executar no Python")


def test_dev_create_implicit_file_alignment() -> None:
    proc = run("dev", "criar", "teste.txt")
    assert proc.returncode == 0
    assert_in(proc.stdout, "trecho original:               criar teste.txt")
    assert_in(proc.stdout, "trecho normalizado:            criar teste.txt")
    assert_in(proc.stdout, "intenção:                      criar")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          arquivo")
    assert_in(proc.stdout, "alvo principal:                teste.txt")
    assert_in(proc.stdout, "resumo:                        Criar 'teste.txt'.")
    assert_in(proc.stdout, "suportada agora")
    assert_in(proc.stdout, "decisão:                       executar no Python")


def test_dev_create_implicit_file_inflected_alignment() -> None:
    proc = run("dev", "crie", "teste.txt")
    assert proc.returncode == 0
    assert_in(proc.stdout, "trecho original:               crie teste.txt")
    assert_in(proc.stdout, "trecho normalizado:            crie teste.txt")
    assert_in(proc.stdout, "intenção:                      criar")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          arquivo")
    assert_in(proc.stdout, "alvo principal:                teste.txt")
    assert_in(proc.stdout, "resumo:                        Criar 'teste.txt'.")
    assert_in(proc.stdout, "suportada agora")
    assert_in(proc.stdout, "decisão:                       executar no Python")


def test_dev_create_implicit_file_located_alignment() -> None:
    proc = run("dev", "criar", "teste.txt", "em", "Downloads")
    assert proc.returncode == 0
    assert_in(proc.stdout, "trecho original:               criar teste.txt em Downloads")
    assert_in(proc.stdout, "trecho normalizado:            criar teste.txt em downloads")
    assert_in(proc.stdout, "intenção:                      criar")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          arquivo")
    assert_in(proc.stdout, "alvo principal:                Downloads/teste.txt")
    assert_in(proc.stdout, "destino:                       Downloads")
    assert_in(proc.stdout, "localização conversacional:    nome: teste.txt | base: Downloads | conector: em")
    assert_in(proc.stdout, "resumo:                        Criar 'Downloads/teste.txt'.")
    assert_in(proc.stdout, "suportada agora")
    assert_in(proc.stdout, "decisão:                       executar no Python")
    assert_in(proc.stdout, "localização conversacional simples usada para recompor a base 'Downloads'")


def test_dev_create_implicit_file_located_inflected_alignment() -> None:
    proc = run("dev", "crie", "teste.txt", "em", "Downloads")
    assert proc.returncode == 0
    assert_in(proc.stdout, "trecho original:               crie teste.txt em Downloads")
    assert_in(proc.stdout, "trecho normalizado:            crie teste.txt em downloads")
    assert_in(proc.stdout, "intenção:                      criar")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          arquivo")
    assert_in(proc.stdout, "alvo principal:                Downloads/teste.txt")
    assert_in(proc.stdout, "destino:                       Downloads")
    assert_in(proc.stdout, "localização conversacional:    nome: teste.txt | base: Downloads | conector: em")
    assert_in(proc.stdout, "resumo:                        Criar 'Downloads/teste.txt'.")
    assert_in(proc.stdout, "suportada agora")
    assert_in(proc.stdout, "decisão:                       executar no Python")


def test_dev_create_implicit_folder_alignment() -> None:
    proc = run("dev", "criar", "projetos/")
    assert proc.returncode == 0
    assert_in(proc.stdout, "trecho original:               criar projetos/")
    assert_in(proc.stdout, "trecho normalizado:            criar projetos/")
    assert_in(proc.stdout, "intenção:                      criar")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          pasta")
    assert_in(proc.stdout, "alvo principal:                projetos/")
    assert_in(proc.stdout, "resumo:                        Criar 'projetos/'.")
    assert_in(proc.stdout, "suportada agora")
    assert_in(proc.stdout, "decisão:                       executar no Python")


def test_dev_create_implicit_folder_inflected_alignment() -> None:
    proc = run("dev", "crie", "projetos/")
    assert proc.returncode == 0
    assert_in(proc.stdout, "trecho original:               crie projetos/")
    assert_in(proc.stdout, "trecho normalizado:            crie projetos/")
    assert_in(proc.stdout, "intenção:                      criar")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          pasta")
    assert_in(proc.stdout, "alvo principal:                projetos/")
    assert_in(proc.stdout, "resumo:                        Criar 'projetos/'.")
    assert_in(proc.stdout, "suportada agora")
    assert_in(proc.stdout, "decisão:                       executar no Python")


def test_dev_create_implicit_folder_located_alignment() -> None:
    proc = run("dev", "criar", "projetos/", "em", "Downloads")
    assert proc.returncode == 0
    assert_in(proc.stdout, "trecho original:               criar projetos/ em Downloads")
    assert_in(proc.stdout, "trecho normalizado:            criar projetos/ em downloads")
    assert_in(proc.stdout, "intenção:                      criar")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          pasta")
    assert_in(proc.stdout, "alvo principal:                Downloads/projetos/")
    assert_in(proc.stdout, "destino:                       Downloads")
    assert_in(proc.stdout, "localização conversacional:    nome: projetos/ | base: Downloads | conector: em")
    assert_in(proc.stdout, "resumo:                        Criar 'Downloads/projetos/'.")
    assert_in(proc.stdout, "suportada agora")
    assert_in(proc.stdout, "decisão:                       executar no Python")
    assert_in(proc.stdout, "localização conversacional simples usada para recompor a base 'Downloads'")


def test_dev_create_implicit_folder_located_inflected_alignment() -> None:
    proc = run("dev", "crie", "projetos/", "em", "Downloads")
    assert proc.returncode == 0
    assert_in(proc.stdout, "trecho original:               crie projetos/ em Downloads")
    assert_in(proc.stdout, "trecho normalizado:            crie projetos/ em downloads")
    assert_in(proc.stdout, "intenção:                      criar")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          pasta")
    assert_in(proc.stdout, "alvo principal:                Downloads/projetos/")
    assert_in(proc.stdout, "destino:                       Downloads")
    assert_in(proc.stdout, "localização conversacional:    nome: projetos/ | base: Downloads | conector: em")
    assert_in(proc.stdout, "resumo:                        Criar 'Downloads/projetos/'.")
    assert_in(proc.stdout, "suportada agora")
    assert_in(proc.stdout, "decisão:                       executar no Python")


def test_dev_create_explicit_folder_slash_located_alignment() -> None:
    proc = run("dev", "criar", "pasta", "projetos/", "em", "Downloads")
    assert proc.returncode == 0
    assert_in(proc.stdout, "trecho original:               criar pasta projetos/ em Downloads")
    assert_in(proc.stdout, "trecho normalizado:            criar pasta projetos/ em downloads")
    assert_in(proc.stdout, "intenção:                      criar")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          pasta")
    assert_in(proc.stdout, "alvo principal:                Downloads/projetos/")
    assert_in(proc.stdout, "destino:                       Downloads")
    assert_in(proc.stdout, "localização conversacional:    nome: projetos/ | base: Downloads | conector: em")
    assert_in(proc.stdout, "resumo:                        Criar 'Downloads/projetos/'.")
    assert_in(proc.stdout, "suportada agora")
    assert_in(proc.stdout, "decisão:                       executar no Python")


def test_dev_copy_file_alignment() -> None:
    proc = run("dev", "copiar", "arquivo", "origem/item.txt", "para", "destino/item-copia.txt")
    assert proc.returncode == 0
    assert_in(proc.stdout, "intenção:                      copiar")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          arquivo")
    assert_in(proc.stdout, "alvo principal:                origem/item.txt")
    assert_in(proc.stdout, "origem:                        origem/item.txt")
    assert_in(proc.stdout, "destino:                       destino/item-copia.txt")
    assert_in(proc.stdout, "resumo:                        Copiar 'origem/item.txt' para 'destino/item-copia.txt'.")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")


def test_dev_move_file_alignment() -> None:
    proc = run("dev", "mover", "arquivo", "destino/item-copia.txt", "para", "destino/item-movido.txt")
    assert proc.returncode == 0
    assert_in(proc.stdout, "intenção:                      mover")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          arquivo")
    assert_in(proc.stdout, "alvo principal:                destino/item-copia.txt")
    assert_in(proc.stdout, "origem:                        destino/item-copia.txt")
    assert_in(proc.stdout, "destino:                       destino/item-movido.txt")
    assert_in(proc.stdout, "resumo:                        Mover 'destino/item-copia.txt' para 'destino/item-movido.txt'.")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")


def test_dev_rename_file_alignment() -> None:
    proc = run("dev", "renomear", "arquivo", "destino/item-movido.txt", "para", "item-final.txt")
    assert proc.returncode == 0
    assert_in(proc.stdout, "intenção:                      renomear")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          arquivo")
    assert_in(proc.stdout, "alvo principal:                destino/item-movido.txt")
    assert_in(proc.stdout, "origem:                        destino/item-movido.txt")
    assert_in(proc.stdout, "destino:                       destino/item-final.txt")
    assert_in(proc.stdout, "novo nome:                     item-final.txt")
    assert_in(proc.stdout, "resumo:                        Renomear 'destino/item-movido.txt' para 'destino/item-final.txt'.")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")


def test_dev_located_rename_file_alignment() -> None:
    proc = run(
        "dev",
        "renomeie",
        "o",
        "arquivo",
        "teste.txt",
        "que",
        "fica",
        "em",
        "Downloads",
        "para",
        "teste-final.txt",
    )
    assert proc.returncode == 0
    assert_in(proc.stdout, "intenção:                      renomear")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          arquivo")
    assert_in(proc.stdout, "alvo principal:                Downloads/teste.txt")
    assert_in(proc.stdout, "origem:                        Downloads/teste.txt")
    assert_in(proc.stdout, "destino:                       Downloads/teste-final.txt")
    assert_in(proc.stdout, "novo nome:                     teste-final.txt")
    assert_in(proc.stdout, "resumo:                        Renomear 'Downloads/teste.txt' para 'Downloads/teste-final.txt'.")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")
    assert_in(proc.stdout, "localização conversacional usada para recompor a base 'Downloads'")


def test_dev_explicit_remove_file_alignment() -> None:
    proc = run("dev", "remover", "o", "arquivo", "apagar.txt")
    assert proc.returncode == 0
    assert_in(proc.stdout, "intenção:                      remover")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          arquivo")
    assert_in(proc.stdout, "alvo principal:                apagar.txt")
    assert_in(proc.stdout, "resumo:                        Remover 'apagar.txt'.")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")
    assert_in(proc.stdout, "confirmação destrutiva no adaptador Fish")


def test_dev_explicit_remove_folder_alignment() -> None:
    proc = run("dev", "remover", "a", "pasta", "pasta_apagar")
    assert proc.returncode == 0
    assert_in(proc.stdout, "intenção:                      remover")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          pasta")
    assert_in(proc.stdout, "alvo principal:                pasta_apagar")
    assert_in(proc.stdout, "resumo:                        Remover 'pasta_apagar'.")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")
    assert_in(proc.stdout, "confirmação destrutiva no adaptador Fish")


def test_dev_explicit_remove_located_folder_alignment() -> None:
    proc = run("dev", "remova", "a", "pasta", "Aury", "que", "fica", "em", "Downloads")
    assert proc.returncode == 0
    assert_in(proc.stdout, "intenção:                      remover")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          pasta")
    assert_in(proc.stdout, "alvo principal:                Downloads/Aury")
    assert_in(proc.stdout, "origem:                        Downloads/Aury")
    assert_in(proc.stdout, "resumo:                        Remover 'Downloads/Aury'.")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")
    assert_in(proc.stdout, "localização conversacional usada para recompor a base 'Downloads'")
    assert_in(proc.stdout, "confirmação destrutiva no adaptador Fish")


def test_dev_explicit_remove_located_file_alignment() -> None:
    proc = run("dev", "remova", "o", "arquivo", "teste.txt", "que", "fica", "em", "destino")
    assert proc.returncode == 0
    assert_in(proc.stdout, "intenção:                      remover")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          arquivo")
    assert_in(proc.stdout, "alvo principal:                destino/teste.txt")
    assert_in(proc.stdout, "origem:                        destino/teste.txt")
    assert_in(proc.stdout, "resumo:                        Remover 'destino/teste.txt'.")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")
    assert_in(proc.stdout, "localização conversacional usada para recompor a base 'destino'")
    assert_in(proc.stdout, "confirmação destrutiva no adaptador Fish")


def test_dev_implicit_remove_file_alignment() -> None:
    proc = run("dev", "remover", "teste.txt")
    assert proc.returncode == 0
    assert_in(proc.stdout, "trecho original:               remover teste.txt")
    assert_in(proc.stdout, "trecho normalizado:            remover teste.txt")
    assert_in(proc.stdout, "intenção:                      remover")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          arquivo")
    assert_in(proc.stdout, "alvo principal:                teste.txt")
    assert_in(proc.stdout, "resumo:                        Remover 'teste.txt'.")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")
    assert_in(proc.stdout, "confirmação no adaptador Fish")


def test_dev_implicit_remove_file_inflected_alignment() -> None:
    proc = run("dev", "remova", "teste.txt")
    assert proc.returncode == 0
    assert_in(proc.stdout, "trecho original:               remova teste.txt")
    assert_in(proc.stdout, "trecho normalizado:            remova teste.txt")
    assert_in(proc.stdout, "intenção:                      remover")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          arquivo")
    assert_in(proc.stdout, "alvo principal:                teste.txt")
    assert_in(proc.stdout, "resumo:                        Remover 'teste.txt'.")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")
    assert_in(proc.stdout, "confirmação no adaptador Fish")


def test_dev_implicit_remove_folder_alignment() -> None:
    proc = run("dev", "remover", "projetos/")
    assert proc.returncode == 0
    assert_in(proc.stdout, "trecho original:               remover projetos/")
    assert_in(proc.stdout, "trecho normalizado:            remover projetos/")
    assert_in(proc.stdout, "intenção:                      remover")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          pasta")
    assert_in(proc.stdout, "alvo principal:                projetos/")
    assert_in(proc.stdout, "resumo:                        Remover 'projetos/'.")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")
    assert_in(proc.stdout, "confirmação no adaptador Fish")


def test_dev_implicit_remove_folder_inflected_alignment() -> None:
    proc = run("dev", "remova", "projetos/")
    assert proc.returncode == 0
    assert_in(proc.stdout, "trecho original:               remova projetos/")
    assert_in(proc.stdout, "trecho normalizado:            remova projetos/")
    assert_in(proc.stdout, "intenção:                      remover")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          pasta")
    assert_in(proc.stdout, "alvo principal:                projetos/")
    assert_in(proc.stdout, "resumo:                        Remover 'projetos/'.")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")
    assert_in(proc.stdout, "confirmação no adaptador Fish")


def test_dev_implicit_remove_located_file_alignment() -> None:
    proc = run("dev", "remover", "teste.txt", "em", "Downloads")
    assert proc.returncode == 0
    assert_in(proc.stdout, "trecho original:               remover teste.txt em Downloads")
    assert_in(proc.stdout, "trecho normalizado:            remover teste.txt em downloads")
    assert_in(proc.stdout, "intenção:                      remover")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          arquivo")
    assert_in(proc.stdout, "alvo principal:                Downloads/teste.txt")
    assert_in(proc.stdout, "origem:                        Downloads/teste.txt")
    assert_in(proc.stdout, "resumo:                        Remover 'Downloads/teste.txt'.")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")
    assert_in(proc.stdout, "localização conversacional simples usada para recompor a base 'Downloads'")
    assert_in(proc.stdout, "confirmação no adaptador Fish")


def test_dev_implicit_remove_located_file_inflected_alignment() -> None:
    proc = run("dev", "remova", "teste.txt", "em", "Downloads")
    assert proc.returncode == 0
    assert_in(proc.stdout, "trecho original:               remova teste.txt em Downloads")
    assert_in(proc.stdout, "trecho normalizado:            remova teste.txt em downloads")
    assert_in(proc.stdout, "intenção:                      remover")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          arquivo")
    assert_in(proc.stdout, "alvo principal:                Downloads/teste.txt")
    assert_in(proc.stdout, "origem:                        Downloads/teste.txt")
    assert_in(proc.stdout, "resumo:                        Remover 'Downloads/teste.txt'.")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")
    assert_in(proc.stdout, "localização conversacional simples usada para recompor a base 'Downloads'")
    assert_in(proc.stdout, "confirmação no adaptador Fish")


def test_dev_implicit_remove_located_folder_alignment() -> None:
    proc = run("dev", "remover", "projetos/", "em", "Downloads")
    assert proc.returncode == 0
    assert_in(proc.stdout, "trecho original:               remover projetos/ em Downloads")
    assert_in(proc.stdout, "trecho normalizado:            remover projetos/ em downloads")
    assert_in(proc.stdout, "intenção:                      remover")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          pasta")
    assert_in(proc.stdout, "alvo principal:                Downloads/projetos/")
    assert_in(proc.stdout, "origem:                        Downloads/projetos/")
    assert_in(proc.stdout, "resumo:                        Remover 'Downloads/projetos/'.")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")
    assert_in(proc.stdout, "localização conversacional simples usada para recompor a base 'Downloads'")
    assert_in(proc.stdout, "confirmação no adaptador Fish")


def test_dev_implicit_remove_located_folder_inflected_alignment() -> None:
    proc = run("dev", "remova", "projetos/", "em", "Downloads")
    assert proc.returncode == 0
    assert_in(proc.stdout, "trecho original:               remova projetos/ em Downloads")
    assert_in(proc.stdout, "trecho normalizado:            remova projetos/ em downloads")
    assert_in(proc.stdout, "intenção:                      remover")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          pasta")
    assert_in(proc.stdout, "alvo principal:                Downloads/projetos/")
    assert_in(proc.stdout, "origem:                        Downloads/projetos/")
    assert_in(proc.stdout, "resumo:                        Remover 'Downloads/projetos/'.")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")
    assert_in(proc.stdout, "localização conversacional simples usada para recompor a base 'Downloads'")
    assert_in(proc.stdout, "confirmação no adaptador Fish")


def test_dev_explicit_remove_short_located_folder_alignment() -> None:
    proc = run("dev", "remover", "a", "pasta", "projetos/", "em", "Downloads")
    assert proc.returncode == 0
    assert_in(proc.stdout, "trecho original:               remover a pasta projetos/ em Downloads")
    assert_in(proc.stdout, "trecho normalizado:            remover a pasta projetos/ em downloads")
    assert_in(proc.stdout, "intenção:                      remover")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          pasta")
    assert_in(proc.stdout, "alvo principal:                Downloads/projetos/")
    assert_in(proc.stdout, "origem:                        Downloads/projetos/")
    assert_in(proc.stdout, "resumo:                        Remover 'Downloads/projetos/'.")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")
    assert_in(proc.stdout, "localização conversacional simples usada para recompor a base 'Downloads'")
    assert_in(proc.stdout, "confirmação no adaptador Fish")


def test_dev_explicit_remove_short_located_folder_inflected_alignment() -> None:
    proc = run("dev", "remova", "a", "pasta", "projetos/", "em", "Downloads")
    assert proc.returncode == 0
    assert_in(proc.stdout, "trecho original:               remova a pasta projetos/ em Downloads")
    assert_in(proc.stdout, "trecho normalizado:            remova a pasta projetos/ em downloads")
    assert_in(proc.stdout, "intenção:                      remover")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          pasta")
    assert_in(proc.stdout, "alvo principal:                Downloads/projetos/")
    assert_in(proc.stdout, "origem:                        Downloads/projetos/")
    assert_in(proc.stdout, "resumo:                        Remover 'Downloads/projetos/'.")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")
    assert_in(proc.stdout, "localização conversacional simples usada para recompor a base 'Downloads'")
    assert_in(proc.stdout, "confirmação no adaptador Fish")


def test_dev_compact_zip_file_alignment() -> None:
    proc = run("dev", "compactar", "arquivo", "teste.txt", "para", "teste.zip")
    assert proc.returncode == 0
    assert_in(proc.stdout, "intenção:                      compactar")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          zip")
    assert_in(proc.stdout, "tipo de origem:                arquivo")
    assert_in(proc.stdout, "alvo principal:                teste.txt")
    assert_in(proc.stdout, "origem:                        teste.txt")
    assert_in(proc.stdout, "saída:                         teste.zip")
    assert_in(proc.stdout, "resumo:                        Compactar 'teste.txt' em 'teste.zip'.")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")
    assert_in(proc.stdout, "formato inferido exclusivamente pelo sufixo da saída 'teste.zip'")


def test_dev_compact_zip_folder_alignment() -> None:
    proc = run("dev", "compactar", "pasta", "projetos/", "para", "projetos.zip")
    assert proc.returncode == 0
    assert_in(proc.stdout, "intenção:                      compactar")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          zip")
    assert_in(proc.stdout, "tipo de origem:                pasta")
    assert_in(proc.stdout, "alvo principal:                projetos/")
    assert_in(proc.stdout, "origem:                        projetos/")
    assert_in(proc.stdout, "saída:                         projetos.zip")
    assert_in(proc.stdout, "resumo:                        Compactar 'projetos/' em 'projetos.zip'.")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")


def test_dev_compact_tar_gz_file_alignment() -> None:
    proc = run("dev", "compactar", "arquivo", "teste.txt", "para", "teste.tar.gz")
    assert proc.returncode == 0
    assert_in(proc.stdout, "intenção:                      compactar")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          tar.gz")
    assert_in(proc.stdout, "tipo de origem:                arquivo")
    assert_in(proc.stdout, "alvo principal:                teste.txt")
    assert_in(proc.stdout, "origem:                        teste.txt")
    assert_in(proc.stdout, "saída:                         teste.tar.gz")
    assert_in(proc.stdout, "resumo:                        Compactar 'teste.txt' em 'teste.tar.gz'.")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")


def test_dev_compact_tar_gz_folder_alignment() -> None:
    proc = run("dev", "compactar", "pasta", "projetos/", "para", "projetos.tar.gz")
    assert proc.returncode == 0
    assert_in(proc.stdout, "intenção:                      compactar")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          tar.gz")
    assert_in(proc.stdout, "tipo de origem:                pasta")
    assert_in(proc.stdout, "alvo principal:                projetos/")
    assert_in(proc.stdout, "origem:                        projetos/")
    assert_in(proc.stdout, "saída:                         projetos.tar.gz")
    assert_in(proc.stdout, "resumo:                        Compactar 'projetos/' em 'projetos.tar.gz'.")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")


def test_dev_compact_missing_output_blocks() -> None:
    proc = run("dev", "compactar", "arquivo", "teste.txt")
    assert proc.returncode == 0
    assert_in(proc.stdout, "intenção:                      compactar")
    assert_in(proc.stdout, "estado:                        BLOQUEADA")
    assert_in(proc.stdout, "lacunas:                       saída explícita obrigatória")
    assert_in(proc.stdout, "resumo:                        Compactação sem saída explícita; leitura bloqueada.")
    assert_in(proc.stdout, "motivo:                        a ação 1 ficou bloqueada por lacuna explícita: saída explícita obrigatória.")
    assert_in(
        proc.stdout,
        "motivo do plano:               a análise ficou bloqueada por lacuna explícita: saída explícita obrigatória.",
    )


def test_dev_compact_invalid_format_blocks() -> None:
    proc = run("dev", "compactar", "arquivo", "teste.txt", "para", "teste.rar")
    assert proc.returncode == 0
    assert_in(proc.stdout, "intenção:                      compactar")
    assert_in(proc.stdout, "estado:                        BLOQUEADA")
    assert_in(proc.stdout, "lacunas:                       saída .zip ou .tar.gz")
    assert_in(proc.stdout, "saída:                         teste.rar")
    assert_in(proc.stdout, "resumo:                        Saída fora do recorte da compactação; leitura bloqueada.")


def test_dev_extract_zip_alignment() -> None:
    proc = run("dev", "extrair", "pacote.zip")
    assert proc.returncode == 0
    assert_in(proc.stdout, "intenção:                      extrair")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          zip")
    assert_in(proc.stdout, "alvo principal:                pacote.zip")
    assert_in(proc.stdout, "arquivo compactado:            pacote.zip")
    assert_in(proc.stdout, "destino:                       ./pacote")
    assert_in(proc.stdout, "resumo:                        Extrair 'pacote.zip' para './pacote'.")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")
    assert_in(proc.stdout, "destino padrão de extração derivado como './pacote'")


def test_dev_extract_tar_gz_alignment() -> None:
    proc = run("dev", "extrair", "pacote.tar.gz")
    assert proc.returncode == 0
    assert_in(proc.stdout, "intenção:                      extrair")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          tar.gz")
    assert_in(proc.stdout, "alvo principal:                pacote.tar.gz")
    assert_in(proc.stdout, "arquivo compactado:            pacote.tar.gz")
    assert_in(proc.stdout, "destino:                       ./pacote")
    assert_in(proc.stdout, "resumo:                        Extrair 'pacote.tar.gz' para './pacote'.")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")
    assert_in(proc.stdout, "destino padrão de extração derivado como './pacote'")


def test_dev_extract_conversational_destination_alignment() -> None:
    proc = run("dev", "extraia", "pacote.tar.gz", "para", "a", "pasta", "que", "fica", "em", "extracao")
    assert proc.returncode == 0
    assert_in(proc.stdout, "intenção:                      extrair")
    assert_in(proc.stdout, "domínio:                       pasta")
    assert_in(proc.stdout, "tipo:                          tar.gz")
    assert_in(proc.stdout, "alvo principal:                pacote.tar.gz")
    assert_in(proc.stdout, "arquivo compactado:            pacote.tar.gz")
    assert_in(proc.stdout, "destino:                       extracao")
    assert_in(proc.stdout, "localização conversacional")
    assert_in(proc.stdout, "destino simples: extracao")
    assert_in(proc.stdout, "resumo:                        Extrair 'pacote.tar.gz' para 'extracao'.")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")
    assert_in(proc.stdout, "localização conversacional simples usada para fechar o destino 'extracao'")


def test_dev_extract_explicit_real_path_destination_alignment() -> None:
    proc = run("dev", "extraia", "pacote.tar.gz", "para", "/usr/steam")
    assert proc.returncode == 0
    assert_in(proc.stdout, "intenção:                      extrair")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          tar.gz")
    assert_in(proc.stdout, "alvo principal:                pacote.tar.gz")
    assert_in(proc.stdout, "arquivo compactado:            pacote.tar.gz")
    assert_in(proc.stdout, "destino:                       /usr/steam")
    assert_in(proc.stdout, "resumo:                        Extrair 'pacote.tar.gz' para '/usr/steam'.")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")
    assert_in(proc.stdout, "destino explícito em caminho real preservado como '/usr/steam'")


def test_dev_copy_rename_local_reference_alignment() -> None:
    phrase = "copie a pasta Aury que fica em origem para destino e renomeie ela para Aury-backup"
    proc = run("dev", *phrase.split())
    assert proc.returncode == 0
    assert_in(proc.stdout, "Plano da sequência")
    assert_in(proc.stdout, "Ação 1")
    assert_in(proc.stdout, "trecho original:               copie a pasta Aury que fica em origem para destino")
    assert_in(proc.stdout, "intenção:                      copiar")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          pasta")
    assert_in(proc.stdout, "alvo principal:                origem/Aury")
    assert_in(proc.stdout, "origem:                        origem/Aury")
    assert_in(proc.stdout, "destino:                       destino/Aury")
    assert_in(proc.stdout, "resumo:                        Copiar 'origem/Aury' para 'destino/Aury'.")
    assert_in(proc.stdout, "localização conversacional usada para recompor a base 'origem'")
    assert_in(proc.stdout, "Ação 2")
    assert_in(proc.stdout, "trecho original:               renomeie ela para Aury-backup")
    assert_in(proc.stdout, "intenção:                      renomear")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          pasta")
    assert_in(proc.stdout, "alvo principal:                destino/Aury")
    assert_in(proc.stdout, "origem:                        destino/Aury")
    assert_in(proc.stdout, "destino:                       destino/Aury-backup")
    assert_in(proc.stdout, "novo nome:                     Aury-backup")
    assert_in(proc.stdout, "referência local:              destino/Aury")
    assert_in(proc.stdout, "resumo:                        Renomear 'destino/Aury' para 'destino/Aury-backup'.")
    assert_in(proc.stdout, "referência local 'ela' resolvida com segurança como 'destino/Aury'")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")


def test_dev_copy_rename_file_local_reference_alignment() -> None:
    phrase = "copie o arquivo teste.txt para copia.txt e renomeie ele para final.txt"
    proc = run("dev", *phrase.split())
    assert proc.returncode == 0
    assert_in(proc.stdout, "Plano da sequência")
    assert_in(proc.stdout, "Ação 1")
    assert_in(proc.stdout, "trecho original:               copie o arquivo teste.txt para copia.txt")
    assert_in(proc.stdout, "intenção:                      copiar")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          arquivo")
    assert_in(proc.stdout, "alvo principal:                teste.txt")
    assert_in(proc.stdout, "origem:                        teste.txt")
    assert_in(proc.stdout, "destino:                       copia.txt")
    assert_in(proc.stdout, "resumo:                        Copiar 'teste.txt' para 'copia.txt'.")
    assert_in(proc.stdout, "Ação 2")
    assert_in(proc.stdout, "trecho original:               renomeie ele para final.txt")
    assert_in(proc.stdout, "intenção:                      renomear")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          arquivo")
    assert_in(proc.stdout, "alvo principal:                copia.txt")
    assert_in(proc.stdout, "origem:                        copia.txt")
    assert_in(proc.stdout, "destino:                       final.txt")
    assert_in(proc.stdout, "novo nome:                     final.txt")
    assert_in(proc.stdout, "referência local:              copia.txt")
    assert_in(proc.stdout, "resumo:                        Renomear 'copia.txt' para 'final.txt'.")
    assert_in(proc.stdout, "referência local 'ele' resolvida com segurança como 'copia.txt'")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")


def test_dev_move_rename_file_local_reference_alignment() -> None:
    phrase = "mova o arquivo teste.txt para pasta2/final.txt e renomeie ele para ultimo.txt"
    proc = run("dev", *phrase.split())
    assert proc.returncode == 0
    assert_in(proc.stdout, "Plano da sequência")
    assert_in(proc.stdout, "Ação 1")
    assert_in(proc.stdout, "trecho original:               mova o arquivo teste.txt para pasta2/final.txt")
    assert_in(proc.stdout, "intenção:                      mover")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          arquivo")
    assert_in(proc.stdout, "alvo principal:                teste.txt")
    assert_in(proc.stdout, "origem:                        teste.txt")
    assert_in(proc.stdout, "destino:                       pasta2/final.txt")
    assert_in(proc.stdout, "resumo:                        Mover 'teste.txt' para 'pasta2/final.txt'.")
    assert_in(proc.stdout, "Ação 2")
    assert_in(proc.stdout, "trecho original:               renomeie ele para ultimo.txt")
    assert_in(proc.stdout, "intenção:                      renomear")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          arquivo")
    assert_in(proc.stdout, "alvo principal:                pasta2/final.txt")
    assert_in(proc.stdout, "origem:                        pasta2/final.txt")
    assert_in(proc.stdout, "destino:                       pasta2/ultimo.txt")
    assert_in(proc.stdout, "novo nome:                     ultimo.txt")
    assert_in(proc.stdout, "referência local:              pasta2/final.txt")
    assert_in(proc.stdout, "resumo:                        Renomear 'pasta2/final.txt' para 'pasta2/ultimo.txt'.")
    assert_in(proc.stdout, "referência local 'ele' resolvida com segurança como 'pasta2/final.txt'")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")


def test_dev_chain() -> None:
    phrase = "copie a pasta Aury que fica em Documentos para Downloads e renomeie ela para Aury-backup"
    proc = run("dev", *phrase.split())
    assert proc.returncode == 0
    assert_in(proc.stdout, "Ação 1")
    assert_in(proc.stdout, "Ação 2")
    assert_in(proc.stdout, "origem:                        Documentos/Aury")
    assert_in(proc.stdout, "destino:                       Downloads/Aury")
    assert_in(proc.stdout, "referência local:              Downloads/Aury")
    assert_in(proc.stdout, "novo nome:                     Aury-backup")
    assert_in(proc.stdout, "destino:                       Downloads/Aury-backup")


def test_dev_sentence_chain_move_local_reference_alignment() -> None:
    phrase = "copie a pasta Aury para Downloads. Depois mova ela para Backup."
    proc = run("dev", *phrase.split())
    assert proc.returncode == 0
    assert_in(proc.stdout, "Ação 1")
    assert_in(proc.stdout, "trecho original:               copie a pasta Aury para Downloads.")
    assert_in(proc.stdout, "intenção:                      copiar")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          pasta")
    assert_in(proc.stdout, "alvo principal:                Aury")
    assert_in(proc.stdout, "origem:                        Aury")
    assert_in(proc.stdout, "destino:                       Downloads/Aury")
    assert_in(proc.stdout, "resumo:                        Copiar 'Aury' para 'Downloads/Aury'.")
    assert_in(proc.stdout, "Ação 2")
    assert_in(proc.stdout, "trecho original:               mova ela para Backup.")
    assert_in(proc.stdout, "intenção:                      mover")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          pasta")
    assert_in(proc.stdout, "alvo principal:                Downloads/Aury")
    assert_in(proc.stdout, "origem:                        Downloads/Aury")
    assert_in(proc.stdout, "referência local:              Downloads/Aury")
    assert_in(proc.stdout, "destino:                       Backup/Aury")
    assert_in(proc.stdout, "resumo:                        Mover 'Downloads/Aury' para 'Backup/Aury'.")
    assert_in(proc.stdout, "referência local 'ela' resolvida com segurança como 'Downloads/Aury'")
    assert_in(proc.stdout, FISH_ROUTED_LABEL)
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")


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
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "pacman", "#!/usr/bin/env bash\necho 'PACMAN_SEARCH_STUB -Ss -- steam'\n")
        os_release = write_os_release(root, distro_id="cachyos", distro_like="arch", name="CachyOS")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}
        proc = run("procurar", "steam", env=env)
        assert proc.returncode == 0
        assert_in(proc.stdout, "PACMAN_SEARCH_STUB")


def test_runtime_package_search_no_results() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "pacman", "#!/usr/bin/env bash\nexit 1\n")
        os_release = write_os_release(root, distro_id="cachyos", distro_like="arch", name="CachyOS")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}
        proc = run("procurar", "steam", env=env)
        assert proc.returncode == 0
        assert_in(proc.stdout, "não encontrei resultados para 'steam' no backend 'pacman'")


def test_runtime_package_search_debian_no_results() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "apt-cache", "#!/usr/bin/env bash\nexit 0\n")
        os_release = write_os_release(root, distro_id="ubuntu", distro_like="debian", name="Ubuntu")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}
        proc = run("procurar", "steam", env=env)
        assert proc.returncode == 0
        assert_in(proc.stdout, "não encontrei resultados para 'steam' no backend 'apt-cache'")


def test_runtime_package_search_opensuse() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "zypper", "#!/usr/bin/env bash\necho 'ZYPPER_SEARCH_STUB search -- steam'\n")
        os_release = write_os_release(root, distro_id="opensuse-tumbleweed", distro_like="opensuse suse", name="openSUSE Tumbleweed")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}
        proc = run("procurar", "steam", env=env)
        assert proc.returncode == 0
        assert_in(proc.stdout, "ZYPPER_SEARCH_STUB")


def test_runtime_package_search_opensuse_no_results() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "zypper", "#!/usr/bin/env bash\necho 'No matching items found.'\nexit 104\n")
        os_release = write_os_release(root, distro_id="opensuse-tumbleweed", distro_like="opensuse suse", name="openSUSE Tumbleweed")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}
        proc = run("procurar", "steam", env=env)
        assert proc.returncode == 0
        assert_in(proc.stdout, "não encontrei resultados para 'steam' no backend 'zypper'")
        if "No matching items found." in proc.stdout:
            raise AssertionError("a busca sem resultado em OpenSUSE deve sair com a superfície honesta da Aury")


def test_runtime_package_install_debian() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        dpkg_state = root / "dpkg.state"
        write_stub(bin_dir, "sudo", "#!/usr/bin/env bash\n\"$@\"\n")
        write_stub(bin_dir, "apt-get", "#!/usr/bin/env bash\necho 'APT_INSTALL_STUB install -y firefox'\n")
        write_stub(
            bin_dir,
            "dpkg",
            "#!/usr/bin/env bash\n"
            f"state={dpkg_state!s}\n"
            "if [ -f \"$state\" ]; then\n"
            "  exit 0\n"
            "fi\n"
            "touch \"$state\"\n"
            "exit 1\n",
        )
        os_release = write_os_release(root, distro_id="ubuntu", distro_like="debian", name="Ubuntu")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}
        proc = run("instalar", "firefox", env=env)
        assert proc.returncode == 0
        assert_in(proc.stdout, "APT_INSTALL_STUB install -y firefox")


def test_runtime_package_install_noop_when_already_installed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "sudo", "#!/usr/bin/env bash\n\"$@\"\n")
        write_stub(bin_dir, "apt-get", "#!/usr/bin/env bash\necho 'APT_SHOULD_NOT_RUN'\n")
        write_stub(bin_dir, "dpkg", "#!/usr/bin/env bash\nexit 0\n")
        os_release = write_os_release(root, distro_id="ubuntu", distro_like="debian", name="Ubuntu")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}
        proc = run("instalar", "firefox", env=env)
        assert proc.returncode == 0
        assert_in(proc.stdout, "o pacote 'firefox' já está instalado neste host. Nada foi feito.")
        if "APT_SHOULD_NOT_RUN" in proc.stdout:
            raise AssertionError("a instalação não deveria chamar o backend quando o pacote já está instalado")


def test_runtime_package_install_requires_state_confirmation() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "sudo", "#!/usr/bin/env bash\n\"$@\"\n")
        write_stub(bin_dir, "apt-get", "#!/usr/bin/env bash\necho 'APT_INSTALL_STUB install -y firefox'\n")
        write_stub(bin_dir, "dpkg", "#!/usr/bin/env bash\nexit 1\n")
        os_release = write_os_release(root, distro_id="ubuntu", distro_like="debian", name="Ubuntu")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}
        proc = run("instalar", "firefox", env=env)
        assert proc.returncode == 1
        assert_in(proc.stdout, "terminou sem eu conseguir confirmar a instalação de 'firefox'")


def test_runtime_package_install_opensuse() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        rpm_state = root / "rpm.state"
        write_stub(bin_dir, "sudo", "#!/usr/bin/env bash\n\"$@\"\n")
        write_stub(
            bin_dir,
            "zypper",
            "#!/usr/bin/env bash\n"
            f"state={rpm_state!s}\n"
            "if [ \"$1\" = \"--non-interactive\" ] && [ \"$2\" = \"install\" ] && [ \"$4\" = \"firefox\" ]; then\n"
            "  touch \"$state\"\n"
            "fi\n"
            "printf 'ZYPPER_INSTALL_STUB %s\\n' \"$*\"\n",
        )
        write_stub(
            bin_dir,
            "rpm",
            "#!/usr/bin/env bash\n"
            f"state={rpm_state!s}\n"
            "if [ \"$1\" = \"-q\" ] && [ \"$2\" = \"firefox\" ]; then\n"
            "  if [ -f \"$state\" ]; then\n"
            "    exit 0\n"
            "  fi\n"
            "  exit 1\n"
            "fi\n"
            "exit 1\n",
        )
        os_release = write_os_release(root, distro_id="opensuse-tumbleweed", distro_like="opensuse suse", name="openSUSE Tumbleweed")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}
        proc = run("instalar", "firefox", env=env)
        assert proc.returncode == 0
        assert_in(proc.stdout, "ZYPPER_INSTALL_STUB --non-interactive install -- firefox")


def test_runtime_package_install_opensuse_requires_state_confirmation() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "sudo", "#!/usr/bin/env bash\n\"$@\"\n")
        write_stub(bin_dir, "zypper", "#!/usr/bin/env bash\necho 'ZYPPER_INSTALL_STUB --non-interactive install -- firefox'\n")
        write_stub(bin_dir, "rpm", "#!/usr/bin/env bash\nexit 1\n")
        os_release = write_os_release(root, distro_id="opensuse-tumbleweed", distro_like="opensuse suse", name="openSUSE Tumbleweed")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}
        proc = run("instalar", "firefox", env=env)
        assert proc.returncode == 1
        assert_in(proc.stdout, "terminou sem eu conseguir confirmar a instalação de 'firefox'")


def test_runtime_package_remove_fedora() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        rpm_state = root / "rpm.state"
        write_stub(bin_dir, "sudo", "#!/usr/bin/env bash\n\"$@\"\n")
        write_stub(bin_dir, "dnf", "#!/usr/bin/env bash\necho 'DNF_REMOVE_STUB remove -y vlc'\n")
        write_stub(
            bin_dir,
            "rpm",
            "#!/usr/bin/env bash\n"
            f"state={rpm_state!s}\n"
            "if [ -f \"$state\" ]; then\n"
            "  exit 1\n"
            "fi\n"
            "touch \"$state\"\n"
            "exit 0\n",
        )
        os_release = write_os_release(root, distro_id="fedora", distro_like="fedora", name="Fedora Linux")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}
        proc = run("remover", "vlc", env=env)
        assert proc.returncode == 0
        assert_in(proc.stdout, "DNF_REMOVE_STUB remove -y vlc")


def test_runtime_package_remove_noop_when_not_installed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "sudo", "#!/usr/bin/env bash\n\"$@\"\n")
        write_stub(bin_dir, "dnf", "#!/usr/bin/env bash\necho 'DNF_SHOULD_NOT_RUN'\n")
        write_stub(bin_dir, "rpm", "#!/usr/bin/env bash\nexit 1\n")
        os_release = write_os_release(root, distro_id="fedora", distro_like="fedora", name="Fedora Linux")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}
        proc = run("remover", "vlc", env=env)
        assert proc.returncode == 0
        assert_in(proc.stdout, "o pacote 'vlc' não está instalado neste host. Nada foi feito.")
        if "DNF_SHOULD_NOT_RUN" in proc.stdout:
            raise AssertionError("a remoção não deveria chamar o backend quando o pacote já está ausente")


def test_runtime_package_remove_opensuse() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        rpm_state = root / "rpm.state"
        rpm_state.write_text("installed\n", encoding="utf-8")
        write_stub(bin_dir, "sudo", "#!/usr/bin/env bash\n\"$@\"\n")
        write_stub(
            bin_dir,
            "zypper",
            "#!/usr/bin/env bash\n"
            f"state={rpm_state!s}\n"
            "if [ \"$1\" = \"--non-interactive\" ] && [ \"$2\" = \"remove\" ] && [ \"$4\" = \"vlc\" ]; then\n"
            "  rm -f \"$state\"\n"
            "fi\n"
            "printf 'ZYPPER_REMOVE_STUB %s\\n' \"$*\"\n",
        )
        write_stub(
            bin_dir,
            "rpm",
            "#!/usr/bin/env bash\n"
            f"state={rpm_state!s}\n"
            "if [ \"$1\" = \"-q\" ] && [ \"$2\" = \"vlc\" ]; then\n"
            "  if [ -f \"$state\" ]; then\n"
            "    exit 0\n"
            "  fi\n"
            "  exit 1\n"
            "fi\n"
            "exit 1\n",
        )
        os_release = write_os_release(root, distro_id="opensuse-tumbleweed", distro_like="opensuse suse", name="openSUSE Tumbleweed")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}
        proc = run("remover", "vlc", env=env)
        assert proc.returncode == 0
        assert_in(proc.stdout, "ZYPPER_REMOVE_STUB --non-interactive remove -- vlc")


def test_runtime_package_remove_opensuse_noop_when_not_installed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "sudo", "#!/usr/bin/env bash\n\"$@\"\n")
        write_stub(bin_dir, "zypper", "#!/usr/bin/env bash\necho 'ZYPPER_SHOULD_NOT_RUN'\n")
        write_stub(bin_dir, "rpm", "#!/usr/bin/env bash\nexit 1\n")
        os_release = write_os_release(root, distro_id="opensuse-tumbleweed", distro_like="opensuse suse", name="openSUSE Tumbleweed")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}
        proc = run("remover", "vlc", env=env)
        assert proc.returncode == 0
        assert_in(proc.stdout, "o pacote 'vlc' não está instalado neste host. Nada foi feito.")
        if "ZYPPER_SHOULD_NOT_RUN" in proc.stdout:
            raise AssertionError("a remoção em OpenSUSE não deveria chamar o backend quando o pacote já está ausente")


def test_runtime_package_remove_opensuse_requires_state_confirmation() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        rpm_state = root / "rpm.state"
        rpm_state.write_text("installed\n", encoding="utf-8")
        write_stub(bin_dir, "sudo", "#!/usr/bin/env bash\n\"$@\"\n")
        write_stub(bin_dir, "zypper", "#!/usr/bin/env bash\necho 'ZYPPER_REMOVE_STUB --non-interactive remove -- vlc'\n")
        write_stub(
            bin_dir,
            "rpm",
            "#!/usr/bin/env bash\n"
            f"state={rpm_state!s}\n"
            "if [ \"$1\" = \"-q\" ] && [ \"$2\" = \"vlc\" ]; then\n"
            "  if [ -f \"$state\" ]; then\n"
            "    exit 0\n"
            "  fi\n"
            "  exit 1\n"
            "fi\n"
            "exit 1\n",
        )
        os_release = write_os_release(root, distro_id="opensuse-tumbleweed", distro_like="opensuse suse", name="openSUSE Tumbleweed")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}
        proc = run("remover", "vlc", env=env)
        assert proc.returncode == 1
        assert_in(proc.stdout, "terminou sem eu conseguir confirmar a remoção de 'vlc'")


def test_runtime_package_opensuse_backend_missing() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        os_release = write_os_release(root, distro_id="opensuse-tumbleweed", distro_like="opensuse suse", name="openSUSE Tumbleweed")
        proc = run("procurar", "steam", env={"PATH": "", "AURY_OS_RELEASE_PATH": str(os_release)})
        assert proc.returncode == 1
        assert_in(proc.stdout, "backend 'zypper' não está disponível")


def test_runtime_package_opensuse_requires_auxiliary_state_probe() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "sudo", "#!/usr/bin/env bash\n\"$@\"\n")
        write_stub(bin_dir, "zypper", "#!/usr/bin/env bash\necho 'ZYPPER_SHOULD_NOT_RUN'\n")
        os_release = write_os_release(root, distro_id="opensuse-tumbleweed", distro_like="opensuse suse", name="openSUSE Tumbleweed")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}
        proc = run("instalar", "firefox", env=env)
        assert proc.returncode == 1
        assert_in(proc.stdout, "ferramenta auxiliar 'rpm'")
        if "ZYPPER_SHOULD_NOT_RUN" in proc.stdout:
            raise AssertionError("instalação em OpenSUSE não deveria rodar sem a ferramenta auxiliar de confirmação")


def test_runtime_package_atomic_without_backend_stays_policy_block() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        os_release = write_os_release(root, distro_id="bazzite", distro_like="fedora", name="Bazzite")
        env = {"PATH": "", "AURY_OS_RELEASE_PATH": str(os_release)}
        proc = run("procurar", "steam", env=env)
        assert proc.returncode == 1
        assert_in(proc.stdout, "bloqueado por política")
        if "backend '" in proc.stdout:
            raise AssertionError("host Atomic não pode parecer simples ausência de backend")


def test_runtime_package_atomic_without_probe_stays_policy_block() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "dnf", "#!/usr/bin/env bash\necho 'DNF_SHOULD_NOT_RUN'\n")
        os_release = write_os_release(root, distro_id="bazzite", distro_like="fedora", name="Bazzite")
        env = {"PATH": str(bin_dir), "AURY_OS_RELEASE_PATH": str(os_release)}
        proc = run("instalar", "firefox", env=env)
        assert proc.returncode == 1
        assert_in(proc.stdout, "bloqueado por política")
        if "ferramenta auxiliar" in proc.stdout:
            raise AssertionError("host Atomic não pode parecer ausência de sonda auxiliar")
        if "DNF_SHOULD_NOT_RUN" in proc.stdout:
            raise AssertionError("host Atomic não pode tentar mutar pacote do sistema")


def test_runtime_create_file() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        proc = subprocess.run(
            [sys.executable, "-m", "aury", "criar", "arquivo", "teste.txt"],
            cwd=workdir,
            env=ENV,
            text=True,
            capture_output=True,
            check=False,
        )
        if proc.returncode != 0:
            raise AssertionError(f"retorno inesperado: {proc.returncode!r} stdout={proc.stdout!r} stderr={proc.stderr!r}")
        assert_in(proc.stdout, "eu criei o arquivo 'teste.txt'")
        if not (workdir / "teste.txt").is_file():
            raise AssertionError("runtime Python não materializou o arquivo simples")


def test_runtime_create_folder_located() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        proc = subprocess.run(
            [sys.executable, "-m", "aury", "criar", "pasta", "Relatorios", "em", "Downloads"],
            cwd=workdir,
            env=ENV,
            text=True,
            capture_output=True,
            check=False,
        )
        if proc.returncode != 0:
            raise AssertionError(f"retorno inesperado: {proc.returncode!r} stdout={proc.stdout!r} stderr={proc.stderr!r}")
        assert_in(proc.stdout, "eu criei a pasta 'Downloads/Relatorios'")
        if not (workdir / "Downloads" / "Relatorios").is_dir():
            raise AssertionError("runtime Python não materializou a pasta localizada")


def test_dev_search_inflected_alignment() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "pacman", "#!/usr/bin/env bash\nexit 0\n")
        os_release = write_os_release(root, distro_id="cachyos", distro_like="arch", name="CachyOS")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}
        proc = run("dev", "procure", "steam", env=env)
        assert proc.returncode == 0
        assert_in(proc.stdout, "trecho original:               procure steam")
        assert_in(proc.stdout, "trecho normalizado:            procure steam")
        assert_in(proc.stdout, "intenção:                      procurar")
        assert_in(proc.stdout, "domínio:                       pacote")
        assert_in(proc.stdout, "alvo principal:                steam")
        assert_in(proc.stdout, "resumo:                        Procurar 'steam'.")
        assert_in(proc.stdout, "suportada agora")
        assert_in(proc.stdout, "rota suportada:                package_search")
        assert_in(proc.stdout, "backend necessário:            pacman")
        assert_in(proc.stdout, "decisão:                       executar no Python")
        assert_in(proc.stdout, "motivo:                        todas as ações têm rota explícita no runtime Python atual.")
        assert_in(
            proc.stdout,
            "motivo do plano:               o perfil do host Linux já resolve esta busca de pacote com backend explícito nesta fase, e a execução real trata ausência de resultado com saída honesta.",
        )


def test_dev_out_of_scope_plan_reason_alignment() -> None:
    proc = run("dev", "abra", "o", "arquivo", "relatorio.pdf")
    assert proc.returncode == 0
    assert_in(proc.stdout, "estado:                        NAO_ENQUADRADA")
    assert_in(proc.stdout, "lacunas:                       pedido fora do recorte")
    assert_in(proc.stdout, "motivo:                        a ação 1 ficou fora do recorte reconhecido com segurança.")
    assert_in(
        proc.stdout,
        "motivo do plano:               a ação ficou fora do recorte reconhecido com segurança para execução direta no runtime Python.",
    )


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


def test_runtime_multi_action_package_supported() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        vlc_state = root / "vlc.removed"
        write_stub(bin_dir, "sudo", "#!/usr/bin/env bash\n\"$@\"\n")
        write_stub(
            bin_dir,
            "pacman",
            "#!/usr/bin/env bash\n"
            f"state={vlc_state!s}\n"
            "if [ \"$1\" = \"-Q\" ] && [ \"$3\" = \"vlc\" ]; then\n"
            "  if [ -f \"$state\" ]; then\n"
            "    exit 1\n"
            "  fi\n"
            "  touch \"$state\"\n"
            "  exit 0\n"
            "fi\n"
            "echo 'PACMAN_MULTI_STUB'\n",
        )
        os_release = write_os_release(root, distro_id="cachyos", distro_like="arch", name="CachyOS")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}
        proc = run("procurar", "steam", "e", "remover", "vlc", env=env)
        assert proc.returncode == 0
        if proc.stdout.count("PACMAN_MULTI_STUB") != 2:
            raise AssertionError(f"multi-ação de pacote deveria executar as duas rotas no Python: {proc.stdout!r}")


def test_sensitive_tokens_contract() -> None:
    original = ["teste.tar.gz", "Downloads/token", "google.com"]
    protected, mapping = protect_sensitive_tokens(original)
    if [item.token_type for item in mapping] != ["file", "path", "host"]:
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
    if [item.token_type for item in protected_phrase.protected_tokens] != ["file", "path"]:
        raise AssertionError(
            f"tokens protegidos inesperados: {[item.token_type for item in protected_phrase.protected_tokens]!r}"
        )
    assert_in(protected_phrase.normalized_text, "teste.tar.gz")
    assert_in(protected_phrase.normalized_text, "Downloads/token")

    _chain_phrase, chain_actions = prepare_text("remova a pasta Aury que fica em Downloads e depois apague ela")
    if [action.original_action for action in chain_actions] != ["remova a pasta Aury que fica em Downloads", "apague ela"]:
        raise AssertionError(f"split destrutivo inesperado: {[action.original_action for action in chain_actions]!r}")

    _rename_chain_phrase, rename_chain_actions = prepare_text(
        "copie a pasta Aury que fica em origem para destino e renomeie ela para Aury-backup"
    )
    if [action.original_action for action in rename_chain_actions] != [
        "copie a pasta Aury que fica em origem para destino",
        "renomeie ela para Aury-backup",
    ]:
        raise AssertionError(
            f"split copiar+renomear inesperado: {[action.original_action for action in rename_chain_actions]!r}"
        )

    _sentence_chain_phrase, sentence_chain_actions = prepare_text(
        "copie a pasta Aury para Downloads. Depois mova ela para Backup."
    )
    if [action.original_action for action in sentence_chain_actions] != [
        "copie a pasta Aury para Downloads.",
        "mova ela para Backup.",
    ]:
        raise AssertionError(
            f"split copiar+mover entre frases inesperado: {[action.original_action for action in sentence_chain_actions]!r}"
        )


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


def test_prepare_analysis_explicit_package_target_strips_domain_noise() -> None:
    _phrase, _action, analysis = prepare_analysis("remover pacote vlc")
    if analysis.domain != "pacote":
        raise AssertionError(f"domínio inesperado: {analysis.domain!r}")
    if analysis.entities.get("alvo_principal") != "vlc":
        raise AssertionError(f"alvo principal inesperado: {analysis.entities.get('alvo_principal')!r}")
    if analysis.summary != "Remover 'vlc'.":
        raise AssertionError(f"resumo inesperado: {analysis.summary!r}")


def test_prepare_analysis_isolated_destructive_remove_local_reference_blocks() -> None:
    _phrase, _action, analysis = prepare_analysis("remover ela")
    if analysis.intent != "remover":
        raise AssertionError(f"intenção inesperada: {analysis.intent!r}")
    if analysis.domain != "arquivo":
        raise AssertionError(f"domínio inesperado: {analysis.domain!r}")
    if analysis.status != "BLOQUEADA":
        raise AssertionError(f"estado inesperado: {analysis.status!r}")
    if analysis.entities.get("referencia_local") != "ela (não resolvida)":
        raise AssertionError(f"referência local inesperada: {analysis.entities.get('referencia_local')!r}")
    if analysis.summary != "Remoção sem alvo seguro; leitura bloqueada.":
        raise AssertionError(f"resumo inesperado: {analysis.summary!r}")
    if "tipo" in analysis.entities:
        raise AssertionError(f"tipo não deveria existir: {analysis.entities.get('tipo')!r}")


def test_prepare_analysis_extract_conversational_destination_alignment() -> None:
    _phrase, _action, analysis = prepare_analysis("extraia pacote.tar.gz para a pasta que fica em extracao")
    if analysis.intent != "extrair":
        raise AssertionError(f"intenção inesperada: {analysis.intent!r}")
    if analysis.domain != "pasta":
        raise AssertionError(f"domínio inesperado: {analysis.domain!r}")
    if analysis.status != "CONSISTENTE":
        raise AssertionError(f"estado inesperado: {analysis.status!r}")
    if analysis.entities.get("tipo") != "tar.gz":
        raise AssertionError(f"tipo inesperado: {analysis.entities.get('tipo')!r}")
    if analysis.entities.get("arquivo_compactado") != "pacote.tar.gz":
        raise AssertionError(
            f"arquivo compactado inesperado: {analysis.entities.get('arquivo_compactado')!r}"
        )
    if analysis.entities.get("alvo_principal") != "pacote.tar.gz":
        raise AssertionError(f"alvo principal inesperado: {analysis.entities.get('alvo_principal')!r}")
    if analysis.entities.get("destino") != "extracao":
        raise AssertionError(f"destino inesperado: {analysis.entities.get('destino')!r}")
    if analysis.entities.get("localizacao_conversacional") != "destino simples: extracao":
        raise AssertionError(
            f"localização inesperada: {analysis.entities.get('localizacao_conversacional')!r}"
        )
    if analysis.summary != "Extrair 'pacote.tar.gz' para 'extracao'.":
        raise AssertionError(f"resumo inesperado: {analysis.summary!r}")
    if not any("localização conversacional simples" in item for item in analysis.observations):
        raise AssertionError(f"observações inesperadas: {analysis.observations!r}")
    if not any("adaptador Fish" in item for item in analysis.observations):
        raise AssertionError(f"observações inesperadas: {analysis.observations!r}")


def test_prepare_analysis_located_rename_alignment() -> None:
    _phrase, _action, analysis = prepare_analysis(
        "renomeie o arquivo teste.txt que fica em Downloads para teste-final.txt"
    )
    if analysis.intent != "renomear":
        raise AssertionError(f"intenção inesperada: {analysis.intent!r}")
    if analysis.domain != "arquivo":
        raise AssertionError(f"domínio inesperado: {analysis.domain!r}")
    if analysis.status != "CONSISTENTE":
        raise AssertionError(f"estado inesperado: {analysis.status!r}")
    if analysis.entities.get("tipo") != "arquivo":
        raise AssertionError(f"tipo inesperado: {analysis.entities.get('tipo')!r}")
    if analysis.entities.get("alvo_principal") != "Downloads/teste.txt":
        raise AssertionError(f"alvo principal inesperado: {analysis.entities.get('alvo_principal')!r}")
    if analysis.entities.get("origem") != "Downloads/teste.txt":
        raise AssertionError(f"origem inesperada: {analysis.entities.get('origem')!r}")
    if analysis.entities.get("destino") != "Downloads/teste-final.txt":
        raise AssertionError(f"destino inesperado: {analysis.entities.get('destino')!r}")
    if analysis.entities.get("novo_nome") != "teste-final.txt":
        raise AssertionError(f"novo nome inesperado: {analysis.entities.get('novo_nome')!r}")
    if analysis.summary != "Renomear 'Downloads/teste.txt' para 'Downloads/teste-final.txt'.":
        raise AssertionError(f"resumo inesperado: {analysis.summary!r}")
    if not any("base 'Downloads'" in item for item in analysis.observations):
        raise AssertionError(f"observações inesperadas: {analysis.observations!r}")


def test_prepare_analysis_extract_explicit_real_path_destination_alignment() -> None:
    _phrase, _action, analysis = prepare_analysis("extraia pacote.tar.gz para /usr/steam")
    if analysis.intent != "extrair":
        raise AssertionError(f"intenção inesperada: {analysis.intent!r}")
    if analysis.domain != "arquivo":
        raise AssertionError(f"domínio inesperado: {analysis.domain!r}")
    if analysis.status != "CONSISTENTE":
        raise AssertionError(f"estado inesperado: {analysis.status!r}")
    if analysis.entities.get("tipo") != "tar.gz":
        raise AssertionError(f"tipo inesperado: {analysis.entities.get('tipo')!r}")
    if analysis.entities.get("arquivo_compactado") != "pacote.tar.gz":
        raise AssertionError(
            f"arquivo compactado inesperado: {analysis.entities.get('arquivo_compactado')!r}"
        )
    if analysis.entities.get("alvo_principal") != "pacote.tar.gz":
        raise AssertionError(f"alvo principal inesperado: {analysis.entities.get('alvo_principal')!r}")
    if analysis.entities.get("destino") != "/usr/steam":
        raise AssertionError(f"destino inesperado: {analysis.entities.get('destino')!r}")
    if analysis.summary != "Extrair 'pacote.tar.gz' para '/usr/steam'.":
        raise AssertionError(f"resumo inesperado: {analysis.summary!r}")
    if "localizacao_conversacional" in analysis.entities:
        raise AssertionError(
            f"localização conversacional não deveria existir: {analysis.entities.get('localizacao_conversacional')!r}"
        )
    if not any("caminho real" in item for item in analysis.observations):
        raise AssertionError(f"observações inesperadas: {analysis.observations!r}")
    if not any("adaptador Fish" in item for item in analysis.observations):
        raise AssertionError(f"observações inesperadas: {analysis.observations!r}")


def test_prepare_analysis_compact_alignment() -> None:
    _phrase, _action, analysis = prepare_analysis("compacte pasta projetos/ para projetos.tar.gz")
    if analysis.intent != "compactar":
        raise AssertionError(f"intenção inesperada: {analysis.intent!r}")
    if analysis.domain != "arquivo":
        raise AssertionError(f"domínio inesperado: {analysis.domain!r}")
    if analysis.status != "CONSISTENTE":
        raise AssertionError(f"estado inesperado: {analysis.status!r}")
    if analysis.entities.get("tipo") != "tar.gz":
        raise AssertionError(f"tipo inesperado: {analysis.entities.get('tipo')!r}")
    if analysis.entities.get("tipo_de_origem") != "pasta":
        raise AssertionError(f"tipo de origem inesperado: {analysis.entities.get('tipo_de_origem')!r}")
    if analysis.entities.get("origem") != "projetos/":
        raise AssertionError(f"origem inesperada: {analysis.entities.get('origem')!r}")
    if analysis.entities.get("saida") != "projetos.tar.gz":
        raise AssertionError(f"saída inesperada: {analysis.entities.get('saida')!r}")
    if analysis.summary != "Compactar 'projetos/' em 'projetos.tar.gz'.":
        raise AssertionError(f"resumo inesperado: {analysis.summary!r}")


def test_prepare_analysis_compact_invalid_format_blocks() -> None:
    _phrase, _action, analysis = prepare_analysis("compactar arquivo teste.txt para teste.rar")
    if analysis.intent != "compactar":
        raise AssertionError(f"intenção inesperada: {analysis.intent!r}")
    if analysis.status != "BLOQUEADA":
        raise AssertionError(f"estado inesperado: {analysis.status!r}")
    if analysis.entities.get("lacuna") != "saída .zip ou .tar.gz":
        raise AssertionError(f"lacuna inesperada: {analysis.entities.get('lacuna')!r}")
    if analysis.entities.get("saida") != "teste.rar":
        raise AssertionError(f"saída inesperada: {analysis.entities.get('saida')!r}")
    if analysis.summary != "Saída fora do recorte da compactação; leitura bloqueada.":
        raise AssertionError(f"resumo inesperado: {analysis.summary!r}")


def test_prepare_analyses_copy_rename_local_reference_alignment() -> None:
    _phrase, actions, analyses = prepare_analyses(
        "copie a pasta Aury que fica em origem para destino e renomeie ela para Aury-backup"
    )
    if [action.original_action for action in actions] != [
        "copie a pasta Aury que fica em origem para destino",
        "renomeie ela para Aury-backup",
    ]:
        raise AssertionError(f"ações preparadas inesperadas: {[action.original_action for action in actions]!r}")
    if analyses[0].intent != "copiar":
        raise AssertionError(f"intenção inesperada na primeira ação: {analyses[0].intent!r}")
    if analyses[0].domain != "arquivo":
        raise AssertionError(f"domínio inesperado na primeira ação: {analyses[0].domain!r}")
    if analyses[0].entities.get("tipo") != "pasta":
        raise AssertionError(f"tipo inesperado na primeira ação: {analyses[0].entities.get('tipo')!r}")
    if analyses[0].entities.get("origem") != "origem/Aury":
        raise AssertionError(f"origem inesperada na primeira ação: {analyses[0].entities.get('origem')!r}")
    if analyses[0].entities.get("destino") != "destino/Aury":
        raise AssertionError(f"destino inesperado na primeira ação: {analyses[0].entities.get('destino')!r}")
    if analyses[1].intent != "renomear":
        raise AssertionError(f"intenção inesperada na segunda ação: {analyses[1].intent!r}")
    if analyses[1].status != "CONSISTENTE":
        raise AssertionError(f"estado inesperado na segunda ação: {analyses[1].status!r}")
    if analyses[1].domain != "arquivo":
        raise AssertionError(f"domínio inesperado na segunda ação: {analyses[1].domain!r}")
    if analyses[1].entities.get("tipo") != "pasta":
        raise AssertionError(f"tipo inesperado na segunda ação: {analyses[1].entities.get('tipo')!r}")
    if analyses[1].entities.get("alvo_principal") != "destino/Aury":
        raise AssertionError(f"alvo principal inesperado na segunda ação: {analyses[1].entities.get('alvo_principal')!r}")
    if analyses[1].entities.get("origem") != "destino/Aury":
        raise AssertionError(f"origem inesperada na segunda ação: {analyses[1].entities.get('origem')!r}")
    if analyses[1].entities.get("destino") != "destino/Aury-backup":
        raise AssertionError(f"destino inesperado na segunda ação: {analyses[1].entities.get('destino')!r}")
    if analyses[1].entities.get("novo_nome") != "Aury-backup":
        raise AssertionError(f"novo nome inesperado na segunda ação: {analyses[1].entities.get('novo_nome')!r}")
    if analyses[1].entities.get("referencia_local") != "destino/Aury":
        raise AssertionError(
            f"referência local inesperada na segunda ação: {analyses[1].entities.get('referencia_local')!r}"
        )
    if analyses[1].summary != "Renomear 'destino/Aury' para 'destino/Aury-backup'.":
        raise AssertionError(f"resumo inesperado na segunda ação: {analyses[1].summary!r}")
    if not any("referência local 'ela' resolvida com segurança como 'destino/Aury'" in item for item in analyses[1].observations):
        raise AssertionError(f"observações inesperadas na segunda ação: {analyses[1].observations!r}")


def test_prepare_analyses_copy_rename_file_local_reference_alignment() -> None:
    _phrase, actions, analyses = prepare_analyses("copie o arquivo teste.txt para copia.txt e renomeie ele para final.txt")
    if [action.original_action for action in actions] != [
        "copie o arquivo teste.txt para copia.txt",
        "renomeie ele para final.txt",
    ]:
        raise AssertionError(f"ações preparadas inesperadas: {[action.original_action for action in actions]!r}")
    if analyses[0].intent != "copiar":
        raise AssertionError(f"intenção inesperada na primeira ação: {analyses[0].intent!r}")
    if analyses[0].status != "CONSISTENTE":
        raise AssertionError(f"estado inesperado na primeira ação: {analyses[0].status!r}")
    if analyses[0].entities.get("tipo") != "arquivo":
        raise AssertionError(f"tipo inesperado na primeira ação: {analyses[0].entities.get('tipo')!r}")
    if analyses[0].entities.get("origem") != "teste.txt":
        raise AssertionError(f"origem inesperada na primeira ação: {analyses[0].entities.get('origem')!r}")
    if analyses[0].entities.get("destino") != "copia.txt":
        raise AssertionError(f"destino inesperado na primeira ação: {analyses[0].entities.get('destino')!r}")
    if analyses[1].intent != "renomear":
        raise AssertionError(f"intenção inesperada na segunda ação: {analyses[1].intent!r}")
    if analyses[1].status != "CONSISTENTE":
        raise AssertionError(f"estado inesperado na segunda ação: {analyses[1].status!r}")
    if analyses[1].domain != "arquivo":
        raise AssertionError(f"domínio inesperado na segunda ação: {analyses[1].domain!r}")
    if analyses[1].entities.get("tipo") != "arquivo":
        raise AssertionError(f"tipo inesperado na segunda ação: {analyses[1].entities.get('tipo')!r}")
    if analyses[1].entities.get("alvo_principal") != "copia.txt":
        raise AssertionError(f"alvo principal inesperado na segunda ação: {analyses[1].entities.get('alvo_principal')!r}")
    if analyses[1].entities.get("origem") != "copia.txt":
        raise AssertionError(f"origem inesperada na segunda ação: {analyses[1].entities.get('origem')!r}")
    if analyses[1].entities.get("destino") != "final.txt":
        raise AssertionError(f"destino inesperado na segunda ação: {analyses[1].entities.get('destino')!r}")
    if analyses[1].entities.get("novo_nome") != "final.txt":
        raise AssertionError(f"novo nome inesperado na segunda ação: {analyses[1].entities.get('novo_nome')!r}")
    if analyses[1].entities.get("referencia_local") != "copia.txt":
        raise AssertionError(
            f"referência local inesperada na segunda ação: {analyses[1].entities.get('referencia_local')!r}"
        )
    if analyses[1].summary != "Renomear 'copia.txt' para 'final.txt'.":
        raise AssertionError(f"resumo inesperado na segunda ação: {analyses[1].summary!r}")
    if not any("referência local 'ele' resolvida com segurança como 'copia.txt'" in item for item in analyses[1].observations):
        raise AssertionError(f"observações inesperadas na segunda ação: {analyses[1].observations!r}")


def test_prepare_analyses_move_rename_file_local_reference_alignment() -> None:
    _phrase, actions, analyses = prepare_analyses("mova o arquivo teste.txt para pasta2/final.txt e renomeie ele para ultimo.txt")
    if [action.original_action for action in actions] != [
        "mova o arquivo teste.txt para pasta2/final.txt",
        "renomeie ele para ultimo.txt",
    ]:
        raise AssertionError(f"ações preparadas inesperadas: {[action.original_action for action in actions]!r}")
    if analyses[0].intent != "mover":
        raise AssertionError(f"intenção inesperada na primeira ação: {analyses[0].intent!r}")
    if analyses[0].status != "CONSISTENTE":
        raise AssertionError(f"estado inesperado na primeira ação: {analyses[0].status!r}")
    if analyses[0].entities.get("tipo") != "arquivo":
        raise AssertionError(f"tipo inesperado na primeira ação: {analyses[0].entities.get('tipo')!r}")
    if analyses[0].entities.get("origem") != "teste.txt":
        raise AssertionError(f"origem inesperada na primeira ação: {analyses[0].entities.get('origem')!r}")
    if analyses[0].entities.get("destino") != "pasta2/final.txt":
        raise AssertionError(f"destino inesperado na primeira ação: {analyses[0].entities.get('destino')!r}")
    if analyses[1].intent != "renomear":
        raise AssertionError(f"intenção inesperada na segunda ação: {analyses[1].intent!r}")
    if analyses[1].status != "CONSISTENTE":
        raise AssertionError(f"estado inesperado na segunda ação: {analyses[1].status!r}")
    if analyses[1].domain != "arquivo":
        raise AssertionError(f"domínio inesperado na segunda ação: {analyses[1].domain!r}")
    if analyses[1].entities.get("tipo") != "arquivo":
        raise AssertionError(f"tipo inesperado na segunda ação: {analyses[1].entities.get('tipo')!r}")
    if analyses[1].entities.get("alvo_principal") != "pasta2/final.txt":
        raise AssertionError(f"alvo principal inesperado na segunda ação: {analyses[1].entities.get('alvo_principal')!r}")
    if analyses[1].entities.get("origem") != "pasta2/final.txt":
        raise AssertionError(f"origem inesperada na segunda ação: {analyses[1].entities.get('origem')!r}")
    if analyses[1].entities.get("destino") != "pasta2/ultimo.txt":
        raise AssertionError(f"destino inesperado na segunda ação: {analyses[1].entities.get('destino')!r}")
    if analyses[1].entities.get("novo_nome") != "ultimo.txt":
        raise AssertionError(f"novo nome inesperado na segunda ação: {analyses[1].entities.get('novo_nome')!r}")
    if analyses[1].entities.get("referencia_local") != "pasta2/final.txt":
        raise AssertionError(
            f"referência local inesperada na segunda ação: {analyses[1].entities.get('referencia_local')!r}"
        )
    if analyses[1].summary != "Renomear 'pasta2/final.txt' para 'pasta2/ultimo.txt'.":
        raise AssertionError(f"resumo inesperado na segunda ação: {analyses[1].summary!r}")
    if not any("referência local 'ele' resolvida com segurança como 'pasta2/final.txt'" in item for item in analyses[1].observations):
        raise AssertionError(f"observações inesperadas na segunda ação: {analyses[1].observations!r}")


def test_prepare_analyses_move_rename_file_local_reference_requires_explicit_destination_shape() -> None:
    _phrase, actions, analyses = prepare_analyses("mova o arquivo teste.txt para pasta2 e renomeie ele para final.txt")
    if [action.original_action for action in actions] != [
        "mova o arquivo teste.txt para pasta2",
        "renomeie ele para final.txt",
    ]:
        raise AssertionError(f"ações preparadas inesperadas: {[action.original_action for action in actions]!r}")
    if analyses[0].intent != "mover":
        raise AssertionError(f"intenção inesperada na primeira ação: {analyses[0].intent!r}")
    if analyses[0].status != "CONSISTENTE":
        raise AssertionError(f"estado inesperado na primeira ação: {analyses[0].status!r}")
    if analyses[1].intent != "não identificada":
        raise AssertionError(f"intenção inesperada na segunda ação: {analyses[1].intent!r}")
    if analyses[1].status != "NAO_ENQUADRADA":
        raise AssertionError(f"estado inesperado na segunda ação: {analyses[1].status!r}")


def test_prepare_analyses_sentence_chain_move_local_reference_alignment() -> None:
    _phrase, actions, analyses = prepare_analyses("copie a pasta Aury para Downloads. Depois mova ela para Backup.")
    if [action.original_action for action in actions] != ["copie a pasta Aury para Downloads.", "mova ela para Backup."]:
        raise AssertionError(f"ações preparadas inesperadas: {[action.original_action for action in actions]!r}")
    if analyses[0].intent != "copiar":
        raise AssertionError(f"intenção inesperada na primeira ação: {analyses[0].intent!r}")
    if analyses[0].status != "CONSISTENTE":
        raise AssertionError(f"estado inesperado na primeira ação: {analyses[0].status!r}")
    if analyses[0].entities.get("tipo") != "pasta":
        raise AssertionError(f"tipo inesperado na primeira ação: {analyses[0].entities.get('tipo')!r}")
    if analyses[0].entities.get("origem") != "Aury":
        raise AssertionError(f"origem inesperada na primeira ação: {analyses[0].entities.get('origem')!r}")
    if analyses[0].entities.get("destino") != "Downloads/Aury":
        raise AssertionError(f"destino inesperado na primeira ação: {analyses[0].entities.get('destino')!r}")
    if analyses[1].intent != "mover":
        raise AssertionError(f"intenção inesperada na segunda ação: {analyses[1].intent!r}")
    if analyses[1].status != "CONSISTENTE":
        raise AssertionError(f"estado inesperado na segunda ação: {analyses[1].status!r}")
    if analyses[1].domain != "arquivo":
        raise AssertionError(f"domínio inesperado na segunda ação: {analyses[1].domain!r}")
    if analyses[1].entities.get("tipo") != "pasta":
        raise AssertionError(f"tipo inesperado na segunda ação: {analyses[1].entities.get('tipo')!r}")
    if analyses[1].entities.get("alvo_principal") != "Downloads/Aury":
        raise AssertionError(f"alvo principal inesperado na segunda ação: {analyses[1].entities.get('alvo_principal')!r}")
    if analyses[1].entities.get("origem") != "Downloads/Aury":
        raise AssertionError(f"origem inesperada na segunda ação: {analyses[1].entities.get('origem')!r}")
    if analyses[1].entities.get("destino") != "Backup/Aury":
        raise AssertionError(f"destino inesperado na segunda ação: {analyses[1].entities.get('destino')!r}")
    if analyses[1].entities.get("referencia_local") != "Downloads/Aury":
        raise AssertionError(
            f"referência local inesperada na segunda ação: {analyses[1].entities.get('referencia_local')!r}"
        )
    if analyses[1].summary != "Mover 'Downloads/Aury' para 'Backup/Aury'.":
        raise AssertionError(f"resumo inesperado na segunda ação: {analyses[1].summary!r}")
    if not any("referência local 'ela' resolvida com segurança como 'Downloads/Aury'" in item for item in analyses[1].observations):
        raise AssertionError(f"observações inesperadas na segunda ação: {analyses[1].observations!r}")


def test_prepare_analyses_multiple_actions() -> None:
    phrase, actions, analyses = prepare_analyses("Aury, procurar steam e remover vlc")
    if phrase.original_text != "procurar steam e remover vlc":
        raise AssertionError(f"frase preparada inesperada: {phrase.original_text!r}")
    if [action.original_action for action in actions] != ["procurar steam", "remover vlc"]:
        raise AssertionError(f"ações preparadas inesperadas: {[action.original_action for action in actions]!r}")
    if [analysis.summary for analysis in analyses] != ["Procurar 'steam'.", "Remover 'vlc'."]:
        raise AssertionError(f"análises inesperadas: {[analysis.summary for analysis in analyses]!r}")


def test_prepare_analyses_destructive_remove_followup_reuses_safe_local_reference() -> None:
    _phrase, actions, analyses = prepare_analyses("remova a pasta Aury que fica em Downloads e depois apague ela")
    if [action.original_action for action in actions] != ["remova a pasta Aury que fica em Downloads", "apague ela"]:
        raise AssertionError(f"ações preparadas inesperadas: {[action.original_action for action in actions]!r}")
    if analyses[0].summary != "Remover 'Downloads/Aury'.":
        raise AssertionError(f"primeira análise inesperada: {analyses[0].summary!r}")
    if analyses[1].intent != "remover":
        raise AssertionError(f"intenção inesperada: {analyses[1].intent!r}")
    if analyses[1].status != "BLOQUEADA":
        raise AssertionError(f"estado inesperado: {analyses[1].status!r}")
    if analyses[1].domain != "arquivo":
        raise AssertionError(f"domínio inesperado: {analyses[1].domain!r}")
    if analyses[1].entities.get("tipo") != "pasta":
        raise AssertionError(f"tipo inesperado: {analyses[1].entities.get('tipo')!r}")
    if analyses[1].entities.get("alvo_principal") != "Downloads/Aury":
        raise AssertionError(f"alvo principal inesperado: {analyses[1].entities.get('alvo_principal')!r}")
    if analyses[1].entities.get("origem") != "Downloads/Aury":
        raise AssertionError(f"origem inesperada: {analyses[1].entities.get('origem')!r}")
    if analyses[1].entities.get("referencia_local") != "Downloads/Aury":
        raise AssertionError(f"referência local inesperada: {analyses[1].entities.get('referencia_local')!r}")
    if analyses[1].entities.get("lacuna") != "alinhamento com runtime atual":
        raise AssertionError(f"lacuna inesperada: {analyses[1].entities.get('lacuna')!r}")
    if analyses[1].summary != "Remoção de 'Downloads/Aury' reconhecida, mas bloqueada no estado atual.":
        raise AssertionError(f"resumo inesperado: {analyses[1].summary!r}")
    if "foi resolvida com segurança" not in analyses[1].reason:
        raise AssertionError(f"motivo inesperado: {analyses[1].reason!r}")

def test_prepare_analyses_destructive_remove_with_previous_package_context_blocks_local_reference() -> None:
    _phrase, actions, analyses = prepare_analyses("procurar steam e depois remover ele")
    if [action.original_action for action in actions] != ["procurar steam", "remover ele"]:
        raise AssertionError(f"ações preparadas inesperadas: {[action.original_action for action in actions]!r}")
    if analyses[1].intent != "remover":
        raise AssertionError(f"intenção inesperada: {analyses[1].intent!r}")
    if analyses[1].domain != "arquivo":
        raise AssertionError(f"domínio inesperado: {analyses[1].domain!r}")
    if analyses[1].status != "BLOQUEADA":
        raise AssertionError(f"estado inesperado: {analyses[1].status!r}")
    if analyses[1].entities.get("referencia_local") != "ele":
        raise AssertionError(f"referência local inesperada: {analyses[1].entities.get('referencia_local')!r}")
    if analyses[1].summary != "Remoção sem alvo seguro; leitura bloqueada.":
        raise AssertionError(f"resumo inesperado: {analyses[1].summary!r}")
    if "contexto anterior" not in analyses[1].reason:
        raise AssertionError(f"motivo inesperado: {analyses[1].reason!r}")
    if not any("domínio 'pacote'" in item and "alvo 'steam'" in item for item in analyses[1].observations):
        raise AssertionError(f"observações inesperadas: {analyses[1].observations!r}")


def test_prepare_analyses_destructive_remove_with_previous_file_context_blocks_incompatible_local_reference() -> None:
    _phrase, actions, analyses = prepare_analyses("criar pasta Aury e depois remover ele")
    if [action.original_action for action in actions] != ["criar pasta Aury", "remover ele"]:
        raise AssertionError(f"ações preparadas inesperadas: {[action.original_action for action in actions]!r}")
    if analyses[0].entities.get("tipo") != "pasta":
        raise AssertionError(f"tipo inesperado na primeira ação: {analyses[0].entities.get('tipo')!r}")
    if analyses[1].intent != "remover":
        raise AssertionError(f"intenção inesperada: {analyses[1].intent!r}")
    if analyses[1].domain != "arquivo":
        raise AssertionError(f"domínio inesperado: {analyses[1].domain!r}")
    if analyses[1].status != "BLOQUEADA":
        raise AssertionError(f"estado inesperado: {analyses[1].status!r}")
    if analyses[1].entities.get("referencia_local") != "ele":
        raise AssertionError(f"referência local inesperada: {analyses[1].entities.get('referencia_local')!r}")
    if not any("tipo 'pasta'" in item and "alvo 'Aury'" in item for item in analyses[1].observations):
        raise AssertionError(f"observações inesperadas: {analyses[1].observations!r}")


def test_prepare_analyses_destructive_remove_followup_reuses_safe_file_reference() -> None:
    _phrase, actions, analyses = prepare_analyses("remova o arquivo teste.txt que fica em destino e depois apague ele")
    if [action.original_action for action in actions] != ["remova o arquivo teste.txt que fica em destino", "apague ele"]:
        raise AssertionError(f"ações preparadas inesperadas: {[action.original_action for action in actions]!r}")
    if analyses[1].intent != "remover":
        raise AssertionError(f"intenção inesperada: {analyses[1].intent!r}")
    if analyses[1].domain != "arquivo":
        raise AssertionError(f"domínio inesperado: {analyses[1].domain!r}")
    if analyses[1].status != "BLOQUEADA":
        raise AssertionError(f"estado inesperado: {analyses[1].status!r}")
    if analyses[1].entities.get("tipo") != "arquivo":
        raise AssertionError(f"tipo inesperado: {analyses[1].entities.get('tipo')!r}")
    if analyses[1].entities.get("alvo_principal") != "destino/teste.txt":
        raise AssertionError(f"alvo principal inesperado: {analyses[1].entities.get('alvo_principal')!r}")
    if analyses[1].entities.get("origem") != "destino/teste.txt":
        raise AssertionError(f"origem inesperada: {analyses[1].entities.get('origem')!r}")
    if analyses[1].entities.get("referencia_local") != "destino/teste.txt":
        raise AssertionError(f"referência local inesperada: {analyses[1].entities.get('referencia_local')!r}")
    if analyses[1].entities.get("lacuna") != "alinhamento com runtime atual":
        raise AssertionError(f"lacuna inesperada: {analyses[1].entities.get('lacuna')!r}")
    if analyses[1].summary != "Remoção de 'destino/teste.txt' reconhecida, mas bloqueada no estado atual.":
        raise AssertionError(f"resumo inesperado: {analyses[1].summary!r}")


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


def test_action_execution_plan_supported_now_for_create_file() -> None:
    _phrase, _action, analysis = prepare_analysis("criar arquivo teste.txt")
    action_plan = plan_action_execution(analysis)
    if action_plan.status != "SUPPORTED_NOW":
        raise AssertionError(f"classificação inesperada: {action_plan.status!r}")
    if action_plan.route != "file_create":
        raise AssertionError(f"rota inesperada: {action_plan.route!r}")
    if action_plan.backend != "runtime Python":
        raise AssertionError(f"backend inesperado: {action_plan.backend!r}")


def test_action_execution_plan_supported_now_for_create_folder() -> None:
    _phrase, _action, analysis = prepare_analysis("criar pasta projetos/")
    action_plan = plan_action_execution(analysis)
    if action_plan.status != "SUPPORTED_NOW":
        raise AssertionError(f"classificação inesperada: {action_plan.status!r}")
    if action_plan.route != "folder_create":
        raise AssertionError(f"rota inesperada: {action_plan.route!r}")
    if action_plan.backend != "runtime Python":
        raise AssertionError(f"backend inesperado: {action_plan.backend!r}")


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
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "pacman", "#!/usr/bin/env bash\nexit 0\n")
        os_release = write_os_release(root, distro_id="cachyos", distro_like="arch", name="CachyOS")
        _phrase, _action, analysis = prepare_analysis("remover vlc")
        with temporary_env({"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}):
            action_plan = plan_action_execution(analysis)
        if action_plan.status != "SUPPORTED_NOW":
            raise AssertionError(f"classificação inesperada: {action_plan.status!r}")
        if action_plan.route != "package_remove":
            raise AssertionError(f"rota inesperada: {action_plan.route!r}")
        if action_plan.backend != "sudo + pacman":
            raise AssertionError(f"backend inesperado: {action_plan.backend!r}")
        if not action_plan.executes_in_python:
            raise AssertionError("a remoção de pacote em Tier 1 já deve fechar direto no runtime Python")


def test_action_execution_plan_fish_fallback_reason_for_out_of_scope() -> None:
    _phrase, _action, analysis = prepare_analysis("abra o arquivo relatorio.pdf")
    action_plan = plan_action_execution(analysis)
    if action_plan.status != "FISH_FALLBACK":
        raise AssertionError(f"classificação inesperada: {action_plan.status!r}")
    if action_plan.reason != "a ação ficou fora do recorte reconhecido com segurança para execução direta no runtime Python.":
        raise AssertionError(f"motivo inesperado: {action_plan.reason!r}")


def test_sequence_execution_plan_supported_now() -> None:
    _phrase, _actions, analyses = prepare_analyses("ver ip e status")
    sequence_plan = plan_sequence_execution(analyses)
    if sequence_plan.decision != "EXECUTE_IN_PYTHON":
        raise AssertionError(f"decisão inesperada: {sequence_plan.decision!r}")
    if len(sequence_plan.action_plans) != 2:
        raise AssertionError(f"plano de sequência inesperado: {len(sequence_plan.action_plans)!r}")


def test_sequence_execution_plan_returns_to_fish() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "pacman", "#!/usr/bin/env bash\nexit 0\n")
        os_release = write_os_release(root, distro_id="cachyos", distro_like="arch", name="CachyOS")
        _phrase, _actions, analyses = prepare_analyses("procurar steam e remover vlc")
        with temporary_env({"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}):
            sequence_plan = plan_sequence_execution(analyses)
        if sequence_plan.decision != "EXECUTE_IN_PYTHON":
            raise AssertionError(f"decisão inesperada: {sequence_plan.decision!r}")
        if sequence_plan.action_plans[1].status != "SUPPORTED_NOW":
            raise AssertionError(f"classificação inesperada: {sequence_plan.action_plans[1].status!r}")


def test_sequence_execution_plan_return_reason_for_blocked_gap() -> None:
    _phrase, _actions, analyses = prepare_analyses("compactar arquivo teste.txt")
    sequence_plan = plan_sequence_execution(analyses)
    if sequence_plan.decision != "RETURN_TO_FISH":
        raise AssertionError(f"decisão inesperada: {sequence_plan.decision!r}")
    if sequence_plan.reason != "a ação 1 ficou bloqueada por lacuna explícita: saída explícita obrigatória.":
        raise AssertionError(f"motivo inesperado: {sequence_plan.reason!r}")


def test_dev_multiple_actions() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "pacman", "#!/usr/bin/env bash\nexit 0\n")
        os_release = write_os_release(root, distro_id="cachyos", distro_like="arch", name="CachyOS")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}
        phrase = "procurar steam e remover vlc"
        proc = run("dev", *phrase.split(), env=env)
        assert proc.returncode == 0
        assert_in(proc.stdout, "Plano da sequência")
        assert_in(proc.stdout, "Ação 1")
        assert_in(proc.stdout, "Ação 2")
        assert_in(proc.stdout, "suportada agora")
        assert_in(proc.stdout, "executar no Python")
        assert_in(proc.stdout, "resumo:                        Procurar 'steam'.")
        assert_in(proc.stdout, "resumo:                        Remover 'vlc'.")
        assert_in(proc.stdout, "rota suportada:                package_search")
        assert_in(proc.stdout, "rota suportada:                package_remove")


def test_detect_host_profile_tiers() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "zypper", "#!/usr/bin/env bash\nexit 0\n")
        os_release = write_os_release(root, distro_id="opensuse-tumbleweed", distro_like="opensuse suse", name="openSUSE Tumbleweed")
        with temporary_env({"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}):
            host_profile = detect_host_profile()
        if host_profile.linux_family != "opensuse":
            raise AssertionError(f"família inesperada: {host_profile.linux_family!r}")
        if host_profile.support_tier != "tier_2":
            raise AssertionError(f"tier inesperado: {host_profile.support_tier!r}")
        if host_profile.support_tier_label != "Tier 2 útil contido":
            raise AssertionError(f"rótulo inesperado: {host_profile.support_tier_label!r}")
        if "zypper" not in host_profile.package_backends:
            raise AssertionError(f"backend inesperado: {host_profile.package_backends!r}")


def test_detect_host_profile_atomic_frontier_labels() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "dnf", "#!/usr/bin/env bash\nexit 0\n")
        os_release = write_os_release(root, distro_id="bluefin", distro_like="fedora", name="Bluefin")
        with temporary_env({"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}):
            host_profile = detect_host_profile()
        if host_profile.linux_family != "fedora":
            raise AssertionError(f"família inesperada: {host_profile.linux_family!r}")
        if host_profile.mutability != "atomic":
            raise AssertionError(f"mutabilidade inesperada: {host_profile.mutability!r}")
        if host_profile.support_tier_label != "suporte limitado":
            raise AssertionError(f"tier inesperado: {host_profile.support_tier_label!r}")
        if host_profile.compatibility_frontier_label != "bloqueado por política":
            raise AssertionError(f"fronteira inesperada: {host_profile.compatibility_frontier_label!r}")


def test_detect_host_profile_opensuse_microos_is_atomic() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "zypper", "#!/usr/bin/env bash\nexit 0\n")
        os_release = write_os_release(root, distro_id="opensuse-microos", distro_like="opensuse suse", name="openSUSE MicroOS")
        with temporary_env({"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}):
            host_profile = detect_host_profile()
        if host_profile.linux_family != "opensuse":
            raise AssertionError(f"família inesperada: {host_profile.linux_family!r}")
        if host_profile.mutability != "atomic":
            raise AssertionError(f"mutabilidade inesperada: {host_profile.mutability!r}")
        if host_profile.support_tier != "limited":
            raise AssertionError(f"tier inesperado: {host_profile.support_tier!r}")
        if host_profile.compatibility_frontier_label != "bloqueado por política":
            raise AssertionError(f"fronteira inesperada: {host_profile.compatibility_frontier_label!r}")


def test_package_policy_opensuse_supported_now() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "zypper", "#!/usr/bin/env bash\nexit 0\n")
        write_stub(bin_dir, "sudo", "#!/usr/bin/env bash\nexit 0\n")
        write_stub(bin_dir, "rpm", "#!/usr/bin/env bash\nexit 0\n")
        os_release = write_os_release(root, distro_id="opensuse-tumbleweed", distro_like="opensuse suse", name="openSUSE Tumbleweed")
        with temporary_env({"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}):
            search_policy = resolve_package_action_policy("procurar")
            install_policy = resolve_package_action_policy("instalar")
            remove_policy = resolve_package_action_policy("remover")
            install_plan = build_package_execution_plan("instalar", "firefox")
            remove_plan = build_package_execution_plan("remover", "vlc")
        if search_policy.status != "SUPPORTED_NOW":
            raise AssertionError(f"classificação inesperada na busca: {search_policy.status!r}")
        if search_policy.backend_label != "zypper":
            raise AssertionError(f"backend inesperado na busca: {search_policy.backend_label!r}")
        if search_policy.compatibility_frontier_label != "suportado contido":
            raise AssertionError(f"fronteira inesperada na busca: {search_policy.compatibility_frontier_label!r}")
        if "recorte contido" not in search_policy.reason:
            raise AssertionError(f"motivo inesperado na busca: {search_policy.reason!r}")
        if install_policy.backend_label != "sudo + zypper":
            raise AssertionError(f"backend inesperado na instalação: {install_policy.backend_label!r}")
        if remove_policy.backend_label != "sudo + zypper":
            raise AssertionError(f"backend inesperado na remoção: {remove_policy.backend_label!r}")
        if install_policy.compatibility_frontier_label != "suportado contido":
            raise AssertionError(f"fronteira inesperada na instalação: {install_policy.compatibility_frontier_label!r}")
        if remove_policy.compatibility_frontier_label != "suportado contido":
            raise AssertionError(f"fronteira inesperada na remoção: {remove_policy.compatibility_frontier_label!r}")
        if install_plan.command != ("sudo", "zypper", "--non-interactive", "install", "--", "firefox"):
            raise AssertionError(f"comando inesperado na instalação: {install_plan.command!r}")
        if install_plan.state_probe_label != "rpm":
            raise AssertionError(f"sonda auxiliar inesperada na instalação: {install_plan.state_probe_label!r}")
        if install_plan.state_probe_command != ("rpm", "-q", "firefox"):
            raise AssertionError(f"sonda inesperada na instalação: {install_plan.state_probe_command!r}")
        if remove_plan.command != ("sudo", "zypper", "--non-interactive", "remove", "--", "vlc"):
            raise AssertionError(f"comando inesperado na remoção: {remove_plan.command!r}")
        if remove_plan.state_probe_label != "rpm":
            raise AssertionError(f"sonda auxiliar inesperada na remoção: {remove_plan.state_probe_label!r}")
        if remove_plan.state_probe_command != ("rpm", "-q", "vlc"):
            raise AssertionError(f"sonda inesperada na remoção: {remove_plan.state_probe_command!r}")


def test_package_policy_atomic_blocked_by_policy_even_with_backend() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "dnf", "#!/usr/bin/env bash\nexit 0\n")
        write_stub(bin_dir, "rpm", "#!/usr/bin/env bash\nexit 0\n")
        write_stub(bin_dir, "sudo", "#!/usr/bin/env bash\nexit 0\n")
        os_release = write_os_release(root, distro_id="bazzite", distro_like="fedora", name="Bazzite")
        with temporary_env({"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}):
            install_policy = resolve_package_action_policy("instalar")
            install_plan = build_package_execution_plan("instalar", "firefox")
        if install_policy.status != "SUPPORTED_WITH_POLICY_BLOCK":
            raise AssertionError(f"classificação inesperada: {install_policy.status!r}")
        if install_policy.compatibility_frontier_label != "bloqueado por política":
            raise AssertionError(f"fronteira inesperada: {install_policy.compatibility_frontier_label!r}")
        if install_policy.backend_label != "-":
            raise AssertionError(f"backend inesperado: {install_policy.backend_label!r}")
        if "bloqueia pacote do host" not in install_policy.reason:
            raise AssertionError(f"motivo inesperado: {install_policy.reason!r}")
        if install_policy.block_message is None or "bloqueado por política" not in install_policy.block_message:
            raise AssertionError(f"mensagem inesperada: {install_policy.block_message!r}")
        if install_plan.required_commands:
            raise AssertionError(f"requisitos inesperados: {install_plan.required_commands!r}")
        if install_plan.state_probe_required_commands:
            raise AssertionError(f"sonda inesperada: {install_plan.state_probe_required_commands!r}")


def test_package_policy_matrix_mutable_hosts() -> None:
    cases = (
        (
            "arch",
            {"distro_id": "cachyos", "distro_like": "arch", "name": "CachyOS"},
            {
                "procurar": {
                    "target": "steam",
                    "compatibility_frontier_label": "suportado agora",
                    "backend_label": "pacman",
                    "command": ("pacman", "-Ss", "--", "steam"),
                    "required_commands": ("pacman",),
                    "state_probe_label": "",
                    "state_probe_command": (),
                },
                "instalar": {
                    "target": "obs studio",
                    "compatibility_frontier_label": "suportado agora",
                    "backend_label": "sudo + pacman",
                    "command": ("sudo", "pacman", "-S", "--needed", "--", "obs-studio"),
                    "required_commands": ("pacman", "sudo"),
                    "state_probe_label": "pacman",
                    "state_probe_command": ("pacman", "-Q", "--", "obs-studio"),
                },
                "remover": {
                    "target": "obs studio",
                    "compatibility_frontier_label": "suportado agora",
                    "backend_label": "sudo + pacman",
                    "command": ("sudo", "pacman", "-Rns", "--", "obs-studio"),
                    "required_commands": ("pacman", "sudo"),
                    "state_probe_label": "pacman",
                    "state_probe_command": ("pacman", "-Q", "--", "obs-studio"),
                },
            },
        ),
        (
            "debian",
            {"distro_id": "ubuntu", "distro_like": "debian", "name": "Ubuntu"},
            {
                "procurar": {
                    "target": "steam",
                    "compatibility_frontier_label": "suportado agora",
                    "backend_label": "apt-cache",
                    "command": ("apt-cache", "search", "steam"),
                    "required_commands": ("apt-cache",),
                    "state_probe_label": "",
                    "state_probe_command": (),
                },
                "instalar": {
                    "target": "obs studio",
                    "compatibility_frontier_label": "suportado agora",
                    "backend_label": "sudo + apt-get",
                    "command": ("sudo", "apt-get", "install", "-y", "obs-studio"),
                    "required_commands": ("apt-get", "sudo"),
                    "state_probe_label": "dpkg",
                    "state_probe_command": ("dpkg", "-s", "obs-studio"),
                },
                "remover": {
                    "target": "obs studio",
                    "compatibility_frontier_label": "suportado agora",
                    "backend_label": "sudo + apt-get",
                    "command": ("sudo", "apt-get", "remove", "-y", "obs-studio"),
                    "required_commands": ("apt-get", "sudo"),
                    "state_probe_label": "dpkg",
                    "state_probe_command": ("dpkg", "-s", "obs-studio"),
                },
            },
        ),
        (
            "fedora",
            {"distro_id": "fedora", "distro_like": "fedora", "name": "Fedora Linux"},
            {
                "procurar": {
                    "target": "steam",
                    "compatibility_frontier_label": "suportado agora",
                    "backend_label": "dnf",
                    "command": ("dnf", "search", "steam"),
                    "required_commands": ("dnf",),
                    "state_probe_label": "",
                    "state_probe_command": (),
                },
                "instalar": {
                    "target": "obs studio",
                    "compatibility_frontier_label": "suportado agora",
                    "backend_label": "sudo + dnf",
                    "command": ("sudo", "dnf", "install", "-y", "obs-studio"),
                    "required_commands": ("dnf", "sudo"),
                    "state_probe_label": "rpm",
                    "state_probe_command": ("rpm", "-q", "obs-studio"),
                },
                "remover": {
                    "target": "obs studio",
                    "compatibility_frontier_label": "suportado agora",
                    "backend_label": "sudo + dnf",
                    "command": ("sudo", "dnf", "remove", "-y", "obs-studio"),
                    "required_commands": ("dnf", "sudo"),
                    "state_probe_label": "rpm",
                    "state_probe_command": ("rpm", "-q", "obs-studio"),
                },
            },
        ),
        (
            "opensuse",
            {"distro_id": "opensuse-tumbleweed", "distro_like": "opensuse suse", "name": "openSUSE Tumbleweed"},
            {
                "procurar": {
                    "target": "steam",
                    "compatibility_frontier_label": "suportado contido",
                    "backend_label": "zypper",
                    "command": ("zypper", "search", "--", "steam"),
                    "required_commands": ("zypper",),
                    "state_probe_label": "",
                    "state_probe_command": (),
                },
                "instalar": {
                    "target": "obs studio",
                    "compatibility_frontier_label": "suportado contido",
                    "backend_label": "sudo + zypper",
                    "command": ("sudo", "zypper", "--non-interactive", "install", "--", "obs-studio"),
                    "required_commands": ("zypper", "sudo"),
                    "state_probe_label": "rpm",
                    "state_probe_command": ("rpm", "-q", "obs-studio"),
                },
                "remover": {
                    "target": "obs studio",
                    "compatibility_frontier_label": "suportado contido",
                    "backend_label": "sudo + zypper",
                    "command": ("sudo", "zypper", "--non-interactive", "remove", "--", "obs-studio"),
                    "required_commands": ("zypper", "sudo"),
                    "state_probe_label": "rpm",
                    "state_probe_command": ("rpm", "-q", "obs-studio"),
                },
            },
        ),
    )
    stub_bodies = {
        "pacman": "#!/usr/bin/env bash\nexit 0\n",
        "apt-cache": "#!/usr/bin/env bash\nexit 0\n",
        "apt-get": "#!/usr/bin/env bash\nexit 0\n",
        "dnf": "#!/usr/bin/env bash\nexit 0\n",
        "zypper": "#!/usr/bin/env bash\nexit 0\n",
        "sudo": "#!/usr/bin/env bash\nexit 0\n",
        "dpkg": "#!/usr/bin/env bash\nexit 0\n",
        "rpm": "#!/usr/bin/env bash\nexit 0\n",
    }
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bin_dir = root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        for name, body in stub_bodies.items():
            write_stub(bin_dir, name, body)
        for family, os_release_kwargs, expectations in cases:
            os_release = write_os_release(root, **os_release_kwargs)
            with temporary_env({"PATH": str(bin_dir), "AURY_OS_RELEASE_PATH": str(os_release)}):
                profile = detect_host_profile()
                for intent, expected in expectations.items():
                    policy = resolve_package_action_policy(intent)
                    plan = build_package_execution_plan(intent, expected["target"])
                    if policy.status != "SUPPORTED_NOW":
                        raise AssertionError(f"classificação inesperada em {family}/{intent}: {policy.status!r}")
                    if plan.policy.status != "SUPPORTED_NOW":
                        raise AssertionError(f"plano inesperado em {family}/{intent}: {plan.policy.status!r}")
                    if policy.compatibility_frontier_label != expected["compatibility_frontier_label"]:
                        raise AssertionError(f"fronteira inesperada em {family}/{intent}: {policy.compatibility_frontier_label!r}")
                    if policy.backend_label != expected["backend_label"]:
                        raise AssertionError(f"backend inesperado em {family}/{intent}: {policy.backend_label!r}")
                    if plan.policy.backend_label != expected["backend_label"]:
                        raise AssertionError(f"backend do plano inesperado em {family}/{intent}: {plan.policy.backend_label!r}")
                    if plan.command != expected["command"]:
                        raise AssertionError(f"comando inesperado em {family}/{intent}: {plan.command!r}")
                    if plan.required_commands != expected["required_commands"]:
                        raise AssertionError(f"requisitos inesperados em {family}/{intent}: {plan.required_commands!r}")
                    if plan.state_probe_label != expected["state_probe_label"]:
                        raise AssertionError(f"sonda auxiliar inesperada em {family}/{intent}: {plan.state_probe_label!r}")
                    if plan.state_probe_command != expected["state_probe_command"]:
                        raise AssertionError(f"sonda inesperada em {family}/{intent}: {plan.state_probe_command!r}")
                    if plan.policy.host_profile.linux_family != family:
                        raise AssertionError(f"família inesperada em {family}/{intent}: {plan.policy.host_profile.linux_family!r}")
                    if family == "opensuse":
                        if profile.support_tier_label != "Tier 2 útil contido":
                            raise AssertionError(f"tier inesperado no OpenSUSE: {profile.support_tier_label!r}")
                        if "recorte contido" not in policy.reason:
                            raise AssertionError(f"motivo inesperado no OpenSUSE/{intent}: {policy.reason!r}")
                    elif "recorte contido" in policy.reason:
                        raise AssertionError(f"tier 1 não pode parecer contido em {family}/{intent}: {policy.reason!r}")


def test_dev_destructive_remove_without_safe_antecedent_blocks_local_reference() -> None:
    proc = run("dev", "remover", "ela")
    assert proc.returncode == 0
    assert_in(proc.stdout, "intenção:                      remover")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "referência local:              ela (não resolvida)")
    assert_in(proc.stdout, "estado:                        BLOQUEADA")
    assert_in(proc.stdout, "lacunas:                       alvo seguro")
    assert_in(proc.stdout, "resumo:                        Remoção sem alvo seguro; leitura bloqueada.")
    assert_in(proc.stdout, "não há antecedente seguro nesta ação destrutiva isolada")
    assert_in(proc.stdout, "decisão:                       voltar ao Fish")
    assert_in(proc.stdout, "motivo:                        a ação 1 ficou bloqueada antes da execução direta no runtime Python.")
    assert_in(proc.stdout, "motivo do plano:               a análise ficou bloqueada antes da execução direta no runtime Python.")
    if "domínio:                       pacote" in proc.stdout:
        raise AssertionError("remoção destrutiva anafórica isolada não pode continuar enquadrada como pacote")


def test_dev_destructive_remove_chain_local_reference_alignment() -> None:
    phrase = "remova a pasta Aury que fica em Downloads e depois apague ela"
    proc = run("dev", *phrase.split())
    assert proc.returncode == 0
    assert_in(proc.stdout, "Ação 1")
    assert_in(proc.stdout, "trecho original:               remova a pasta Aury que fica em Downloads")
    assert_in(proc.stdout, "alvo principal:                Downloads/Aury")
    assert_in(proc.stdout, "origem:                        Downloads/Aury")
    assert_in(proc.stdout, "resumo:                        Remover 'Downloads/Aury'.")
    assert_in(proc.stdout, "Ação 2")
    assert_in(proc.stdout, "trecho original:               apague ela")
    assert_in(proc.stdout, "intenção:                      remover")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          pasta")
    assert_in(proc.stdout, "alvo principal:                Downloads/Aury")
    assert_in(proc.stdout, "origem:                        Downloads/Aury")
    assert_in(proc.stdout, "referência local:              Downloads/Aury")
    assert_in(proc.stdout, "estado:                        BLOQUEADA")
    assert_in(proc.stdout, "lacunas:                       alinhamento com runtime atual")
    assert_in(proc.stdout, "resumo:                        Remoção de 'Downloads/Aury' reconhecida, mas bloqueada no estado atual.")
    assert_in(proc.stdout, "foi resolvida com segurança como 'Downloads/Aury'")
    assert_in(proc.stdout, "referência local 'ela' resolvida com segurança como 'Downloads/Aury'")
    assert_in(proc.stdout, "runtime legado atual ainda bloqueia continuação destrutiva anafórica equivalente")
    if "Downloads e/Aury" in proc.stdout:
        raise AssertionError("o alvo localizado não pode continuar contaminado pelo conector antes de 'depois'")


def test_dev_destructive_remove_chain_local_reference_inflected_alignment() -> None:
    phrase = "remova a pasta Aury que fica em Downloads e depois remova ela"
    proc = run("dev", *phrase.split())
    assert proc.returncode == 0
    assert_in(proc.stdout, "Ação 1")
    assert_in(proc.stdout, "trecho original:               remova a pasta Aury que fica em Downloads")
    assert_in(proc.stdout, "alvo principal:                Downloads/Aury")
    assert_in(proc.stdout, "origem:                        Downloads/Aury")
    assert_in(proc.stdout, "resumo:                        Remover 'Downloads/Aury'.")
    assert_in(proc.stdout, "Ação 2")
    assert_in(proc.stdout, "trecho original:               remova ela")
    assert_in(proc.stdout, "intenção:                      remover")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          pasta")
    assert_in(proc.stdout, "alvo principal:                Downloads/Aury")
    assert_in(proc.stdout, "origem:                        Downloads/Aury")
    assert_in(proc.stdout, "referência local:              Downloads/Aury")
    assert_in(proc.stdout, "estado:                        BLOQUEADA")
    assert_in(proc.stdout, "lacunas:                       alinhamento com runtime atual")
    assert_in(proc.stdout, "resumo:                        Remoção de 'Downloads/Aury' reconhecida, mas bloqueada no estado atual.")
    assert_in(proc.stdout, "foi resolvida com segurança como 'Downloads/Aury'")
    assert_in(proc.stdout, "referência local 'ela' resolvida com segurança como 'Downloads/Aury'")
    assert_in(proc.stdout, "runtime legado atual ainda bloqueia continuação destrutiva anafórica equivalente")
    if "Downloads e/Aury" in proc.stdout:
        raise AssertionError("o alvo localizado não pode continuar contaminado pelo conector antes de 'depois'")


def test_dev_destructive_remove_with_previous_package_context_blocks_local_reference() -> None:
    phrase = "procurar steam e depois remover ele"
    proc = run("dev", *phrase.split())
    assert proc.returncode == 0
    assert_in(proc.stdout, "Ação 1")
    assert_in(proc.stdout, "intenção:                      procurar")
    assert_in(proc.stdout, "domínio:                       pacote")
    assert_in(proc.stdout, "alvo principal:                steam")
    assert_in(proc.stdout, "Ação 2")
    assert_in(proc.stdout, "trecho original:               remover ele")
    assert_in(proc.stdout, "intenção:                      remover")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "referência local:              ele")
    assert_in(proc.stdout, "estado:                        BLOQUEADA")
    assert_in(proc.stdout, "lacunas:                       alvo seguro")
    assert_in(proc.stdout, "resumo:                        Remoção sem alvo seguro; leitura bloqueada.")
    assert_in(proc.stdout, "contexto anterior insuficiente ou incompatível")
    assert_in(proc.stdout, "domínio 'pacote'")
    if "alvo principal:                ele" in proc.stdout:
        raise AssertionError("remoção destrutiva com contexto anterior incompatível não pode voltar a expor 'ele' como alvo de pacote")


def test_dev_destructive_remove_with_previous_file_context_blocks_incompatible_local_reference() -> None:
    phrase = "criar pasta Aury e depois remover ele"
    proc = run("dev", *phrase.split())
    assert proc.returncode == 0
    assert_in(proc.stdout, "Ação 1")
    assert_in(proc.stdout, "intenção:                      criar")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          pasta")
    assert_in(proc.stdout, "alvo principal:                Aury")
    assert_in(proc.stdout, "Ação 2")
    assert_in(proc.stdout, "trecho original:               remover ele")
    assert_in(proc.stdout, "intenção:                      remover")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "referência local:              ele")
    assert_in(proc.stdout, "estado:                        BLOQUEADA")
    assert_in(proc.stdout, "lacunas:                       alvo seguro")
    assert_in(proc.stdout, "tipo 'pasta'")
    if "alvo principal:                ele" in proc.stdout:
        raise AssertionError("referência local destrutiva incompatível não pode reaparecer como alvo principal de pacote")


def test_dev_destructive_remove_followup_reuses_safe_file_reference() -> None:
    phrase = "remova o arquivo teste.txt que fica em destino e depois apague ele"
    proc = run("dev", *phrase.split())
    assert proc.returncode == 0
    assert_in(proc.stdout, "Ação 1")
    assert_in(proc.stdout, "trecho original:               remova o arquivo teste.txt que fica em destino")
    assert_in(proc.stdout, "alvo principal:                destino/teste.txt")
    assert_in(proc.stdout, "origem:                        destino/teste.txt")
    assert_in(proc.stdout, "Ação 2")
    assert_in(proc.stdout, "trecho original:               apague ele")
    assert_in(proc.stdout, "intenção:                      remover")
    assert_in(proc.stdout, "domínio:                       arquivo")
    assert_in(proc.stdout, "tipo:                          arquivo")
    assert_in(proc.stdout, "alvo principal:                destino/teste.txt")
    assert_in(proc.stdout, "origem:                        destino/teste.txt")
    assert_in(proc.stdout, "referência local:              destino/teste.txt")
    assert_in(proc.stdout, "estado:                        BLOQUEADA")
    assert_in(proc.stdout, "lacunas:                       alinhamento com runtime atual")
    assert_in(proc.stdout, "resumo:                        Remoção de 'destino/teste.txt' reconhecida, mas bloqueada no estado atual.")
    assert_in(proc.stdout, "referência local 'ele' resolvida com segurança como 'destino/teste.txt'")


def main() -> int:
    tests = [
        test_help,
        test_version,
        test_dev_remove_pkg,
        test_dev_install_package_alignment,
        test_dev_package_atomic_block_alignment,
        test_dev_package_opensuse_search_alignment,
        test_dev_package_opensuse_install_alignment,
        test_dev_package_opensuse_remove_alignment,
        test_dev_ping_host_alignment,
        test_dev_network_speed_rede_alignment,
        test_dev_create_file_alignment,
        test_dev_create_folder_alignment,
        test_dev_create_folder_inflected_alignment,
        test_dev_create_file_inflected_alignment,
        test_dev_create_folder_located_alignment,
        test_dev_create_folder_located_inflected_alignment,
        test_dev_create_file_located_alignment,
        test_dev_create_file_located_inflected_alignment,
        test_dev_create_implicit_file_alignment,
        test_dev_create_implicit_file_inflected_alignment,
        test_dev_create_implicit_file_located_alignment,
        test_dev_create_implicit_file_located_inflected_alignment,
        test_dev_create_implicit_folder_alignment,
        test_dev_create_implicit_folder_inflected_alignment,
        test_dev_create_implicit_folder_located_alignment,
        test_dev_create_implicit_folder_located_inflected_alignment,
        test_dev_create_explicit_folder_slash_located_alignment,
        test_dev_copy_file_alignment,
        test_dev_move_file_alignment,
        test_dev_rename_file_alignment,
        test_dev_located_rename_file_alignment,
        test_dev_explicit_remove_file_alignment,
        test_dev_explicit_remove_folder_alignment,
        test_dev_explicit_remove_located_folder_alignment,
        test_dev_explicit_remove_located_file_alignment,
        test_dev_implicit_remove_file_alignment,
        test_dev_implicit_remove_file_inflected_alignment,
        test_dev_implicit_remove_folder_alignment,
        test_dev_implicit_remove_folder_inflected_alignment,
        test_dev_implicit_remove_located_file_alignment,
        test_dev_implicit_remove_located_file_inflected_alignment,
        test_dev_implicit_remove_located_folder_alignment,
        test_dev_implicit_remove_located_folder_inflected_alignment,
        test_dev_explicit_remove_short_located_folder_alignment,
        test_dev_explicit_remove_short_located_folder_inflected_alignment,
        test_dev_compact_zip_file_alignment,
        test_dev_compact_zip_folder_alignment,
        test_dev_compact_tar_gz_file_alignment,
        test_dev_compact_tar_gz_folder_alignment,
        test_dev_compact_missing_output_blocks,
        test_dev_compact_invalid_format_blocks,
        test_dev_extract_zip_alignment,
        test_dev_extract_tar_gz_alignment,
        test_dev_extract_conversational_destination_alignment,
        test_dev_extract_explicit_real_path_destination_alignment,
        test_dev_copy_rename_local_reference_alignment,
        test_dev_copy_rename_file_local_reference_alignment,
        test_dev_move_rename_file_local_reference_alignment,
        test_dev_chain,
        test_dev_sentence_chain_move_local_reference_alignment,
        test_runtime_speedtest,
        test_runtime_ping,
        test_runtime_package_search,
        test_runtime_package_search_no_results,
        test_runtime_package_search_debian_no_results,
        test_runtime_package_search_opensuse,
        test_runtime_package_search_opensuse_no_results,
        test_runtime_package_install_debian,
        test_runtime_package_install_noop_when_already_installed,
        test_runtime_package_install_requires_state_confirmation,
        test_runtime_package_install_opensuse,
        test_runtime_package_install_opensuse_requires_state_confirmation,
        test_runtime_package_remove_fedora,
        test_runtime_package_remove_noop_when_not_installed,
        test_runtime_package_remove_opensuse,
        test_runtime_package_remove_opensuse_noop_when_not_installed,
        test_runtime_package_remove_opensuse_requires_state_confirmation,
        test_runtime_package_opensuse_backend_missing,
        test_runtime_package_opensuse_requires_auxiliary_state_probe,
        test_runtime_package_atomic_without_backend_stays_policy_block,
        test_runtime_package_atomic_without_probe_stays_policy_block,
        test_runtime_create_file,
        test_runtime_create_folder_located,
        test_dev_search_inflected_alignment,
        test_runtime_gpu,
        test_runtime_multi_action_supported,
        test_runtime_multi_action_package_supported,
        test_sensitive_tokens_contract,
        test_pipeline_prepare_text,
        test_prepare_analysis_uses_prepared_action,
        test_prepare_analysis_explicit_package_target_strips_domain_noise,
        test_prepare_analysis_isolated_destructive_remove_local_reference_blocks,
        test_prepare_analysis_extract_conversational_destination_alignment,
        test_prepare_analysis_located_rename_alignment,
        test_prepare_analysis_extract_explicit_real_path_destination_alignment,
        test_prepare_analysis_compact_alignment,
        test_prepare_analysis_compact_invalid_format_blocks,
        test_prepare_analyses_copy_rename_local_reference_alignment,
        test_prepare_analyses_copy_rename_file_local_reference_alignment,
        test_prepare_analyses_move_rename_file_local_reference_alignment,
        test_prepare_analyses_move_rename_file_local_reference_requires_explicit_destination_shape,
        test_prepare_analyses_sentence_chain_move_local_reference_alignment,
        test_prepare_analyses_multiple_actions,
        test_prepare_analyses_destructive_remove_followup_reuses_safe_local_reference,
        test_prepare_analyses_destructive_remove_with_previous_package_context_blocks_local_reference,
        test_prepare_analyses_destructive_remove_with_previous_file_context_blocks_incompatible_local_reference,
        test_prepare_analyses_destructive_remove_followup_reuses_safe_file_reference,
        test_action_execution_plan_supported_now,
        test_action_execution_plan_supported_now_for_create_file,
        test_action_execution_plan_supported_now_for_create_folder,
        test_action_execution_plan_supported_runtime_route_contract,
        test_action_execution_plan_future_migration_candidate,
        test_action_execution_plan_fish_fallback_reason_for_out_of_scope,
        test_sequence_execution_plan_supported_now,
        test_sequence_execution_plan_returns_to_fish,
        test_sequence_execution_plan_return_reason_for_blocked_gap,
        test_dev_multiple_actions,
        test_detect_host_profile_tiers,
        test_detect_host_profile_atomic_frontier_labels,
        test_detect_host_profile_opensuse_microos_is_atomic,
        test_package_policy_opensuse_supported_now,
        test_package_policy_atomic_blocked_by_policy_even_with_backend,
        test_package_policy_matrix_mutable_hosts,
        test_dev_destructive_remove_without_safe_antecedent_blocks_local_reference,
        test_dev_destructive_remove_chain_local_reference_alignment,
        test_dev_destructive_remove_chain_local_reference_inflected_alignment,
        test_dev_destructive_remove_with_previous_package_context_blocks_local_reference,
        test_dev_destructive_remove_with_previous_file_context_blocks_incompatible_local_reference,
        test_dev_destructive_remove_followup_reuses_safe_file_reference,
        test_dev_out_of_scope_plan_reason_alignment,
    ]
    for test in tests:
        test()
    print(f"python_core_smoke: ok ({len(tests)} testes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
