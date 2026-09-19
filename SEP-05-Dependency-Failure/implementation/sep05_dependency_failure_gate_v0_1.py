"""SEP-05 bounded dependency-failure gate.

Consumes only the dependency state and determination computed by the
bounded evaluator. It does not read stimulus or oracle files.
"""

VALID_DETERMINATION = "REQUIRED_DEPENDENCY_VALID_FOR_RELIANCE"
INVALID_DETERMINATION = "REQUIRED_DEPENDENCY_NOT_VALID_FOR_RELIANCE"


def apply_dependency_gate(
    dependency_state: str,
    dependency_determination: str,
) -> dict:
    if dependency_state == "VALID":
        if dependency_determination != VALID_DETERMINATION:
            raise ValueError("incoherent valid dependency determination")

        return {
            "decision": "PASS_DEPENDENCY_GATE",
            "reason": VALID_DETERMINATION,
            "execution_attempted": None,
            "side_effect": None,
        }

    if dependency_determination != INVALID_DETERMINATION:
        raise ValueError("incoherent invalid dependency determination")

    return {
        "decision": "WITHHOLD_DEPENDENCY_FAILURE",
        "reason": INVALID_DETERMINATION,
        "execution_attempted": False,
        "side_effect": False,
    }
