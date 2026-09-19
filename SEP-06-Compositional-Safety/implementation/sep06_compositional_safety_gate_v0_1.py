FAILURE_REASON = "FROZEN_COMPOSITIONAL_SAFETY_CONSTRAINT_VIOLATION"
CONTROL_REASON = "NO_FROZEN_COMPOSITIONAL_SAFETY_CONSTRAINT_VIOLATION"


def apply_compositional_gate(
    compositional_state: str,
    violation_count: int,
    violation_class: str,
) -> dict:
    if compositional_state == "COMPOSITIONALLY_INADMISSIBLE":
        if violation_count < 1:
            raise ValueError(
                "inadmissible composition requires one or more violations"
            )

        if violation_class == "NONE":
            raise ValueError(
                "inadmissible composition requires a violation class"
            )

        return {
            "decision": "WITHHOLD_COMPOSITIONAL_SAFETY",
            "reason": FAILURE_REASON,
            "execution_attempted": False,
            "side_effect": False,
        }

    if compositional_state == "COMPOSITIONALLY_ADMISSIBLE":
        if violation_count != 0:
            raise ValueError(
                "admissible composition requires zero violations"
            )

        if violation_class != "NONE":
            raise ValueError(
                "admissible composition requires NONE violation class"
            )

        return {
            "decision": "PASS_COMPOSITIONAL_GATE",
            "reason": CONTROL_REASON,
            "execution_attempted": None,
            "side_effect": None,
        }

    raise ValueError(
        f"unknown compositional state: {compositional_state}"
    )
