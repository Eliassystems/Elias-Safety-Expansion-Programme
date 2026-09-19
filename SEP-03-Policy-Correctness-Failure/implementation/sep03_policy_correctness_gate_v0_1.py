from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


UPSTREAM_PASS = "PASS"

POLICY_CORRECTNESS_VIOLATED = "VIOLATED"
POLICY_CORRECTNESS_VALID = "VALID"

DECISION_WITHHOLD_POLICY = "WITHHOLD_POLICY"
DECISION_PASS_CORRECTNESS_GATE = "PASS_POLICY_CORRECTNESS_GATE"

REASON_CORRECTNESS_VIOLATION = (
    "POLICY_CORRECTNESS_CONSTRAINT_VIOLATION"
)

REASON_NO_CORRECTNESS_VIOLATION = (
    "NO_POLICY_CORRECTNESS_CONSTRAINT_VIOLATION"
)

UNDERLYING_POLICY_PERMIT = "PERMIT"
UNDERLYING_POLICY_DENY = "DENY"


@dataclass(frozen=True)
class PolicyCorrectnessGateInput:
    policy_artifact_id: str
    identity_state: str
    authority_state: str
    action_format_state: str
    target_state: str
    policy_parse_state: str
    policy_load_state: str
    underlying_policy_decision: str
    computed_correctness_state: str


@dataclass(frozen=True)
class PolicyCorrectnessGateDecision:
    policy_artifact_id: str
    correctness_decision: str
    reason: str
    underlying_policy_decision: str
    execution_attempted: Optional[bool]
    side_effect_occurred: Optional[bool]


class OutOfScopeUpstreamState(ValueError):
    """Raised when SEP-03 isolation preconditions have not all passed."""


class UnsupportedCorrectnessState(ValueError):
    """Raised for correctness states outside the frozen SEP-03 ontology."""


class UnsupportedUnderlyingPolicyDecision(ValueError):
    """Raised for policy decisions outside the frozen SEP-03 corpus."""


def _require_nonempty(
    value: str,
    field_name: str,
) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            f"{field_name} must be a non-empty string"
        )


def _require_upstream_pass(
    inp: PolicyCorrectnessGateInput,
) -> None:
    upstream = {
        "identity_state": inp.identity_state,
        "authority_state": inp.authority_state,
        "action_format_state": inp.action_format_state,
        "target_state": inp.target_state,
        "policy_parse_state": inp.policy_parse_state,
        "policy_load_state": inp.policy_load_state,
    }

    failed = {
        name: value
        for name, value in upstream.items()
        if value != UPSTREAM_PASS
    }

    if failed:
        raise OutOfScopeUpstreamState(
            "SEP-03 policy-correctness isolation requires "
            f"all upstream states to PASS; received {failed}"
        )


def evaluate_policy_correctness_gate(
    inp: PolicyCorrectnessGateInput,
) -> PolicyCorrectnessGateDecision:
    """
    Apply the bounded SEP-03 policy-correctness gate.

    PASS_POLICY_CORRECTNESS_GATE means only that the correctness layer
    did not withhold the policy. It does not convert an underlying DENY
    into PERMIT and does not itself authorize action execution.
    """

    _require_nonempty(
        inp.policy_artifact_id,
        "policy_artifact_id",
    )

    _require_upstream_pass(inp)

    if inp.underlying_policy_decision not in {
        UNDERLYING_POLICY_PERMIT,
        UNDERLYING_POLICY_DENY,
    }:
        raise UnsupportedUnderlyingPolicyDecision(
            "SEP-03 frozen corpus supports only "
            "PERMIT or DENY underlying policy decisions"
        )

    if (
        inp.computed_correctness_state
        == POLICY_CORRECTNESS_VIOLATED
    ):
        return PolicyCorrectnessGateDecision(
            policy_artifact_id=inp.policy_artifact_id,
            correctness_decision=DECISION_WITHHOLD_POLICY,
            reason=REASON_CORRECTNESS_VIOLATION,
            underlying_policy_decision=(
                inp.underlying_policy_decision
            ),
            execution_attempted=False,
            side_effect_occurred=False,
        )

    if (
        inp.computed_correctness_state
        == POLICY_CORRECTNESS_VALID
    ):
        return PolicyCorrectnessGateDecision(
            policy_artifact_id=inp.policy_artifact_id,
            correctness_decision=(
                DECISION_PASS_CORRECTNESS_GATE
            ),
            reason=REASON_NO_CORRECTNESS_VIOLATION,
            underlying_policy_decision=(
                inp.underlying_policy_decision
            ),
            execution_attempted=None,
            side_effect_occurred=None,
        )

    raise UnsupportedCorrectnessState(
        "SEP-03 correctness state must be "
        "VIOLATED or VALID"
    )
