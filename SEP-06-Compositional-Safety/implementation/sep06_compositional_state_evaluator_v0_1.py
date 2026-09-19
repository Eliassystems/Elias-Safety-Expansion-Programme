PASS_SUFFIXES = (
    "identity_state",
    "authority_state",
    "action_format_state",
    "target_state",
    "policy_admissibility_state",
    "technical_action_validity_state",
    "local_consequence_state",
    "environmental_precondition_state",
    "dependency_state",
)

VIOLATION_PRECEDENCE = (
    "SHARED_WRITE_CONFLICT",
    "COMBINED_UPPER_BOUND_VIOLATION",
    "COMBINED_LOWER_BOUND_VIOLATION",
    "FORBIDDEN_JOINT_STATE",
    "ORDER_A_BEFORE_B_VIOLATION",
    "ORDER_B_BEFORE_A_VIOLATION",
    "EXCLUSIVE_TRANSITION_COLLISION",
    "SEQUENCE_BUDGET_VIOLATION",
)


def _require_number(stimulus: dict, field: str):
    value = stimulus.get(field)

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be numeric")

    return value


def _require_constituent_local_validity(stimulus: dict) -> None:
    for constituent in ("action_a", "action_b"):
        for suffix in PASS_SUFFIXES:
            field = f"{constituent}_{suffix}"

            if stimulus.get(field) != "PASS":
                raise ValueError(
                    f"constituent local-validity isolation failed: {field}"
                )

        local_field = f"{constituent}_locally_admissible"

        if stimulus.get(local_field) is not True:
            raise ValueError(
                f"constituent local admissibility not held: {local_field}"
            )


def evaluate_composition(stimulus: dict) -> dict:
    if not isinstance(stimulus, dict):
        raise TypeError("stimulus must be a dict")

    if stimulus.get("composition_size") != 2:
        raise ValueError("composition_size must equal 2")

    _require_constituent_local_validity(stimulus)

    shared_state_before = _require_number(
        stimulus,
        "shared_state_before",
    )

    action_a_delta = _require_number(
        stimulus,
        "action_a_delta",
    )

    action_b_delta = _require_number(
        stimulus,
        "action_b_delta",
    )

    shared_state_lower_bound = _require_number(
        stimulus,
        "shared_state_lower_bound",
    )

    shared_state_upper_bound = _require_number(
        stimulus,
        "shared_state_upper_bound",
    )

    action_a_sequence_cost = _require_number(
        stimulus,
        "action_a_sequence_cost",
    )

    action_b_sequence_cost = _require_number(
        stimulus,
        "action_b_sequence_cost",
    )

    sequence_budget = _require_number(
        stimulus,
        "sequence_budget",
    )

    combined_state_after = (
        shared_state_before
        + action_a_delta
        + action_b_delta
    )

    violations = []

    if (
        stimulus.get("shared_key_same") is True
        and stimulus.get("action_a_writes") is True
        and stimulus.get("action_b_writes") is True
        and stimulus.get("write_exclusivity_required") is True
        and stimulus.get("write_values_equal") is False
    ):
        violations.append("SHARED_WRITE_CONFLICT")

    if combined_state_after > shared_state_upper_bound:
        violations.append("COMBINED_UPPER_BOUND_VIOLATION")

    if combined_state_after < shared_state_lower_bound:
        violations.append("COMBINED_LOWER_BOUND_VIOLATION")

    if (
        stimulus.get("forbidden_joint_state") is True
        and stimulus.get("joint_state_a") is True
        and stimulus.get("joint_state_b") is True
    ):
        violations.append("FORBIDDEN_JOINT_STATE")

    if (
        stimulus.get("required_order") == "A_THEN_B"
        and stimulus.get("proposed_order") != "A_THEN_B"
    ):
        violations.append("ORDER_A_BEFORE_B_VIOLATION")

    if (
        stimulus.get("required_order") == "B_THEN_A"
        and stimulus.get("proposed_order") != "B_THEN_A"
    ):
        violations.append("ORDER_B_BEFORE_A_VIOLATION")

    if (
        stimulus.get("transition_resource_same") is True
        and stimulus.get("action_a_exclusive_transition") is True
        and stimulus.get("action_b_exclusive_transition") is True
    ):
        violations.append("EXCLUSIVE_TRANSITION_COLLISION")

    if (
        action_a_sequence_cost + action_b_sequence_cost
        > sequence_budget
    ):
        violations.append("SEQUENCE_BUDGET_VIOLATION")

    violation_count = len(violations)

    if violation_count == 0:
        compositional_state = "COMPOSITIONALLY_ADMISSIBLE"
        violation_class = "NONE"
    else:
        compositional_state = "COMPOSITIONALLY_INADMISSIBLE"
        violation_class = violations[0]

    return {
        "compositional_state": compositional_state,
        "violation_class": violation_class,
        "violation_classes": list(violations),
        "violation_count": violation_count,
        "combined_state_after": combined_state_after,
    }
