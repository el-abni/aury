from __future__ import annotations

import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

_OS_RELEASE_ENV = "AURY_OS_RELEASE_PATH"
_OSTREE_BOOTED_ENV = "AURY_OSTREE_BOOTED"
_KNOWN_PACKAGE_BACKENDS = ("pacman", "paru", "apt-cache", "apt-get", "dnf", "zypper", "flatpak", "rpm-ostree")
_ARCH_FAMILY_IDS = {"arch", "archlinux", "artix", "cachyos", "endeavouros", "manjaro"}
_DEBIAN_FAMILY_IDS = {"debian", "ubuntu", "linuxmint", "pop", "neon", "raspbian", "elementary"}
_FEDORA_FAMILY_IDS = {"fedora", "rhel", "centos", "rocky", "almalinux", "nobara", "bazzite", "bluefin", "aurora"}
_OPENSUSE_FAMILY_IDS = {"opensuse", "opensuse-leap", "opensuse-tumbleweed", "opensuse-microos", "sles", "sled", "microos", "suse"}
_ATOMIC_IDS = {
    "aurora",
    "bazzite",
    "bluefin",
    "fedora-coreos",
    "kinoite",
    "microos",
    "opensuse-microos",
    "silverblue",
    "sericea",
    "onyx",
}
_ATOMIC_VARIANTS = {"atomic", "coreos", "immutable", "kinoite", "microos", "ostree", "sericea", "silverblue", "onyx"}
_PACKAGE_ROUTES = {
    "procurar": "package_search",
    "instalar": "package_install",
    "remover": "package_remove",
}


@dataclass(frozen=True)
class HostProfile:
    linux_family: str
    distro_id: str
    distro_like: tuple[str, ...]
    variant_id: str
    mutability: str
    package_backends: tuple[str, ...]
    support_tier: str

    @property
    def linux_family_label(self) -> str:
        if self.linux_family == "unknown":
            return "desconhecida"
        return self.linux_family

    @property
    def mutability_label(self) -> str:
        if self.mutability == "atomic":
            return "Atomic"
        return "mutável"

    @property
    def support_tier_label(self) -> str:
        if self.support_tier == "tier_1":
            return "Tier 1 inicial"
        if self.support_tier == "tier_2":
            return "Tier 2 útil contido"
        if self.support_tier == "limited":
            return "suporte limitado"
        return "fora do recorte"

    @property
    def package_backends_label(self) -> str:
        if not self.package_backends:
            return "-"
        return ", ".join(self.package_backends)


@dataclass(frozen=True)
class PackageActionPolicy:
    intent: str
    route: str
    status: str
    backend_label: str
    reason: str
    host_profile: HostProfile
    block_message: str | None = None


@dataclass(frozen=True)
class PackageExecutionPlan:
    policy: PackageActionPolicy
    package_target: str = ""
    command: tuple[str, ...] = ()
    required_commands: tuple[str, ...] = ()
    state_probe_label: str = ""
    state_probe_command: tuple[str, ...] = ()
    state_probe_required_commands: tuple[str, ...] = ()


def _read_os_release(environ: dict[str, str]) -> dict[str, str]:
    path = Path(environ.get(_OS_RELEASE_ENV, "/etc/os-release"))
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return {}

    parsed: dict[str, str] = {}
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        parsed[key.strip().upper()] = value.strip()
    return parsed


def _tokenize(value: str) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(token for token in re.split(r"[^a-z0-9._+-]+", value.lower()) if token)


def _split_like(value: str) -> tuple[str, ...]:
    return tuple(token for token in value.lower().split() if token)


def _detect_linux_family(distro_id: str, distro_like: tuple[str, ...]) -> str:
    tokens = {distro_id, *distro_like}
    if tokens & _ARCH_FAMILY_IDS:
        return "arch"
    if tokens & _DEBIAN_FAMILY_IDS:
        return "debian"
    if tokens & _FEDORA_FAMILY_IDS:
        return "fedora"
    if tokens & _OPENSUSE_FAMILY_IDS:
        return "opensuse"
    return "unknown"


def _detect_mutability(
    distro_id: str,
    variant_id: str,
    name: str,
    pretty_name: str,
    environ: dict[str, str],
) -> str:
    atomic_tokens = {
        *(_tokenize(distro_id)),
        *(_tokenize(variant_id)),
        *(_tokenize(name)),
        *(_tokenize(pretty_name)),
    }
    if distro_id in _ATOMIC_IDS:
        return "atomic"
    if variant_id in _ATOMIC_VARIANTS:
        return "atomic"
    if atomic_tokens & (_ATOMIC_IDS | _ATOMIC_VARIANTS):
        return "atomic"
    if environ.get(_OSTREE_BOOTED_ENV, "").strip() == "1":
        return "atomic"
    if Path("/run/ostree-booted").exists():
        return "atomic"
    return "mutable"


def _detect_package_backends(environ: dict[str, str]) -> tuple[str, ...]:
    path = environ.get("PATH")
    detected: list[str] = []
    for backend in _KNOWN_PACKAGE_BACKENDS:
        if shutil.which(backend, path=path) is not None:
            detected.append(backend)
    return tuple(detected)


def detect_host_profile(environ: dict[str, str] | None = None) -> HostProfile:
    resolved_environ = os.environ if environ is None else environ
    os_release = _read_os_release(resolved_environ)
    distro_id = os_release.get("ID", "").strip().lower()
    distro_like = _split_like(os_release.get("ID_LIKE", ""))
    variant_id = os_release.get("VARIANT_ID", "").strip().lower()
    name = os_release.get("NAME", "").strip().lower()
    pretty_name = os_release.get("PRETTY_NAME", "").strip().lower()
    linux_family = _detect_linux_family(distro_id, distro_like)
    mutability = _detect_mutability(distro_id, variant_id, name, pretty_name, resolved_environ)
    package_backends = _detect_package_backends(resolved_environ)

    if mutability == "atomic":
        support_tier = "limited"
    elif linux_family in {"arch", "debian", "fedora"}:
        support_tier = "tier_1"
    elif linux_family == "opensuse":
        support_tier = "tier_2"
    else:
        support_tier = "out_of_scope"

    return HostProfile(
        linux_family=linux_family,
        distro_id=distro_id,
        distro_like=distro_like,
        variant_id=variant_id,
        mutability=mutability,
        package_backends=package_backends,
        support_tier=support_tier,
    )


def _package_block_reason(profile: HostProfile) -> tuple[str, str]:
    if profile.mutability == "atomic":
        reason = "o host Linux foi detectado como Atomic, e o recorte atual ainda só sustenta bloqueio honesto para pacote do host nesse perfil."
        message = "❌ este host Linux foi detectado como Atomic; o recorte atual ainda não sustenta pacote do host neste perfil."
        return reason, message

    reason = "a família Linux deste host ficou fora do recorte atual de pacote da linha 1.x."
    message = "❌ a família Linux deste host ficou fora do recorte atual de pacote da linha 1.x."
    return reason, message


def _package_backend_label(intent: str, profile: HostProfile) -> str:
    backends = set(profile.package_backends)
    if profile.linux_family == "arch":
        if intent == "procurar":
            if "pacman" in backends:
                return "pacman"
            if "paru" in backends:
                return "paru"
            return "pacman"
        if intent == "instalar":
            return "paru + pacman" if "paru" in backends else "sudo + pacman"
        if "pacman" in backends:
            return "sudo + pacman"
        if "paru" in backends:
            return "paru + pacman"
        return "sudo + pacman"
    if profile.linux_family == "debian":
        return "apt-cache" if intent == "procurar" else "sudo + apt-get"
    if profile.linux_family == "opensuse":
        return "zypper" if intent == "procurar" else "sudo + zypper"
    return "dnf" if intent == "procurar" else "sudo + dnf"


def _supported_package_reason(intent: str, profile: HostProfile) -> str:
    scope = "neste recorte contido" if profile.support_tier == "tier_2" else "nesta fase"
    if intent == "procurar":
        return f"o perfil do host Linux já resolve esta busca de pacote com backend explícito {scope}, e a execução real trata ausência de resultado com saída honesta."
    return f"o perfil do host Linux já resolve esta ação de pacote com backend explícito {scope}, e a execução real verifica o estado do pacote antes de agir e confirma o resultado depois."


def _package_state_probe_spec(profile: HostProfile, target: str) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
    if profile.linux_family == "arch":
        return "pacman", ("pacman", "-Q", "--", target), ("pacman",)
    if profile.linux_family == "debian":
        return "dpkg", ("dpkg", "-s", target), ("dpkg",)
    return "rpm", ("rpm", "-q", target), ("rpm",)


def resolve_package_action_policy(
    intent: str,
    profile: HostProfile | None = None,
    environ: dict[str, str] | None = None,
) -> PackageActionPolicy:
    resolved_profile = profile or detect_host_profile(environ)
    route = _PACKAGE_ROUTES[intent]

    if resolved_profile.mutability == "atomic" or resolved_profile.linux_family == "unknown":
        reason, message = _package_block_reason(resolved_profile)
        return PackageActionPolicy(
            intent=intent,
            route=route,
            status="SUPPORTED_WITH_POLICY_BLOCK",
            backend_label="-",
            reason=reason,
            host_profile=resolved_profile,
            block_message=message,
        )

    return PackageActionPolicy(
        intent=intent,
        route=route,
        status="SUPPORTED_NOW",
        backend_label=_package_backend_label(intent, resolved_profile),
        reason=_supported_package_reason(intent, resolved_profile),
        host_profile=resolved_profile,
    )


def package_no_results_message(target: str, backend_label: str) -> str:
    return f"ℹ️ não encontrei resultados para '{target}' no backend '{backend_label}'."


def package_noop_message(intent: str, target: str) -> str:
    if intent == "instalar":
        return f"ℹ️ o pacote '{target}' já está instalado neste host. Nada foi feito."
    return f"ℹ️ o pacote '{target}' não está instalado neste host. Nada foi feito."


def package_state_confirmation_message(intent: str, target: str, backend_label: str) -> str:
    if intent == "instalar":
        return f"❌ o backend '{backend_label}' terminou sem eu conseguir confirmar a instalação de '{target}'."
    return f"❌ o backend '{backend_label}' terminou sem eu conseguir confirmar a remoção de '{target}'."


def package_state_probe_missing_message(backend_label: str, probe_label: str) -> str:
    return f"❌ a confirmação de estado para o backend '{backend_label}' depende da ferramenta auxiliar '{probe_label}', que não está disponível."


def package_success_message(intent: str, target: str) -> str:
    if intent == "instalar":
        return f"✅ pronto, o pacote '{target}' está instalado."
    return f"✅ pronto, o pacote '{target}' foi removido."


def _normalize_package_target(intent: str, target: str) -> str:
    normalized = target.strip()
    if intent not in {"instalar", "remover"}:
        return normalized
    parts = [part for part in normalized.split() if part]
    if len(parts) <= 1:
        return normalized
    return "-".join(parts)


def build_package_execution_plan(
    intent: str,
    target: str,
    profile: HostProfile | None = None,
    environ: dict[str, str] | None = None,
) -> PackageExecutionPlan:
    policy = resolve_package_action_policy(intent, profile=profile, environ=environ)
    if policy.block_message is not None:
        return PackageExecutionPlan(policy=policy)

    package_target = _normalize_package_target(intent, target)
    backends = set(policy.host_profile.package_backends)
    state_probe_label = ""
    state_probe_command: tuple[str, ...] = ()
    state_probe_required_commands: tuple[str, ...] = ()
    if intent in {"instalar", "remover"}:
        state_probe_label, state_probe_command, state_probe_required_commands = _package_state_probe_spec(
            policy.host_profile,
            package_target,
        )

    if policy.host_profile.linux_family == "arch":
        if intent == "procurar":
            if "pacman" in backends:
                return PackageExecutionPlan(
                    policy=policy,
                    package_target=package_target,
                    command=("pacman", "-Ss", "--", package_target),
                    required_commands=("pacman",),
                )
            if "paru" in backends:
                return PackageExecutionPlan(
                    policy=policy,
                    package_target=package_target,
                    command=("paru", "-Ss", "--", package_target),
                    required_commands=("paru",),
                )
            return PackageExecutionPlan(
                policy=policy,
                package_target=package_target,
                command=("pacman", "-Ss", "--", package_target),
                required_commands=("pacman",),
            )
        if intent == "instalar":
            if "paru" in backends:
                return PackageExecutionPlan(
                    policy=policy,
                    package_target=package_target,
                    command=("paru", "-S", "--needed", "--", package_target),
                    required_commands=("paru", "pacman"),
                    state_probe_label=state_probe_label,
                    state_probe_command=state_probe_command,
                    state_probe_required_commands=state_probe_required_commands,
                )
            return PackageExecutionPlan(
                policy=policy,
                package_target=package_target,
                command=("sudo", "pacman", "-S", "--needed", "--", package_target),
                required_commands=("pacman", "sudo"),
                state_probe_label=state_probe_label,
                state_probe_command=state_probe_command,
                state_probe_required_commands=state_probe_required_commands,
            )
        if "pacman" in backends:
            return PackageExecutionPlan(
                policy=policy,
                package_target=package_target,
                command=("sudo", "pacman", "-Rns", "--", package_target),
                required_commands=("pacman", "sudo"),
                state_probe_label=state_probe_label,
                state_probe_command=state_probe_command,
                state_probe_required_commands=state_probe_required_commands,
            )
        if "paru" in backends:
            return PackageExecutionPlan(
                policy=policy,
                package_target=package_target,
                command=("paru", "-Rns", "--", package_target),
                required_commands=("paru", "pacman"),
                state_probe_label=state_probe_label,
                state_probe_command=state_probe_command,
                state_probe_required_commands=state_probe_required_commands,
            )
        return PackageExecutionPlan(
            policy=policy,
            package_target=package_target,
            command=("sudo", "pacman", "-Rns", "--", package_target),
            required_commands=("pacman", "sudo"),
            state_probe_label=state_probe_label,
            state_probe_command=state_probe_command,
            state_probe_required_commands=state_probe_required_commands,
        )

    if policy.host_profile.linux_family == "debian":
        if intent == "procurar":
            return PackageExecutionPlan(
                policy=policy,
                package_target=package_target,
                command=("apt-cache", "search", package_target),
                required_commands=("apt-cache",),
            )
        if intent == "instalar":
            return PackageExecutionPlan(
                policy=policy,
                package_target=package_target,
                command=("sudo", "apt-get", "install", "-y", package_target),
                required_commands=("apt-get", "sudo"),
                state_probe_label=state_probe_label,
                state_probe_command=state_probe_command,
                state_probe_required_commands=state_probe_required_commands,
            )
        return PackageExecutionPlan(
            policy=policy,
            package_target=package_target,
            command=("sudo", "apt-get", "remove", "-y", package_target),
            required_commands=("apt-get", "sudo"),
            state_probe_label=state_probe_label,
            state_probe_command=state_probe_command,
            state_probe_required_commands=state_probe_required_commands,
        )

    if policy.host_profile.linux_family == "opensuse":
        if intent == "procurar":
            return PackageExecutionPlan(
                policy=policy,
                package_target=package_target,
                command=("zypper", "search", "--", package_target),
                required_commands=("zypper",),
            )
        if intent == "instalar":
            return PackageExecutionPlan(
                policy=policy,
                package_target=package_target,
                command=("sudo", "zypper", "--non-interactive", "install", "--", package_target),
                required_commands=("zypper", "sudo"),
                state_probe_label=state_probe_label,
                state_probe_command=state_probe_command,
                state_probe_required_commands=state_probe_required_commands,
            )
        return PackageExecutionPlan(
            policy=policy,
            package_target=package_target,
            command=("sudo", "zypper", "--non-interactive", "remove", "--", package_target),
            required_commands=("zypper", "sudo"),
            state_probe_label=state_probe_label,
            state_probe_command=state_probe_command,
            state_probe_required_commands=state_probe_required_commands,
        )

    if intent == "procurar":
        return PackageExecutionPlan(
            policy=policy,
            package_target=package_target,
            command=("dnf", "search", package_target),
            required_commands=("dnf",),
        )
    if intent == "instalar":
        return PackageExecutionPlan(
            policy=policy,
            package_target=package_target,
            command=("sudo", "dnf", "install", "-y", package_target),
            required_commands=("dnf", "sudo"),
            state_probe_label=state_probe_label,
            state_probe_command=state_probe_command,
            state_probe_required_commands=state_probe_required_commands,
        )
    return PackageExecutionPlan(
        policy=policy,
        package_target=package_target,
        command=("sudo", "dnf", "remove", "-y", package_target),
        required_commands=("dnf", "sudo"),
        state_probe_label=state_probe_label,
        state_probe_command=state_probe_command,
        state_probe_required_commands=state_probe_required_commands,
    )
