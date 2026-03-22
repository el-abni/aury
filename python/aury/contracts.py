from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProtectedToken:
    placeholder: str
    value: str
    token_type: str


@dataclass
class InputPhrase:
    original_tokens: list[str] = field(default_factory=list)
    protected_tokens: list[ProtectedToken] = field(default_factory=list)
    corrected_tokens: list[str] = field(default_factory=list)
    normalized_tokens: list[str] = field(default_factory=list)
    normalized_display_tokens: list[str] = field(default_factory=list)

    @property
    def original_text(self) -> str:
        return " ".join(self.original_tokens).strip()

    @property
    def corrected_text(self) -> str:
        return " ".join(self.corrected_tokens).strip()

    @property
    def normalized_text(self) -> str:
        return " ".join(self.normalized_display_tokens).strip()

    @property
    def ascii_normalized_text(self) -> str:
        return " ".join(self.normalized_tokens).strip()


@dataclass
class PreparedAction:
    index: int
    original_tokens: list[str] = field(default_factory=list)
    corrected_tokens: list[str] = field(default_factory=list)
    normalized_tokens: list[str] = field(default_factory=list)
    normalized_display_tokens: list[str] = field(default_factory=list)
    original_action: str = ""

    @property
    def corrected_action(self) -> str:
        return " ".join(self.corrected_tokens).strip()

    @property
    def normalized_action(self) -> str:
        return " ".join(self.normalized_display_tokens).strip()


@dataclass
class Analysis:
    original_text: str
    normalized_text: str
    intent: str
    domain: str
    status: str
    reason: str
    summary: str
    entities: dict[str, str] = field(default_factory=dict)
    observations: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SupportedRuntimeRoute:
    route: str
    backend: str


@dataclass(frozen=True)
class ActionExecutionPlan:
    status: str
    supported_runtime_route: SupportedRuntimeRoute | None
    executor: str
    reason: str

    @classmethod
    def supported_now(cls, supported_runtime_route: SupportedRuntimeRoute, *, reason: str) -> ActionExecutionPlan:
        return cls(
            status="SUPPORTED_NOW",
            supported_runtime_route=supported_runtime_route,
            executor="python",
            reason=reason,
        )

    @classmethod
    def future_migration_candidate(cls, *, reason: str) -> ActionExecutionPlan:
        return cls(
            status="FUTURE_MIGRATION_CANDIDATE",
            supported_runtime_route=None,
            executor="fish",
            reason=reason,
        )

    @classmethod
    def fish_fallback(cls, *, reason: str) -> ActionExecutionPlan:
        return cls(
            status="FISH_FALLBACK",
            supported_runtime_route=None,
            executor="fish",
            reason=reason,
        )

    @property
    def route(self) -> str | None:
        if self.supported_runtime_route is None:
            return None
        return self.supported_runtime_route.route

    @property
    def backend(self) -> str | None:
        if self.supported_runtime_route is None:
            return None
        return self.supported_runtime_route.backend

    @property
    def executes_in_python(self) -> bool:
        return self.executor == "python"

    def matches_supported_runtime_route(self, supported_runtime_route: SupportedRuntimeRoute) -> bool:
        return self.supported_runtime_route == supported_runtime_route


@dataclass(frozen=True)
class SequenceExecutionPlan:
    action_plans: tuple[ActionExecutionPlan, ...] = field(default_factory=tuple)
    decision: str = "RETURN_TO_FISH"
    reason: str = ""

    @property
    def executes_in_python(self) -> bool:
        return self.decision == "EXECUTE_IN_PYTHON"
