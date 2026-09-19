"""SEP-08 bounded pre-execution recoverability evaluator v0.1.

Pure internal classification only.
No filesystem, network, subprocess, oracle, or real-world execution.
"""


def _unavailable():
    return {
        "safety_state": "RECOVERABILITY_CONFLICT_ESTABLISHED",
        "recovery_state": "RECOVERY_GUARANTEE_UNAVAILABLE",
        "reason": "RECOVERY_GUARANTEE_UNAVAILABLE",
    }


def _not_established():
    return {
        "safety_state": "RECOVERABILITY_CONFLICT_ESTABLISHED",
        "recovery_state": "RECOVERY_GUARANTEE_NOT_ESTABLISHED",
        "reason": "RECOVERY_GUARANTEE_NOT_ESTABLISHED",
    }


def _established():
    return {
        "safety_state": "NO_RECOVERABILITY_CONFLICT_ESTABLISHED",
        "recovery_state": "RECOVERY_GUARANTEE_ESTABLISHED",
        "reason": "RECOVERY_GUARANTEE_ESTABLISHED",
    }


def evaluate_recoverability(record):
    required_upstream = (
        "identity_valid",
        "authority_valid",
        "policy_admissible",
        "technical_valid",
        "target_valid",
    )

    for field in required_upstream:
        if record.get(field) is not True:
            raise ValueError("upstream condition outside frozen SEP-08 proposition")

    requirement = record.get("recovery_requirement")
    evidence = record.get("recovery_evidence")

    if not isinstance(requirement, dict):
        raise ValueError("recovery requirement absent")

    if not isinstance(evidence, dict):
        raise ValueError("recovery evidence absent as structured input")

    if requirement.get("required") is not True:
        raise ValueError("frozen recovery requirement not required")

    if requirement.get("required_target_id") != record.get("target_id"):
        raise ValueError("recovery requirement target binding mismatch")

    if requirement.get("required_operation") != record.get("requested_operation"):
        raise ValueError("recovery requirement operation binding mismatch")

    if evidence.get("rollback_path_state") == "UNAVAILABLE":
        return _unavailable()

    if evidence.get("target_coverage_state") == "NOT_COVERED":
        return _unavailable()

    if evidence.get("recovery_window_state") == "UNAVAILABLE":
        return _unavailable()

    if evidence.get("operation_coverage_state") == "UNSUPPORTED":
        return _unavailable()

    if evidence.get("evidence_presence_state") == "ABSENT":
        return _not_established()

    if evidence.get("evidence_verifiability_state") == "UNVERIFIABLE":
        return _not_established()

    if evidence.get("target_binding_state") == "NOT_ESTABLISHED":
        return _not_established()

    if evidence.get("operation_coverage_state") == "NOT_ESTABLISHED":
        return _not_established()

    established_requirements = (
        evidence.get("evidence_presence_state") == "PRESENT",
        evidence.get("evidence_verifiability_state") == "VERIFIED",
        evidence.get("rollback_path_state") == "AVAILABLE",
        evidence.get("recovery_state_presence") == "PRESENT",
        evidence.get("target_coverage_state") == "COVERED",
        evidence.get("recovery_window_state") == "AVAILABLE",
        evidence.get("target_binding_state") == "ESTABLISHED",
        evidence.get("operation_coverage_state") == "SUPPORTED",
    )

    if all(established_requirements):
        return _established()

    return _not_established()
