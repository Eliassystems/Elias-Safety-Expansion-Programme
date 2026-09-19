from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

STIMULI_PATH = HERE / "SEP-03-POLICY-STIMULI-v1.0.jsonl"
SPEC_PATH = HERE / "SEP-03-POLICY-CORRECTNESS-SPEC-v1.0.jsonl"
MATRIX_PATH = HERE / "SEP-03-TEST-MATRIX-v1.0.jsonl"

EVALUATOR_PATH = (
    ROOT
    / "implementation"
    / "sep03_policy_correctness_evaluator_v0_1.py"
)

GATE_PATH = (
    ROOT
    / "implementation"
    / "sep03_policy_correctness_gate_v0_1.py"
)


EXPECTED_STIMULI_SHA256 = (
    "6DB566603525C7339B6D31A1B3C14CAAED0839152A3ECC7A2C0278913D4E598A"
)

EXPECTED_SPEC_SHA256 = (
    "82786FE3390D1A691A0B275C4619E6F8DD172E525809EEB2CD978ED5B54ADB61"
)

EXPECTED_MATRIX_SHA256 = (
    "2E2A2309937CBD036E9E7C91A87BBBD62D950C40EFE260754B5DC86AC94C585F"
)

EXPECTED_EVALUATOR_SHA256 = (
    "F68F369AF42FCCDAFA32AACE67A820340F29F7C78730EB3956585B56E46B7DE4"
)

EXPECTED_GATE_SHA256 = (
    "5E65230746424365F53F283BA9B86796703CC9418717BA652B8DE683BB8E5BB7"
)


EXPECTED_STIMULUS_FIELDS = {
    "stimulus_id",
    "policy_artifact_id",
    "constraint_id",
    "identity_state",
    "authority_state",
    "action_format_state",
    "target_state",
    "policy_parse_state",
    "policy_load_state",
    "underlying_policy_decision",
    "facts",
}


EXPECTED_ORACLE_FIELDS = {
    "test_id",
    "stimulus_id",
    "policy_artifact_id",
    "test_type",
    "policy_failure_class",
    "constraint_id",
    "expected_correctness_state",
    "expected_correctness_decision",
    "expected_reason",
    "expected_execution_attempted",
    "expected_side_effect",
    "expected_underlying_policy_decision",
    "expected_case_result",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def verify_bound_identities() -> None:
    bound = {
        STIMULI_PATH: EXPECTED_STIMULI_SHA256,
        SPEC_PATH: EXPECTED_SPEC_SHA256,
        MATRIX_PATH: EXPECTED_MATRIX_SHA256,
        EVALUATOR_PATH: EXPECTED_EVALUATOR_SHA256,
        GATE_PATH: EXPECTED_GATE_SHA256,
    }

    for path, expected in bound.items():
        actual = sha256_file(path)

        if actual != expected:
            raise RuntimeError(
                f"Bound identity mismatch for {path.name}: "
                f"{actual} != {expected}"
            )


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line.strip():
            continue

        value = json.loads(line)

        if not isinstance(value, dict):
            raise ValueError(
                f"{path.name}:{line_number} must be an object"
            )

        rows.append(value)

    return rows


def load_module(path: Path, module_name: str) -> Any:
    spec = importlib.util.spec_from_file_location(
        module_name,
        path,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            f"Unable to load module specification: {path}"
        )

    module = importlib.util.module_from_spec(spec)

    sys.modules[spec.name] = module

    spec.loader.exec_module(module)

    return module


def load_stimuli() -> list[dict[str, Any]]:
    rows = load_jsonl(STIMULI_PATH)

    if len(rows) != 10:
        raise ValueError(
            f"Expected 10 stimuli; received {len(rows)}"
        )

    seen: set[str] = set()

    for row in rows:
        if set(row) != EXPECTED_STIMULUS_FIELDS:
            raise ValueError(
                "Stimulus field set differs from frozen SEP-03 schema"
            )

        stimulus_id = row["stimulus_id"]

        if stimulus_id in seen:
            raise ValueError(
                f"Duplicate stimulus_id: {stimulus_id}"
            )

        seen.add(stimulus_id)

        for field in (
            "identity_state",
            "authority_state",
            "action_format_state",
            "target_state",
            "policy_parse_state",
            "policy_load_state",
        ):
            if row[field] != "PASS":
                raise ValueError(
                    f"{stimulus_id}: {field} must be PASS"
                )

        if row["underlying_policy_decision"] not in {
            "PERMIT",
            "DENY",
        }:
            raise ValueError(
                f"{stimulus_id}: unsupported underlying policy decision"
            )

        if not isinstance(row["facts"], dict):
            raise ValueError(
                f"{stimulus_id}: facts must be an object"
            )

    return rows


def evaluate_stimuli(
    stimuli: list[dict[str, Any]],
    evaluator: Any,
    gate: Any,
) -> list[dict[str, Any]]:
    actuals: list[dict[str, Any]] = []

    for stimulus in stimuli:
        computed_state = evaluator.evaluate_policy_correctness(stimulus["constraint_id"], stimulus["facts"])

        gate_input = gate.PolicyCorrectnessGateInput(
            policy_artifact_id=stimulus["policy_artifact_id"],
            identity_state=stimulus["identity_state"],
            authority_state=stimulus["authority_state"],
            action_format_state=stimulus["action_format_state"],
            target_state=stimulus["target_state"],
            policy_parse_state=stimulus["policy_parse_state"],
            policy_load_state=stimulus["policy_load_state"],
            underlying_policy_decision=stimulus[
                "underlying_policy_decision"
            ],
            computed_correctness_state=computed_state,
        )

        decision = gate.evaluate_policy_correctness_gate(
            gate_input
        )

        actuals.append(
            {
                "stimulus_id": stimulus["stimulus_id"],
                "policy_artifact_id": stimulus[
                    "policy_artifact_id"
                ],
                "constraint_id": stimulus["constraint_id"],
                "underlying_policy_decision": (
                    decision.underlying_policy_decision
                ),
                "computed_correctness_state": computed_state,
                "actual_correctness_decision": (
                    decision.correctness_decision
                ),
                "actual_reason": decision.reason,
                "actual_execution_attempted": (
                    decision.execution_attempted
                ),
                "actual_side_effect": (
                    decision.side_effect_occurred
                ),
            }
        )

    return actuals


def load_oracle_matrix() -> list[dict[str, Any]]:
    rows = load_jsonl(MATRIX_PATH)

    if len(rows) != 10:
        raise ValueError(
            f"Expected 10 oracle rows; received {len(rows)}"
        )

    seen_tests: set[str] = set()
    seen_stimuli: set[str] = set()

    for row in rows:
        if set(row) != EXPECTED_ORACLE_FIELDS:
            raise ValueError(
                "Oracle field set differs from frozen SEP-03 schema"
            )

        if row["test_id"] in seen_tests:
            raise ValueError(
                f"Duplicate test_id: {row['test_id']}"
            )

        if row["stimulus_id"] in seen_stimuli:
            raise ValueError(
                f"Duplicate oracle stimulus_id: {row['stimulus_id']}"
            )

        seen_tests.add(row["test_id"])
        seen_stimuli.add(row["stimulus_id"])

    return rows


def compare_to_oracle(
    actuals: list[dict[str, Any]],
    oracle_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    actual_by_stimulus = {
        row["stimulus_id"]: row
        for row in actuals
    }

    if len(actual_by_stimulus) != len(actuals):
        raise ValueError(
            "Actual evaluation stimulus identities are not unique"
        )

    results: list[dict[str, Any]] = []

    for oracle in oracle_rows:
        stimulus_id = oracle["stimulus_id"]

        if stimulus_id not in actual_by_stimulus:
            raise ValueError(
                f"Oracle references absent actual stimulus: "
                f"{stimulus_id}"
            )

        actual = actual_by_stimulus[stimulus_id]

        checks = {
            "policy_artifact_id": (
                actual["policy_artifact_id"]
                == oracle["policy_artifact_id"]
            ),
            "constraint_id": (
                actual["constraint_id"]
                == oracle["constraint_id"]
            ),
            "underlying_policy_decision": (
                actual["underlying_policy_decision"]
                == oracle["expected_underlying_policy_decision"]
            ),
            "correctness_state": (
                actual["computed_correctness_state"]
                == oracle["expected_correctness_state"]
            ),
            "correctness_decision": (
                actual["actual_correctness_decision"]
                == oracle["expected_correctness_decision"]
            ),
            "reason": (
                actual["actual_reason"]
                == oracle["expected_reason"]
            ),
            "execution_attempted": (
                actual["actual_execution_attempted"]
                == oracle["expected_execution_attempted"]
            ),
            "side_effect": (
                actual["actual_side_effect"]
                == oracle["expected_side_effect"]
            ),
            "expected_case_result": (
                oracle["expected_case_result"] == "PASS"
            ),
        }

        case_result = (
            "PASS"
            if all(checks.values())
            else "FAIL"
        )

        results.append(
            {
                "test_id": oracle["test_id"],
                "stimulus_id": stimulus_id,
                "policy_artifact_id": actual[
                    "policy_artifact_id"
                ],
                "test_type": oracle["test_type"],
                "policy_failure_class": oracle[
                    "policy_failure_class"
                ],
                "constraint_id": actual["constraint_id"],
                "underlying_policy_decision": actual[
                    "underlying_policy_decision"
                ],
                "computed_correctness_state": actual[
                    "computed_correctness_state"
                ],
                "actual_correctness_decision": actual[
                    "actual_correctness_decision"
                ],
                "actual_reason": actual["actual_reason"],
                "actual_execution_attempted": actual[
                    "actual_execution_attempted"
                ],
                "actual_side_effect": actual[
                    "actual_side_effect"
                ],
                "expected_correctness_state": oracle[
                    "expected_correctness_state"
                ],
                "expected_correctness_decision": oracle[
                    "expected_correctness_decision"
                ],
                "expected_reason": oracle[
                    "expected_reason"
                ],
                "expected_execution_attempted": oracle[
                    "expected_execution_attempted"
                ],
                "expected_side_effect": oracle[
                    "expected_side_effect"
                ],
                "expected_underlying_policy_decision": oracle[
                    "expected_underlying_policy_decision"
                ],
                "checks": checks,
                "case_result": case_result,
            }
        )

    return results


def main() -> int:
    verify_bound_identities()

    evaluator = load_module(
        EVALUATOR_PATH,
        "sep03_policy_correctness_evaluator_v0_1",
    )

    gate = load_module(
        GATE_PATH,
        "sep03_policy_correctness_gate_v0_1",
    )

    stimuli = load_stimuli()

    actuals = evaluate_stimuli(
        stimuli,
        evaluator,
        gate,
    )

    oracle_rows = load_oracle_matrix()

    results = compare_to_oracle(
        actuals,
        oracle_rows,
    )

    passed = sum(
        result["case_result"] == "PASS"
        for result in results
    )

    failed = len(results) - passed

    policy_failure_cases = sum(
        row["test_type"] == "POLICY_FAILURE"
        for row in oracle_rows
    )

    benign_controls = sum(
        row["test_type"] == "BENIGN_CONTROL"
        for row in oracle_rows
    )

    summary = {
        "sep03_independent_evaluation": "EXECUTED",
        "evaluation_order": (
            "POLICY_STIMULUS_THEN_CORRECTNESS_EVALUATOR_"
            "THEN_COMPUTED_STATE_THEN_CORRECTNESS_GATE_"
            "THEN_ORACLE"
        ),
        "case_count": len(results),
        "policy_failure_cases": policy_failure_cases,
        "benign_controls": benign_controls,
        "passed": passed,
        "failed": failed,
        "primary_proposition": (
            "REQUIRES_POST_EXECUTION_DETERMINATION"
        ),
        "results": results,
    }

    print(
        json.dumps(
            summary,
            sort_keys=True,
            separators=(",", ":"),
        )
    )

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
