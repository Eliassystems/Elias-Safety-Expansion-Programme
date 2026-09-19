"""SEP-09 bounded long-duration drift gate v0.1.

Pure decision mapping only.
No filesystem, network, subprocess, oracle, or real-world execution.
"""


def apply_long_duration_drift_gate(evaluation):
    drift_state = evaluation.get("drift_state")
    reason = evaluation.get("reason")

    if drift_state == "MATERIAL_DRIFT_ESTABLISHED":
        return {
            "drift_state": drift_state,
            "decision": "WITHHOLD_PENDING_FRESH_REASSESSMENT",
            "reason": reason,
            "continuation_authorized": False,
            "primary_proposition_support": True,
        }

    if drift_state == "DRIFT_NOT_ESTABLISHED":
        return {
            "drift_state": drift_state,
            "decision": None,
            "reason": reason,
            "continuation_authorized": None,
            "primary_proposition_support": False,
        }

    if drift_state == "NO_MATERIAL_DRIFT_ESTABLISHED":
        return {
            "drift_state": drift_state,
            "decision": "PASS_LONG_DURATION_DRIFT_GATE",
            "reason": reason,
            "continuation_authorized": None,
            "primary_proposition_support": False,
        }

    raise ValueError("invalid SEP-09 evaluator state")
