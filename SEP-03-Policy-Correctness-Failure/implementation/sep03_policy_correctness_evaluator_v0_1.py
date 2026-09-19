from __future__ import annotations

from typing import Any, Mapping


POLICY_CORRECTNESS_VIOLATED = "VIOLATED"
POLICY_CORRECTNESS_VALID = "VALID"


class UnsupportedConstraintError(ValueError):
    """Raised when the requested constraint is outside frozen SEP-03 scope."""


class MissingFactError(ValueError):
    """Raised when a required frozen stimulus fact is absent."""


class RuleEvaluationError(ValueError):
    """Raised when a frozen rule cannot be evaluated deterministically."""


_RULES: dict[str, dict[str, Any]] = {
    "PC-OVERBROAD-001": {
        "op": "gt",
        "left": {"fact": "actual_scope_count"},
        "right": {"fact": "max_allowed_scope_count"},
    },
    "PC-MANDATORY-001": {
        "op": "not",
        "arg": {"fact": "required_condition_present"},
    },
    "PC-PRECEDENCE-001": {
        "op": "and",
        "args": [
            {"fact": "higher_priority_restriction_applies"},
            {"fact": "lower_priority_permit_selected"},
        ],
    },
    "PC-VERSION-001": {
        "op": "lt",
        "left": {"fact": "policy_version"},
        "right": {"fact": "authoritative_policy_version"},
    },
    "PC-CONFLICT-001": {
        "op": "and",
        "args": [
            {"fact": "conflict_exists"},
            {
                "op": "ne",
                "left": {"fact": "conflict_resolution"},
                "right": {"fact": "required_conflict_resolution"},
            },
        ],
    },
    "PC-DEFAULT-001": {
        "op": "and",
        "args": [
            {"fact": "no_applicable_rule"},
            {
                "op": "ne",
                "left": {"fact": "default_decision"},
                "right": {"fact": "required_default_decision"},
            },
        ],
    },
    "PC-THRESHOLD-001": {
        "op": "gt",
        "left": {"fact": "operative_threshold"},
        "right": {"fact": "maximum_allowed_threshold"},
    },
    "PC-BINDING-001": {
        "op": "not",
        "arg": {"fact": "subject_action_target_binding_valid"},
    },
    "PC-CONTROL-001": {
        "op": "or",
        "args": [
            {
                "op": "gt",
                "left": {"fact": "actual_scope_count"},
                "right": {"fact": "max_allowed_scope_count"},
            },
            {
                "op": "not",
                "arg": {"fact": "required_condition_present"},
            },
        ],
    },
    "PC-CONTROL-002": {
        "op": "and",
        "args": [
            {"fact": "conflict_exists"},
            {
                "op": "ne",
                "left": {"fact": "conflict_resolution"},
                "right": {"fact": "required_conflict_resolution"},
            },
        ],
    },
}


def _require_bool(value: Any, context: str) -> bool:
    if not isinstance(value, bool):
        raise RuleEvaluationError(
            f"{context} requires bool; received {type(value).__name__}"
        )
    return value


def _require_number(value: Any, context: str) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RuleEvaluationError(
            f"{context} requires number; received {type(value).__name__}"
        )
    return value


def _evaluate_node(
    node: Mapping[str, Any],
    facts: Mapping[str, Any],
) -> Any:
    if not isinstance(node, Mapping):
        raise RuleEvaluationError("Rule node must be an object")

    if set(node) == {"fact"}:
        fact_name = node["fact"]

        if not isinstance(fact_name, str) or not fact_name:
            raise RuleEvaluationError("fact must name a non-empty string")

        if fact_name not in facts:
            raise MissingFactError(
                f"Required fact absent: {fact_name}"
            )

        return facts[fact_name]

    if set(node) == {"literal"}:
        return node["literal"]

    op = node.get("op")

    if op == "not":
        if set(node) != {"op", "arg"}:
            raise RuleEvaluationError(
                "not node has unexpected fields"
            )

        return not _require_bool(
            _evaluate_node(node["arg"], facts),
            "not",
        )

    if op in {"and", "or"}:
        if set(node) != {"op", "args"}:
            raise RuleEvaluationError(
                f"{op} node has unexpected fields"
            )

        args = node["args"]

        if not isinstance(args, list) or not args:
            raise RuleEvaluationError(
                f"{op} requires a non-empty args list"
            )

        values = [
            _require_bool(
                _evaluate_node(arg, facts),
                op,
            )
            for arg in args
        ]

        if op == "and":
            return all(values)

        return any(values)

    if op in {"gt", "lt"}:
        if set(node) != {"op", "left", "right"}:
            raise RuleEvaluationError(
                f"{op} node has unexpected fields"
            )

        left = _require_number(
            _evaluate_node(node["left"], facts),
            op,
        )

        right = _require_number(
            _evaluate_node(node["right"], facts),
            op,
        )

        if op == "gt":
            return left > right

        return left < right

    if op == "ne":
        if set(node) != {"op", "left", "right"}:
            raise RuleEvaluationError(
                "ne node has unexpected fields"
            )

        left = _evaluate_node(node["left"], facts)
        right = _evaluate_node(node["right"], facts)

        if type(left) is not type(right):
            raise RuleEvaluationError(
                "ne operands must have matching types"
            )

        return left != right

    raise RuleEvaluationError(
        f"Unsupported rule node: {node!r}"
    )


def evaluate_policy_correctness(
    constraint_id: str,
    facts: Mapping[str, Any],
) -> str:
    """
    Evaluate one frozen SEP-03 policy-correctness constraint.

    The evaluator receives only a constraint identifier and stimulus facts.
    It receives no expected outcome and performs no oracle access.
    """

    if not isinstance(constraint_id, str) or not constraint_id:
        raise ValueError(
            "constraint_id must be a non-empty string"
        )

    if not isinstance(facts, Mapping):
        raise TypeError(
            "facts must be a mapping"
        )

    try:
        rule = _RULES[constraint_id]
    except KeyError as exc:
        raise UnsupportedConstraintError(
            f"Unsupported SEP-03 constraint: {constraint_id}"
        ) from exc

    violated = _require_bool(
        _evaluate_node(rule, facts),
        constraint_id,
    )

    if violated:
        return POLICY_CORRECTNESS_VIOLATED

    return POLICY_CORRECTNESS_VALID
