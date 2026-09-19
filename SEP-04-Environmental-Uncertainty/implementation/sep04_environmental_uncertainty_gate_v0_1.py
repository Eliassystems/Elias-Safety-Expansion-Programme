from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


PASS = "PASS"

NOT_ESTABLISHED = "NOT_ESTABLISHED"
ESTABLISHED = "ESTABLISHED"

WITHHOLD_ENVIRONMENTAL_UNCERTAINTY = (
    "WITHHOLD_ENVIRONMENTAL_UNCERTAINTY"
)

PASS_ENVIRONMENTAL_UNCERTAINTY_GATE = (
    "PASS_ENVIRONMENTAL_UNCERTAINTY_GATE"
)

ENVIRONMENTAL_PRECONDITION_NOT_ESTABLISHED = (
    "ENVIRONMENTAL_PRECONDITION_NOT_ESTABLISHED"
)

ENVIRONMENTAL_PRECONDITION_ESTABLISHED = (
    "ENVIRONMENTAL_PRECONDITION_ESTABLISHED"
)


class OutOfScopeUpstreamState(ValueError):
    pass


class OutOfScopeEnvironmentalPrecondition(ValueError):
    pass


class UnsupportedEnvironmentalState(ValueError):
    pass


@dataclass(frozen=True)
class EnvironmentalUncertaintyGateInput:
    evidence_artifact_id: str
    identity_state: str
    authority_state: str
    action_format_state: str
    target_state: str
    policy_admissibility_state: str
    technical_action_validity_state: str
    environmental_precondition_required: bool
    computed_environmental_precondition_state: str


@dataclass(frozen=True)
class EnvironmentalUncertaintyGateDecision:
    evidence_artifact_id: str
    environmental_uncertainty_decision: str
    reason: str
    execution_attempted: Optional[bool]
    side_effect_occurred: Optional[bool]


def evaluate_environmental_uncertainty_gate(
    gate_input: EnvironmentalUncertaintyGateInput,
) -> EnvironmentalUncertaintyGateDecision:
    if (
        not isinstance(
            gate_input.evidence_artifact_id,
            str,
        )
        or not gate_input.evidence_artifact_id
    ):
        raise ValueError(
            "evidence_artifact_id must be non-empty string"
        )

    upstream_states = {
        "identity_state": gate_input.identity_state,
        "authority_state": gate_input.authority_state,
        "action_format_state": gate_input.action_format_state,
        "target_state": gate_input.target_state,
        "policy_admissibility_state": (
            gate_input.policy_admissibility_state
        ),
        "technical_action_validity_state": (
            gate_input.technical_action_validity_state
        ),
    }

    for name, state in upstream_states.items():
        if state != PASS:
            raise OutOfScopeUpstreamState(
                f"{name} must be PASS"
            )

    if gate_input.environmental_precondition_required is not True:
        raise OutOfScopeEnvironmentalPrecondition(
            "environmental precondition must be required"
        )

    state = (
        gate_input.computed_environmental_precondition_state
    )

    if state == NOT_ESTABLISHED:
        return EnvironmentalUncertaintyGateDecision(
            evidence_artifact_id=(
                gate_input.evidence_artifact_id
            ),
            environmental_uncertainty_decision=(
                WITHHOLD_ENVIRONMENTAL_UNCERTAINTY
            ),
            reason=(
                ENVIRONMENTAL_PRECONDITION_NOT_ESTABLISHED
            ),
            execution_attempted=False,
            side_effect_occurred=False,
        )

    if state == ESTABLISHED:
        return EnvironmentalUncertaintyGateDecision(
            evidence_artifact_id=(
                gate_input.evidence_artifact_id
            ),
            environmental_uncertainty_decision=(
                PASS_ENVIRONMENTAL_UNCERTAINTY_GATE
            ),
            reason=(
                ENVIRONMENTAL_PRECONDITION_ESTABLISHED
            ),
            execution_attempted=None,
            side_effect_occurred=None,
        )

    raise UnsupportedEnvironmentalState(
        f"Unsupported environmental state: {state}"
    )
