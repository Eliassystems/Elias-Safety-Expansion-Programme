"""SEP-05 bounded dependency-state evaluator.

No oracle data is accepted by this module.
No execution side effects are performed by this module.
"""

REQUIRED_UPSTREAM_FIELDS = (
    "identity_state",
    "authority_state",
    "action_format_state",
    "target_state",
    "policy_admissibility_state",
    "technical_action_validity_state",
    "consequence_gate_state",
    "environmental_precondition_state",
)

VALID_DETERMINATION = "REQUIRED_DEPENDENCY_VALID_FOR_RELIANCE"
INVALID_DETERMINATION = "REQUIRED_DEPENDENCY_NOT_VALID_FOR_RELIANCE"


def evaluate_dependency_state(stimulus: dict) -> dict:
    if not isinstance(stimulus, dict):
        raise TypeError("stimulus must be a dict")

    for field in REQUIRED_UPSTREAM_FIELDS:
        if stimulus.get(field) != "PASS":
            raise ValueError(f"upstream isolation not held: {field}")

    if stimulus.get("dependency_required") is not True:
        raise ValueError("dependency_required must be true")

    if stimulus.get("dependency_present") is not True:
        state = "ABSENT"

    elif stimulus.get("dependency_revoked") is True:
        state = "REVOKED"

    elif stimulus.get("dependency_dispute_open") is True:
        state = "DISPUTED"

    elif stimulus.get("verification_succeeds") is not True:
        state = "UNVERIFIABLE"

    elif stimulus.get("intrinsic_valid") is not True:
        state = "INVALID"

    elif stimulus.get("freshness_valid") is not True:
        state = "STALE"

    elif stimulus.get("binding_matches") is not True:
        state = "BINDING_MISMATCH"

    elif (
        stimulus.get("version_matches") is not True
        or stimulus.get("epoch_matches") is not True
    ):
        state = "VERSION_OR_EPOCH_MISMATCH"

    else:
        state = "VALID"

    determination = (
        VALID_DETERMINATION
        if state == "VALID"
        else INVALID_DETERMINATION
    )

    return {
        "dependency_state": state,
        "dependency_determination": determination,
    }
