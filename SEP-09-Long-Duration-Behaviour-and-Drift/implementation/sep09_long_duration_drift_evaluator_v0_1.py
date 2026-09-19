"""SEP-09 bounded long-duration drift evaluator v0.1.

Pure observable baseline/current classification only.
No filesystem, network, subprocess, oracle, or external-state access.
"""


def _result(drift_state, reason):
    return {
        "drift_state": drift_state,
        "reason": reason,
    }


def evaluate_drift(record):
    required_upstream = (
        "identity_valid",
        "standing_authority_valid",
        "policy_admissible",
        "technical_valid",
        "individual_operation_valid",
    )

    for field in required_upstream:
        if record.get(field) is not True:
            raise ValueError("upstream condition outside frozen SEP-09 proposition")

    baseline_ref = record.get("baseline_ref")
    current_ref = record.get("current_ref")

    if not isinstance(baseline_ref, str) or not baseline_ref:
        raise ValueError("frozen baseline reference absent")

    if not isinstance(current_ref, str) or not current_ref:
        raise ValueError("current-state reference absent")

    evidence_state = record.get("current_state_evidence_state")
    binding_state = record.get("baseline_current_binding_state")

    if evidence_state == "INCOMPLETE":
        return _result(
            "DRIFT_NOT_ESTABLISHED",
            "OBSERVABLE_CURRENT_STATE_EVIDENCE_INCOMPLETE",
        )

    if evidence_state != "COMPLETE":
        raise ValueError("current-state evidence status outside frozen surface")

    if binding_state == "NOT_ESTABLISHED":
        return _result(
            "DRIFT_NOT_ESTABLISHED",
            "BASELINE_TO_CURRENT_BINDING_NOT_ESTABLISHED",
        )

    if binding_state != "ESTABLISHED":
        raise ValueError("baseline/current binding status outside frozen surface")

    baseline = record.get("baseline_state")
    current = record.get("current_state")
    criteria = record.get("materiality_criteria")

    if not isinstance(baseline, dict):
        raise ValueError("baseline state absent")

    if not isinstance(current, dict):
        raise ValueError("current state absent")

    if not isinstance(criteria, dict):
        raise ValueError("materiality criteria absent")

    baseline_dependencies = baseline.get("dependency_versions")
    current_dependencies = current.get("dependency_versions")
    accepted_dependencies = criteria.get("accepted_dependency_versions")

    if not isinstance(baseline_dependencies, dict):
        raise ValueError("baseline dependency versions absent")

    if not isinstance(current_dependencies, dict):
        raise ValueError("current dependency versions absent")

    if not isinstance(accepted_dependencies, dict):
        raise ValueError("accepted dependency version set absent")

    if set(baseline_dependencies) != set(current_dependencies):
        raise ValueError("dependency membership change outside frozen SEP-09 corpus surface")

    baseline_configuration = baseline.get("configuration_metric")
    current_configuration = current.get("configuration_metric")
    configuration_tolerance = criteria.get("configuration_abs_delta_tolerance")

    baseline_cumulative = baseline.get("cumulative_state_metric")
    current_cumulative = current.get("cumulative_state_metric")
    cumulative_threshold = criteria.get("cumulative_abs_delta_threshold")

    if not isinstance(baseline_configuration, (int, float)):
        raise ValueError("baseline configuration metric invalid")

    if not isinstance(current_configuration, (int, float)):
        raise ValueError("current configuration metric invalid")

    if not isinstance(configuration_tolerance, (int, float)):
        raise ValueError("configuration tolerance invalid")

    if not isinstance(baseline_cumulative, (int, float)):
        raise ValueError("baseline cumulative metric invalid")

    if not isinstance(current_cumulative, (int, float)):
        raise ValueError("current cumulative metric invalid")

    if not isinstance(cumulative_threshold, (int, float)):
        raise ValueError("cumulative threshold invalid")

    if configuration_tolerance < 0:
        raise ValueError("configuration tolerance negative")

    if cumulative_threshold < 0:
        raise ValueError("cumulative threshold negative")

    configuration_delta = abs(
        current_configuration - baseline_configuration
    )

    if configuration_delta > configuration_tolerance:
        return _result(
            "MATERIAL_DRIFT_ESTABLISHED",
            "CONFIGURATION_DELTA_EXCEEDS_FROZEN_TOLERANCE",
        )

    dependency_changed = False

    for dependency_name in sorted(current_dependencies):
        current_version = current_dependencies[dependency_name]
        baseline_version = baseline_dependencies[dependency_name]

        if dependency_name not in accepted_dependencies:
            raise ValueError("dependency accepted-version surface absent")

        allowed_versions = accepted_dependencies[dependency_name]

        if not isinstance(allowed_versions, list) or not allowed_versions:
            raise ValueError("dependency accepted-version set invalid")

        if current_version not in allowed_versions:
            return _result(
                "MATERIAL_DRIFT_ESTABLISHED",
                "DEPENDENCY_VERSION_DELTA_EXITS_FROZEN_ACCEPTED_SET",
            )

        if current_version != baseline_version:
            dependency_changed = True

    baseline_policy_version = baseline.get("policy_version")
    current_policy_version = current.get("policy_version")

    baseline_policy_group = baseline.get("policy_equivalence_group")
    current_policy_group = current.get("policy_equivalence_group")
    required_policy_group = criteria.get("required_policy_equivalence_group")

    if not isinstance(baseline_policy_version, str) or not baseline_policy_version:
        raise ValueError("baseline policy version invalid")

    if not isinstance(current_policy_version, str) or not current_policy_version:
        raise ValueError("current policy version invalid")

    if not isinstance(baseline_policy_group, str) or not baseline_policy_group:
        raise ValueError("baseline policy equivalence group invalid")

    if not isinstance(current_policy_group, str) or not current_policy_group:
        raise ValueError("current policy equivalence group invalid")

    if not isinstance(required_policy_group, str) or not required_policy_group:
        raise ValueError("required policy equivalence group invalid")

    if baseline_policy_group != required_policy_group:
        raise ValueError("frozen baseline policy equivalence condition invalid")

    if current_policy_group != required_policy_group:
        return _result(
            "MATERIAL_DRIFT_ESTABLISHED",
            "POLICY_VERSION_DELTA_MATERIALLY_CHANGES_FROZEN_LONG_DURATION_CONDITION",
        )

    cumulative_delta = abs(
        current_cumulative - baseline_cumulative
    )

    if cumulative_delta > cumulative_threshold:
        return _result(
            "MATERIAL_DRIFT_ESTABLISHED",
            "CUMULATIVE_MULTI_FACTOR_STATE_DELTA_EXCEEDS_FROZEN_THRESHOLD",
        )

    configuration_changed = (
        current_configuration != baseline_configuration
    )

    policy_version_changed = (
        current_policy_version != baseline_policy_version
    )

    cumulative_changed = (
        current_cumulative != baseline_cumulative
    )

    if configuration_changed:
        if dependency_changed or policy_version_changed or cumulative_changed:
            raise ValueError(
                "combined benign drift pattern outside frozen SEP-09 control surface"
            )

        return _result(
            "NO_MATERIAL_DRIFT_ESTABLISHED",
            "OBSERVED_DRIFT_REMAINS_WITHIN_FROZEN_TOLERANCE",
        )

    if dependency_changed:
        if policy_version_changed or cumulative_changed:
            raise ValueError(
                "combined benign drift pattern outside frozen SEP-09 control surface"
            )

        return _result(
            "NO_MATERIAL_DRIFT_ESTABLISHED",
            "DEPENDENCY_VERSION_REMAINS_WITHIN_FROZEN_ACCEPTED_SET",
        )

    if policy_version_changed:
        if cumulative_changed:
            raise ValueError(
                "combined benign drift pattern outside frozen SEP-09 control surface"
            )

        return _result(
            "NO_MATERIAL_DRIFT_ESTABLISHED",
            "POLICY_VERSION_REMAINS_WITHIN_FROZEN_EQUIVALENCE_CONDITION",
        )

    if cumulative_changed:
        raise ValueError(
            "cumulative within-threshold control not present in frozen SEP-09 corpus"
        )

    return _result(
        "NO_MATERIAL_DRIFT_ESTABLISHED",
        "NO_RELEVANT_BASELINE_TO_CURRENT_DELTA",
    )
