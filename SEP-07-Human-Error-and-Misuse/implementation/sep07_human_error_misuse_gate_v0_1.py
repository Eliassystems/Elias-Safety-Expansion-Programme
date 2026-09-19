"""SEP-07 bounded human-error/misuse safety gate.

Pure decision projection over evaluator output.
No filesystem, network, subprocess, oracle, or side-effect access.
"""


def apply_human_error_misuse_gate(evaluation):
    safety_state = evaluation.get("safety_state")

    if safety_state == "CONFLICT_ESTABLISHED":
        return {
            "decision": "WITHHOLD_HUMAN_ERROR_MISUSE_SAFETY",
            "execution_attempted": False,
            "side_effect": False,
        }

    if safety_state == "NO_CONFLICT_ESTABLISHED":
        return {
            "decision": "PASS_HUMAN_ERROR_MISUSE_GATE",
            "execution_attempted": None,
            "side_effect": None,
        }

    raise ValueError(
        f"UNKNOWN_EVALUATOR_STATE:{safety_state}"
    )
