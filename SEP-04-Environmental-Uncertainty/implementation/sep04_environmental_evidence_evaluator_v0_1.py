from __future__ import annotations

from typing import Any, Mapping


NOT_ESTABLISHED = "NOT_ESTABLISHED"
ESTABLISHED = "ESTABLISHED"


class UnsupportedConstraintError(ValueError):
    pass


class MissingFactError(ValueError):
    pass


class RuleEvaluationError(ValueError):
    pass


_RULES: dict[str, dict[str, Any]] = {
    "EU-PRESENCE-001": {
        "op": "not",
        "arg": {
            "fact": "required_observation_present",
        },
    },
    "EU-FRESHNESS-001": {
        "op": "gt",
        "left": {
            "fact": "observation_age",
        },
        "right": {
            "fact": "maximum_allowed_observation_age",
        },
    },
    "EU-CONSISTENCY-001": {
        "op": "not",
        "arg": {
            "fact": "observations_consistent",
        },
    },
    "EU-SUFFICIENCY-001": {
        "op": "lt",
        "left": {
            "fact": "available_evidence_count",
        },
        "right": {
            "fact": "required_evidence_count",
        },
    },
    "EU-BINDING-001": {
        "op": "ne",
        "left": {
            "fact": "observed_environment_id",
        },
        "right": {
            "fact": "required_environment_id",
        },
    },
    "EU-EPOCH-001": {
        "op": "ne",
        "left": {
            "fact": "observation_epoch",
        },
        "right": {
            "fact": "required_execution_epoch",
        },
    },
    "EU-PROVENANCE-001": {
        "op": "not",
        "arg": {
            "fact": "source_provenance_established",
        },
    },
    "EU-MEASUREMENT-001": {
        "op": "not",
        "arg": {
            "fact": "measurement_validity_established",
        },
    },
    "EU-CONTROL-001": {
        "op": "or",
        "args": [
            {
                "op": "not",
                "arg": {
                    "fact": "required_observation_present",
                },
            },
            {
                "op": "gt",
                "left": {
                    "fact": "observation_age",
                },
                "right": {
                    "fact": "maximum_allowed_observation_age",
                },
            },
            {
                "op": "not",
                "arg": {
                    "fact": "observations_consistent",
                },
            },
            {
                "op": "ne",
                "left": {
                    "fact": "observed_environment_id",
                },
                "right": {
                    "fact": "required_environment_id",
                },
            },
            {
                "op": "not",
                "arg": {
                    "fact": "source_provenance_established",
                },
            },
            {
                "op": "not",
                "arg": {
                    "fact": "measurement_validity_established",
                },
            },
        ],
    },
    "EU-CONTROL-002": {
        "op": "or",
        "args": [
            {
                "op": "lt",
                "left": {
                    "fact": "available_evidence_count",
                },
                "right": {
                    "fact": "required_evidence_count",
                },
            },
            {
                "op": "not",
                "arg": {
                    "fact": "observations_consistent",
                },
            },
            {
                "op": "gt",
                "left": {
                    "fact": "observation_age",
                },
                "right": {
                    "fact": "maximum_allowed_observation_age",
                },
            },
            {
                "op": "ne",
                "left": {
                    "fact": "observed_environment_id",
                },
                "right": {
                    "fact": "required_environment_id",
                },
            },
            {
                "op": "ne",
                "left": {
                    "fact": "observation_epoch",
                },
                "right": {
                    "fact": "required_execution_epoch",
                },
            },
            {
                "op": "not",
                "arg": {
                    "fact": "source_provenance_established",
                },
            },
            {
                "op": "not",
                "arg": {
                    "fact": "measurement_validity_established",
                },
            },
        ],
    },
}


def _require_bool(value: Any, name: str) -> bool:
    if type(value) is not bool:
        raise RuleEvaluationError(
            f"{name} must be bool"
        )

    return value


def _require_number(value: Any, name: str) -> int | float:
    if isinstance(value, bool) or not isinstance(
        value,
        (int, float),
    ):
        raise RuleEvaluationError(
            f"{name} must be numeric"
        )

    return value


def _fact_value(
    node: Mapping[str, Any],
    facts: Mapping[str, Any],
) -> Any:
    if set(node) != {"fact"}:
        raise RuleEvaluationError(
            "Fact node contains unexpected fields"
        )

    name = node["fact"]

    if not isinstance(name, str) or not name:
        raise RuleEvaluationError(
            "Fact name must be non-empty string"
        )

    if name not in facts:
        raise MissingFactError(
            f"Required fact absent: {name}"
        )

    return facts[name]


def _value(
    node: Mapping[str, Any],
    facts: Mapping[str, Any],
) -> Any:
    if "fact" in node:
        return _fact_value(node, facts)

    raise RuleEvaluationError(
        "Unsupported value node"
    )


def _evaluate_node(
    node: Mapping[str, Any],
    facts: Mapping[str, Any],
) -> bool:
    if not isinstance(node, Mapping):
        raise RuleEvaluationError(
            "Rule node must be mapping"
        )

    op = node.get("op")

    if op == "not":
        if set(node) != {"op", "arg"}:
            raise RuleEvaluationError(
                "not node contains unexpected fields"
            )

        value = _value(node["arg"], facts)

        return not _require_bool(
            value,
            "not operand",
        )

    if op == "or":
        if set(node) != {"op", "args"}:
            raise RuleEvaluationError(
                "or node contains unexpected fields"
            )

        args = node["args"]

        if (
            not isinstance(args, list)
            or not args
        ):
            raise RuleEvaluationError(
                "or args must be non-empty list"
            )

        return any(
            _evaluate_node(arg, facts)
            for arg in args
        )

    if op in {"gt", "lt"}:
        if set(node) != {"op", "left", "right"}:
            raise RuleEvaluationError(
                f"{op} node contains unexpected fields"
            )

        left = _require_number(
            _value(node["left"], facts),
            f"{op} left operand",
        )

        right = _require_number(
            _value(node["right"], facts),
            f"{op} right operand",
        )

        if op == "gt":
            return left > right

        return left < right

    if op == "ne":
        if set(node) != {"op", "left", "right"}:
            raise RuleEvaluationError(
                "ne node contains unexpected fields"
            )

        left = _value(node["left"], facts)
        right = _value(node["right"], facts)

        return left != right

    raise RuleEvaluationError(
        f"Unsupported rule operation: {op!r}"
    )


def evaluate_environmental_precondition(
    constraint_id: str,
    facts: Mapping[str, Any],
) -> str:
    if not isinstance(constraint_id, str) or not constraint_id:
        raise UnsupportedConstraintError(
            "constraint_id must be non-empty string"
        )

    if not isinstance(facts, Mapping):
        raise RuleEvaluationError(
            "facts must be mapping"
        )

    if constraint_id not in _RULES:
        raise UnsupportedConstraintError(
            f"Unsupported environmental constraint: {constraint_id}"
        )

    uncertainty_condition = _evaluate_node(
        _RULES[constraint_id],
        facts,
    )

    if uncertainty_condition:
        return NOT_ESTABLISHED

    return ESTABLISHED
