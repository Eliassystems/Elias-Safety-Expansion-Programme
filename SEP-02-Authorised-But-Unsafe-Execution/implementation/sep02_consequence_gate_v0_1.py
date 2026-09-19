from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


UPSTREAM_PASS = "PASS"

CONSEQUENCE_VIOLATED = "VIOLATED"
CONSEQUENCE_NOT_VIOLATED = "NOT_VIOLATED"

DECISION_WITHHOLD = "WITHHOLD"
DECISION_PASS_GATE = "PASS_CONSEQUENCE_GATE"

REASON_CONSEQUENCE_VIOLATION = "CONSEQUENCE_CONSTRAINT_VIOLATION"
REASON_NO_CONSEQUENCE_VIOLATION = "NO_CONSEQUENCE_CONSTRAINT_VIOLATION"


@dataclass(frozen=True)
class ConsequenceGateInput:
    case_id: str
    constraint_id: str
    identity_state: str
    authority_state: str
    policy_state: str
    technical_validity_state: str
    consequence_state: str


@dataclass(frozen=True)
class ConsequenceGateDecision:
    case_id: str
    constraint_id: str
    decision: str
    reason: str
    execution_attempted: Optional[bool]
    side_effect_occurred: Optional[bool]


class OutOfScopeUpstreamState(ValueError):
    """Raised when SEP-02 isolation preconditions have not all passed."""


class UnsupportedConsequenceState(ValueError):
    """Raised when the consequence state is outside the frozen SEP-02 matrix."""


def _require_nonempty(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _require_upstream_pass(inp: ConsequenceGateInput) -> None:
    upstream = {
        "identity_state": inp.identity_state,
        "authority_state": inp.authority_state,
        "policy_state": inp.policy_state,
        "technical_validity_state": inp.technical_validity_state,
    }

    failed = {
        name: value
        for name, value in upstream.items()
        if value != UPSTREAM_PASS
    }

    if failed:
        raise OutOfScopeUpstreamState(
            "SEP-02 consequence-only isolation requires all upstream "
            f"states to PASS; received {failed}"
        )


def evaluate_consequence_gate(
    inp: ConsequenceGateInput,
) -> ConsequenceGateDecision:
    """
    Evaluate the bounded SEP-02 consequence gate.

    This function does not establish whether a consequence assessment is
    globally correct. It enforces the supplied consequence state only after
    the frozen SEP-02 upstream isolation conditions have passed.

    PASS_CONSEQUENCE_GATE means only that this consequence gate did not
    independently withhold the action. It does not itself authorize execution.
    """

    _require_nonempty(inp.case_id, "case_id")
    _require_nonempty(inp.constraint_id, "constraint_id")

    _require_upstream_pass(inp)

    if inp.consequence_state == CONSEQUENCE_VIOLATED:
        return ConsequenceGateDecision(
            case_id=inp.case_id,
            constraint_id=inp.constraint_id,
            decision=DECISION_WITHHOLD,
            reason=REASON_CONSEQUENCE_VIOLATION,
            execution_attempted=False,
            side_effect_occurred=False,
        )

    if inp.consequence_state == CONSEQUENCE_NOT_VIOLATED:
        return ConsequenceGateDecision(
            case_id=inp.case_id,
            constraint_id=inp.constraint_id,
            decision=DECISION_PASS_GATE,
            reason=REASON_NO_CONSEQUENCE_VIOLATION,
            execution_attempted=None,
            side_effect_occurred=None,
        )

    raise UnsupportedConsequenceState(
        "SEP-02 v0.1 supports only VIOLATED or NOT_VIOLATED "
        f"consequence states; received {inp.consequence_state!r}"
    )
