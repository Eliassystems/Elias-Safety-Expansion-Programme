"""SEP-08 bounded containment/recovery decision gate v0.1.

Pure mapping only.
No filesystem, network, subprocess, oracle, or real-world execution.
"""


def apply_recoverability_gate(evaluation):
    safety_state = evaluation.get("safety_state")
    recovery_state = evaluation.get("recovery_state")
    reason = evaluation.get("reason")

    if (
        safety_state == "RECOVERABILITY_CONFLICT_ESTABLISHED"
        and recovery_state
        in {
            "RECOVERY_GUARANTEE_UNAVAILABLE",
            "RECOVERY_GUARANTEE_NOT_ESTABLISHED",
        }
    ):
        return {
            "safety_state": safety_state,
            "recovery_state": recovery_state,
            "decision": "WITHHOLD_CONTAINMENT_RECOVERY_SAFETY",
            "reason": reason,
            "execution_attempted": False,
            "side_effect": False,
        }

    if (
        safety_state == "NO_RECOVERABILITY_CONFLICT_ESTABLISHED"
        and recovery_state == "RECOVERY_GUARANTEE_ESTABLISHED"
    ):
        return {
            "safety_state": safety_state,
            "recovery_state": recovery_state,
            "decision": "PASS_CONTAINMENT_RECOVERY_GATE",
            "reason": reason,
            "execution_attempted": None,
            "side_effect": None,
        }

    raise ValueError("invalid SEP-08 evaluator state")
