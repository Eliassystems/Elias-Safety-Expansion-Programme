"""SEP-07 bounded human-error/misuse safety evaluator.

Pure internal evaluation logic only.
No filesystem, network, subprocess, oracle, human-intent, or side-effect access.
"""

_REQUIRED_TRUE_FIELDS = (
    "human_identity_valid",
    "human_authority_valid",
    "approval_authentic",
    "policy_admissible",
    "request_technically_valid",
)


def _require_upstream_validity(case):
    for field in _REQUIRED_TRUE_FIELDS:
        if case.get(field) is not True:
            raise ValueError(
                f"OUT_OF_SCOPE_UPSTREAM_PRECONDITION_FAILURE:{field}"
            )


def _targets_are_subset(requested, allowed):
    return set(requested).issubset(set(allowed))


def evaluate_human_error_misuse(case):
    _require_upstream_validity(case)

    if case.get("stated_objective_present") is True:
        if case["requested_scope"] not in case["objective_allowed_scopes"]:
            return {
                "safety_state": "CONFLICT_ESTABLISHED",
                "conflict_class": "OBJECTIVE_SCOPE_MISMATCH",
                "reason": "OBJECTIVE_SCOPE_CONFLICT",
            }

        if not _targets_are_subset(
            case["requested_targets"],
            case["objective_allowed_targets"],
        ):
            return {
                "safety_state": "CONFLICT_ESTABLISHED",
                "conflict_class": "OBJECTIVE_TARGET_SET_MISMATCH",
                "reason": "OBJECTIVE_TARGET_SET_CONFLICT",
            }

        objective_max = case.get("objective_max_quantity")
        if (
            objective_max is not None
            and case["requested_quantity"] > objective_max
        ):
            return {
                "safety_state": "CONFLICT_ESTABLISHED",
                "conflict_class": "OBJECTIVE_QUANTITY_BOUND_MISMATCH",
                "reason": "OBJECTIVE_QUANTITY_BOUND_CONFLICT",
            }

        if (
            case["requested_operation"]
            not in case["objective_allowed_operations"]
        ):
            return {
                "safety_state": "CONFLICT_ESTABLISHED",
                "conflict_class": "OBJECTIVE_OPERATION_MISMATCH",
                "reason": "OBJECTIVE_OPERATION_CONFLICT",
            }

    if case.get("human_use_constraint_present") is True:
        if (
            case["requested_scope"]
            not in case["use_constraint_allowed_scopes"]
        ):
            return {
                "safety_state": "CONFLICT_ESTABLISHED",
                "conflict_class": "USE_CONSTRAINT_SCOPE_VIOLATION",
                "reason": "USE_CONSTRAINT_SCOPE_CONFLICT",
            }

        if not _targets_are_subset(
            case["requested_targets"],
            case["use_constraint_allowed_targets"],
        ):
            return {
                "safety_state": "CONFLICT_ESTABLISHED",
                "conflict_class": "USE_CONSTRAINT_TARGET_SET_VIOLATION",
                "reason": "USE_CONSTRAINT_TARGET_SET_CONFLICT",
            }

        use_max = case.get("use_constraint_max_quantity")
        if (
            use_max is not None
            and case["requested_quantity"] > use_max
        ):
            return {
                "safety_state": "CONFLICT_ESTABLISHED",
                "conflict_class": "USE_CONSTRAINT_QUANTITY_BOUND_VIOLATION",
                "reason": "USE_CONSTRAINT_QUANTITY_BOUND_CONFLICT",
            }

        if (
            case["requested_operation"]
            not in case["use_constraint_allowed_operations"]
        ):
            return {
                "safety_state": "CONFLICT_ESTABLISHED",
                "conflict_class": "USE_CONSTRAINT_OPERATION_VIOLATION",
                "reason": "USE_CONSTRAINT_OPERATION_CONFLICT",
            }

    return {
        "safety_state": "NO_CONFLICT_ESTABLISHED",
        "conflict_class": "NONE",
        "reason": "NO_HUMAN_ERROR_MISUSE_CONFLICT",
    }
